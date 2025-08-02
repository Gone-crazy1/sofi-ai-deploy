"""
WhatsApp Flow System - Exactly Like Xara
Creates native WhatsApp forms that open within the chat interface
"""

import os
import json
import uuid
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SofiWhatsAppFlow:
    def __init__(self):
        """Initialize WhatsApp Flow system"""
        
        # WhatsApp Cloud API configuration
        self.whatsapp_token = os.getenv('WHATSAPP_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.flow_id = os.getenv('WHATSAPP_FLOW_ID')  # You'll get this from Meta Business
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        required_vars = [
            ('WHATSAPP_TOKEN', self.whatsapp_token),
            ('WHATSAPP_PHONE_NUMBER_ID', self.phone_number_id)
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        logger.info("✅ WhatsApp Flow configuration validated")
    
    def create_onboarding_flow_json(self) -> Dict[str, Any]:
        """
        Create WhatsApp Flow JSON for onboarding (like Xara's PIN form)
        Clean, minimal design with no emojis
        """
        
        flow_json = {
            "version": "7.2",
            "data_api_version": "3.0",
            "routing_model": {
                "ONBOARDING": []
            },
            "screens": [
                {
                    "id": "ONBOARDING",
                    "title": "Complete Setup",
                    "terminal": True,
                    "success": True,
                    "data": {},
                    "layout": {
                        "type": "SingleColumnLayout",
                        "children": [
                            {
                                "type": "Form",
                                "name": "onboarding_form",
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
                                        "label": "Set PIN",
                                        "name": "pin",
                                        "input-type": "password",
                                        "helper-text": "4 digit transaction PIN"
                                    },
                                    {
                                        "type": "OptIn",
                                        "name": "terms_agreement",
                                        "label": "I agree to the terms and conditions",
                                        "required": True
                                    },
                                    {
                                        "type": "Footer",
                                        "label": "Create Account",
                                        "on-click-action": {
                                            "name": "data_exchange",
                                            "payload": {
                                                "full_name": "${form.full_name}",
                                                "email": "${form.email}",
                                                "pin": "${form.pin}",
                                                "terms_agreement": "${form.terms_agreement}",
                                                "action": "create_account"
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        return flow_json
    
    def create_pin_verification_flow_json(self, amount: float, recipient: str, account: str) -> Dict[str, Any]:
        """
        Create PIN verification flow (exactly like Xara's)
        """
        
        flow_json = {
            "version": "7.2",
            "data_api_version": "3.0",
            "routing_model": {
                "PIN_VERIFICATION": []
            },
            "screens": [
                {
                    "id": "PIN_VERIFICATION",
                    "title": "Approve Transaction",
                    "terminal": True,
                    "success": True,
                    "data": {},
                    "layout": {
                        "type": "SingleColumnLayout",
                        "children": [
                            {
                                "type": "Form",
                                "name": "pin_form",
                                "children": [
                                    {
                                        "type": "TextBody",
                                        "text": f"Confirm transfer of ₦{amount:,.2f} to {recipient} ({account})"
                                    },
                                    {
                                        "type": "TextInput",
                                        "required": True,
                                        "label": "PIN",
                                        "name": "transaction_pin",
                                        "input-type": "password",
                                        "helper-text": "Enter your 4 Digit Transaction PIN"
                                    },
                                    {
                                        "type": "Footer",
                                        "label": "Approve Transaction",
                                        "on-click-action": {
                                            "name": "data_exchange",
                                            "payload": {
                                                "pin": "${form.transaction_pin}",
                                                "amount": amount,
                                                "recipient": recipient,
                                                "account": account,
                                                "action": "approve_transfer"
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        return flow_json
    
    def send_onboarding_flow_message(self, whatsapp_number: str) -> Dict[str, Any]:
        """
        Send onboarding message with Flow button (like Xara's Verify Transaction button)
        """
        try:
            # Clean WhatsApp number
            clean_number = whatsapp_number.lstrip('+')
            
            # Generate secure flow token
            flow_token = str(uuid.uuid4())
            
            # Build message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": "interactive",
                "interactive": {
                    "type": "flow",
                    "header": {
                        "type": "text",
                        "text": "Complete Your Setup"
                    },
                    "body": {
                        "text": "Welcome to Sofi. Tap the button below to complete your account setup and start banking."
                    },
                    "footer": {
                        "text": "Secure setup powered by Sofi"
                    },
                    "action": {
                        "name": "flow",
                        "parameters": {
                            "flow_message_version": "3",
                            "flow_id": self.flow_id or "YOUR_FLOW_ID",
                            "flow_token": flow_token,
                            "flow_action": "navigate",
                            "flow_action_payload": {
                                "screen": "ONBOARDING",
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
            logger.info(f"📤 Sending Flow onboarding message to {clean_number}")
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Flow message sent successfully to {clean_number}")
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
    
    def send_transfer_verification_flow(self, whatsapp_number: str, amount: float, recipient: str, account: str) -> Dict[str, Any]:
        """
        Send transfer verification message with Flow button (exactly like Xara)
        """
        try:
            clean_number = whatsapp_number.lstrip('+')
            flow_token = str(uuid.uuid4())
            
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": "interactive",
                "interactive": {
                    "type": "flow",
                    "body": {
                        "text": f"Click the Verify Transaction button below to complete transfer of ₦{amount:,.2f} to {recipient} ({account})"
                    },
                    "action": {
                        "name": "flow",
                        "parameters": {
                            "flow_message_version": "3",
                            "flow_id": self.flow_id or "YOUR_FLOW_ID",
                            "flow_token": flow_token,
                            "flow_action": "navigate",
                            "flow_action_payload": {
                                "screen": "PIN_VERIFICATION",
                                "data": {
                                    "amount": amount,
                                    "recipient": recipient,
                                    "account": account,
                                    "whatsapp_number": whatsapp_number
                                }
                            }
                        }
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"📤 Sending transfer verification Flow to {clean_number}")
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Transfer verification Flow sent to {clean_number}")
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "flow_token": flow_token,
                    "response": result
                }
            else:
                logger.error(f"❌ Failed to send transfer Flow: {response.status_code}")
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error sending transfer Flow: {e}")
            return {"success": False, "error": str(e)}

# Convenience functions
def send_onboarding_flow(whatsapp_number: str) -> Dict[str, Any]:
    """Quick function to send onboarding flow"""
    flow_manager = SofiWhatsAppFlow()
    return flow_manager.send_onboarding_flow_message(whatsapp_number)

def send_transfer_flow(whatsapp_number: str, amount: float, recipient: str, account: str) -> Dict[str, Any]:
    """Quick function to send transfer verification flow"""
    flow_manager = SofiWhatsAppFlow()
    return flow_manager.send_transfer_verification_flow(whatsapp_number, amount, recipient, account)

# Test function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sofi_whatsapp_flow.py <whatsapp_number>")
        print("Example: python sofi_whatsapp_flow.py +2348104611794")
        sys.exit(1)
    
    whatsapp_number = sys.argv[1]
    
    print(f"🚀 Testing WhatsApp Flow for {whatsapp_number}")
    
    try:
        flow_manager = SofiWhatsAppFlow()
        
        # Test onboarding flow
        result = flow_manager.send_onboarding_flow_message(whatsapp_number)
        
        if result['success']:
            print(f"✅ Success! Message ID: {result['message_id']}")
            print(f"🎯 Flow Token: {result['flow_token']}")
        else:
            print(f"❌ Failed: {result['error']}")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)
