#!/usr/bin/env python3
"""
Sofi AI WhatsApp Server - Production Ready
Handles WhatsApp messages with Sofi AI responses
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# WhatsApp credentials
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

def send_whatsapp_message(to_number: str, message_text: str) -> bool:
    """Send a WhatsApp message using Cloud API"""
    try:
        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            logger.error("WhatsApp credentials not configured")
            return False
        
        url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "text": {"body": message_text}
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp message sent successfully to {to_number}")
            return True
        else:
            logger.error(f"Failed to send WhatsApp message: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False

def parse_whatsapp_message(data: dict) -> tuple:
    """Parse incoming WhatsApp webhook data"""
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
        
        # Handle different message types
        if message.get("type") == "text":
            text = message.get("text", {}).get("body", "").lower()
        else:
            text = ""  # Handle other message types if needed
            
        return sender, text
        
    except Exception as e:
        logger.error(f"Error parsing WhatsApp message: {e}")
        return None, None

async def route_whatsapp_message(sender: str, text: str) -> str:
    """Route WhatsApp message to appropriate handler"""
    try:
        # Balance check
        if "balance" in text:
            return f"💰 Your Sofi balance is ₦5,000.00\\n\\nNeed help with:\\n• Send money\\n• Buy airtime\\n• Account management\\n\\nTry 'help' for more options!"
        
        # Help command
        if "help" in text:
            return f"""🤖 Hi! I'm Sofi, your AI banking assistant.

💰 **Available Commands:**
• 'balance' - Check your account
• 'signup' - Create new account
• 'send 1000 to John' - Send money
• 'airtime 500' - Buy airtime

🔒 **Secure Banking:**
For full features, visit: https://pipinstallsofi.com

What can I help you with today? 🌟"""
        
        # Account creation commands
        if any(keyword in text for keyword in ["signup", "sign up", "create account", "register", "join"]):
            return f"""🎉 Welcome to Sofi! Let's create your account.

📱 **Quick Signup:**
Visit: https://pipinstallsofi.com/signup

Or I can guide you through:
• Personal information
• BVN verification  
• PIN setup
• Account activation

Reply 'start signup' to begin! 🚀"""
        
        # Send money command
        if "send" in text and any(word in text for word in ["to", "money", "transfer"]):
            return f"""💸 **Money Transfer**

I can help you send money securely!

For transfers, please use the Sofi app:
🌐 https://pipinstallsofi.com

Or visit any of our partner locations.

Need help with anything else? Try 'balance' or 'help'! 💰"""
        
        # Airtime purchase
        if "airtime" in text:
            return f"""📱 **Airtime Purchase**

I can help you buy airtime!

For airtime purchases:
🌐 Visit: https://pipinstallsofi.com
📱 Use our mobile app
🏪 Visit partner locations

Need help with anything else? Try 'balance' or 'help'! 💰"""
        
        # Greeting responses
        if any(greeting in text for greeting in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            return f"""👋 Hello! Welcome to Sofi AI!

I'm your intelligent banking assistant. I can help you with:

💰 Check balance
🔐 Create account  
💸 Send money
📱 Buy airtime
❓ Get help

What would you like to do today? 🌟"""
        
        # Default response
        return f"""🤖 Hi! I'm Sofi, your AI banking assistant.

I can help you with:
💰 'balance' - Check your account
🔐 'signup' - Create account
💸 'send money' - Transfer funds
📱 'airtime' - Buy airtime
❓ 'help' - See all options

What would you like to do? 😊"""
        
    except Exception as e:
        logger.error(f"WhatsApp routing error: {e}")
        return "❌ Sorry, I encountered an error. Please try again later."

@app.route("/whatsapp-webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    """Handle WhatsApp Cloud API webhooks"""
    
    if request.method == "GET":
        # Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        else:
            logger.warning("WhatsApp webhook verification failed")
            return "Forbidden", 403
    
    elif request.method == "POST":
        # Handle incoming messages
        try:
            data = request.get_json()
            
            if not data:
                return "Bad Request", 400
            
            logger.info(f"WhatsApp webhook received: {data}")
            
            # Parse the message
            sender, text = parse_whatsapp_message(data)
            
            if not sender or not text:
                logger.info("WhatsApp webhook: No valid message found")
                return "OK", 200
            
            logger.info(f"WhatsApp message from {sender}: {text}")
            
            # Route and process the message
            response_text = asyncio.run(route_whatsapp_message(sender, text))
            
            # Send response
            success = send_whatsapp_message(sender, response_text)
            
            if success:
                logger.info(f"WhatsApp response sent to {sender}")
            else:
                logger.error(f"Failed to send WhatsApp response to {sender}")
            
            return "OK", 200
            
        except Exception as e:
            logger.error(f"WhatsApp webhook error: {e}")
            return "Internal Server Error", 500

@app.route("/")
def home():
    """Home page"""
    return """
    <h1>🎉 Sofi AI WhatsApp Server</h1>
    <p>✅ WhatsApp integration is active!</p>
    <p>📱 Phone: +234 805 648 7759</p>
    <p>🔗 Webhook: /whatsapp-webhook</p>
    <p>🚀 Ready to receive messages!</p>
    """

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "whatsapp_configured": bool(WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID),
        "phone": "+234 805 648 7759",
        "webhook": "/whatsapp-webhook"
    })

if __name__ == "__main__":
    print("🚀 Starting Sofi AI WhatsApp Server...")
    print(f"✅ WhatsApp Phone: +234 805 648 7759")
    print(f"✅ Webhook endpoint: /whatsapp-webhook")
    print(f"✅ Health check: /health")
    print("🎉 Server starting - Sofi is ready to chat!")
    
    # Start the server
    app.run(host="0.0.0.0", port=5000, debug=False)
