"""
📲 ENHANCED NOTIFICATION SYSTEM

Comprehensive notification system for Sofi AI that ensures:
1. Users get notified on all deposits
2. Admin gets notified on profits
3. Real-time balance updates
4. Beautiful notification formatting
"""

import os
import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
logger = logging.getLogger(__name__)

class NotificationManager:
    """Enhanced notification system for Sofi AI"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        self.telegram_api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_deposit_notification(self, user_id: str, amount: float, balance: float, 
                                      account_name: str, reference: str) -> bool:
        """Send beautiful deposit notification to user"""
        try:
            # Get user's full name and chat ID
            user_result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                logger.error(f"User {user_id} not found for deposit notification")
                return False
            
            user = user_result.data[0]
            chat_id = user.get("telegram_id")
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            # Create beautiful notification message
            message = f"""
🎉 **DEPOSIT CONFIRMED!**

💰 **Amount:** ₦{amount:,.2f}
📊 **New Balance:** ₦{balance:,.2f}
👤 **Account:** {account_name}
🔢 **Reference:** {reference}
⏰ **Time:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

✅ **Hi {full_name}!** Your deposit has been successfully credited to your Sofi AI account. You can now make transfers, buy airtime, or trade crypto!

💡 **What's next?**
• Type "Balance" to check your balance
• Type "Transfer" to send money
• Type "Menu" to see all options
"""
            
            # Send notification
            success = await self._send_telegram_message(chat_id, message)
            
            if success:
                # Log notification
                await self._log_notification(user_id, "deposit", {
                    "amount": amount,
                    "balance": balance,
                    "reference": reference
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending deposit notification: {e}")
            return False
    
    async def send_transfer_confirmation(self, user_id: str, recipient_name: str, 
                                       amount: float, fee: float, reference: str) -> bool:
        """Send transfer confirmation notification"""
        try:
            user_result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                return False
            
            user = user_result.data[0]
            chat_id = user.get("telegram_id")
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            message = f"""
✅ **TRANSFER SUCCESSFUL!**

👤 **From:** {full_name}
🎯 **To:** {recipient_name}
💰 **Amount:** ₦{amount:,.2f}
💸 **Fee:** ₦{fee:,.2f}
🔢 **Reference:** {reference}
⏰ **Time:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

🎉 **Transfer completed successfully!** The recipient will receive the money within minutes.

📊 Type "Balance" to check your updated balance
📋 Type "History" to see your transaction history
"""
            
            return await self._send_telegram_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending transfer confirmation: {e}")
            return False
    
    async def send_low_balance_alert(self, user_id: str, balance: float, attempted_amount: float) -> bool:
        """Send low balance alert"""
        try:
            user_result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                return False
            
            user = user_result.data[0]
            chat_id = user.get("telegram_id")
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            message = f"""
⚠️ **INSUFFICIENT BALANCE**

👤 **Hi {full_name}!**
💰 **Current Balance:** ₦{balance:,.2f}
❌ **Attempted Amount:** ₦{attempted_amount:,.2f}

💡 **To complete this transaction:**
1. Add more funds to your account
2. Try a smaller amount

🏦 **Fund your account by transferring to your Sofi AI account number**
📞 **Need help? Contact support**
"""
            
            return await self._send_telegram_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending low balance alert: {e}")
            return False
    
    async def send_admin_profit_notification(self, transaction_type: str, profit_amount: float, 
                                           total_profit: float) -> bool:
        """Send profit notification to admin"""
        try:
            # Load admin chat IDs
            admin_settings = self.supabase.table("system_settings").select("setting_value").eq("setting_key", "admin_chat_ids").execute()
            
            admin_ids = []
            if admin_settings.data:
                import json
                admin_ids = json.loads(admin_settings.data[0]["setting_value"])
            
            # Fallback to environment variable
            if not admin_ids:
                env_admin_ids = os.getenv("ADMIN_CHAT_IDS", "").split(",")
                admin_ids = [id.strip() for id in env_admin_ids if id.strip()]
            
            if not admin_ids:
                logger.warning("No admin chat IDs configured for profit notifications")
                return False
            
            message = f"""
💰 **NEW PROFIT EARNED!**

📈 **Transaction Type:** {transaction_type.title()}
💵 **Profit Amount:** ₦{profit_amount:,.2f}
📊 **Total Profit:** ₦{total_profit:,.2f}
⏰ **Time:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

🎯 **Your Sofi AI is making money!**
Type "How much profit do I have?" to see full details.
"""
            
            # Send to all admin chat IDs
            success_count = 0
            for admin_id in admin_ids:
                if await self._send_telegram_message(admin_id, message):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending admin profit notification: {e}")
            return False
    
    async def send_system_alert(self, alert_type: str, message: str, is_critical: bool = False) -> bool:
        """Send system alerts to admin"""
        try:
            # Load admin chat IDs
            admin_settings = self.supabase.table("system_settings").select("setting_value").eq("setting_key", "admin_chat_ids").execute()
            
            admin_ids = []
            if admin_settings.data:
                import json
                admin_ids = json.loads(admin_settings.data[0]["setting_value"])
            
            if not admin_ids:
                env_admin_ids = os.getenv("ADMIN_CHAT_IDS", "").split(",")
                admin_ids = [id.strip() for id in env_admin_ids if id.strip()]
            
            if not admin_ids:
                logger.warning("No admin chat IDs configured for system alerts")
                return False
            
            icon = "🚨" if is_critical else "⚠️"
            alert_msg = f"""
{icon} **SYSTEM ALERT - {alert_type.upper()}**

{message}

⏰ **Time:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
🤖 **Source:** Sofi AI System Monitor
"""
            
            # Send to all admin chat IDs
            success_count = 0
            for admin_id in admin_ids:
                if await self._send_telegram_message(admin_id, alert_msg):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending system alert: {e}")
            return False
    
    async def _send_telegram_message(self, chat_id: str, message: str) -> bool:
        """Send message via Telegram Bot API"""
        try:
            url = f"{self.telegram_api_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def _log_notification(self, user_id: str, notification_type: str, metadata: Dict) -> bool:
        """Log notification for tracking"""
        try:
            log_data = {
                "user_id": user_id,
                "notification_type": notification_type,
                "metadata": metadata,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # Create notifications log table if it doesn't exist
            # This would be better in a migration, but adding here for completeness
            try:
                self.supabase.table("notification_logs").insert(log_data).execute()
            except:
                # Table might not exist, that's ok for now
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
            return False

# Global notification manager instance
notification_manager = NotificationManager()

# Convenience functions for easy import
async def notify_deposit(user_id: str, amount: float, balance: float, account_name: str, reference: str):
    """Send deposit notification"""
    return await notification_manager.send_deposit_notification(user_id, amount, balance, account_name, reference)

async def notify_transfer(user_id: str, recipient_name: str, amount: float, fee: float, reference: str):
    """Send transfer confirmation"""
    return await notification_manager.send_transfer_confirmation(user_id, recipient_name, amount, fee, reference)

async def notify_low_balance(user_id: str, balance: float, attempted_amount: float):
    """Send low balance alert"""
    return await notification_manager.send_low_balance_alert(user_id, balance, attempted_amount)

async def notify_admin_profit(transaction_type: str, profit_amount: float, total_profit: float):
    """Send admin profit notification"""
    return await notification_manager.send_admin_profit_notification(transaction_type, profit_amount, total_profit)

async def send_system_alert(alert_type: str, message: str, is_critical: bool = False):
    """Send system alert to admin"""
    return await notification_manager.send_system_alert(alert_type, message, is_critical)
