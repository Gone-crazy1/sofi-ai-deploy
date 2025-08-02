"""
WhatsApp Balance Helper for Sofi AI
===================================
Integrates with existing Supabase schema to check user balances
"""

import logging
from typing import Optional
from utils.whatsapp_account_manager_simple import whatsapp_account_manager

logger = logging.getLogger(__name__)

async def get_user_balance(whatsapp_number: str) -> float:
    """
    Get user balance by WhatsApp number
    
    Args:
        whatsapp_number: User's WhatsApp number (e.g., +2348056487759)
        
    Returns:
        float: Account balance in naira (0.0 if not found)
    """
    try:
        balance = await whatsapp_account_manager.get_account_balance(whatsapp_number)
        logger.info(f"Balance retrieved for {whatsapp_number}: ₦{balance:,.2f}")
        return balance
        
    except Exception as e:
        logger.error(f"Error getting balance for {whatsapp_number}: {e}")
        return 0.0

async def format_balance_message(whatsapp_number: str) -> str:
    """
    Format balance information for WhatsApp message
    
    Args:
        whatsapp_number: User's WhatsApp number
        
    Returns:
        str: Formatted balance message
    """
    try:
        # Get user details
        user = await whatsapp_account_manager.get_user_by_whatsapp(whatsapp_number)
        
        if not user:
            return "❌ Account not found. Please create a Sofi account first by saying 'create account'."
        
        # Get account and balance
        account = await whatsapp_account_manager.get_virtual_account(whatsapp_number)
        balance = await get_user_balance(whatsapp_number)
        
        if not account:
            return "❌ Virtual account not found. Please contact support."
        
        # Format message
        message = f"""💰 **Account Balance**

👤 **Name:** {user.get('full_name', 'N/A')}
🏦 **Account:** {account.get('account_number', 'N/A')}
🏪 **Bank:** {account.get('bank_name', 'Wema Bank')}
💵 **Balance:** ₦{balance:,.2f}

📲 **What's Next?**
• Send money to friends/family
• Buy airtime or data
• Fund your account using your account number above
• Ask me anything else!"""
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting balance message: {e}")
        return "❌ Unable to check balance right now. Please try again later."

async def check_account_exists(whatsapp_number: str) -> bool:
    """
    Check if user has a Sofi account
    
    Args:
        whatsapp_number: User's WhatsApp number
        
    Returns:
        bool: True if account exists
    """
    try:
        user = await whatsapp_account_manager.get_user_by_whatsapp(whatsapp_number)
        return user is not None
    except Exception as e:
        logger.error(f"Error checking account existence: {e}")
        return False
