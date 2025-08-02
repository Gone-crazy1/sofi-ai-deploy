"""
WhatsApp Flow-Based Onboarding System
Uses WhatsApp's native Flow interface for seamless onboarding
"""

import os
import json
import requests
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppFlowOnboarding:
    def __init__(self):
        """Initialize WhatsApp Flow onboarding system"""
        
        # WhatsApp Cloud API configuration
        self.whatsapp_token = os.getenv('WHATSAPP_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
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
        
        logger.info("✅ WhatsApp Flow configuration validated")
    
    def create_sofi_onboarding_flow(self) -> Dict[str, Any]:
        """Create Sofi banking onboarding flow JSON"""
        
        flow_json = {
            "version": "4.0",
            "data_api_version": "3.0",
            "routing_model": {
                "ACCOUNT_SETUP": [
                    "ACCOUNT_CREATED"
                ],
                "ACCOUNT_CREATED": []
            },
            "screens": [
                {
                    "id": "ACCOUNT_SETUP",
                    "title": "Create Sofi Account",
                    "terminal": False,
                    "data": {},
                    "layout": {
                        "type": "SingleColumnLayout",
                        "children": [
                            {
                                "type": "Form",
                                "name": "sofi_signup_form",
                                "children": [
                                    {
                                        "type": "TextInput",
                                        "required": True,
                                        "label": "Full Name",
                                        "name": "full_name",
                                        "input-type": "text"
                                    },
                                    {
                                        "type": "TextInput",
                                        "required": True,
                                        "label": "Email Address",
                                        "name": "email",
                                        "input-type": "email"
                                    },
                                    {
                                        "type": "TextInput",
                                        "required": True,
                                        "label": "WhatsApp Number",
                                        "name": "whatsapp_number",
                                        "input-type": "phone"
                                    },
                                    {
                                        "type": "Dropdown",
                                        "required": True,
                                        "label": "State of Residence",
                                        "name": "state",
                                        "data-source": [
                                            {"id": "lagos", "title": "Lagos"},
                                            {"id": "abuja", "title": "Abuja"},
                                            {"id": "rivers", "title": "Rivers"},
                                            {"id": "kano", "title": "Kano"},
                                            {"id": "ogun", "title": "Ogun"},
                                            {"id": "kaduna", "title": "Kaduna"},
                                            {"id": "other", "title": "Other"}
                                        ]
                                    },
                                    {
                                        "type": "OptIn",
                                        "name": "terms_agreement",
                                        "label": "I agree to Sofi Terms of Service",
                                        "required": True
                                    },
                                    {
                                        "type": "OptIn",
                                        "name": "notifications_opt_in",
                                        "label": "Send me account notifications"
                                    },
                                    {
                                        "type": "Footer",
                                        "label": "Create Account",
                                        "on-click-action": {
                                            "name": "navigate",
                                            "next": {
                                                "type": "screen",
                                                "name": "ACCOUNT_CREATED"
                                            },
                                            "payload": {
                                                "full_name": "${form.full_name}",
                                                "email": "${form.email}",
                                                "whatsapp_number": "${form.whatsapp_number}",
                                                "state": "${form.state}",
                                                "terms_agreement": "${form.terms_agreement}",
                                                "notifications_opt_in": "${form.notifications_opt_in}"
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": "ACCOUNT_CREATED",
                    "title": "Account Created",
                    "terminal": True,
                    "success": True,
                    "data": {
                        "account_number": {
                            "type": "string",
                            "__example__": "9325935424"
                        },
                        "bank_name": {
                            "type": "string", 
                            "__example__": "9PSB"
                        },
                        "user_name": {
                            "type": "string",
                            "__example__": "John Doe"
                        }
                    },
                    "layout": {
                        "type": "SingleColumnLayout",
                        "children": [
                            {
                                "type": "TextHeading",
                                "text": "Welcome to Sofi, ${data.user_name}!"
                            },
                            {
                                "type": "TextBody",
                                "text": "Your banking account has been created successfully."
                            },
                            {
                                "type": "TextBody",
                                "text": "Account Number: ${data.account_number}"
                            },
                            {
                                "type": "TextBody",
                                "text": "Bank: ${data.bank_name}"
                            },
                            {
                                "type": "TextBody",
                                "text": "You can now send money, check balance, and buy airtime using WhatsApp."
                            },
                            {
                                "type": "Footer",
                                "label": "Start Banking",
                                "on-click-action": {
                                    "name": "complete"
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        return flow_json
    
    def send_flow_message(self, whatsapp_number: str, user_name: str = None) -> Dict[str, Any]:
        """Send WhatsApp Flow message for onboarding"""
        try:
            # Clean WhatsApp number
            clean_number = whatsapp_number.lstrip('+')
            
            # Generate flow token for this user
            flow_token = str(uuid.uuid4())
            
            # Personalize welcome message
            if user_name:
                welcome_text = f"Hi {user_name}! Welcome to Sofi Banking. Complete your account setup below."
            else:
                welcome_text = "Welcome to Sofi Banking! Complete your account setup in just a few steps."
            
            # Create flow message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": "interactive",
                "interactive": {
                    "type": "flow",
                    "header": {
                        "type": "text",
                        "text": "Sofi Account Setup"
                    },
                    "body": {
                        "text": welcome_text
                    },
                    "footer": {
                        "text": "Secure • Fast • Easy"
                    },
                    "action": {
                        "name": "flow",
                        "parameters": {
                            "flow_message_version": "3",
                            "flow_token": flow_token,
                            "flow_id": "YOUR_FLOW_ID",  # You need to create this in Meta Business Manager
                            "flow_cta": "Start Setup",
                            "flow_action": "navigate",
                            "flow_action_payload": {
                                "screen": "ACCOUNT_SETUP",
                                "data": {
                                    "whatsapp_number": whatsapp_number
                                }
                            }
                        }
                    }
                }
            }
            
            # Set headers
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            # Send message
            logger.info(f"📤 Sending Flow message to {clean_number}")
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Flow message sent successfully to {clean_number}")
                
                # Store flow token for validation
                self._store_flow_token(whatsapp_number, flow_token)
                
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "flow_token": flow_token,
                    "response": result
                }
            else:
                logger.error(f"❌ Failed to send Flow message: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"WhatsApp API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Error sending Flow message: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_flow_response(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flow completion and create user account"""
        try:
            # Extract user data from flow response
            user_data = {
                "full_name": flow_data.get("full_name", ""),
                "email": flow_data.get("email", ""),
                "whatsapp_number": flow_data.get("whatsapp_number", ""),
                "state": flow_data.get("state", ""),
                "terms_agreement": flow_data.get("terms_agreement", False),
                "notifications_opt_in": flow_data.get("notifications_opt_in", False)
            }
            
            # Validate required fields
            if not all([user_data["full_name"], user_data["email"], user_data["whatsapp_number"]]):
                return {"success": False, "error": "Missing required fields"}
            
            # Create user account
            user_id = str(uuid.uuid4())
            account_number = self._generate_account_number()
            
            # Insert user into database
            user_record = {
                "id": user_id,
                "full_name": user_data["full_name"],
                "email": user_data["email"],
                "whatsapp_number": user_data["whatsapp_number"],
                "state": user_data["state"],
                "created_at": datetime.now().isoformat(),
                "wallet_balance": 0.0,
                "status": "active",
                "signup_source": "whatsapp_flow",
                "terms_accepted": user_data["terms_agreement"],
                "notifications_enabled": user_data["notifications_opt_in"]
            }
            
            result = self.supabase.table("users").insert(user_record).execute()
            
            if result.data:
                # Create virtual account
                virtual_account = {
                    "user_id": user_id,
                    "account_number": account_number,
                    "bank_name": "9PSB",
                    "bank_code": "120001",
                    "whatsapp_number": user_data["whatsapp_number"],
                    "balance": 0.0,
                    "created_at": datetime.now().isoformat()
                }
                
                self.supabase.table("virtual_accounts").insert(virtual_account).execute()
                
                logger.info(f"✅ User account created via Flow: {user_data['whatsapp_number']}")
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "account_number": account_number,
                    "bank_name": "9PSB",
                    "user_name": user_data["full_name"]
                }
            else:
                return {"success": False, "error": "Database error"}
                
        except Exception as e:
            logger.error(f"❌ Error handling Flow response: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_account_number(self) -> str:
        """Generate a unique 10-digit account number"""
        import random
        while True:
            account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            
            # Check if account number already exists
            existing = self.supabase.table("virtual_accounts").select("account_number").eq("account_number", account_number).execute()
            
            if not existing.data:
                return account_number
    
    def _store_flow_token(self, whatsapp_number: str, flow_token: str):
        """Store flow token for validation"""
        try:
            token_data = {
                "whatsapp_number": whatsapp_number,
                "flow_token": flow_token,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Store in database or cache
            # For now, we'll just log it
            logger.info(f"📝 Flow token stored: {flow_token[:10]}... for {whatsapp_number}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not store flow token: {e}")

# Convenience functions
def send_flow_onboarding(whatsapp_number: str, user_name: str = None) -> Dict[str, Any]:
    """Quick function to send flow onboarding"""
    flow_onboarding = WhatsAppFlowOnboarding()
    return flow_onboarding.send_flow_message(whatsapp_number, user_name)

def handle_flow_completion(flow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick function to handle flow completion"""
    flow_onboarding = WhatsAppFlowOnboarding()
    return flow_onboarding.handle_flow_response(flow_data)

# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python whatsapp_flow_onboarding.py <command> [args]")
        print("Commands:")
        print("  flow <whatsapp_number> [user_name] - Send flow message")
        print("  json - Print flow JSON")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "flow":
        if len(sys.argv) < 3:
            print("Usage: python whatsapp_flow_onboarding.py flow <whatsapp_number> [user_name]")
            sys.exit(1)
        
        whatsapp_number = sys.argv[2]
        user_name = sys.argv[3] if len(sys.argv) > 3 else None
        
        print(f"🚀 Sending Flow message to {whatsapp_number}")
        if user_name:
            print(f"👤 User name: {user_name}")
        
        try:
            flow_onboarding = WhatsAppFlowOnboarding()
            result = flow_onboarding.send_flow_message(whatsapp_number, user_name)
            
            if result['success']:
                print(f"✅ Success! Message ID: {result['message_id']}")
                print(f"🔗 Flow Token: {result['flow_token']}")
            else:
                print(f"❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"💥 Error: {e}")
    
    elif command == "json":
        print("📋 Sofi Flow JSON:")
        flow_onboarding = WhatsAppFlowOnboarding()
        flow_json = flow_onboarding.create_sofi_onboarding_flow()
        print(json.dumps(flow_json, indent=2))
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
