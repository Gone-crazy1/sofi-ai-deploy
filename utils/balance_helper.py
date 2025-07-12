"""
💰 BALANCE CHECKING UTILITIES

Provides clean balance checking functions that work with the existing system
"""

import logging
from typing import Dict
from utils.permanent_memory import get_user_balance as secure_get_user_balance

logger = logging.getLogger(__name__)

async def get_user_balance(chat_id: str, force_sync: bool = True) -> float:
    """
    Get user balance with optional force sync to fix 0.00 display issue
    
    Args:
        chat_id: Telegram chat ID
        force_sync: Force balance sync between tables (default True)
        
    Returns:
        float: User's current balance
    """
    try:        # Get user ID from chat ID
        from supabase import create_client
        import os
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Try telegram_chat_id first, then chat_id as fallback
        user_result = client.table("users").select("id, wallet_balance").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            # Try with chat_id column as fallback
            user_result = client.table("users").select("id, wallet_balance").eq("chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            logger.error(f"User not found for chat_id {chat_id} (tried both telegram_chat_id and chat_id columns)")
            return 0.0
        
        user_id = user_result.data[0]["id"]
        current_wallet_balance = user_result.data[0].get("wallet_balance", 0)
        
        # Use secure balance checking
        balance_info = await secure_get_user_balance(str(user_id))
        
        if balance_info["success"]:
            real_balance = float(balance_info["balance"])
            
            # Force sync if there's a discrepancy and force_sync is True
            if force_sync and abs(real_balance - (current_wallet_balance or 0)) > 0.01:
                logger.info(f"Syncing balance for user {chat_id}: {current_wallet_balance} → {real_balance}")
                
                # Update wallet_balance in users table
                client.table("users").update({
                    "wallet_balance": real_balance
                }).eq("id", user_id).execute()
                
                # Also update virtual_accounts table if exists
                va_result = client.table("virtual_accounts").select("id").eq("user_id", user_id).execute()
                if va_result.data:
                    client.table("virtual_accounts").update({
                        "balance": real_balance
                    }).eq("user_id", user_id).execute()
            
            return real_balance
        else:
            logger.error(f"Error getting balance: {balance_info.get('error')}")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error in get_user_balance: {e}")
        return 0.0

async def check_virtual_account(chat_id: str) -> Dict:
    """
    Get virtual account details for a user - now with smart detection
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        dict: Virtual account information with proper status
    """
    try:
        from supabase import create_client
        import os
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # First get user ID from telegram_chat_id
        user_result = client.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            logger.error(f"User not found for chat_id {chat_id}")
            return {
                "status": "user_not_found",
                "accountNumber": "Not available",
                "bankName": "Wema Bank", 
                "accountName": "Not available",
                "balance": 0.0
            }
        
        user_id = user_result.data[0]["id"]
        
        # Get virtual account by user_id
        result = client.table("virtual_accounts").select("*").eq("user_id", user_id).execute()
        
        if result.data:
            account = result.data[0]
            account_number = account.get("account_number")
            
            # Check if account is properly set up
            if account_number and account_number != "Not available":
                return {
                    "status": "active",
                    "accountNumber": account_number,
                    "bankName": account.get("bank_name", "Wema Bank"),
                    "accountName": account.get("account_name", "Sofi User"),
                    "balance": account.get("balance", 0.0)
                }
            else:
                return {
                    "status": "incomplete_setup",
                    "accountNumber": "Setup in progress...",
                    "bankName": "Wema Bank",
                    "accountName": "Setup in progress...",
                    "balance": 0.0
                }
        else:
            logger.warning(f"No virtual account found for user_id {user_id}")
            return {
                "status": "not_created",
                "accountNumber": "Not available",
                "bankName": "Wema Bank",
                "accountName": "Not available",
                "balance": 0.0
            }
            
    except Exception as e:
        logger.error(f"Error checking virtual account: {e}")
        return {
            "status": "error",
            "accountNumber": "Not available",
            "bankName": "Wema Bank",
            "accountName": "Not available", 
            "balance": 0.0
        }

async def update_user_balance(user_id: str, new_balance: float) -> Dict:
    """
    Update user balance in Supabase
    
    Args:
        user_id: User ID
        new_balance: New balance amount
        
    Returns:
        dict: Success status and updated balance
    """
    try:
        from supabase import create_client
        import os
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Update balance in virtual_accounts table
        result = client.table("virtual_accounts").update({
            "balance": new_balance
        }).eq("user_id", user_id).execute()
        
        if result.data:
            logger.info(f"Successfully updated balance for user {user_id} to {new_balance}")
            return {
                "success": True,
                "balance": new_balance,
                "message": "Balance updated successfully"
            }
        else:
            logger.error(f"Failed to update balance for user {user_id}")
            return {
                "success": False,
                "error": "Failed to update balance in database"
            }
            
    except Exception as e:
        logger.error(f"Error updating user balance: {e}")
        return {
            "success": False,
            "error": str(e)
        }
