"""
Balance Checking Utilities

Provides clean balance checking functions that work with the existing system
"""

import logging
import os
from typing import Dict

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
    try:
        # Try to use secure balance function if available
        try:
            from utils.permanent_memory import get_user_balance as secure_get_user_balance
            return await secure_get_user_balance(chat_id)
        except ImportError:
            pass
        
        # Fallback to direct database query
        from supabase import create_client
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Try telegram_chat_id first, then chat_id as fallback
        result = client.table("virtual_accounts").select("balance, user_id").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not result.data:
            # Try with chat_id field as fallback
            result = client.table("virtual_accounts").select("balance, user_id").eq("chat_id", str(chat_id)).execute()
        
        if result.data:
            current_balance = float(result.data[0].get("balance", 0))
            user_id = result.data[0].get("user_id")
            
            if force_sync and user_id:
                # Force sync balance from transactions if balance is 0
                if current_balance == 0:
                    synced_balance = await sync_balance_from_transactions(user_id)
                    if synced_balance > 0:
                        # Update the balance in virtual_accounts
                        client.table("virtual_accounts").update({
                            "balance": synced_balance
                        }).eq("user_id", user_id).execute()
                        return synced_balance
            
            return current_balance
        else:
            logger.warning(f"No virtual account found for chat_id: {chat_id}")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error getting user balance for {chat_id}: {e}")
        return 0.0

async def sync_balance_from_transactions(user_id: str) -> float:
    """
    Calculate balance from transaction history
    
    Args:
        user_id: User ID
        
    Returns:
        float: Calculated balance from transactions
    """
    try:
        from supabase import create_client
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get all successful transactions for the user
        credit_result = client.table("bank_transactions").select("amount").eq("user_id", user_id).eq("transaction_type", "credit").eq("status", "success").execute()
        
        debit_result = client.table("bank_transactions").select("amount").eq("user_id", user_id).eq("transaction_type", "debit").eq("status", "success").execute()
        
        total_credits = sum(float(tx.get("amount", 0)) for tx in credit_result.data)
        total_debits = sum(float(tx.get("amount", 0)) for tx in debit_result.data)
        
        calculated_balance = total_credits - total_debits
        
        logger.info(f"Synced balance for user {user_id}: Credits={total_credits}, Debits={total_debits}, Balance={calculated_balance}")
        
        return max(0, calculated_balance)  # Never return negative balance
        
    except Exception as e:
        logger.error(f"Error syncing balance from transactions for user {user_id}: {e}")
        return 0.0

async def check_virtual_account(chat_id: str) -> Dict:
    """
    Check virtual account details for a user
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        Dict: Virtual account information
    """
    try:
        from supabase import create_client
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get virtual account details
        result = client.table("virtual_accounts").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not result.data:
            # Try with chat_id field as fallback
            result = client.table("virtual_accounts").select("*").eq("chat_id", str(chat_id)).execute()
        
        if result.data:
            account = result.data[0]
            return {
                "success": True,
                "account_number": account.get("account_number", "N/A"),
                "account_name": account.get("account_name", "N/A"),
                "bank_name": account.get("bank_name", "N/A"),
                "balance": float(account.get("balance", 0)),
                "user_id": account.get("user_id"),
                "created_at": account.get("created_at")
            }
        else:
            return {
                "success": False,
                "error": "Virtual account not found",
                "account_number": "N/A",
                "account_name": "N/A",
                "bank_name": "N/A",
                "balance": 0.0
            }
            
    except Exception as e:
        logger.error(f"Error checking virtual account for {chat_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "account_number": "N/A",
            "account_name": "N/A",
            "bank_name": "N/A",
            "balance": 0.0
        }

async def update_user_balance(chat_id: str, new_balance: float) -> bool:
    """
    Update user balance in virtual_accounts table
    
    Args:
        chat_id: Telegram chat ID
        new_balance: New balance to set
        
    Returns:
        bool: Success status
    """
    try:
        from supabase import create_client
        from datetime import datetime
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Update balance
        result = client.table("virtual_accounts").update({
            "balance": new_balance,
            "updated_at": datetime.now().isoformat()
        }).eq("telegram_chat_id", str(chat_id)).execute()
        
        if not result.data:
            # Try with chat_id field as fallback
            result = client.table("virtual_accounts").update({
                "balance": new_balance,
                "updated_at": datetime.now().isoformat()
            }).eq("chat_id", str(chat_id)).execute()
        
        if result.data:
            logger.info(f"Updated balance for {chat_id} to {new_balance}")
            return True
        else:
            logger.warning(f"Failed to update balance for {chat_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating balance for {chat_id}: {e}")
        return False

async def get_balance_with_formatting(chat_id: str) -> str:
    """
    Get formatted balance string for display
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        str: Formatted balance message
    """
    try:
        balance = await get_user_balance(chat_id)
        account_info = await check_virtual_account(chat_id)
        
        if account_info["success"]:
            return f"""💰 **Your Sofi Wallet Balance**

Current Balance: ₦{balance:,.2f}

📋 **Account Details:**
• Account Number: {account_info['account_number']}
• Account Name: {account_info['account_name']}
• Bank: {account_info['bank_name']}

💡 You can send money, buy airtime, or save with Sofi AI!"""
        else:
            return f"""💰 **Your Sofi Wallet Balance**

Current Balance: ₦{balance:,.2f}

⚠️ Account details not available. Contact support if needed.

💡 You can send money, buy airtime, or save with Sofi AI!"""
            
    except Exception as e:
        logger.error(f"Error formatting balance for {chat_id}: {e}")
        return "❌ Unable to retrieve balance. Please try again later."
