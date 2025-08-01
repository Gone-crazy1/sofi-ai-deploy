# WhatsApp Assistant Integration
# Integrates WhatsApp with the main Sofi Assistant system like Telegram

import os
import json
import logging
import asyncio
from datetime import datetime, timezone
import requests
from supabase import create_client, Client
from assistant import get_assistant

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# WhatsApp API credentials
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "791159074061207")

def send_whatsapp_message(phone_number: str, message: str, keyboard=None):
    """Send message to WhatsApp user"""
    try:
        url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        # Add interactive buttons if keyboard provided
        if keyboard and "inline_keyboard" in keyboard:
            buttons = []
            for row in keyboard["inline_keyboard"]:
                for button in row:
                    if "web_app" in button:
                        # Convert to WhatsApp URL button
                        buttons.append({
                            "type": "reply",
                            "reply": {
                                "id": f"url_{len(buttons)}",
                                "title": button["text"][:20]  # WhatsApp limit
                            }
                        })
            
            if buttons:
                payload["type"] = "interactive"
                payload["interactive"] = {
                    "type": "button",
                    "body": {"text": message},
                    "action": {"buttons": buttons[:3]}  # WhatsApp limit of 3 buttons
                }
                del payload["text"]
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            logger.info(f"✅ WhatsApp message sent to {phone_number}")
            return True
        else:
            logger.error(f"❌ Failed to send WhatsApp message: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {e}")
        return False

def send_typing_action(phone_number: str):
    """Send typing indicator to WhatsApp (not available in WhatsApp API, so we skip)"""
    # WhatsApp Business API doesn't support typing indicators
    # This is kept for compatibility with Telegram code structure
    pass

def get_user_by_whatsapp_number(phone_number: str):
    """Get user from database by WhatsApp number"""
    try:
        # Normalize phone number to E.164 format
        normalized_phone = normalize_phone_number(phone_number)
        
        # Check for existing user
        result = supabase.table("users").select("*").eq("whatsapp_number", normalized_phone).execute()
        
        if result.data:
            logger.info(f"✅ Found existing user for WhatsApp {normalized_phone}")
            return result.data[0]
        
        # Also check platform field for backwards compatibility
        result = supabase.table("users").select("*").eq("platform", "whatsapp").eq("whatsapp_number", normalized_phone).execute()
        
        if result.data:
            logger.info(f"✅ Found existing user via platform for WhatsApp {normalized_phone}")
            return result.data[0]
        
        logger.info(f"❌ No user found for WhatsApp {normalized_phone}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting user by WhatsApp number: {e}")
        return None

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number to E.164 format"""
    if not phone:
        return phone
        
    # Remove non-digits
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # If starts with 234, it's already in E.164 format
    if digits_only.startswith('234') and len(digits_only) == 13:
        return f"+{digits_only}"
    
    # If starts with 0, replace with 234 (Nigerian format)
    if digits_only.startswith('0') and len(digits_only) == 11:
        return f"+234{digits_only[1:]}"
    
    # If 10 digits, assume Nigerian and add 234
    if len(digits_only) == 10:
        return f"+234{digits_only}"
    
    # Return as-is with + if not already there
    return f"+{digits_only}" if not phone.startswith('+') else phone

async def check_virtual_account(whatsapp_number: str):
    """Check if user has virtual account"""
    try:
        normalized_phone = normalize_phone_number(whatsapp_number)
        result = supabase.table("virtual_accounts").select("*").eq("whatsapp_number", normalized_phone).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error checking virtual account: {e}")
        return None

def log_message_to_db(user_id, platform, direction, content, intent=None, raw_payload=None):
    """Log message to database"""
    try:
        data = {
            "user_id": user_id,
            "platform": platform,
            "direction": direction,
            "content": content,
            "intent": intent,
            "raw_payload": raw_payload or {},
            "session_state": {}
        }
        
        result = supabase.table("message_logs").insert(data).execute()
        return True
        
    except Exception as e:
        logger.error(f"Error logging message: {e}")
        return False

async def process_whatsapp_message(phone_number: str, message_text: str, raw_payload: dict):
    """Process WhatsApp message using the main Sofi assistant system"""
    try:
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)
        logger.info(f"📱 Processing WhatsApp message from {normalized_phone}: {message_text}")
        
        # Send typing indicator (no-op for WhatsApp but kept for consistency)
        send_typing_action(normalized_phone)
        
        # Get user data
        user_data = get_user_by_whatsapp_number(normalized_phone)
        user_exists = user_data is not None
        
        # Log inbound message
        if user_data:
            log_message_to_db(
                user_id=user_data.get("id"),
                platform="whatsapp",
                direction="inbound",
                content=message_text,
                raw_payload=raw_payload
            )
        
        # Handle new users with onboarding
        if not user_exists:
            logger.info(f"🆕 New WhatsApp user detected: {normalized_phone}")
            
            # Check for skip onboarding keywords
            skip_onboarding_keywords = [
                "already registered", "i have account", "just created", "completed registration",
                "just signed up", "thanks", "thank you", "okay", "ok", "got it", "understood",
                "will do", "sure", "alright", "fine", "done", "yes", "no problem"
            ]
            
            if any(keyword in message_text.lower() for keyword in skip_onboarding_keywords):
                response = "Ready to help! Complete your registration using the link below:\n\nhttps://pipinstallsofi.com/onboard"
                send_whatsapp_message(normalized_phone, response)
                return {"status": "onboarding_skip", "response": response}
            
            # Full onboarding for substantial messages
            substantial_message = len(message_text.split()) > 2 or any(
                intent in message_text.lower() for intent in 
                ["balance", "send money", "transfer", "airtime", "help", "what can you do"]
            )
            
            if substantial_message:
                # Use the assistant system for new users too
                assistant = get_assistant()
                
                # Create context for new user
                context_data = {
                    "platform": "whatsapp",
                    "whatsapp_number": normalized_phone,
                    "user_exists": False,
                    "is_new_user": True
                }
                
                # Process message through assistant
                logger.info(f"🤖 Processing new user message through assistant for {normalized_phone}")
                response, function_data = await assistant.process_message(normalized_phone, message_text, context_data)
                
                # Log assistant response
                log_message_to_db(
                    user_id=None,  # No user ID yet
                    platform="whatsapp",
                    direction="outbound",
                    content=response,
                    raw_payload={"assistant_response": True, "function_data": function_data}
                )
                
                # Send response
                send_whatsapp_message(normalized_phone, response)
                return {"status": "assistant_response", "response": response}
            else:
                # Quick onboarding
                response = "👋 Welcome to Sofi! I'm your AI banking assistant.\n\nTo get started, I'll need you to complete registration:\nhttps://pipinstallsofi.com/onboard\n\nOnce registered, I can help you with:\n• Check account balance\n• Send money\n• Buy airtime\n• Crypto trading\n• And much more!"
                send_whatsapp_message(normalized_phone, response)
                return {"status": "onboarding", "response": response}
        
        # Handle existing users with full assistant integration
        else:
            logger.info(f"👤 Existing user found: {user_data.get('id')} - {normalized_phone}")
            
            # Update last active
            try:
                supabase.table("users").update({
                    "last_active_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", user_data["id"]).execute()
            except Exception as e:
                logger.error(f"Error updating last_active_at: {e}")
            
            # Get assistant instance
            assistant = get_assistant()
            
            # Create context data
            context_data = {
                "platform": "whatsapp",
                "whatsapp_number": normalized_phone,
                "user_exists": True,
                "user_data": user_data,
                "user_id": user_data["id"]
            }
            
            # Process message through assistant - THIS IS THE KEY INTEGRATION!
            logger.info(f"🤖 Processing message through assistant for user {user_data.get('id')}")
            
            # Use the chat_id as the WhatsApp number for thread management
            response, function_data = await assistant.process_message(normalized_phone, message_text, context_data)
            
            # Log assistant response
            log_message_to_db(
                user_id=user_data["id"],
                platform="whatsapp",
                direction="outbound",
                content=response,
                raw_payload={"assistant_response": True, "function_data": function_data}
            )
            
            # Send response via WhatsApp
            send_whatsapp_message(normalized_phone, response)
            
            logger.info(f"✅ Assistant response sent to {normalized_phone}")
            return {"status": "assistant_response", "response": response}
            
    except Exception as e:
        logger.error(f"❌ Error processing WhatsApp message: {e}")
        
        # Send error response to user
        error_response = "I'm having a temporary issue. Please try again in a moment."
        send_whatsapp_message(phone_number, error_response)
        
        return {"status": "error", "response": error_response, "error": str(e)}

def handle_whatsapp_webhook(request_data):
    """Main WhatsApp webhook handler - integrates with Sofi assistant system"""
    try:
        logger.info(f"📨 WhatsApp webhook received: {json.dumps(request_data, indent=2)}")
        
        # Extract message data
        entry = request_data.get("entry", [])
        if not entry:
            return {"status": "no_entry"}
        
        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "no_changes"}
        
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            # Handle status updates
            statuses = value.get("statuses", [])
            if statuses:
                logger.info(f"📋 WhatsApp status update: {statuses}")
                return {"status": "status_update"}
            return {"status": "no_messages"}
        
        # Process each message
        for message in messages:
            # Extract phone number and message text
            phone_number = message.get("from", "")
            message_id = message.get("id", "")
            message_type = message.get("type", "")
            
            # Handle text messages
            if message_type == "text":
                message_text = message.get("text", {}).get("body", "")
                
                if phone_number and message_text:
                    # Process the message asynchronously
                    logger.info(f"🔄 Starting async processing for {phone_number}")
                    
                    # Create async task for processing
                    async def process_async():
                        return await process_whatsapp_message(phone_number, message_text, message)
                    
                    # Run async processing
                    result = asyncio.run(process_async())
                    logger.info(f"✅ Async processing completed: {result}")
                    
                    return {"status": "processed", "result": result}
            
            # Handle other message types
            else:
                response = f"I received your {message_type} message. Currently, I can only process text messages. Please send your message as text."
                send_whatsapp_message(phone_number, response)
                return {"status": "unsupported_type", "type": message_type}
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"❌ WhatsApp webhook error: {e}")
        return {"status": "error", "error": str(e)}
