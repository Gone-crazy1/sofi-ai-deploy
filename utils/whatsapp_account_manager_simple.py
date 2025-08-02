"""
WhatsApp Account Manager - Compatible with Existing Supabase Schema
===================================================================
Creates accounts using existing Telegram table structure but for WhatsApp users
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

logger = logging.getLogger(__name__)

class WhatsAppAccountManager:
    """Manages WhatsApp accounts using existing Telegram table structure"""
    
    def __init__(self):
        """Initialize Paystack service"""
        from paystack.paystack_service import PaystackService
        self.paystack_service = PaystackService()
        logger.info("✅ WhatsApp Account Manager initialized with existing schema")
    
    async def create_whatsapp_account(self, whatsapp_data: Dict) -> Dict[str, Any]:
        """
        Create a WhatsApp account using existing Telegram table structure
        
        Args:
            whatsapp_data: {
                'whatsapp_number': '+2348056487759',
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'phone': '08056487759',
                'city': 'Lagos',
                'state': 'Lagos State',
                'bvn': '12345678901',
                'address': 'Lagos, Nigeria'
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
            
            # Check if user already exists (by whatsapp_phone or phone)
            existing_user = await self.get_user_by_whatsapp(whatsapp_number)
            if existing_user:
                return {
                    'success': False,
                    'error': 'Account already exists for this WhatsApp number',
                    'existing_account': existing_user
                }
            
            # Generate email if not provided
            if not email:
                clean_phone = whatsapp_number.replace('+', '').replace('-', '')
                email = f"user{clean_phone}@sofi.ai"
            
            # Extract phone from WhatsApp number if not provided
            if not phone:
                phone = whatsapp_number.replace('+234', '0') if whatsapp_number.startswith('+234') else whatsapp_number
            
            # Build address from city and state
            address = whatsapp_data.get('address', '')
            if not address:
                city = whatsapp_data.get('city', '')
                state = whatsapp_data.get('state', '')
                if city or state:
                    address = ', '.join([city, state]).strip(', ')
            
            # Prepare Paystack customer data
            paystack_user_data = {
                'email': email,
                'first_name': full_name.split()[0] if full_name else 'User',
                'last_name': ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else 'Sofi',
                'phone': whatsapp_number
            }
            
            # Create Paystack customer with virtual account
            logger.info(f"🏦 Creating Paystack account for {whatsapp_number}")
            account_result = self.paystack_service.create_user_account(paystack_user_data)
            
            if not account_result.get('success'):
                return {
                    'success': False,
                    'error': f"Failed to create virtual account: {account_result.get('error', 'Unknown error')}"
                }
            
            # Extract account details from Paystack response
            account_info = account_result.get('account_info', {})
            
            # Handle pending DVA
            if not account_info.get('account_number'):
                customer_code = account_info.get('customer_code')
                if customer_code:
                    logger.info(f"DVA pending for {customer_code}, attempting to fetch details...")
                    retry_result = self.paystack_service.get_user_dva_details(customer_code)
                    
                    if retry_result.get('success'):
                        account_info = retry_result.get('account_info', {})
                        logger.info(f"✅ DVA details retrieved: {account_info.get('account_number')}")
                    else:
                        return {
                            'success': False,
                            'error': 'Virtual account creation is still in progress. Please try again in a few moments.'
                        }
            
            # Extract account details
            account_number = account_info.get('account_number')
            account_name = account_info.get('account_name', full_name.upper())
            bank_name = account_info.get('bank_name', 'Wema Bank')
            bank_code = account_info.get('bank_code', '035')
            customer_code = account_info.get('customer_code')
            customer_id = account_info.get('customer_id')
            
            if not account_number:
                return {
                    'success': False,
                    'error': 'No account number received from Paystack'
                }
            
            # Generate telegram_chat_id for WhatsApp users (use whatsapp number hash)
            import hashlib
            telegram_chat_id = f"whatsapp_{hashlib.md5(whatsapp_number.encode()).hexdigest()[:10]}"
            
            # Save user to Supabase using all the proper columns
            user_record = {
                'telegram_chat_id': telegram_chat_id,
                'full_name': full_name,
                'email': email,
                'phone': phone,  # Store original phone
                'whatsapp_phone': whatsapp_number,  # Store WhatsApp number separately
                'address': address,
                'bvn': whatsapp_data.get('bvn', ''),
                'wallet_balance': 0.0,
                'created_at': datetime.now().isoformat(),
                
                # Paystack virtual account details
                'ninepsb_account_number': account_number,
                'ninepsb_bank_name': bank_name,
                'ninepsb_bank_code': bank_code,
                'ninepsb_wallet_created': True,
                
                # Paystack customer info
                'paystack_customer_code': customer_code,
                'paystack_customer_id': str(customer_id) if customer_id else None
            }
            
            # Store additional metadata in notes as JSON
            whatsapp_metadata = {
                'platform': 'whatsapp',
                'city': whatsapp_data.get('city', ''),
                'state': whatsapp_data.get('state', ''),
                'created_via': 'whatsapp_web_form'
            }
            
            import json
            user_record['notes'] = json.dumps(whatsapp_metadata)
            
            # Insert user into Supabase
            logger.info(f"💾 Saving WhatsApp user to Supabase: {whatsapp_number}")
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
                    'account_number': account_number,
                    'account_name': account_name,
                    'bank_name': bank_name,
                    'bank_code': bank_code,
                    'balance': 0.00
                },
                'paystack': {
                    'customer_id': customer_id,
                    'customer_code': customer_code
                }
            }
            
            logger.info(f"✅ WhatsApp account created successfully: {whatsapp_number}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error creating WhatsApp account: {e}")
            return {
                'success': False,
                'error': f'Account creation failed: {str(e)}'
            }
    
    async def get_user_by_whatsapp(self, whatsapp_number: str) -> Optional[Dict]:
        """Get user by WhatsApp number"""
        try:
            # Try whatsapp_phone column first (after schema update)
            result = supabase.table("users").select("*").eq("whatsapp_phone", whatsapp_number).execute()
            if result.data:
                return result.data[0]
            
            # Fallback to phone column for backward compatibility
            result = supabase.table("users").select("*").eq("phone", whatsapp_number).execute()
            if result.data:
                return result.data[0]
            
            # Also try searching in telegram_chat_id for the hash
            import hashlib
            telegram_chat_id = f"whatsapp_{hashlib.md5(whatsapp_number.encode()).hexdigest()[:10]}"
            result = supabase.table("users").select("*").eq("telegram_chat_id", telegram_chat_id).execute()
            if result.data:
                return result.data[0]
            
            return None
        except Exception as e:
            logger.error(f"Error getting user by WhatsApp: {e}")
            return None
    
    async def get_virtual_account(self, whatsapp_number: str) -> Optional[Dict]:
        """Get virtual account details for a WhatsApp user"""
        try:
            user = await self.get_user_by_whatsapp(whatsapp_number)
            if not user:
                return None
            
            return {
                'account_number': user.get('ninepsb_account_number'),
                'account_name': user.get('full_name', '').upper(),
                'bank_name': user.get('ninepsb_bank_name', 'Wema Bank'),
                'bank_code': user.get('ninepsb_bank_code', '035'),
                'balance': float(user.get('wallet_balance', 0)),
                'status': 'active',
                'customer_code': user.get('paystack_customer_code')
            }
        except Exception as e:
            logger.error(f"Error getting virtual account: {e}")
            return None
    
    async def get_account_balance(self, whatsapp_number: str) -> float:
        """Get account balance"""
        try:
            user = await self.get_user_by_whatsapp(whatsapp_number)
            if not user:
                return 0.0
            
            # Return wallet balance from database
            return float(user.get('wallet_balance', 0))
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return 0.0
    
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
whatsapp_account_manager = WhatsAppAccountManager()
