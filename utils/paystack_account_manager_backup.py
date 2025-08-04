"""
Paystack Virtual Account Manager for Sofi AI
============================================
Handles Paystack virtual account creation, management, and integration with WhatsApp onboarding
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from supabase import create_client, Client
import requests
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaystackVirtualAccountManager:
        """
        try:
            # Get user data from database
            user_response = self.supabase.table('users').select('*').eq('id', user_id).execute()
            
            if not user_response.data:
                return {
                    'success': False,
                    'error': f'User not found with ID: {user_id}'
                }
            
            user_data = user_response.data[0]
            
            whatsapp_number = user_data.get('whatsapp_number', '').strip()
            first_name = user_data.get('first_name', '').strip() 
            last_name = user_data.get('last_name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            email = user_data.get('email', '').strip()
            phone = user_data.get('whatsapp_number', '').strip()
            
            logger.info(f"🏦 Creating Paystack account for existing user: {whatsapp_number}")rom dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

logger = logging.getLogger(__name__)

class PaystackVirtualAccountManager:
    """Manages Paystack virtual accounts for Sofi AI users"""
    
    def __init__(self):
        """Initialize Paystack service"""
        from paystack.paystack_service import PaystackService
        self.paystack = PaystackService()
        logger.info("✅ Paystack Virtual Account Manager initialized")
    
    def create_whatsapp_account(self, whatsapp_data: Dict) -> Dict[str, Any]:
        """
        Create a complete Sofi account from WhatsApp onboarding
        
        Args:
            whatsapp_data: {
                'whatsapp_number': '+2348056487759',
                'full_name': 'John Doe',
                'email': 'john@example.com',  # optional
                'phone': '08056487759',       # optional, derived from whatsapp
                'address': 'Lagos, Nigeria',  # optional
                'bvn': '12345678901',        # optional
                'pin': '1234'               # optional
            }
            
        Returns:
            Dict with account creation result
        """
        try:
            whatsapp_number = whatsapp_data.get('whatsapp_number', '').strip()
            full_name = whatsapp_data.get('full_name', '').strip()
            email = whatsapp_data.get('email', '').strip()
            phone = whatsapp_data.get('phone', '').strip()
            
            # Validate required fields
            if not whatsapp_number or not full_name:
                return {
                    'success': False,
                    'error': 'WhatsApp number and full name are required'
                }
            
            # Check if user already exists
            existing_user = self.get_user_by_whatsapp(whatsapp_number)
            if existing_user:
                return {
                    'success': False,
                    'error': 'Account already exists for this WhatsApp number',
                    'existing_account': existing_user
                }
            
            # Generate email if not provided
            if not email:
                # Create email from phone number
                clean_phone = whatsapp_number.replace('+', '').replace('-', '')
                email = f"user{clean_phone}@sofi.ai"
            
            # Extract phone from WhatsApp number if not provided
            if not phone:
                phone = whatsapp_number.replace('+234', '0') if whatsapp_number.startswith('+234') else whatsapp_number
            
            # Prepare Paystack customer data
            paystack_data = {
                'email': email,
                'first_name': full_name.split()[0] if full_name else 'User',
                'last_name': ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else 'Sofi',
                'phone': whatsapp_number,
                'metadata': {
                    'whatsapp_number': whatsapp_number,
                    'phone': phone,
                    'platform': 'whatsapp',
                    'created_via': 'sofi_ai_assistant'
                }
            }
            
            # Create Paystack customer with virtual account
            logger.info(f"🏦 Creating Paystack account for {whatsapp_number}")
            logger.info(f"🏦 Paystack data: {json.dumps({k: v for k, v in paystack_data.items() if k != 'metadata'}, indent=2)}")
            
            # Enhanced error handling with retry logic
            max_retries = 3
            retry_count = 0
            paystack_result = None
            
            while retry_count < max_retries:
                try:
                    paystack_result = self.paystack.create_user_account(paystack_data)
                    
                    # Log detailed response for debugging
                    logger.info(f"🏦 Paystack API response (attempt {retry_count + 1}): {json.dumps(paystack_result, indent=2)}")
                    
                    if paystack_result.get('success'):
                        logger.info(f"✅ Paystack account created successfully on attempt {retry_count + 1}")
                        break
                    else:
                        # Log detailed error information
                        error_msg = paystack_result.get('error', 'Unknown error')
                        debug_data = paystack_result.get('debug_data', {})
                        logger.error(f"❌ Paystack account creation failed (attempt {retry_count + 1}): {error_msg}")
                        
                        if debug_data:
                            logger.error(f"❌ Debug data: {json.dumps(debug_data, indent=2)}")
                        
                        # If this was the last attempt, return the error
                        if retry_count == max_retries - 1:
                            return {
                                'success': False,
                                'error': f"Failed to create virtual account after {max_retries} attempts: {error_msg}",
                                'paystack_response': paystack_result,
                                'retry_count': retry_count + 1
                            }
                        
                        # Wait before retrying (exponential backoff)
                        import time
                        wait_time = 2 ** retry_count  # 1s, 2s, 4s
                        logger.info(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        
                except Exception as e:
                    logger.error(f"❌ Exception during Paystack API call (attempt {retry_count + 1}): {str(e)}")
                    logger.error(f"❌ Exception type: {type(e).__name__}")
                    
                    if retry_count == max_retries - 1:
                        return {
                            'success': False,
                            'error': f"Paystack API exception after {max_retries} attempts: {str(e)}",
                            'exception_type': type(e).__name__,
                            'retry_count': retry_count + 1
                        }
                    
                    # Wait before retrying
                    import time
                    wait_time = 2 ** retry_count
                    logger.info(f"⏳ Waiting {wait_time}s before retry due to exception...")
                    time.sleep(wait_time)
                
                retry_count += 1
            
            # If we get here and still don't have success, something is wrong
            if not paystack_result or not paystack_result.get('success'):
                final_error = paystack_result.get('error', 'Unknown error') if paystack_result else 'No response from Paystack'
                logger.error(f"❌ Final Paystack failure after all retries: {final_error}")
                return {
                    'success': False,
                    'error': f"Failed to create virtual account: {final_error}",
                    'final_response': paystack_result
                }
            
            # Extract account details
            virtual_account = paystack_result.get('account', {})
            customer = paystack_result.get('customer', {})
            
            # Save user to Supabase
            user_record = {
                'whatsapp_number': whatsapp_number,
                'phone': phone,
                'email': email,
                'full_name': full_name,
                'address': whatsapp_data.get('address', ''),
                'bvn': whatsapp_data.get('bvn', ''),
                'platform': 'whatsapp',
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                
                # Paystack details
                'paystack_customer_id': customer.get('id'),
                'paystack_customer_code': customer.get('customer_code'),
                
                # Virtual account details
                'account_number': virtual_account.get('account_number'),
                'account_name': virtual_account.get('account_name'),
                'bank_name': virtual_account.get('bank_name', 'Wema Bank'),
                'bank_code': virtual_account.get('bank_code', '035'),
                'account_reference': virtual_account.get('account_reference'),
                
                # Additional metadata
                'metadata': {
                    'onboarding_source': 'whatsapp_ai',
                    'paystack_data': paystack_result
                }
            }
            
            # Handle PIN if provided
            if whatsapp_data.get('pin'):
                # Hash and store PIN securely
                import hashlib
                pin_hash = hashlib.sha256(whatsapp_data['pin'].encode()).hexdigest()
                user_record['pin_hash'] = pin_hash
            
            # Insert user into Supabase
            logger.info(f"💾 Saving user to Supabase: {whatsapp_number}")
            result = supabase.table("users").insert(user_record).execute()
            
            if not result.data:
                return {
                    'success': False,
                    'error': 'Failed to save user to database'
                }
            
            saved_user = result.data[0]
            
            # Create successful response
            response = {
                'success': True,
                'message': 'Account created successfully!',
                'user': {
                    'id': saved_user['id'],
                    'whatsapp_number': whatsapp_number,
                    'full_name': full_name,
                    'email': email,
                    'phone': phone
                },
                'account': {
                    'account_number': virtual_account.get('account_number'),
                    'account_name': virtual_account.get('account_name'),
                    'bank_name': virtual_account.get('bank_name', 'Wema Bank'),
                    'bank_code': virtual_account.get('bank_code', '035'),
                    'balance': 0.00
                },
                'paystack': {
                    'customer_id': customer.get('id'),
                    'customer_code': customer.get('customer_code')
                }
            }
            
            logger.info(f"✅ Account created successfully for {whatsapp_number}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error creating WhatsApp account: {e}")
            return {
                'success': False,
                'error': f'Account creation failed: {str(e)}'
            }
    
    def get_user_by_whatsapp(self, whatsapp_number: str) -> Optional[Dict]:
        """Get user by WhatsApp number"""
        try:
            result = supabase.table("users").select("*").eq("whatsapp_number", whatsapp_number).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by WhatsApp: {e}")
            return None
    
    def get_virtual_account(self, whatsapp_number: str) -> Optional[Dict]:
        """Get virtual account details for a WhatsApp user"""
        try:
            user = self.get_user_by_whatsapp(whatsapp_number)
            if not user:
                return None
            
            return {
                'account_number': user.get('account_number'),
                'account_name': user.get('account_name'),
                'bank_name': user.get('bank_name'),
                'bank_code': user.get('bank_code'),
                'balance': self.get_account_balance(whatsapp_number),
                'status': user.get('status', 'active'),
                'paystack_customer_code': user.get('paystack_customer_code')
            }
        except Exception as e:
            logger.error(f"Error getting virtual account: {e}")
            return None
    
    def get_account_balance(self, whatsapp_number: str) -> float:
        """Get account balance from Paystack"""
        try:
            user = self.get_user_by_whatsapp(whatsapp_number)
            if not user or not user.get('paystack_customer_code'):
                return 0.0
            
            # Use Paystack balance API
            balance = self.paystack.get_customer_balance(user['paystack_customer_code'])
            return float(balance.get('balance', 0)) / 100  # Convert from kobo to naira
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return 0.0
    
    def update_user_profile(self, whatsapp_number: str, updates: Dict) -> Dict[str, Any]:
        """Update user profile"""
        try:
            # Remove sensitive fields
            allowed_updates = {
                'full_name', 'email', 'phone', 'address', 'bvn'
            }
            safe_updates = {k: v for k, v in updates.items() if k in allowed_updates}
            safe_updates['updated_at'] = datetime.utcnow().isoformat()
            
            result = supabase.table("users").update(safe_updates).eq("whatsapp_number", whatsapp_number).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Profile updated successfully',
                    'user': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': 'User not found'
                }
                
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return {
                'success': False,
                'error': f'Profile update failed: {str(e)}'
            }
    
        def create_paystack_for_existing_user(self, user_id: str) -> Dict[str, Any]:
        """
        Create Paystack virtual account for an existing user who doesn't have one
        
        Args:
            user_id: The UUID of the existing user in the database
            
        Returns:
            Dict with Paystack account creation result
        """
        try:
            # Get user data from database
            user_response = self.supabase.table('users').select('*').eq('id', user_id).execute()
            
            if not user_response.data:
                return {
                    'success': False,
                    'error': f'User not found with ID: {user_id}'
                }
            
            user_data = user_response.data[0]
            
            whatsapp_number = user_data.get('whatsapp_number', '').strip()
            first_name = user_data.get('first_name', '').strip() 
            last_name = user_data.get('last_name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            email = user_data.get('email', '').strip()
            phone = user_data.get('whatsapp_number', '').strip()
            
            logger.info(f"🏦 Creating Paystack account for existing user: {whatsapp_number}")
            
            # Check if user already has Paystack account
            if user_data.get('account_number'):
                return {
                    'success': True,
                    'account_number': user_data['account_number'],
                    'bank_name': 'Wema Bank',
                    'customer_code': user_data.get('paystack_customer_code', ''),
                    'customer_id': user_data.get('paystack_customer_id', ''),
                    'message': 'User already has Paystack account'
                }
            
            # Create Paystack customer with virtual account using the Paystack integration
            logger.info(f"🏦 Creating Paystack account with data: {json.dumps({'email': email, 'first_name': first_name, 'last_name': last_name, 'phone': phone}, indent=2)}")
            
            # Prepare Paystack customer data
            paystack_data = {
                'email': email,
                'first_name': first_name if first_name else 'User',
                'last_name': last_name if last_name else 'Sofi',
                'phone': phone,
                'metadata': {
                    'whatsapp_number': whatsapp_number,
                    'phone': phone,
                    'platform': 'whatsapp',
                    'created_via': 'sofi_ai_assistant',
                    'existing_user_update': True
                }
            }
            
            # Create Paystack customer with virtual account
            paystack_result = self.paystack.create_user_account(paystack_data)
            logger.info(f"🏦 Paystack API response: {json.dumps(paystack_result, indent=2)}")
            
            if not paystack_result.get('success'):
                error_msg = paystack_result.get('error', 'Unknown Paystack error')
                logger.error(f"❌ Paystack account creation failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Failed to create virtual account: {error_msg}",
                    'paystack_response': paystack_result
                }
            
            # Extract account details
            virtual_account = paystack_result.get('account', {})
            customer = paystack_result.get('customer', {})
            
            logger.info(f"✅ Paystack account created: {virtual_account.get('account_number')}")
            
            # Update existing user record with Paystack details
            update_data = {
                'paystack_customer_id': customer.get('id'),
                'paystack_customer_code': customer.get('customer_code'),
                'account_number': virtual_account.get('account_number'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Update user in Supabase
            result = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
            
            if not result.data:
                logger.error(f"❌ Failed to update user with Paystack details")
                return {
                    'success': False,
                    'error': 'Failed to update user record with Paystack details'
                }
            
            logger.info(f"✅ User updated with Paystack details: {virtual_account.get('account_number')}")
            
            return {
                'success': True,
                'message': f'Paystack account created successfully for existing user',
                'account_number': virtual_account.get('account_number'),
                'bank_name': virtual_account.get('bank_name', 'Wema Bank'),
                'customer_code': customer.get('customer_code'),
                'customer_id': customer.get('id'),
                'account_data': {
                    'account_number': virtual_account.get('account_number'),
                    'account_name': virtual_account.get('account_name'),
                    'bank_name': virtual_account.get('bank_name', 'Wema Bank'),
                    'bank_code': virtual_account.get('bank_code', '035'),
                    'customer_code': customer.get('customer_code'),
                    'dva_id': virtual_account.get('account_reference')
                },
                'account_details': {
                    'account_number': virtual_account.get('account_number'),
                    'account_name': virtual_account.get('account_name'),
                    'bank_name': virtual_account.get('bank_name', 'Wema Bank')
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Exception creating Paystack account for existing user: {str(e)}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Exception creating Paystack account: {str(e)}'
            }

    def format_account_message(self, account_data: Dict) -> str:
        """Format account details for WhatsApp message"""
        try:
            account = account_data.get('account', {})
            user = account_data.get('user', {})
            
            return f"""✅ **Account Created Successfully!**

👤 **Name:** {user.get('full_name')}
📱 **WhatsApp:** {user.get('whatsapp_number')}
📧 **Email:** {user.get('email')}

🏦 **Virtual Account Details:**
**Account:** {account.get('account_number')}
**Name:** {account.get('account_name')}
**Bank:** {account.get('bank_name')}
**Balance:** ₦{account.get('balance', 0):,.2f}

💡 **What's Next:**
• Send money to your account number to add funds
• Use voice commands or chat to check balance
• Transfer money to friends and family
• Buy airtime and pay bills

🎉 Welcome to Sofi AI - Your intelligent banking assistant!"""
            
        except Exception as e:
            logger.error(f"Error formatting account message: {e}")
            return "✅ Account created successfully! Check your account details in the app."

# Global instance
paystack_account_manager = PaystackVirtualAccountManager()
