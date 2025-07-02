"""
💰 BALANCE CHECKING UTILITIES

Provides clean balance checking functions that work with the existing system
"""

import logging
from typing import Dict
from utils.permanent_memory import get_user_balance as secure_get_user_balance

logger = logging.getLogger(__name__)

async def get_user_balance(chat_id: str) -> float:
    """
    Get user balance - simplified interface for backward compatibility
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        float: User's current balance
    """
    try:        # Get user ID from chat ID
        from supabase import create_client
        import os
        
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Try telegram_chat_id first, then chat_id as fallback
        user_result = client.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            # Try with chat_id column as fallback
            user_result = client.table("users").select("id").eq("chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            logger.error(f"User not found for chat_id {chat_id} (tried both telegram_chat_id and chat_id columns)")
            return 0.0
        
        user_id = user_result.data[0]["id"]
        
        # Use secure balance checking
        balance_info = await secure_get_user_balance(str(user_id))
        
        if balance_info["success"]:
            return float(balance_info["balance"])
        else:
            logger.error(f"Error getting balance: {balance_info.get('error')}")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error in get_user_balance: {e}")
        return 0.0

async def check_virtual_account(chat_id: str) -> Dict:
    """
    Get virtual account details for a user
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        dict: Virtual account information
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
                "accountNumber": "Not available",
                "bankName": "Moniepoint MFB", 
                "accountName": "Not available",
                "balance": 0.0
            }
        
        user_id = user_result.data[0]["id"]
        
        # Get virtual account by user_id
        result = client.table("virtual_accounts").select("*").eq("user_id", user_id).execute()
        
        if result.data:
            account = result.data[0]
            return {
                "accountNumber": account.get("account_number"),
                "bankName": account.get("bank_name", "Wema Bank"),
                "accountName": account.get("account_name", "Sofi User"),
                "balance": account.get("balance", 0.0)
            }
        else:
            logger.warning(f"No virtual account found for user_id {user_id}")
            return {
                "accountNumber": "Not available",
                "bankName": "Wema Bank",
                "accountName": "Not available",
                "balance": 0.0
            }
            
    except Exception as e:
        logger.error(f"Error checking virtual account: {e}")
        return {
            "accountNumber": "Not available",
            "bankName": "Wema Bank",
            "accountName": "Not available", 
            "balance": 0.0
        }
