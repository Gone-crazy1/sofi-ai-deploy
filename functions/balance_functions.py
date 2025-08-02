"""
Balance-related functions for Sofi AI Assistant
Fixed to use proper WhatsApp field mapping and automatic onboarding
"""

import logging
from typing import Dict, Any
from supabase import create_client
import os
from utils.fixed_balance_manager import balance_manager, handle_whatsapp_user_auto_onboard
from flask import current_app as app

logger = logging.getLogger(__name__)

async def check_balance(chat_id: str, **kwargs) -> Dict[str, Any]:
    """
    Check user's account balance with proper WhatsApp handling
    
    Args:
        chat_id (str): User's WhatsApp phone number or Telegram chat ID
        
    Returns:
        Dict containing balance information
    """
    try:
        logger.info(f"💰 Checking balance for user {chat_id}")
        
        # Determine channel type (WhatsApp uses phone numbers, Telegram uses numeric IDs)
        if chat_id.startswith('+') or len(chat_id) >= 10:
            channel = "whatsapp"
        else:
            channel = "telegram"
        
        logger.info(f"📱 Detected channel: {channel} for identifier: {chat_id}")
        
        # For WhatsApp users, check if they need onboarding first
        if channel == "whatsapp":
            user_status = await handle_whatsapp_user_auto_onboard(chat_id)
            
            if user_status["is_new_user"]:
                return {
                    "success": False,
                    "error": "Account setup required",
                    "message": user_status["message"],
                    "action": "onboarding_sent",
                    "balance": 0
                }
        
        # Check virtual account using fixed manager
        virtual_account = await balance_manager.check_virtual_account(channel, chat_id)
        
        if not virtual_account["success"]:
            if virtual_account.get("needs_onboarding"):
                return {
                    "success": False,
                    "error": "No account found. Please complete registration first.",
                    "balance": 0,
                    "account_number": None,
                    "bank_name": None,
                    "action": "needs_onboarding"
                }
            else:
                return {
                    "success": False,
                    "error": virtual_account.get("error", "Account not found"),
                    "balance": 0,
                    "account_number": None,
                    "bank_name": None
                }
        
        # Get current balance using fixed manager
        current_balance, user_id = await balance_manager.get_user_balance(channel, chat_id)
        
        # Format response
        return {
            "success": True,
            "balance": float(current_balance),
            "formatted_balance": f"₦{current_balance:,.2f}",
            "account_number": virtual_account.get("account_number"),
            "bank_name": virtual_account.get("bank_name", "Sofi Digital Bank"),
            "account_name": virtual_account.get("account_name"),
            "currency": "NGN",
            "user_id": user_id,
            "channel": channel
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking balance for {chat_id}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to check balance: {str(e)}",
            "balance": 0,
            "action": "retry"
        }
