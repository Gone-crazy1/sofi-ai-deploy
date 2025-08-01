"""
WhatsApp Webhook Handler with Database Integration
Comprehensive webhook handler with deduplication, user management, and onboarding
"""

import logging
from typing import Dict, Any, Optional, Tuple
from flask import request, jsonify
from utils.whatsapp_database import whatsapp_db
from utils.whatsapp_onboarding_service import whatsapp_onboarding
from utils.whatsapp_intent_parser import whatsapp_intent_parser
from utils.whatsapp_business_service import whatsapp_business

logger = logging.getLogger(__name__)

class WhatsAppWebhookHandler:
    """Main webhook handler for WhatsApp integration"""
    
    def __init__(self):
        self.db = whatsapp_db
        self.onboarding = whatsapp_onboarding
        self.intent_parser = whatsapp_intent_parser
        self.business = whatsapp_business
    
    def handle_webhook_get(self, verify_token: str) -> Tuple[Any, int]:
        """Handle webhook verification (GET request)"""
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == verify_token:
            logger.info("✅ WhatsApp webhook verified successfully")
            return challenge, 200
        else:
            logger.warning("❌ WhatsApp webhook verification failed")
            return "Forbidden", 403
    
    def handle_webhook_post(self) -> Tuple[Any, int]:
        """Handle incoming WhatsApp messages (POST request)"""
        try:
            data = request.get_json()
            
            if not data:
                logger.warning("No JSON data in webhook POST")
                return "Bad Request", 400
            
            # Extract message details
            event_id, sender, message_text = self._extract_message_data(data)
            
            if not event_id:
                logger.info("No valid message ID found in webhook")
                return "OK", 200
            
            # Check for duplicate processing (idempotency)
            if self.db.has_processed_event(event_id):
                logger.info(f"Event {event_id} already processed, skipping")
                return "OK", 200
            
            # Log the webhook event
            self.db.log_webhook_event(event_id, data)
            
            if not sender or not message_text:
                logger.info("Invalid sender or message text")
                return "OK", 200
            
            logger.info(f"📱 Processing WhatsApp message from {sender}: {message_text}")
            
            # Process the message
            response_text = self._process_user_message(sender, message_text, data)
            
            # Send response
            success = self._send_whatsapp_response(sender, response_text)
            
            if success:
                logger.info(f"✅ Response sent to {sender}")
            else:
                logger.error(f"❌ Failed to send response to {sender}")
            
            return "OK", 200
            
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {e}")
            return "Internal Server Error", 500
    
    def _extract_message_data(self, data: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract event ID, sender, and message from webhook data"""
        try:
            if not data.get("entry"):
                return None, None, None
            
            entry = data["entry"][0]
            changes = entry.get("changes", [])
            
            if not changes:
                return None, None, None
            
            value = changes[0].get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return None, None, None
            
            message = messages[0]
            event_id = message.get("id")  # WhatsApp message ID
            sender = message.get("from")
            
            # Extract text content
            if message.get("type") == "text":
                message_text = message.get("text", {}).get("body", "").strip()
            else:
                message_text = ""  # Handle other message types if needed
            
            return event_id, sender, message_text
            
        except Exception as e:
            logger.error(f"Error extracting message data: {e}")
            return None, None, None
    
    def _process_user_message(self, sender: str, message_text: str, raw_payload: dict) -> str:
        """Process user message and return response"""
        try:
            # Look up user by WhatsApp number
            user = self.db.get_user_by_whatsapp_number(sender)
            
            if user:
                # Existing user - process business logic
                return self._handle_existing_user(user, message_text, raw_payload)
            else:
                # New user - handle onboarding
                return self._handle_new_user(sender, message_text, raw_payload)
                
        except Exception as e:
            logger.error(f"Error processing message from {sender}: {e}")
            return "❌ Sorry, I'm experiencing technical difficulties. Please try again later."
    
    def _handle_existing_user(self, user: Dict[str, Any], message_text: str, raw_payload: dict) -> str:
        """Handle message from existing user"""
        user_id = user["id"]
        
        # Update last active timestamp
        self.db.update_user_last_active(user_id)
        
        # Parse intent from message
        intent_data = self.intent_parser.parse_intent(message_text)
        intent = intent_data["intent"]
        parameters = intent_data["parameters"]
        
        # Log inbound message
        self.db.log_message(
            user_id=user_id,
            platform="whatsapp",
            direction="inbound",
            content=message_text,
            intent=intent,
            raw_payload=raw_payload,
            session_state={"user_authenticated": True}
        )
        
        # Route to appropriate business function
        success, response = self._route_user_intent(user, intent, parameters, message_text)
        
        # Log outbound response
        self.db.log_message(
            user_id=user_id,
            platform="whatsapp", 
            direction="outbound",
            content=response,
            intent=f"{intent}_response",
            raw_payload={},
            session_state={"success": success}
        )
        
        return response
    
    def _handle_new_user(self, sender: str, message_text: str, raw_payload: dict) -> str:
        """Handle message from new user (onboarding flow)"""
        # Check if user is in onboarding process
        continue_onboarding, response = self.onboarding.process_onboarding_message(sender, message_text)
        
        if not continue_onboarding:
            # Onboarding complete or cancelled - check if user was created
            user = self.db.get_user_by_whatsapp_number(sender)
            if user:
                # User was created, log the completion message
                self.db.log_message(
                    user_id=user["id"],
                    platform="whatsapp",
                    direction="outbound", 
                    content=response,
                    intent="onboarding_complete",
                    raw_payload={},
                    session_state={"onboarding_completed": True}
                )
        
        return response
    
    def _route_user_intent(self, user: Dict[str, Any], intent: str, parameters: Dict[str, Any], message_text: str) -> Tuple[bool, str]:
        """Route user intent to appropriate business function"""
        try:
            if intent == "balance":
                return self.business.get_user_balance(user)
            
            elif intent == "send_money":
                return self.business.process_money_transfer(user, parameters)
            
            elif intent == "airtime":
                return self.business.process_airtime_purchase(user, parameters)
            
            elif intent == "crypto":
                return self.business.process_crypto_request(user, parameters)
            
            elif intent == "help":
                return self.business.get_help_message(user)
            
            elif intent == "greeting":
                first_name = user.get("first_name", "")
                return True, f"👋 Hi {first_name}! Welcome back to Sofi. How can I help you today?"
            
            else:
                # General query or unclear intent
                return self.business.get_general_response(user, message_text)
                
        except Exception as e:
            logger.error(f"Error routing intent {intent} for user {user.get('id')}: {e}")
            return False, "❌ Sorry, I couldn't process that request. Please try again."
    
    def _send_whatsapp_response(self, to_number: str, message_text: str) -> bool:
        """Send WhatsApp response message"""
        try:
            import os
            import requests
            
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            
            if not access_token or not phone_number_id:
                logger.error("Missing WhatsApp credentials")
                return False
            
            url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "text": {"body": message_text}
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False

# Global handler instance
whatsapp_handler = WhatsAppWebhookHandler()
