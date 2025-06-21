"""
🎯 ADMIN COMMAND HANDLER

This module handles admin-specific commands like:
- "How much profit do I have?"
- "Sofi, I want to withdraw ₦50,000 profit"
- "Show me my profit report"
- "Mark withdrawal 123 as completed"

SECURITY: Only authorized admin chat IDs can access these commands.
"""

import re
import os
import logging
from typing import Dict, Optional
from utils.admin_profit_manager import profit_manager
from utils.admin_dashboard_live import admin_dashboard
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

class AdminCommandHandler:
    """Handles admin-specific commands for profit management"""
    
    def __init__(self):
        logger.info("🔐 Initializing Admin Command Handler...")
        
        # FORCE reload environment variables
        load_dotenv(override=True)
        
        # SECURITY: Load admin chat IDs from environment
        self.admin_chat_ids = self._load_admin_chat_ids()
        
        if self.admin_chat_ids:
            logger.info(f"✅ Admin security initialized. {len(self.admin_chat_ids)} authorized admin(s): {self.admin_chat_ids}")
        else:
            logger.warning("⚠️ No admin IDs loaded from environment!")
            # Try different environment variable names as fallback
            fallback_admin_id = os.getenv("ADMIN_CHAT_ID") or os.getenv("TELEGRAM_ADMIN_ID")
            if fallback_admin_id:
                self.admin_chat_ids = [fallback_admin_id]
                logger.info(f"✅ Found fallback admin ID: {fallback_admin_id}")
            else:
                logger.error("❌ CRITICAL: No admin access configured! Admin commands disabled.")
    
    def _load_admin_chat_ids(self):
        """Load admin chat IDs from environment"""
        try:
            # Force reload environment variables
            load_dotenv(override=True)
            
            # Load from environment variable
            admin_ids_str = os.getenv("ADMIN_CHAT_IDS", "")
            logger.info(f"🔍 Raw ADMIN_CHAT_IDS from env: '{admin_ids_str}'")
              # Debug: Print all environment variables starting with ADMIN
            admin_env_vars = {k: v for k, v in os.environ.items() if 'ADMIN' in k}
            logger.info(f"🔍 All ADMIN environment variables: {admin_env_vars}")
            
            if not admin_ids_str:
                logger.warning("⚠️ ADMIN_CHAT_IDS not configured! Admin commands will be disabled.")
                return []
            
            # Parse comma-separated admin IDs
            admin_ids = [id.strip() for id in admin_ids_str.split(",") if id.strip()]
            
            # Convert to integers and back to strings for validation
            validated_ids = []
            for admin_id in admin_ids:
                try:
                    # Validate it's a proper Telegram chat ID (integer)
                    int(admin_id)
                    validated_ids.append(admin_id)
                    logger.info(f"✅ Validated admin ID: {admin_id}")
                except ValueError:
                    logger.error(f"❌ Invalid admin chat ID format: {admin_id}")
            
            if validated_ids:
                logger.info(f"✅ Loaded {len(validated_ids)} admin chat ID(s)")
                return validated_ids
            else:
                logger.warning("⚠️ No valid admin chat IDs found!")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error loading admin chat IDs: {e}")
            return []
    
    def is_admin(self, chat_id: str) -> bool:
        """SECURITY: Check if the chat ID belongs to an authorized admin"""
        # Convert chat_id to string for comparison
        chat_id_str = str(chat_id)
        
        # SECURITY: If no admin IDs configured, DENY ALL ACCESS
        if not self.admin_chat_ids:
            logger.warning(f"🚨 Admin access denied for {chat_id_str}: No admin IDs configured")
            # Try to reload admin IDs once more
            self.admin_chat_ids = self._load_admin_chat_ids()
            if not self.admin_chat_ids:
                return False
        
        # Check if this chat ID is in the authorized admin list
        is_authorized = chat_id_str in self.admin_chat_ids
        
        if is_authorized:
            logger.info(f"✅ Admin access granted for chat ID: {chat_id_str}")
        else:
            logger.warning(f"🚨 Admin access DENIED for unauthorized chat ID: {chat_id_str}")
            logger.info(f"🔍 Authorized admin IDs: {self.admin_chat_ids}")
        
        return is_authorized
    
    async def detect_admin_command(self, message: str, chat_id: str) -> Optional[str]:
        """Detect if message is an admin command and return command type"""
        if not self.is_admin(chat_id):
            return None
        
        message_lower = message.lower()
        
        # Profit inquiry commands
        profit_patterns = [
            r'how much profit',
            r'what.*profit.*have',
            r'show.*profit',
            r'profit balance',
            r'total profit',
            r'my profit'
        ]
        
        # Withdrawal commands
        withdrawal_patterns = [
            r'withdraw.*profit',
            r'i want to withdraw',
            r'withdraw.*₦',
            r'take out.*profit'
        ]        
        # Dashboard commands
        dashboard_patterns = [
            r'how many.*deposit',
            r'deposit.*today',
            r'today.*deposit',
            r'dashboard',
            r'admin.*summary',
            r'business.*summary',
            r'today.*business',
            r'daily.*report',
            r'stats.*today'
        ]
        
        # Report commands
        report_patterns = [
            r'profit report',
            r'show.*report',
            r'business report',
            r'generate report'
        ]
          # Completion commands
        completion_patterns = [
            r'mark.*completed',
            r'completed.*withdrawal',
            r'opay.*done',
            r'withdrawal.*complete'
        ]
        
        for pattern in dashboard_patterns:
            if re.search(pattern, message_lower):
                return 'admin_dashboard'
        
        for pattern in profit_patterns:
            if re.search(pattern, message_lower):
                return 'profit_inquiry'
        
        for pattern in withdrawal_patterns:
            if re.search(pattern, message_lower):
                return 'profit_withdrawal'
        
        for pattern in report_patterns:
            if re.search(pattern, message_lower):
                return 'profit_report'
        
        for pattern in completion_patterns:
            if re.search(pattern, message_lower):
                return 'mark_completion'
        
        return None
    
    async def handle_admin_command(self, command_type: str, message: str, chat_id: str) -> str:
        """Process admin commands and return appropriate response"""
        try:
            if command_type == 'profit_inquiry':
                return await self._handle_profit_inquiry()
            
            elif command_type == 'profit_withdrawal':
                return await self._handle_profit_withdrawal(message, chat_id)
            
            elif command_type == 'profit_report':
                return await self._handle_profit_report(message)
            
            elif command_type == 'mark_completion':
                return await self._handle_mark_completion(message)
            
            elif command_type == 'admin_dashboard' or 'deposit' in message.lower() or 'today' in message.lower():
                return await self._handle_admin_dashboard()
            
            else:
                return "I didn't understand that admin command. Try asking about profit or requesting a withdrawal."
                
        except Exception as e:
            logger.error(f"Error handling admin command: {e}")
            return f"❌ Error processing admin command: {str(e)}"
    
    async def _handle_profit_inquiry(self) -> str:
        """Handle profit balance inquiries"""
        summary = await profit_manager.get_profit_summary()
        
        if 'error' in summary:
            return f"❌ Error getting profit info: {summary['error']}"
        
        available = summary['available_profit']
        total_earned = summary['total_profit_earned']
        total_withdrawn = summary['total_withdrawn']
        
        response = f"""
💰 **Boss, here's your profit summary:**

💵 **Available Profit:** ₦{available:,.2f}
📈 **Total Earned:** ₦{total_earned:,.2f}
📤 **Total Withdrawn:** ₦{total_withdrawn:,.2f}

"""
        
        # Add pending withdrawals info
        pending = summary.get('pending_withdrawals', [])
        if pending:
            response += f"⏳ **Pending Withdrawals:** {len(pending)} totaling ₦{sum(p['withdrawal_amount'] for p in pending):,.2f}\n"
        
        if available > 0:
            response += f"\n✅ Ready to withdraw? Just say: \"Sofi, I want to withdraw ₦{available:,.2f} profit\""
        else:
            response += f"\n📊 Keep growing! Your Sofi AI has processed {summary['total_profit_transactions']} profit transactions."
        
        return response
    
    async def _handle_profit_withdrawal(self, message: str, chat_id: str) -> str:
        """Handle profit withdrawal requests"""
        # Extract amount from message
        amount = self._extract_amount(message)
        
        if not amount:
            return "Please specify the amount you want to withdraw. Example: \"Sofi, I want to withdraw ₦50,000 profit\""
        
        # Process virtual withdrawal with admin ID validation
        result = await profit_manager.process_virtual_withdrawal(amount, chat_id)
        
        if result['success']:
            response = f"""
✅ **Withdrawal Processed!**

💰 **Amount:** ₦{amount:,.2f}
📊 **Balance Before:** ₦{result['balance_before']:,.2f}
📉 **Balance After:** ₦{result['balance_after']:,.2f}

🏦 **Next Step:** Complete the withdrawal manually via your Opay Merchant App or Dashboard.

⏰ **Reminder:** I've logged this withdrawal in your records. The profit balance has been updated immediately.
"""
            return response
        else:
            return f"❌ **Withdrawal Failed:** {result['error']}"
    
    async def _handle_profit_report(self, message: str) -> str:
        """Handle profit report requests"""
        # Extract days from message if specified
        days = 30  # default
        
        days_match = re.search(r'(\d+)\s*days?', message.lower())
        if days_match:
            days = int(days_match.group(1))
        
        report = await profit_manager.generate_profit_report(days)
        return report
    
    async def _handle_mark_completion(self, message: str) -> str:
        """Handle marking withdrawals as completed"""
        # Get pending withdrawals first
        pending = await profit_manager.get_pending_withdrawals()
        
        if not pending:
            return "✅ No pending withdrawals to mark as completed."
        
        # For simplicity, mark the most recent pending withdrawal as completed
        latest_withdrawal = pending[0]
        
        result = await profit_manager.mark_opay_completion(latest_withdrawal['id'], True)
        
        if result['success']:
            amount = latest_withdrawal['withdrawal_amount']
            return f"✅ **Withdrawal Completed!**\n\n₦{amount:,.2f} withdrawal has been marked as completed in Opay. Your records are now up to date!"
        else:
            return f"❌ Error marking completion: {result['error']}"
    
    async def _handle_admin_dashboard(self) -> str:
        """Handle admin dashboard queries - live database statistics"""
        try:
            # Generate live dashboard summary from Supabase
            dashboard_summary = await admin_dashboard.generate_admin_dashboard_summary()
            return dashboard_summary
            
        except Exception as e:
            logger.error(f"Error generating admin dashboard: {e}")
            return f"""❌ **Dashboard Error:** {str(e)}

📋 **Alternative Options:**
• Check your Supabase connection
• Verify database tables exist
• Try again in a few minutes

💡 **Need Help?** Contact your developer to troubleshoot the database connection."""
    
    def _extract_amount(self, message: str) -> Optional[float]:
        """Extract monetary amount from message"""
        # Look for patterns like ₦50,000 or 50000 or 50,000
        patterns = [
            r'₦([\d,]+(?:\.\d{2})?)',  # ₦50,000 or ₦50,000.00
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # 50,000 or 50,000.00
            r'(\d+(?:\.\d{2})?)'  # 50000 or 50000.00
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None

# No global instance - let main.py create it after environment loading
