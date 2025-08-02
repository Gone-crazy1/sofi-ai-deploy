"""
WhatsApp Interactive Onboarding Message Sender
Sends interactive URL buttons for secure onboarding within WhatsApp's webview
"""

import os
import uuid
import hashlib
import hmac
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppOnboardingManager:
    def __init__(self):
        """Initialize WhatsApp onboarding manager with secure token handling"""
        
        # WhatsApp Cloud API configuration
        self.whatsapp_token = os.getenv('WHATSAPP_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
        # Onboarding configuration
        self.onboard_domain = os.getenv('ONBOARD_DOMAIN', 'https://sofi-ai-deploy.onrender.com')
        self.token_secret = os.getenv('ONBOARD_TOKEN_SECRET', 'your-secret-key-change-this')
        
        # Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        required_vars = [
            ('WHATSAPP_TOKEN', self.whatsapp_token),
            ('WHATSAPP_PHONE_NUMBER_ID', self.phone_number_id),
            ('SUPABASE_URL', os.getenv('SUPABASE_URL')),
            ('SUPABASE_KEY', os.getenv('SUPABASE_KEY'))
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        logger.info("✅ WhatsApp onboarding configuration validated")
    
    def generate_secure_token(self, whatsapp_number: str, expires_hours: int = 24) -> str:
        """
        Generate a secure, time-limited token for onboarding
        
        Args:
            whatsapp_number: User's WhatsApp number
            expires_hours: Token expiration time in hours (default 24)
        
        Returns:
            Secure token string
        """
        try:
            # Create token data
            token_data = {
                'whatsapp_number': whatsapp_number,
                'expires_at': int((datetime.now() + timedelta(hours=expires_hours)).timestamp()),
                'nonce': str(uuid.uuid4())
            }
            
            # Create token string
            token_string = f"{token_data['whatsapp_number']}:{token_data['expires_at']}:{token_data['nonce']}"
            
            # Generate HMAC signature
            signature = hmac.new(
                self.token_secret.encode(),
                token_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Combine token and signature
            secure_token = f"{token_string}:{signature}"
            
            logger.info(f"✅ Generated secure token for {whatsapp_number}")
            return secure_token
            
        except Exception as e:
            logger.error(f"❌ Error generating secure token: {e}")
            raise
    
    def validate_token(self, token: str, whatsapp_number: str) -> bool:
        """
        Validate a secure onboarding token
        
        Args:
            token: Token to validate
            whatsapp_number: Expected WhatsApp number
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Split token components
            parts = token.split(':')
            if len(parts) != 4:
                logger.warning("❌ Invalid token format")
                return False
            
            token_number, expires_at, nonce, signature = parts
            
            # Verify WhatsApp number matches
            if token_number != whatsapp_number:
                logger.warning(f"❌ Token WhatsApp number mismatch: {token_number} != {whatsapp_number}")
                return False
            
            # Check expiration
            if int(expires_at) < int(time.time()):
                logger.warning("❌ Token expired")
                return False
            
            # Verify signature
            token_string = f"{token_number}:{expires_at}:{nonce}"
            expected_signature = hmac.new(
                self.token_secret.encode(),
                token_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("❌ Invalid token signature")
                return False
            
            logger.info(f"✅ Token validated for {whatsapp_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating token: {e}")
            return False
    
    def send_onboarding_message(self, whatsapp_number: str, user_name: str = None) -> Dict[str, Any]:
        """
        Send interactive onboarding message with URL button
        
        Args:
            whatsapp_number: User's WhatsApp number (international format)
            user_name: Optional user name for personalization
        
        Returns:
            API response dictionary
        """
        try:
            # Clean WhatsApp number (remove + if present)
            clean_number = whatsapp_number.lstrip('+')
            
            # Generate secure token
            secure_token = self.generate_secure_token(whatsapp_number)
            
            # Build onboarding URL
            onboard_url = f"{self.onboard_domain}/onboard?token={secure_token}"
            
            # Personalize welcome message
            if user_name:
                welcome_text = f"Hi {user_name}! 👋\n\nWelcome to Sofi - your smart banking assistant! Tap the button below to securely complete your onboarding and start banking smarter."
            else:
                welcome_text = "Welcome to Sofi! 👋\n\nYour smart banking assistant is ready. Tap the button below to securely complete your onboarding and start banking smarter."
            
            # Build interactive message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": welcome_text
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "url",
                                "url": onboard_url,
                                "title": "Start Banking 🚀"
                            }
                        ]
                    }
                }
            }
            
            # Set headers
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            # Send message
            logger.info(f"📤 Sending onboarding message to {clean_number}")
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Onboarding message sent successfully to {clean_number}")
                
                # Log to database for tracking
                self._log_onboarding_sent(whatsapp_number, secure_token, onboard_url)
                
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "onboard_url": onboard_url,
                    "response": result
                }
            else:
                logger.error(f"❌ Failed to send onboarding message: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"WhatsApp API error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout sending onboarding message")
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error sending onboarding message: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Unexpected error sending onboarding message: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def _log_onboarding_sent(self, whatsapp_number: str, token: str, url: str):
        """Log onboarding message sent for tracking"""
        try:
            # Create or update user record with onboarding info
            user_data = {
                "whatsapp_number": whatsapp_number,
                "onboarding_token": token,
                "onboarding_url": url,
                "onboarding_sent_at": datetime.now().isoformat(),
                "onboarding_status": "sent"
            }
            
            # Try to update existing user first
            existing = self.supabase.table('users').select('id').eq('whatsapp_number', whatsapp_number).execute()
            
            if existing.data:
                # Update existing user
                self.supabase.table('users').update(user_data).eq('whatsapp_number', whatsapp_number).execute()
                logger.info(f"✅ Updated existing user onboarding record for {whatsapp_number}")
            else:
                # Create new user record
                user_data.update({
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.now().isoformat()
                })
                self.supabase.table('users').insert(user_data).execute()
                logger.info(f"✅ Created new user onboarding record for {whatsapp_number}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not log onboarding to database: {e}")
    
    def send_welcome_back_message(self, whatsapp_number: str, user_name: str = None) -> Dict[str, Any]:
        """
        Send welcome back message for returning users
        
        Args:
            whatsapp_number: User's WhatsApp number
            user_name: Optional user name for personalization
        
        Returns:
            API response dictionary
        """
        try:
            clean_number = whatsapp_number.lstrip('+')
            
            # Build dashboard URL with secure token
            secure_token = self.generate_secure_token(whatsapp_number)
            dashboard_url = f"{self.onboard_domain}/dashboard?token={secure_token}"
            
            # Personalize message
            if user_name:
                welcome_text = f"Welcome back, {user_name}! 👋\n\nYour Sofi banking dashboard is ready. Tap below to access your account securely."
            else:
                welcome_text = "Welcome back to Sofi! 👋\n\nYour banking dashboard is ready. Tap below to access your account securely."
            
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": welcome_text
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "url",
                                "url": dashboard_url,
                                "title": "Open Dashboard 📊"
                            }
                        ]
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Welcome back message sent to {clean_number}")
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "dashboard_url": dashboard_url,
                    "response": result
                }
            else:
                logger.error(f"❌ Failed to send welcome back message: {response.status_code}")
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error sending welcome back message: {e}")
            return {"success": False, "error": str(e)}

# Convenience functions for easy import
def send_onboarding_message(whatsapp_number: str, user_name: str = None) -> Dict[str, Any]:
    """
    Quick function to send onboarding message
    
    Args:
        whatsapp_number: User's WhatsApp number
        user_name: Optional user name
    
    Returns:
        Result dictionary
    """
    manager = WhatsAppOnboardingManager()
    return manager.send_onboarding_message(whatsapp_number, user_name)

def validate_onboarding_token(token: str, whatsapp_number: str) -> bool:
    """
    Quick function to validate onboarding token
    
    Args:
        token: Token to validate
        whatsapp_number: WhatsApp number
    
    Returns:
        True if valid, False otherwise
    """
    manager = WhatsAppOnboardingManager()
    return manager.validate_token(token, whatsapp_number)

# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python whatsapp_onboarding.py <whatsapp_number> [user_name]")
        print("Example: python whatsapp_onboarding.py +2348104611794 'John Doe'")
        sys.exit(1)
    
    whatsapp_number = sys.argv[1]
    user_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🚀 Sending onboarding message to {whatsapp_number}")
    if user_name:
        print(f"👤 User name: {user_name}")
    
    try:
        manager = WhatsAppOnboardingManager()
        result = manager.send_onboarding_message(whatsapp_number, user_name)
        
        if result['success']:
            print(f"✅ Success! Message ID: {result['message_id']}")
            print(f"🔗 Onboarding URL: {result['onboard_url']}")
        else:
            print(f"❌ Failed: {result['error']}")
            if 'details' in result:
                print(f"📝 Details: {result['details']}")
                
    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)
