"""
Balance-related functions for Sofi AI Assistant
Handles balance checking and account information
"""

import logging
from typing import Dict, Any
from supabase import create_client
import os
from utils.balance_helper import get_user_balance as get_balance_secure, check_virtual_account as check_virtual_account_secure

logger = logging.getLogger(__name__)

async def check_balance(chat_id: str, **kwargs) -> Dict[str, Any]:
    """
    Check user's account balance
    
    Args:
        chat_id (str): User's Telegram chat ID
        
    Returns:
        Dict containing balance information
    """
    try:
        logger.info(f"💰 Checking balance for user {chat_id}")
        
        # Check if user has virtual account
        virtual_account = await check_virtual_account_secure(str(chat_id))
        
        if not virtual_account:
            return {
                "success": False,
                "error": "No virtual account found. Please complete registration first.",
                "balance": 0,
                "account_number": None,
                "bank_name": None
            }
        
        # Get current balance
        current_balance = await get_balance_secure(str(chat_id))
        
        # Get account details
        account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number")
        bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Paystack Bank")
        account_name = virtual_account.get("accountName") or virtual_account.get("account_name")
        
        # Get user profile for full name
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        
        full_name = account_name
        if user_result.data:
            user_data = user_result.data[0]
            full_name = user_data.get('full_name', account_name)
        
        return {
            "success": True,
            "balance": float(current_balance),
            "formatted_balance": f"₦{current_balance:,.2f}",
            "account_number": account_number,
            "bank_name": bank_name,
            "account_name": full_name,
            "currency": "NGN"
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking balance for {chat_id}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to check balance: {str(e)}",
            "balance": 0
        }
