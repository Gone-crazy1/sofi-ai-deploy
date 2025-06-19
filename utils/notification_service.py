"""
Enhanced Notification System for Sofi AI

This module provides comprehensive notification features for:
- Deposit alerts
- Transfer notifications  
- Balance updates
- Transaction summaries
- Rich formatting and emoji support
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional, List
import requests
from supabase import create_client
from dotenv import load_dotenv
import sys
from beautiful_receipt_generator import receipt_generator

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

logger = logging.getLogger(__name__)

class NotificationService:
    """Enhanced notification service for Sofi AI"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
        
    def format_currency(self, amount: float) -> str:
        """Format currency with proper Nigerian Naira formatting"""
        return f"₦{amount:,.2f}"
    
    def get_transaction_emoji(self, transaction_type: str) -> str:
        """Get appropriate emoji for transaction type"""
        emoji_map = {
            "credit": "💰",
            "debit": "💸", 
            "deposit": "🏦",
            "transfer": "📤",
            "airtime": "📱",
            "withdrawal": "💳",
            "fee": "💳"
        }
        return emoji_map.get(transaction_type.lower(), "💳")
    
    def get_status_emoji(self, status: str) -> str:
        """Get appropriate emoji for transaction status"""
        status_map = {
            "success": "✅",
            "successful": "✅",
            "completed": "✅",
            "failed": "❌",
            "pending": "⏳",
            "processing": "🔄"
        }
        return status_map.get(status.lower(), "ℹ️")
    
    async def send_deposit_alert(self, user_data: Dict, transaction_data: Dict) -> bool:
        """Send enhanced deposit alert to user"""
        try:
            chat_id = user_data.get('chat_id')
            if not chat_id:
                logger.error("No chat_id found for deposit alert")
                return False
            
            amount = float(transaction_data.get('amount', 0))
            account_number = transaction_data.get('account_number', 'N/A')
            reference = transaction_data.get('reference', 'N/A')
            sender_name = transaction_data.get('sender_name', 'Unknown')
            sender_bank = transaction_data.get('sender_bank', 'Unknown Bank')
            
            # Get updated balance            # Get user's current balance
            balance = await self.get_user_balance(user_data.get('user_id'))
            
            # Get user's name for personalized greeting
            user_name = user_data.get('full_name', 'there')
            first_name = user_name.split()[0] if user_name else 'there'
            
            # Create rich, branded notification message with sender details
            message = f"""
💰 *MONEY RECEIVED!*

Hey {first_name}! 👋

You just received {self.format_currency(amount)} in your Sofi Wallet!

� *Transfer Details:*
• From: {sender_name}
• Bank: {sender_bank}
• Account: {account_number}
• Purpose: {transaction_data.get('narration', 'Transfer')}
• Amount: {self.format_currency(amount)}
• Your New Balance: {self.format_currency(balance)}

⏰ Received: {datetime.now().strftime('%I:%M %p, %B %d, %Y')}
✅ Status: Confirmed & Secured

� *What happens next?*
• Money is instantly available in your wallet
• No fees charged for receiving money  
• You can transfer, buy airtime, or withdraw anytime

🎯 *Quick Actions:*
• Type "balance" to check your wallet
• Type "transfer" to send money to others
• Type "airtime" to buy airtime/data

Thanks for using Sofi AI Wallet! 
*Powered by Pip install -ai Tech* 🚀
            """
            
            # Send notification
            success = await self.send_telegram_message(chat_id, message)
            
            if success:
                # Log notification
                await self.log_notification_sent(user_data.get('user_id'), 'deposit_alert', transaction_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending deposit alert: {e}")
            return False
    
    async def send_transfer_alert(self, user_data: Dict, transaction_data: Dict) -> bool:
        """Send transfer completion alert to user"""
        try:
            chat_id = user_data.get('chat_id')
            if not chat_id:
                logger.error("No chat_id found for transfer alert")
                return False
            
            amount = float(transaction_data.get('amount', 0))
            recipient_name = transaction_data.get('recipient_name', 'N/A')
            recipient_bank = transaction_data.get('recipient_bank', 'N/A')
            recipient_account = transaction_data.get('recipient_account', 'N/A')
            reference = transaction_data.get('reference', 'N/A')
            status = transaction_data.get('status', 'completed')
            
            # Get updated balance
            balance = await self.get_user_balance(user_data.get('user_id'))
            
            status_emoji = self.get_status_emoji(status)
            
            if status.lower() in ['success', 'successful', 'completed']:
                message = f"""
{status_emoji} *TRANSFER COMPLETED!*

💸 *Amount Sent:* {self.format_currency(amount)}
👤 *To:* {recipient_name}
🏦 *Bank:* {recipient_bank}
📍 *Account:* {recipient_account}
📝 *Reference:* {reference}
⏰ *Time:* {datetime.now().strftime('%d %b %Y, %I:%M %p')}

💳 *Remaining Balance:* {self.format_currency(balance)}

✅ *Transfer successful!*
_Powered by OPay_
                """
            else:
                message = f"""
{status_emoji} *TRANSFER {status.upper()}*

💸 *Amount:* {self.format_currency(amount)}
👤 *To:* {recipient_name}
🏦 *Bank:* {recipient_bank}
📝 *Reference:* {reference}
⏰ *Time:* {datetime.now().strftime('%d %b %Y, %I:%M %p')}

💳 *Current Balance:* {self.format_currency(balance)}

Status: *{status.title()}*
_We'll notify you when the status changes_
                """
            
            success = await self.send_telegram_message(chat_id, message)
            
            if success:
                await self.log_notification_sent(user_data.get('user_id'), 'transfer_alert', transaction_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending transfer alert: {e}")
            return False
    
    async def send_airtime_alert(self, user_data: Dict, transaction_data: Dict) -> bool:
        """Send airtime purchase alert to user"""
        try:
            chat_id = user_data.get('chat_id')
            if not chat_id:
                return False
            
            amount = float(transaction_data.get('amount', 0))
            phone_number = transaction_data.get('phone_number', 'N/A')
            network = transaction_data.get('network', 'N/A')
            reference = transaction_data.get('reference', 'N/A')
            status = transaction_data.get('status', 'completed')
            
            balance = await self.get_user_balance(user_data.get('user_id'))
            status_emoji = self.get_status_emoji(status)
            
            message = f"""
{status_emoji} *AIRTIME PURCHASE {status.upper()}!*

📱 *Amount:* {self.format_currency(amount)}
📞 *Phone:* {phone_number}
🌐 *Network:* {network}
📝 *Reference:* {reference}
⏰ *Time:* {datetime.now().strftime('%d %b %Y, %I:%M %p')}

💳 *Remaining Balance:* {self.format_currency(balance)}

{'✅ Airtime delivered successfully!' if status.lower() == 'success' else f'Status: {status.title()}'}
_Powered by OPay_
            """
            
            success = await self.send_telegram_message(chat_id, message)
            
            if success:
                await self.log_notification_sent(user_data.get('user_id'), 'airtime_alert', transaction_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending airtime alert: {e}")
            return False
    
    async def send_low_balance_alert(self, user_data: Dict, current_balance: float, threshold: float = 1000.0) -> bool:
        """Send low balance warning to user"""
        try:
            if current_balance > threshold:
                return True  # No need to send alert
                
            chat_id = user_data.get('chat_id')
            if not chat_id:
                return False
            
            message = f"""
⚠️ *LOW BALANCE ALERT*

Your current balance is: *{self.format_currency(current_balance)}*

This is below the recommended minimum of {self.format_currency(threshold)}.

💡 *To add funds:*
• Send money to your virtual account
• Account: {user_data.get('account_number', 'N/A')}
• Bank: OPay

Type /account to see your account details! 🏦
            """
            
            return await self.send_telegram_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending low balance alert: {e}")
            return False
    
    async def send_daily_summary(self, user_data: Dict) -> bool:
        """Send daily transaction summary to user"""
        try:
            chat_id = user_data.get('chat_id')
            user_id = user_data.get('user_id')
            
            if not chat_id or not user_id:
                return False
            
            # Get today's transactions
            today = datetime.now().date()
            transactions = await self.get_user_transactions_for_date(user_id, today)
            
            if not transactions:
                return True  # No transactions today
            
            # Calculate summary
            credits = sum(t['amount'] for t in transactions if t['transaction_type'] == 'credit')
            debits = sum(t['amount'] for t in transactions if t['transaction_type'] == 'debit')
            total_transactions = len(transactions)
            
            current_balance = await self.get_user_balance(user_id)
            
            message = f"""
📊 *DAILY SUMMARY - {today.strftime('%d %b %Y')}*

💰 *Money In:* {self.format_currency(credits)}
💸 *Money Out:* {self.format_currency(debits)}
📈 *Net Change:* {self.format_currency(credits - debits)}
🔢 *Total Transactions:* {total_transactions}

💳 *Current Balance:* {self.format_currency(current_balance)}

Have a great day! 🌟
_Your daily summary from Sofi AI - Powered by Pip install -ai Tech_
            """
            
            return await self.send_telegram_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    async def send_telegram_message(self, chat_id: str, message: str, parse_mode: str = "Markdown") -> bool:
        """Send message to Telegram user with enhanced formatting"""
        try:
            if not self.bot_token:
                logger.error("Telegram bot token not configured")
                return False
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def get_user_balance(self, user_id: str) -> float:
        """Get current user balance"""
        try:
            if not supabase:
                return 0.0
            
            # Try different possible column names for user identification
            response = None
            for id_column in ['user_id', 'telegram_chat_id']:
                try:
                    response = supabase.table('virtual_accounts').select('balance').eq(id_column, user_id).execute()
                    if response.data:
                        break
                except:
                    continue
            
            if response and response.data:
                return float(response.data[0].get('balance', 0.0))
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return 0.0
    
    async def get_user_transactions_for_date(self, user_id: str, date) -> List[Dict]:
        """Get user transactions for a specific date"""
        try:
            if not supabase:
                return []
            
            start_date = f"{date}T00:00:00"
            end_date = f"{date}T23:59:59"
            
            response = supabase.table('bank_transactions').select('*').eq('user_id', user_id).gte('created_at', start_date).lte('created_at', end_date).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting user transactions: {e}")
            return []
    
    async def log_notification_sent(self, user_id: str, notification_type: str, transaction_data: Dict) -> bool:
        """Log notification sent for tracking"""
        try:
            if not supabase:
                return False
            
            log_data = {
                "user_id": user_id,
                "notification_type": notification_type,
                "transaction_reference": transaction_data.get('reference'),
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            
            supabase.table('notification_logs').insert(log_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
            return False
        
    async def send_transfer_receipt(self, user_data: dict, transaction_data: dict) -> bool:
        """
        Send beautiful transfer receipt to user
        
        Args:
            user_data: Dict with user information (user_id, chat_id, etc.)
            transaction_data: Dict with transaction details
            
        Returns:
            bool: Success status
        """
        try:
            chat_id = str(user_data.get('chat_id', ''))
            if not chat_id:
                return False
            
            # Prepare receipt data
            receipt_data = {
                'user_name': user_data.get('full_name', 'Valued Customer'),
                'amount': float(transaction_data.get('amount', 0)),
                'recipient_name': transaction_data.get('recipient_name', 'Unknown'),
                'recipient_account': transaction_data.get('recipient_account', 'N/A'),
                'recipient_bank': transaction_data.get('recipient_bank', 'Unknown Bank'),
                'transfer_fee': float(transaction_data.get('transfer_fee', 30)),
                'new_balance': await self.get_user_balance(user_data.get('user_id')),
                'reference': transaction_data.get('reference', 'N/A')
            }
            
            # Generate beautiful receipt
            receipt = receipt_generator.create_bank_transfer_receipt(receipt_data)
            
            # Send via Telegram
            success = await self.send_telegram_message(chat_id, receipt, parse_mode='Markdown')
            
            if success:
                # Log notification
                await self.log_notification(
                    user_data.get('user_id'),
                    'transfer_receipt',
                    f"Transfer receipt sent for ₦{receipt_data['amount']:,.2f}",
                    'sent'
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending transfer receipt: {e}")
            return False
    
    async def send_airtime_receipt(self, user_data: dict, transaction_data: dict) -> bool:
        """
        Send beautiful airtime purchase receipt to user
        
        Args:
            user_data: Dict with user information
            transaction_data: Dict with transaction details
            
        Returns:
            bool: Success status
        """
        try:
            chat_id = str(user_data.get('chat_id', ''))
            if not chat_id:
                return False
            
            # Prepare receipt data
            receipt_data = {
                'user_name': user_data.get('full_name', 'Valued Customer'),
                'amount': float(transaction_data.get('amount', 0)),
                'phone_number': transaction_data.get('phone_number', 'N/A'),
                'network': transaction_data.get('network', 'MTN'),
                'new_balance': await self.get_user_balance(user_data.get('user_id')),
                'reference': transaction_data.get('reference', 'N/A')
            }
            
            # Generate beautiful receipt
            receipt = receipt_generator.create_airtime_purchase_receipt(receipt_data)
            
            # Send via Telegram
            success = await self.send_telegram_message(chat_id, receipt, parse_mode='Markdown')
            
            if success:
                # Log notification
                await self.log_notification(
                    user_data.get('user_id'),
                    'airtime_receipt',
                    f"Airtime receipt sent for ₦{receipt_data['amount']:,.2f} {receipt_data['network']}",
                    'sent'
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending airtime receipt: {e}")
            return False
    
    async def send_data_receipt(self, user_data: dict, transaction_data: dict) -> bool:
        """
        Send beautiful data purchase receipt to user
        
        Args:
            user_data: Dict with user information
            transaction_data: Dict with transaction details
            
        Returns:
            bool: Success status
        """
        try:
            chat_id = str(user_data.get('chat_id', ''))
            if not chat_id:
                return False
            
            # Prepare receipt data
            receipt_data = {
                'user_name': user_data.get('full_name', 'Valued Customer'),
                'amount': float(transaction_data.get('amount', 0)),
                'phone_number': transaction_data.get('phone_number', 'N/A'),
                'network': transaction_data.get('network', 'MTN'),
                'data_plan': transaction_data.get('data_plan', '1GB Monthly'),
                'validity': transaction_data.get('validity', '30 days'),
                'new_balance': await self.get_user_balance(user_data.get('user_id')),
                'reference': transaction_data.get('reference', 'N/A')
            }
            
            # Generate beautiful receipt
            receipt = receipt_generator.create_data_purchase_receipt(receipt_data)
            
            # Send via Telegram
            success = await self.send_telegram_message(chat_id, receipt, parse_mode='Markdown')
            
            if success:
                # Log notification
                await self.log_notification(
                    user_data.get('user_id'),
                    'data_receipt',
                    f"Data receipt sent for ₦{receipt_data['amount']:,.2f} {receipt_data['network']} {receipt_data['data_plan']}",
                    'sent'
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending data receipt: {e}")
            return False
    
    async def send_crypto_receipt(self, user_data: dict, transaction_data: dict) -> bool:
        """
        Send beautiful crypto purchase receipt to user
        
        Args:
            user_data: Dict with user information
            transaction_data: Dict with transaction details
            
        Returns:
            bool: Success status
        """
        try:
            chat_id = str(user_data.get('chat_id', ''))
            if not chat_id:
                return False
            
            # Prepare receipt data  
            receipt_data = {
                'user_name': user_data.get('full_name', 'Valued Customer'),
                'naira_amount': float(transaction_data.get('naira_amount', 0)),
                'crypto_amount': float(transaction_data.get('crypto_amount', 0)),
                'crypto_type': transaction_data.get('crypto_type', 'USDT'),
                'exchange_rate': float(transaction_data.get('exchange_rate', 1600)),
                'new_balance': await self.get_user_balance(user_data.get('user_id')),
                'reference': transaction_data.get('reference', 'N/A')
            }
            
            # Generate beautiful receipt
            receipt = receipt_generator.create_crypto_purchase_receipt(receipt_data)
            
            # Send via Telegram
            success = await self.send_telegram_message(chat_id, receipt, parse_mode='Markdown')
            
            if success:
                # Log notification
                await self.log_notification(
                    user_data.get('user_id'),
                    'crypto_receipt',
                    f"Crypto receipt sent for ${receipt_data['crypto_amount']:,.4f} {receipt_data['crypto_type']}",
                    'sent'
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending crypto receipt: {e}")
            return False

# Global notification service instance
notification_service = NotificationService()
