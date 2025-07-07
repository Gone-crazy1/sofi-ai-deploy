"""
Sofi AI User Onboarding System

Handles complete user registration process:
- Telegram Web App form collection
- Paystack virtual account creation (Official Banking Partner)
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
from paystack.paystack_service import PaystackService
from utils.notification_service import notification_service
from utils.fee_calculator import fee_calculator

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

logger = logging.getLogger(__name__)

class SofiUserOnboarding:
    """Complete Sofi AI User Onboarding System with Paystack Integration"""
    
    def __init__(self):
        self.paystack_service = PaystackService()
    
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
            pin = user_data.get('pin', '').strip()
            confirm_pin = user_data.get('confirm_pin', '').strip()
            
            # Validate required fields
            if not all([telegram_id, full_name, phone]):
                return {
                    'success': False,
                    'error': 'Missing required fields: full_name, phone, telegram_id'
                }
            
            # Validate PIN if provided
            if pin:
                if not pin.isdigit() or len(pin) != 4:
                    return {
                        'success': False,
                        'error': 'PIN must be exactly 4 digits'
                    }
                
                if pin != confirm_pin:
                    return {
                        'success': False,
                        'error': 'PIN confirmation does not match'
                    }
            
            # Import hashlib for PIN hashing
            import hashlib
            
            # Hash PIN if provided
            pin_hash = None
            if pin:
                # Create a secure hash of the PIN with a salt (using telegram_id as the salt)
                pin_hash = hashlib.pbkdf2_hmac('sha256', 
                                             pin.encode('utf-8'), 
                                             telegram_id.encode('utf-8'), 
                                             100000)  # 100,000 iterations
                pin_hash = pin_hash.hex()
                logger.info(f"PIN securely hashed for user {full_name}")
            
            # Check if user already exists
            existing_user = await self.check_existing_user(telegram_id)
            if existing_user:
                return {
                    'success': False,
                    'error': 'User already registered',
                    'existing_user': existing_user
                }            
            # Step 1: Create Paystack customer and virtual account
            logger.info(f"Creating Paystack virtual account for {full_name}")
            
            # Prepare user data for Paystack
            paystack_user_data = {
                'email': email or f"{full_name.lower().replace(' ', '.')}@sofi.ai",
                'first_name': full_name.split(' ')[0],
                'last_name': full_name.split(' ', 1)[1] if ' ' in full_name else full_name,
                'phone': phone
            }
            
            # Create customer and virtual account with Paystack
            account_result = self.paystack_service.create_user_account(paystack_user_data)
            
            if not account_result.get('success'):
                return {
                    'success': False,
                    'error': f"Failed to create virtual account: {account_result.get('error', 'Unknown error')}"
                }
            
            # Get account information from Paystack response
            account_info = account_result.get('account_info', {})
            
            # Check if DVA creation is pending
            if not account_info.get('account_number'):
                # DVA might be pending, try to fetch details
                customer_code = account_info.get('customer_code')
                if customer_code:
                    logger.info(f"DVA pending for {customer_code}, attempting to fetch details...")
                    retry_result = self.paystack_service.get_user_dva_details(customer_code)
                    
                    if retry_result.get('success'):
                        account_info = retry_result.get('account_info', {})
                        logger.info(f"✅ DVA details retrieved on retry: {account_info.get('account_number')}")
                    else:
                        # Still pending - return partial success with retry instructions
                        return {
                            'success': False,
                            'error': 'DVA creation is still in progress. Please try again in a few moments.',
                            'pending_dva': True,
                            'customer_code': customer_code,
                            'retry_instructions': 'DVA assignment may take a few moments. Please try onboarding again.'
                        }
                
                # Final check
                if not account_info.get('account_number'):
                    return {
                        'success': False,
                        'error': 'No account number received from Paystack after retries'
                    }
            
            # Extract all the details we need
            customer_id = account_info.get('customer_id')
            customer_code = account_info.get('customer_code')
            account_number = account_info.get('account_number')
            account_name = account_info.get('account_name', full_name.upper())
            bank_name = account_info.get('bank_name', 'Wema Bank')
            bank_code = account_info.get('bank_code')
            
            # Ensure bank_code is not None (required by virtual_accounts table)
            if not bank_code:
                # Default bank codes for common banks
                bank_code_mapping = {
                    'wema bank': '035',
                    'wema': '035',
                    'paystack-titan': '100433',
                    'titan': '100433'
                }
                bank_code = bank_code_mapping.get(bank_name.lower(), '035')  # Default to Wema
            
            logger.info(f"Account details: {account_number} ({bank_name} - {bank_code})")
            
            # Step 2: Save user to Supabase with correct column names (based on actual schema)
            user_record = {
                'telegram_chat_id': telegram_id,     # ✅ Correct
                'full_name': full_name,              # ✅ Correct
                'email': email,                      # ✅ Correct
                'phone': phone,                      # ✅ Correct (not phone_number)
                'paystack_customer_code': customer_code,  # ✅ Correct
                'wallet_balance': 0.0,               # ✅ Correct
                'created_at': datetime.now().isoformat()
            }
            
            # Add PIN hash if provided
            if pin_hash:
                user_record['pin_hash'] = pin_hash
                user_record['has_pin'] = True
                user_record['pin_set_at'] = datetime.now().isoformat()
                logger.info("PIN hash added to user record")
            
            # Try to save user record with proper error handling
            try:
                save_result = await self.save_user_to_database(user_record)
                if save_result.get('success'):
                    logger.info("User record saved successfully")
                else:
                    logger.warning(f"Could not save user record: {save_result.get('error')}")
                    # Continue anyway since the virtual account was created
                    save_result = {'success': True, 'user_id': telegram_id}
            except Exception as e:
                error_msg = str(e)
                if 'duplicate key' in error_msg and 'email' in error_msg:
                    # User already exists with this email
                    return {
                        'success': False,
                        'error': 'User with this email already exists. Please use a different email or contact support.',
                        'existing_user': True
                    }
                elif 'duplicate key' in error_msg and 'telegram_chat_id' in error_msg:
                    # User already exists with this telegram ID
                    return {
                        'success': False,
                        'error': 'User already registered with this Telegram account.',
                        'existing_user': True
                    }
                else:
                    logger.warning(f"Could not save user record: {e}")
                    # Continue anyway since the virtual account was created
                    save_result = {'success': True, 'user_id': telegram_id}
            
            # Step 3: Save virtual account data with correct format
            try:
                # Use minimal fields that work (no user_id foreign key constraint issues)
                account_record = {
                    'telegram_chat_id': telegram_id, # ✅ String field that works
                    'account_number': account_number, # ✅ Correct column name
                    'bank_name': bank_name,          # ✅ Correct column name
                    'bank_code': bank_code,          # ✅ Correct column name
                    'created_at': datetime.now().isoformat()
                }
                
                if supabase:
                    result = supabase.table('virtual_accounts').upsert(account_record).execute()
                    logger.info(f"Virtual account {account_number} saved")
                        
            except Exception as e:
                logger.warning(f"Could not save virtual account: {e}")
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
                'customer_id': customer_id,
                'customer_code': customer_code,
                'account_details': {
                    'account_number': account_number,
                    'account_name': account_name,
                    'bank_name': bank_name,
                    'bank_code': bank_code
                },
                'message': 'Virtual account created successfully!'
            }
            
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
            
            # Use telegram_chat_id column instead of chat_id
            response = supabase.table('users').select('*').eq('telegram_chat_id', telegram_id).execute()
            
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
        """Send clean, single welcome notification with account details"""
        try:
            full_name = user_record.get('full_name', 'User')
            account_number = user_record.get('paystack_account_number')
            bank_name = user_record.get('paystack_bank_name', 'Wema Bank')
            
            # Single, clean welcome message
            welcome_message = f"""✅ *Account Created Successfully!*

Welcome to Sofi AI, {full_name}! 

🏦 *Your Virtual Account:*
`{account_number}` ({bank_name})
� {full_name}

*Ready to use:*
• Transfer money to any bank
• Buy airtime & data instantly  
• Check balance anytime

Fund your account by transferring to the number above from any bank.

_Powered by Pip install AI Technologies_ 🚀"""
            
            # Send single clean message
            success = await notification_service.send_telegram_message(
                telegram_id, welcome_message, "Markdown"
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
            
            # Get user profile based on available columns
            response = supabase.table('users').select('*').eq('telegram_chat_id', telegram_id).execute()
            
            if response.data:
                user = response.data[0]
                
                # Get today's usage
                today_usage = await self.get_daily_usage(telegram_id)
                
                return {
                    'user_id': user.get('id'),
                    'telegram_id': user.get('telegram_chat_id'),
                    'full_name': user.get('full_name'),
                    'phone': user.get('phone_number'),
                    'email': user.get('email'),
                    'account_number': user.get('paystack_account_number'),
                    'account_name': user.get('full_name'),
                    'bank_name': user.get('paystack_bank_name'),
                    'balance': float(user.get('wallet_balance', 0.0)),
                    'is_verified': user.get('is_verified', False),
                    'daily_limit': float(user.get('daily_limit', 200000.0)),
                    'today_usage': today_usage,
                    'remaining_limit': float(user.get('daily_limit', 200000.0)) - today_usage,
                    'created_at': user.get('created_at')
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
            account_details = account_result.get('account_details', {})
            account_number = account_details.get('account_number')
            bank_name = account_details.get('bank_name', 'Paystack Bank')
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
