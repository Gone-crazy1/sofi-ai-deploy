"""
WhatsApp Onboarding System - Mirror Telegram Experience
Implement proper user lookup, detection, and interactive button onboarding
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from utils.supabase_client import supabase
import secrets
import hashlib
import time

logger = logging.getLogger(__name__)

class WhatsAppOnboardingManager:
    """Handles WhatsApp user onboarding exactly like Telegram"""
    
    def __init__(self):
        self.onboarding_tokens = {}  # Store secure tokens for users
    
    async def handle_whatsapp_incoming(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main handler for WhatsApp messages - mirrors Telegram onboarding flow
        
        Args:
            payload: WhatsApp webhook payload
            
        Returns:
            dict: Response with message and optional button data
        """
        try:
            # 1. Extract user info
            whatsapp_id = self.extract_sender_id(payload)
            text = self.extract_text(payload).strip().lower()
            
            logger.info(f"📱 Processing WhatsApp message from {whatsapp_id}: '{text}'")
            
            # 2. Lookup user by whatsapp_chat_id in Supabase (NOT chat_id!)
            user = await self.get_user_by_whatsapp_id(whatsapp_id)
            
            if not user:
                # 3. New user: create record and treat as onboarding-needed
                logger.info(f"🆕 New WhatsApp user detected: {whatsapp_id}")
                user = await self.create_user_with_whatsapp_id(whatsapp_id)
                
                # Send welcome message with interactive button
                return await self.send_onboarding_flow(whatsapp_id, user, is_new=True)
            else:
                logger.info(f"🔄 Returning WhatsApp user: {whatsapp_id}")
                
                # Check if user has completed onboarding
                if not user.get('account_number') or not user.get('account_name'):
                    # User exists but hasn't completed onboarding
                    return await self.send_onboarding_flow(whatsapp_id, user, is_new=False)
                else:
                    # User is fully onboarded - continue with normal Assistant flow
                    return {
                        "proceed_to_assistant": True,
                        "user": user,
                        "whatsapp_id": whatsapp_id,
                        "text": text
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error handling WhatsApp incoming: {e}")
            return {
                "message": "Sorry, I'm having trouble right now. Please try again later.",
                "button_data": None
            }
    
    def extract_sender_id(self, payload: Dict[str, Any]) -> str:
        """Extract WhatsApp phone number from webhook payload"""
        try:
            # Standard WhatsApp webhook structure
            entry = payload.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])
            
            if messages:
                return messages[0].get('from', '')
            
            return ''
        except Exception as e:
            logger.error(f"❌ Error extracting sender ID: {e}")
            return ''
    
    def extract_text(self, payload: Dict[str, Any]) -> str:
        """Extract message text from webhook payload"""
        try:
            entry = payload.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [{}])
            
            if messages:
                message = messages[0]
                if message.get('type') == 'text':
                    return message.get('text', {}).get('body', '')
            
            return ''
        except Exception as e:
            logger.error(f"❌ Error extracting text: {e}")
            return ''
    
    async def get_user_by_whatsapp_id(self, whatsapp_id: str) -> Optional[Dict[str, Any]]:
        """
        Lookup user by whatsapp_chat_id (NOT chat_id!) in Supabase
        
        Args:
            whatsapp_id: WhatsApp phone number
            
        Returns:
            User record or None if not found
        """
        try:
            logger.info(f"🔍 Looking up user by whatsapp_chat_id: {whatsapp_id}")
            
            # Query using the correct field name
            response = supabase.table('users').select('*').eq('whatsapp_chat_id', whatsapp_id).execute()
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                logger.info(f"✅ Found existing user: {user.get('id')} - {user.get('first_name', 'Unknown')}")
                return user
            else:
                logger.info(f"❌ No user found with whatsapp_chat_id: {whatsapp_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error looking up user: {e}")
            return None
    
    async def create_user_with_whatsapp_id(self, whatsapp_id: str) -> Dict[str, Any]:
        """
        Create new user record with whatsapp_chat_id
        
        Args:
            whatsapp_id: WhatsApp phone number
            
        Returns:
            Created user record
        """
        try:
            logger.info(f"👤 Creating new user with whatsapp_chat_id: {whatsapp_id}")
            
            user_data = {
                'whatsapp_chat_id': whatsapp_id,
                'phone_number': whatsapp_id,  # Store phone as backup
                'created_at': 'now()',
                'onboarding_status': 'pending',
                'channel': 'whatsapp'
            }
            
            response = supabase.table('users').insert(user_data).execute()
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                logger.info(f"✅ Created new user: {user.get('id')}")
                return user
            else:
                logger.error(f"❌ Failed to create user for {whatsapp_id}")
                raise Exception("User creation failed")
                
        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            raise e
    
    async def send_onboarding_flow(self, whatsapp_id: str, user: Dict[str, Any], is_new: bool = True) -> Dict[str, Any]:
        """
        Send onboarding flow with interactive button (mirrors Telegram)
        
        Args:
            whatsapp_id: WhatsApp phone number
            user: User record
            is_new: Whether this is a new or returning incomplete user
            
        Returns:
            Response with message and button data
        """
        try:
            # Generate secure token for onboarding link
            token = self.generate_user_token(user['id'])
            
            # Welcome message
            if is_new:
                welcome_text = """👋 *Welcome to Sofi AI!*

I'm your intelligent financial assistant powered by Pip Install AI Technologies.

🏦 *Get started in 2 minutes:*
• Create your virtual account
• Get instant account number  
• Start sending money immediately

Tap the button below to complete your secure registration! 🚀"""
            else:
                welcome_text = """👋 *Welcome back to Sofi!*

Let's continue setting up your account. You're just one step away from accessing all Sofi features!

Tap the button below to complete your registration! 🚀"""
            
            # Interactive button data (Meta's official structure)
            button_data = {
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "header": {
                        "type": "text",
                        "text": "🏦 Sofi Digital Banking"
                    },
                    "body": {
                        "text": welcome_text
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "url",
                                "url": f"https://www.pipinstallsofi.com/whatsapp-onboard?token={token}",
                                "title": "Start Banking 🚀"
                            }
                        ]
                    },
                    "footer": {
                        "text": "Secure • Fast • Intelligent Banking"
                    }
                }
            }
            
            logger.info(f"📤 Sending onboarding flow to {whatsapp_id}")
            
            return {
                "message": None,  # No plain text message
                "button_data": button_data,
                "user": user,
                "onboarding_needed": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending onboarding flow: {e}")
            
            # Fallback to plain text with URL
            fallback_message = f"""👋 Welcome to Sofi AI!

Complete your registration here: https://www.pipinstallsofi.com/whatsapp-onboard?token={self.generate_user_token(user['id'])}

Reply "help" if you need assistance."""
            
            return {
                "message": fallback_message,
                "button_data": None,
                "user": user,
                "onboarding_needed": True
            }
    
    def generate_user_token(self, user_id: int) -> str:
        """
        Generate secure token for onboarding link
        
        Args:
            user_id: User database ID
            
        Returns:
            Secure token string
        """
        try:
            # Create secure token with timestamp
            timestamp = int(time.time())
            random_part = secrets.token_urlsafe(16)
            
            # Create HMAC signature (you should use a secret key from env)
            secret_key = "sofi_onboarding_secret_2024"  # TODO: Move to environment variable
            message = f"{user_id}:{timestamp}:{random_part}"
            signature = hashlib.sha256(f"{message}:{secret_key}".encode()).hexdigest()[:16]
            
            token = f"{user_id}:{timestamp}:{random_part}:{signature}"
            
            # Store token for validation (expires in 1 hour)
            self.onboarding_tokens[token] = {
                'user_id': user_id,
                'created': timestamp,
                'expires': timestamp + 3600  # 1 hour
            }
            
            logger.info(f"🔐 Generated secure token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Error generating token: {e}")
            return f"{user_id}:{int(time.time())}:fallback"
    
    def validate_token(self, token: str) -> Optional[int]:
        """
        Validate onboarding token and return user_id
        
        Args:
            token: Token to validate
            
        Returns:
            User ID if valid, None if invalid/expired
        """
        try:
            if token not in self.onboarding_tokens:
                return None
            
            token_data = self.onboarding_tokens[token]
            current_time = int(time.time())
            
            if current_time > token_data['expires']:
                # Token expired
                del self.onboarding_tokens[token]
                return None
            
            return token_data['user_id']
            
        except Exception as e:
            logger.error(f"❌ Error validating token: {e}")
            return None

# Global instance
whatsapp_onboarding = WhatsAppOnboardingManager()
