#!/usr/bin/env python3
"""
Sofi WhatsApp GPT Server
Dedicated server for handling WhatsApp messages with GPT-3.5 integration
"""

import os
import asyncio
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils.whatsapp_gpt_integration import sofi_whatsapp_gpt

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# WhatsApp functions
def send_whatsapp_message(to_number: str, message_text: str) -> bool:
    """Send WhatsApp message"""
    try:
        import requests
        
        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        
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
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False

def parse_whatsapp_message(data: dict) -> tuple:
    """Parse incoming WhatsApp message"""
    try:
        if not data.get("entry"):
            return None, None
            
        entry = data["entry"][0]
        changes = entry.get("changes", [])
        
        if not changes:
            return None, None
            
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return None, None
            
        message = messages[0]
        sender = message.get("from")
        
        if message.get("type") == "text":
            text = message.get("text", {}).get("body", "")
        else:
            text = ""
            
        return sender, text
        
    except Exception as e:
        logger.error(f"Error parsing WhatsApp message: {e}")
        return None, None

@app.route("/whatsapp-webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    """Handle WhatsApp webhook with GPT integration"""
    
    if request.method == "GET":
        # Webhook verification
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "sofi_ai_webhook_verify_2024")
        
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == verify_token:
            logger.info("✅ WhatsApp webhook verified successfully")
            return challenge
        else:
            logger.warning("❌ WhatsApp webhook verification failed")
            return "Forbidden", 403
    
    elif request.method == "POST":
        # Handle incoming messages with GPT
        try:
            data = request.get_json()
            
            if not data:
                return "Bad Request", 400
            
            # Parse message
            sender, text = parse_whatsapp_message(data)
            
            if not sender or not text:
                logger.info("📱 WhatsApp webhook: No valid message found")
                return "OK", 200
            
            logger.info(f"📱 WhatsApp message from {sender}: {text}")
            
            # Process with GPT-3.5 Turbo
            async def process_and_respond():
                try:
                    response_text = await sofi_whatsapp_gpt.process_whatsapp_message(sender, text)
                    
                    # Send response
                    success = send_whatsapp_message(sender, response_text)
                    
                    if success:
                        logger.info(f"✅ GPT response sent to {sender}")
                    else:
                        logger.error(f"❌ Failed to send response to {sender}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    # Send fallback message
                    fallback = "🤖 Hi! I'm Sofi, your AI banking assistant. I'm having a small technical issue but I'm here to help with your banking needs!"
                    send_whatsapp_message(sender, fallback)
            
            # Run async processing
            asyncio.run(process_and_respond())
            
            return "OK", 200
            
        except Exception as e:
            logger.error(f"❌ WhatsApp webhook error: {e}")
            return "Internal Server Error", 500

@app.route("/test-gpt", methods=["GET"])
def test_gpt():
    """Test endpoint for GPT integration"""
    try:
        async def test():
            response = await sofi_whatsapp_gpt.process_whatsapp_message(
                "+2348056487759", 
                "Hello Sofi, test my banking assistant"
            )
            return response
        
        result = asyncio.run(test())
        return jsonify({
            "status": "success",
            "gpt_response": result,
            "message": "GPT-3.5 integration working!"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route("/", methods=["GET"])
def home():
    """Server status"""
    return jsonify({
        "status": "active",
        "service": "Sofi WhatsApp GPT-3.5 Server",
        "phone": "+234 805 648 7759",
        "endpoints": {
            "webhook": "/whatsapp-webhook",
            "test_gpt": "/test-gpt"
        },
        "features": [
            "WhatsApp message processing",
            "GPT-3.5 Turbo integration", 
            "Banking assistance",
            "Intelligent responses"
        ]
    })

if __name__ == "__main__":
    print("🚀 Starting Sofi WhatsApp GPT Server...")
    print("📱 Phone: +234 805 648 7759")
    print("🤖 GPT-3.5 Turbo: Ready")
    print("🔄 Webhook: /whatsapp-webhook")
    print("✅ Server starting on http://0.0.0.0:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
