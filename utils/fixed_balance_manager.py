"""
Fixed Balance and User Management System
Handles WhatsApp users correctly with proper field mapping and automatic onboarding
"""

import logging
import os
from typing import Dict, Optional, Tuple
from supabase import create_client

logger = logging.getLogger(__name__)

class UserChannelManager:
    """Manages user identification across different channels (WhatsApp, Telegram)"""
    
    def __init__(self):
        self.supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    async def resolve_user_info(self, channel: str, identifier: str) -> Optional[Dict]:
        """
        Resolve user information from channel identifier
        
        Args:
            channel: 'whatsapp' or 'telegram'
            identifier: Phone number for WhatsApp, chat_id for Telegram
            
        Returns:
            Dict with user_id, channel_identifier, and user details
        """
        try:
            if channel == "whatsapp":
                # WhatsApp uses phone number as identifier
                # First check users table
                user_result = self.supabase.table("users").select("*").eq("whatsapp_number", identifier).execute()
                
                if user_result.data:
                    return {
                        "exists": True,
                        "user_id": user_result.data[0]["id"],
                        "user_data": user_result.data[0],
                        "channel": "whatsapp",
                        "identifier": identifier
                    }
                else:
                    return {
                        "exists": False,
                        "channel": "whatsapp",
                        "identifier": identifier
                    }
            
            elif channel == "telegram":
                # Telegram uses chat_id as identifier
                # Check for telegram_chat_id in users table
                user_result = self.supabase.table("users").select("*").eq("telegram_chat_id", identifier).execute()
                
                if user_result.data:
                    return {
                        "exists": True,
                        "user_id": user_result.data[0]["id"],
                        "user_data": user_result.data[0],
                        "channel": "telegram", 
                        "identifier": identifier
                    }
                else:
                    return {
                        "exists": False,
                        "channel": "telegram",
                        "identifier": identifier
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving user info for {channel}:{identifier} - {e}")
            return None

class FixedBalanceManager:
    """Fixed balance manager that uses correct field mappings"""
    
    def __init__(self):
        self.supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        self.user_manager = UserChannelManager()
    
    async def get_user_balance(self, channel: str, identifier: str) -> Tuple[float, Optional[str]]:
        """
        Get user balance with proper channel handling
        
        Args:
            channel: 'whatsapp' or 'telegram'
            identifier: Channel-specific identifier
            
        Returns:
            Tuple of (balance, user_id)
        """
        try:
            # Resolve user info first
            user_info = await self.user_manager.resolve_user_info(channel, identifier)
            
            if not user_info or not user_info.get("exists"):
                logger.warning(f"No user found for {channel}:{identifier}")
                return 0.0, None
            
            user_id = user_info["user_id"]
            
            # Get balance from virtual_accounts table using user_id
            va_result = self.supabase.table("virtual_accounts").select("balance, account_number, account_name, bank_name").eq("user_id", user_id).execute()
            
            if va_result.data:
                balance = float(va_result.data[0].get("balance", 0))
                
                # If balance is 0, sync from transactions
                if balance == 0:
                    balance = await self._sync_balance_from_transactions(user_id)
                
                return balance, str(user_id)
            else:
                logger.warning(f"No virtual account found for user_id {user_id}")
                return 0.0, str(user_id)
                
        except Exception as e:
            logger.error(f"Error getting balance for {channel}:{identifier} - {e}")
            return 0.0, None
    
    async def check_virtual_account(self, channel: str, identifier: str) -> Dict:
        """
        Check virtual account with proper channel handling
        
        Args:
            channel: 'whatsapp' or 'telegram'
            identifier: Channel-specific identifier
            
        Returns:
            Dict with virtual account details
        """
        try:
            # Resolve user info first
            user_info = await self.user_manager.resolve_user_info(channel, identifier)
            
            if not user_info or not user_info.get("exists"):
                return {
                    "success": False,
                    "error": "User not found - need to onboard",
                    "needs_onboarding": True
                }
            
            user_id = user_info["user_id"]
            user_data = user_info["user_data"]
            
            # Get virtual account details using user_id
            va_result = self.supabase.table("virtual_accounts").select("*").eq("user_id", user_id).execute()
            
            if va_result.data:
                account = va_result.data[0]
                
                # Get current balance
                balance, _ = await self.get_user_balance(channel, identifier)
                
                return {
                    "success": True,
                    "account_number": account.get("account_number"),
                    "account_name": account.get("account_name") or user_data.get("full_name"),
                    "bank_name": account.get("bank_name", "Sofi Digital Bank"),
                    "balance": balance,
                    "user_id": user_id,
                    "whatsapp_number": user_data.get("whatsapp_number"),
                    "created_at": account.get("created_at")
                }
            else:
                return {
                    "success": False,
                    "error": "Virtual account not found - contact support",
                    "user_id": user_id
                }
                
        except Exception as e:
            logger.error(f"Error checking virtual account for {channel}:{identifier} - {e}")
            return {
                "success": False,
                "error": f"Error checking account: {str(e)}"
            }
    
    async def _sync_balance_from_transactions(self, user_id: str) -> float:
        """Sync balance from transaction history"""
        try:
            # Get all successful transactions
            credit_result = self.supabase.table("bank_transactions").select("amount").eq("user_id", user_id).eq("transaction_type", "credit").eq("status", "success").execute()
            
            debit_result = self.supabase.table("bank_transactions").select("amount").eq("user_id", user_id).eq("transaction_type", "debit").eq("status", "success").execute()
            
            total_credits = sum(float(tx.get("amount", 0)) for tx in credit_result.data)
            total_debits = sum(float(tx.get("amount", 0)) for tx in debit_result.data)
            
            calculated_balance = max(0, total_credits - total_debits)
            
            # Update virtual_accounts table with synced balance
            self.supabase.table("virtual_accounts").update({"balance": calculated_balance}).eq("user_id", user_id).execute()
            
            logger.info(f"Synced balance for user {user_id}: {calculated_balance}")
            return calculated_balance
            
        except Exception as e:
            logger.error(f"Error syncing balance for user {user_id}: {e}")
            return 0.0

class AutoOnboardingManager:
    """Handles automatic onboarding for new WhatsApp users"""
    
    def __init__(self):
        self.user_manager = UserChannelManager()
    
    async def handle_new_whatsapp_user(self, phone_number: str) -> Dict:
        """
        Handle new WhatsApp user - check if exists, if not send onboarding
        
        Args:
            phone_number: WhatsApp phone number
            
        Returns:
            Dict with user status and action taken
        """
        try:
            user_info = await self.user_manager.resolve_user_info("whatsapp", phone_number)
            
            if user_info and user_info.get("exists"):
                logger.info(f"Existing WhatsApp user: {phone_number}")
                return {
                    "is_new_user": False,
                    "user_exists": True,
                    "user_id": user_info["user_id"],
                    "action": "proceed_with_request"
                }
            else:
                logger.info(f"New WhatsApp user detected: {phone_number}")
                
                # Send onboarding link
                await self._send_whatsapp_onboarding(phone_number)
                
                return {
                    "is_new_user": True,
                    "user_exists": False,
                    "action": "onboarding_sent",
                    "message": "Welcome to Sofi! I've sent you an onboarding link to get started."
                }
                
        except Exception as e:
            logger.error(f"Error handling new WhatsApp user {phone_number}: {e}")
            return {
                "is_new_user": None,
                "user_exists": False,
                "action": "error",
                "message": "Sorry, I'm having trouble right now. Please try again later."
            }
    
    async def _send_whatsapp_onboarding(self, phone_number: str):
        """Send WhatsApp onboarding link to new user"""
        try:
            from utils.whatsapp_api_fixed import whatsapp_api
            
            onboarding_message = """🎉 *Welcome to Sofi Digital Bank!*

I'm Sofi, your AI banking assistant. To get started, I need to set up your account.

Please click the link below to complete your registration:
👉 https://sofi-ai-deploy.onrender.com/whatsapp-onboard

*What you'll get:*
✅ Virtual account number for receiving money
✅ Send money to any Nigerian bank
✅ Check your balance anytime
✅ Transaction history and alerts
✅ 24/7 AI banking assistant

The setup takes just 2 minutes. Let's get you banking! 🚀"""
            
            await whatsapp_api.send_text_message(phone_number, onboarding_message)
            logger.info(f"Onboarding link sent to {phone_number}")
            
        except Exception as e:
            logger.error(f"Error sending onboarding to {phone_number}: {e}")

# Global instances
balance_manager = FixedBalanceManager()
onboarding_manager = AutoOnboardingManager()

# Convenience functions for backward compatibility
async def get_user_balance_fixed(channel: str, identifier: str) -> float:
    """Get user balance with proper channel handling"""
    balance, _ = await balance_manager.get_user_balance(channel, identifier)
    return balance

async def check_virtual_account_fixed(channel: str, identifier: str) -> Dict:
    """Check virtual account with proper channel handling"""
    return await balance_manager.check_virtual_account(channel, identifier)

async def handle_whatsapp_user_auto_onboard(phone_number: str) -> Dict:
    """Handle WhatsApp user with auto-onboarding"""
    return await onboarding_manager.handle_new_whatsapp_user(phone_number)
