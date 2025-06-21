"""
Sofi AI User Onboarding System

Handles complete user registration process:
- Telegram Web App form collection
- Monnify virtual account creation (Official Banking Partner)
- User data storage in Supabase
- Welcome notifications with account details
- Account upgrade options
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from supabase import create_client
from dotenv import load_dotenv

# Import our modules
from monnify.monnify_api import MonnifyAPI
from utils.notification_service import notification_service
from utils.fee_calculator import fee_calculator

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

logger = logging.getLogger(__name__)

class SofiUserOnboarding:
    """Complete Sofi AI User Onboarding System with Monnify Integration"""
    
    def __init__(self):
        self.monnify_api = MonnifyAPI()
    
    async def create_new_user(self, user_data: Dict) -> Dict:
        """
        Complete user onboarding process
        
        Args:
            user_data: User form data from Telegram Web App
            {
                'telegram_id': '4343434',
                'full_name': 'John Doe',
                'phone': '08034567890',
                'email': 'john@example.com',
                'address': 'Lagos, Nigeria',
                'bvn': '12345678901'  # Optional
            }
            
        Returns:
            Dict with onboarding result and account details
        """
        try:
            telegram_id = str(user_data.get('telegram_id'))
            full_name = user_data.get('full_name', '').strip()
            phone = user_data.get('phone', '').strip()
            email = user_data.get('email', '').strip()
            address = user_data.get('address', '').strip()
            bvn = user_data.get('bvn', '').strip()
            
            # Validate required fields
            if not all([telegram_id, full_name, phone]):
                return {
                    'success': False,
                    'error': 'Missing required fields: full_name, phone, telegram_id'
                }
            
            # Check if user already exists
            existing_user = await self.check_existing_user(telegram_id)
            if existing_user:
                return {
                    'success': False,
                    'error': 'User already registered',
                    'existing_user': existing_user
                }            
            # Step 1: Create Monnify virtual account
            logger.info(f"Creating Monnify virtual account for {full_name}")
            
            # Split full name for Monnify API
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else first_name
            
            # Create virtual account with Monnify
            account_result = self.monnify_api.create_virtual_account({
                'first_name': first_name,
                'last_name': last_name,
                'email': email or f"{first_name.lower()}.{last_name.lower()}@sofi.ai",
                'phone': phone,
                'user_id': telegram_id
            })
            
            if not account_result.get('success'):
                return {
                    'success': False,
                    'error': f"Failed to create virtual account: {account_result.get('error', 'Unknown error')}"
                }
            
            # Get account information
            accounts = account_result.get('accounts', [])
            if not accounts:
                return {
                    'success': False,
                    'error': 'No virtual accounts created'
                }
            
            # Use the first account as primary
            primary_account = accounts[0]
            account_number = primary_account.get('account_number')
            account_name = primary_account.get('account_name', full_name.upper())
            bank_name = primary_account.get('bank_name')
            
            if not account_number:
                return {
                    'success': False,
                    'error': 'No account number received from Monnify'
                }
              # Step 2: Save user to Supabase (simplified for existing schema)
            user_record = {
                'chat_id': telegram_id,  # Use existing column
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            
            # Try to save user record, but don't fail if it doesn't work
            try:
                save_result = await self.save_user_to_database(user_record)
                logger.info("User record saved successfully")
            except Exception as e:
                logger.warning(f"Could not save user record: {e}")
                # Continue anyway since the virtual account was created
                save_result = {'success': True, 'user_id': telegram_id}
            
            # Step 3: Save virtual account data
            try:
                for account in accounts:
                    account_record = {
                        'user_id': telegram_id,
                        'bank_name': account['bank_name'],
                        'account_number': account['account_number'],
                        'account_name': account['account_name'],
                        'bank_code': account['bank_code'],
                        'provider': 'monnify',
                        'status': 'active',
                        'created_at': datetime.now().isoformat()
                    }
                    
                    if supabase:
                        result = supabase.table('virtual_accounts').upsert(account_record).execute()
                        logger.info(f"Virtual account {account['account_number']} saved")
                        
            except Exception as e:
                logger.warning(f"Could not save virtual accounts: {e}")
                # Continue anyway since account was created
            
            # Step 4: Send welcome notification (skip if no telegram integration)
            try:
                await self.send_welcome_notification(telegram_id, user_record)
            except Exception as e:
                logger.warning(f"Could not send welcome notification: {e}")
            
            logger.info(f"Successfully onboarded user {full_name} (ID: {telegram_id})")
            
            return {
                'success': True,
                'user_id': telegram_id,
                'full_name': full_name,
                'accounts': accounts,
                'primary_account': {
                    'account_number': account_number,
                    'account_name': account_name,
                    'bank_name': bank_name
                },
                'account_reference': account_result.get('account_reference'),
                'message': 'Virtual account created successfully!'            }
            
        except Exception as e:
            logger.error(f"Error in user onboarding: {e}")
            return {
                'success': False,
                'error': f"Onboarding failed: {str(e)}"
            }
            
    async def check_existing_user(self, telegram_id: str) -> Optional[Dict]:
        """Check if user already exists"""
        try:
            if not supabase:
                return None
            
            # Use chat_id column instead of telegram_id
            response = supabase.table('users').select('*').eq('chat_id', telegram_id).execute()
            
            if response.data:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking existing user: {e}")
            return None
    
    async def save_user_to_database(self, user_record: Dict) -> Dict:
        """Save user record to Supabase"""
        try:
            if not supabase:
                return {'success': False, 'error': 'Database not available'}
            
            response = supabase.table('users').insert(user_record).execute()
            
            if response.data:
                user_id = response.data[0]['id']
                return {'success': True, 'user_id': user_id}
            else:
                return {'success': False, 'error': 'No data returned from database'}
                
        except Exception as e:
            logger.error(f"Error saving user to database: {e}")
            return {'success': False, 'error': str(e)}

    async def send_welcome_notification(self, telegram_id: str, user_record: Dict) -> bool:
        """Send comprehensive welcome notification with account details"""
        try:
            full_name = user_record.get('full_name', 'User')
            account_number = user_record.get('opay_account_number')
            # Show user's full name from Supabase, not the truncated Monnify account name
            display_name = full_name  # Always use the full name from Supabase
            bank_name = user_record.get('opay_bank_name', 'OPay')
            is_verified = user_record.get('is_verified', False)
            daily_limit = user_record.get('daily_limit', 200000.00)
            
            # Main welcome message with account details
            welcome_message = f"""
🎉 *Welcome to Sofi AI Wallet, {full_name}!*

Your virtual account has been created successfully! 🏦
_Powered by Pip install -ai Tech - Nigeria's AI FinTech Leader_

*📋 Your Account Details:*
👤 *Account Name:* {display_name}
🏦 *Bank Name:* {bank_name}
🔢 *Account Number:* `{account_number}`
💳 *Current Balance:* ₦0.00

*💰 Daily Transfer Limit:*
{'₦1,000,000+ (Verified Account)' if is_verified else f'₦{daily_limit:,.2f} (Unverified)'}

*📱 How to Fund Your Account:*
• Transfer money to your account number above
• Use any Nigerian bank or mobile app
• Funds are credited instantly!

*💡 Available Services:*
• 🏦 Bank Transfers
• 📱 Airtime Purchase  
• 🌐 Data Purchase
• 💱 Crypto Trading (Buy/Sell USDT, BTC)
• 💰 Balance Management

*🔔 Important Notes:*
• You'll receive instant notifications for all transactions
• All transfers have small fees (transparently shown)
• Your funds are secured with Monnify banking infrastructure

Type /help to see all available commands!

_Welcome to the future of digital banking! 🚀_
            """
            
            # Send welcome message
            success = await notification_service.send_telegram_message(
                telegram_id, welcome_message, "Markdown"
            )
            
            # Send additional upgrade message if not verified
            if not is_verified:
                upgrade_message = f"""
⬆️ *Upgrade Your Account*

Currently, your daily transfer limit is ₦{daily_limit:,.2f}.

*Want to increase your limit to ₦1,000,000+?*
📝 Provide your BVN for account verification

*Benefits of Verification:*
• Higher daily transfer limits
• Priority customer support  
• Access to premium features
• Enhanced security

Type /upgrade when you're ready to verify your account! 🔐
                """
                
                await notification_service.send_telegram_message(
                    telegram_id, upgrade_message, "Markdown"
                )
            
            # Log the notification
            if success:
                await self.log_onboarding_notification(telegram_id, user_record)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending welcome notification: {e}")
            return False
    
    async def initialize_daily_limits(self, user_id: str, telegram_id: str) -> bool:
        """Initialize daily limits tracking for new user"""
        try:
            if not supabase:
                return False
            
            # Get user's daily limit
            user_response = supabase.table('users').select('daily_limit').eq('id', user_id).execute()
            
            if not user_response.data:
                return False
            
            daily_limit = float(user_response.data[0].get('daily_limit', 200000.00))
            
            # Create today's limit record
            limit_record = {
                'user_id': user_id,
                'telegram_id': telegram_id,
                'date': datetime.now().date().isoformat(),
                'total_transferred': 0.00,
                'limit_amount': daily_limit,
                'transactions_count': 0
            }
            
            supabase.table('user_daily_limits').insert(limit_record).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error initializing daily limits: {e}")
            return False
    
    async def log_onboarding_notification(self, telegram_id: str, user_record: Dict) -> bool:
        """Log onboarding notification for tracking"""
        try:
            if not supabase:
                return False
            
            # Get user ID
            user_response = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
            
            if not user_response.data:
                return False
            
            user_id = user_response.data[0]['id']
            
            notification_log = {
                'user_id': user_id,
                'telegram_id': telegram_id,
                'notification_type': 'welcome_onboarding',
                'message_content': f"Welcome notification sent to {user_record.get('full_name')}",
                'sent_at': datetime.now().isoformat(),
                'status': 'sent'
            }
            
            supabase.table('notification_logs').insert(notification_log).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error logging onboarding notification: {e}")
            return False
    
    async def upgrade_user_account(self, telegram_id: str, bvn: str) -> Dict:
        """Upgrade user account with BVN verification"""
        try:
            if not supabase:
                return {'success': False, 'error': 'Database not available'}
            
            # Get user
            user_response = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
            
            if not user_response.data:
                return {'success': False, 'error': 'User not found'}
            
            user = user_response.data[0]
            
            if user.get('is_verified'):
                return {'success': False, 'error': 'Account already verified'}
            
            # Update user with BVN and verification
            update_data = {
                'bvn': bvn,
                'is_verified': True,
                'daily_limit': 1000000.00,  # Upgrade to 1M limit
                'updated_at': datetime.now().isoformat()
            }
            
            update_response = supabase.table('users').update(update_data).eq('telegram_id', telegram_id).execute()
            
            if update_response.data:
                # Send upgrade confirmation
                upgrade_message = f"""
✅ *Account Verification Successful!*

🎉 Congratulations {user.get('full_name', 'User')}!

*Your account has been upgraded:*
• ✅ BVN Verified
• 💰 Daily Limit: ₦1,000,000+
• 🔐 Enhanced Security
• 🚀 Premium Features Unlocked

You can now enjoy higher transfer limits and priority support!

_Thank you for upgrading your Sofi AI Wallet! 🌟_
                """
                
                await notification_service.send_telegram_message(
                    telegram_id, upgrade_message, "Markdown"
                )
                
                return {
                    'success': True,
                    'message': 'Account successfully upgraded',
                    'new_daily_limit': 1000000.00,
                    'is_verified': True
                }
            else:
                return {'success': False, 'error': 'Failed to update user record'}
                
        except Exception as e:
            logger.error(f"Error upgrading user account: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_user_profile(self, telegram_id: str) -> Optional[Dict]:
        """Get complete user profile"""
        try:
            if not supabase:
                return None
            
            # Try both telegram_chat_id and chat_id columns
            response = supabase.table('users').select('*').eq('telegram_chat_id', telegram_id).execute()
            
            if not response.data:
                # Try with chat_id as fallback
                response = supabase.table('users').select('*').eq('chat_id', telegram_id).execute()
            
            if response.data:
                user = response.data[0]
                
                # Get today's usage
                today_usage = await self.get_daily_usage(telegram_id)
                
                return {
                    'user_id': user['id'],
                    'telegram_id': user['telegram_id'],
                    'full_name': user['full_name'],
                    'phone': user['phone'],
                    'email': user['email'],
                    'account_number': user['opay_account_number'],
                    'account_name': user['opay_account_name'],
                    'bank_name': user['opay_bank_name'],
                    'balance': float(user['total_balance']),
                    'is_verified': user['is_verified'],
                    'daily_limit': float(user['daily_limit']),
                    'today_usage': today_usage,
                    'remaining_limit': float(user['daily_limit']) - today_usage,
                    'created_at': user['created_at']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def get_daily_usage(self, telegram_id: str) -> float:
        """Get user's daily transfer usage"""
        try:
            if not supabase:
                return 0.0
            
            today = datetime.now().date().isoformat()
            
            response = supabase.table('user_daily_limits').select('total_transferred').eq('telegram_id', telegram_id).eq('date', today).execute()
            
            if response.data:
                return float(response.data[0].get('total_transferred', 0.0))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting daily usage: {e}")
            return 0.0

    def create_virtual_account(self, user_data: Dict) -> Dict:
        """
        Synchronous wrapper for create_new_user - called from Flask API endpoint
        This is the method called when users submit the onboarding form
        """
        try:
            # Convert to async and run
            import asyncio
            
            # Handle the case where we're already in an async context
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're in an async context, need to create a new thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            lambda: asyncio.run(self.create_new_user(user_data))
                        )
                        result = future.result()
                else:
                    result = loop.run_until_complete(self.create_new_user(user_data))
            except RuntimeError:
                # No event loop, create one
                result = asyncio.run(self.create_new_user(user_data))
            
            # After successful account creation, send the account details to user
            if result.get('success'):
                telegram_id = user_data.get('telegram_id')
                if telegram_id:
                    # Send account details automatically
                    self._send_account_details_notification(result, telegram_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in create_virtual_account: {e}")
            return {
                'success': False,
                'error': f"Account creation failed: {str(e)}"
            }
    
    def _send_account_details_notification(self, account_result: Dict, telegram_id: str):
        """Send account details to user after successful registration"""
        try:
            # Extract account details
            full_name = account_result.get('full_name', 'User')
            account_number = account_result.get('account_number')
            bank_name = account_result.get('bank_name', 'Monnify')
            is_verified = account_result.get('is_verified', False)
            daily_limit = account_result.get('daily_limit', 200000.00)
            
            # Create account details message with FULL NAME from Supabase
            account_message = f"""
🎉 *Welcome to Sofi AI, {full_name}!*

Your virtual account is ready! 🏦

*📋 Your Account Details:*
👤 *Account Name:* {full_name}
🏦 *Bank Name:* {bank_name}
🔢 *Account Number:* `{account_number}`
💳 *Balance:* ₦0.00

*💰 Daily Transfer Limit:*
{'₦1,000,000+ (Verified)' if is_verified else f'₦{daily_limit:,.2f} (Unverified)'}

*📱 How to Fund Your Account:*
• Transfer money to your account number above
• Use any Nigerian bank or mobile app
• Funds are credited instantly!

*💡 Available Services:*
• 🏦 Bank Transfers • 📱 Airtime & Data
• 💱 Crypto Trading • 💰 Balance Management

Type /menu to see all available commands!

_Welcome to the future of digital banking! 🚀_
            """
            
            # Send message using notification service
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule the async call
                    loop.create_task(notification_service.send_telegram_message(
                        telegram_id, account_message, "Markdown"
                    ))
                else:
                    loop.run_until_complete(notification_service.send_telegram_message(
                        telegram_id, account_message, "Markdown"
                    ))
            except RuntimeError:
                asyncio.run(notification_service.send_telegram_message(
                    telegram_id, account_message, "Markdown"
                ))
            
            logger.info(f"Account details sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending account details notification: {e}")

# Global onboarding service instance
onboarding_service = SofiUserOnboarding()
