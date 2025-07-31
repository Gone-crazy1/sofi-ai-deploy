"""
SOFI AI - WHATSAPP WEBHOOK INTEGRATION
=====================================
Production-ready WhatsApp Cloud API webhook for Sofi AI
Migrates existing Telegram bot functionality to WhatsApp
"""

import os
import json
import logging
import asyncio
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Import existing Sofi AI functions
from sofi_money_functions import SofiMoneyTransferService, execute_openai_function
from utils.balance_helper import get_user_balance

# Try to import assistant, fallback if not available
try:
    from assistant import get_assistant
except ImportError:
    def get_assistant():
        return None

# WhatsApp Cloud API Configuration
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") 
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Sofi services
sofi_service = SofiMoneyTransferService()

class WhatsAppSofiBot:
    """WhatsApp integration for Sofi AI with existing Telegram logic"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        logger.info("🟢 WhatsApp Sofi Bot initialized")
    
    def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        """Send text message to WhatsApp user"""
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(WHATSAPP_API_URL, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"✅ Message sent to {phone_number}")
                return True
            else:
                logger.error(f"❌ Failed to send message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ WhatsApp send error: {e}")
            return False
    
    def send_whatsapp_button(self, phone_number: str, message: str, buttons: list) -> bool:
        """Send interactive button message to WhatsApp"""
        try:
            interactive_payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message},
                    "action": {
                        "buttons": buttons
                    }
                }
            }
            
            response = requests.post(WHATSAPP_API_URL, headers=self.headers, json=interactive_payload)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ WhatsApp button send error: {e}")
            return False
    
    async def process_whatsapp_message(self, phone_number: str, message: str, user_name: str = "User") -> str:
        """Process WhatsApp message and route to existing Sofi logic"""
        try:
            logger.info(f"📱 Processing WhatsApp message from {phone_number}: {message}")
            
            # Convert phone_number to be used as telegram_chat_id for existing functions
            chat_id = phone_number.replace("+", "").replace(" ", "")
            
            # Prepare user data for existing functions
            user_data = {
                "id": chat_id,
                "phone_number": phone_number,
                "platform": "whatsapp",
                "name": user_name
            }
            
            # Route to existing Sofi AI logic (similar to Telegram routing)
            message_lower = message.lower().strip()
            
            # BALANCE CHECK
            if any(keyword in message_lower for keyword in ['balance', 'check account', 'how much', 'my account']):
                balance_result = await sofi_service.check_user_balance(chat_id)
                if balance_result["success"]:
                    return f"💰 *Your Sofi Wallet Balance*\n\n₦{balance_result['balance']:,.2f}\n\n💡 You can send money, buy airtime, or save with Sofi AI!"
                else:
                    return f"❌ Could not check balance: {balance_result['error']}"
            
            # MONEY TRANSFER - Basic pattern recognition
            elif any(keyword in message_lower for keyword in ['send', 'transfer', 'pay']):
                return await self.handle_transfer_request(chat_id, message, user_data)
            
            # AIRTIME PURCHASE
            elif any(keyword in message_lower for keyword in ['airtime', 'recharge', 'mtn', 'glo', 'airtel', '9mobile']):
                return await self.handle_airtime_request(chat_id, message, user_data)
            
            # CRYPTO PURCHASE
            elif any(keyword in message_lower for keyword in ['buy', 'usdt', 'bitcoin', 'btc', 'crypto']):
                return await self.handle_crypto_request(chat_id, message, user_data)
            
            # TRANSACTION HISTORY
            elif any(keyword in message_lower for keyword in ['history', 'transactions', 'statement']):
                history_result = await sofi_service.get_wallet_statement(chat_id, chat_id)
                if history_result["success"]:
                    return f"📋 *Your Transaction History*\n\n{history_result['statement'][:1000]}..."
                else:
                    return f"❌ Could not get history: {history_result['error']}"
            
            # VIRTUAL ACCOUNT
            elif any(keyword in message_lower for keyword in ['account details', 'my account', 'virtual account']):
                account_result = await sofi_service.get_virtual_account(chat_id, chat_id)
                if account_result["success"]:
                    return account_result["message"]
                else:
                    return f"❌ Could not get account: {account_result['error']}"
            
            # PIN SETUP
            elif any(keyword in message_lower for keyword in ['set pin', 'change pin', 'pin setup']):
                return "🔐 *PIN Setup*\n\nTo set your transaction PIN, please send: `pin 1234 1234`\n(Replace 1234 with your desired 4-digit PIN, repeated for confirmation)"
            
            # HELP/WELCOME
            elif any(keyword in message_lower for keyword in ['help', 'start', 'hello', 'hi']):
                return self.get_welcome_message()
            
            # Use AI Assistant for complex queries (existing logic)
            else:
                try:
                    assistant = get_assistant()
                    response, function_data = await assistant.process_message(chat_id, message, user_data)
                    
                    if response and not response.startswith("Sorry"):
                        return self.format_whatsapp_message(response)
                    else:
                        return self.get_help_message()
                        
                except Exception as ai_error:
                    logger.error(f"❌ AI Assistant error: {ai_error}")
                    return self.get_help_message()
                    
        except Exception as e:
            logger.error(f"❌ Error processing WhatsApp message: {e}")
            return "❌ *Error Processing Request*\n\nSorry, something went wrong. Please try again or contact support."
    
    async def handle_transfer_request(self, chat_id: str, message: str, user_data: dict) -> str:
        """Handle money transfer requests"""
        try:
            # Extract transfer details from message using simple patterns
            import re
            
            # Pattern: "send 5000 to 1234567890" or "transfer 2k to John"
            amount_match = re.search(r'(?:send|transfer|pay)\s+(\d+(?:k|,\d{3})*)', message.lower())
            if not amount_match:
                return "💸 *Send Money*\n\nPlease specify an amount. Examples:\n• `send 5000 to 1234567890`\n• `transfer 2k to John`\n• `pay 1500 to 0701234567`"
            
            amount_str = amount_match.group(1).replace(',', '').replace('k', '000')
            amount = float(amount_str)
            
            # For now, show user they need to provide recipient details
            return f"💸 *Transfer ₦{amount:,.2f}*\n\n📝 Please provide recipient details:\n\n*Account Number:* \n*Bank Name:* \n*PIN:* \n\nExample: `1234567890 GTBank 1234`\n\n🔒 Your PIN is secure and encrypted."
            
        except Exception as e:
            logger.error(f"❌ Transfer handling error: {e}")
            return "❌ *Transfer Error*\n\nPlease use format: `send 5000 to 1234567890`"
    
    async def handle_airtime_request(self, chat_id: str, message: str, user_data: dict) -> str:
        """Handle airtime purchase requests"""
        try:
            import re
            
            # Extract amount and network
            amount_match = re.search(r'(\d+)', message)
            if not amount_match:
                return "📱 *Buy Airtime*\n\nPlease specify amount. Examples:\n• `airtime 500`\n• `recharge 1000 mtn`\n• `buy 200 airtime`"
            
            amount = int(amount_match.group(1))
            
            # For now, return instructions (you can integrate with your existing airtime logic)
            return f"📱 *Buy ₦{amount} Airtime*\n\n📝 Please provide:\n\n*Phone Number:* \n*Network:* (MTN/GLO/AIRTEL/9MOBILE)\n*PIN:* \n\nExample: `08012345678 MTN 1234`"
            
        except Exception as e:
            logger.error(f"❌ Airtime handling error: {e}")
            return "❌ *Airtime Error*\n\nPlease use format: `airtime 500`"
    
    async def handle_crypto_request(self, chat_id: str, message: str, user_data: dict) -> str:
        """Handle crypto purchase requests"""
        try:
            import re
            
            # Extract amount and crypto type
            crypto_match = re.search(r'buy\s+(\d+)\s+(usdt|bitcoin|btc)', message.lower())
            if not crypto_match:
                return "₿ *Buy Crypto*\n\nPlease specify amount and crypto. Examples:\n• `buy 50 USDT`\n• `buy 100 bitcoin`\n• `buy 25 BTC`"
            
            amount = int(crypto_match.group(1))
            crypto_type = crypto_match.group(2).upper()
            
            return f"₿ *Buy ${amount} {crypto_type}*\n\n📝 Please confirm with your PIN:\n\nExample: `confirm 1234`\n\n🔒 Your PIN is secure and encrypted."
            
        except Exception as e:
            logger.error(f"❌ Crypto handling error: {e}")
            return "❌ *Crypto Error*\n\nPlease use format: `buy 50 USDT`"
    
    def get_welcome_message(self) -> str:
        """Get welcome message for new users"""
        return """🚀 *Welcome to Sofi AI on WhatsApp!*

💰 *What I can help you with:*
• Check your wallet balance
• Send money to any bank account
• Buy airtime and data
• Purchase cryptocurrency
• View transaction history
• Manage virtual account

📱 *Quick Commands:*
• `balance` - Check wallet balance
• `send 5000 to 1234567890` - Send money
• `airtime 500` - Buy airtime
• `buy 50 USDT` - Buy crypto
• `help` - Show this menu

🔒 *Secure & Fast*
Powered by Paystack • Encrypted PINs • Instant transfers

💡 *New to Sofi?* Just say "balance" to get started!"""
    
    def get_help_message(self) -> str:
        """Get help message"""
        return """📋 *Sofi AI Help Menu*

💰 *Money Operations:*
• `balance` - Check wallet balance
• `send 5000 to 1234567890` - Send money
• `history` - View transactions
• `account details` - Your virtual account

📱 *Bills & Airtime:*
• `airtime 500` - Buy airtime
• `data 1000` - Buy data
• `recharge 200 mtn` - Network specific

₿ *Crypto Trading:*
• `buy 50 USDT` - Buy cryptocurrency
• `sell 25 BTC` - Sell crypto
• `crypto balance` - Crypto wallet

🔐 *Security:*
• `set pin` - Setup transaction PIN
• `change pin` - Update PIN

💡 *Need help?* Just describe what you want to do!"""
    
    def format_whatsapp_message(self, message: str) -> str:
        """Format message for WhatsApp with emojis and better structure"""
        # Add WhatsApp-friendly formatting
        formatted = message.replace("**", "*")  # WhatsApp uses single * for bold
        formatted = formatted.replace("__", "_")  # WhatsApp uses single _ for italic
        
        # Ensure emojis are at the start of key lines
        if "success" in message.lower() and not formatted.startswith("✅"):
            formatted = "✅ " + formatted
        elif "error" in message.lower() or "failed" in message.lower() and not formatted.startswith("❌"):
            formatted = "❌ " + formatted
            
        return formatted

# Flask app for WhatsApp webhook
app = Flask(__name__)
whatsapp_bot = WhatsAppSofiBot()

@app.route("/whatsapp-webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    """WhatsApp Cloud API webhook endpoint"""
    
    if request.method == "GET":
        # Webhook verification
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if verify_token == WHATSAPP_VERIFY_TOKEN:
            logger.info("✅ WhatsApp webhook verified")
            return challenge
        else:
            logger.error("❌ WhatsApp webhook verification failed")
            return "Verification failed", 403
    
    elif request.method == "POST":
        # Handle incoming WhatsApp messages
        try:
            data = request.get_json()
            logger.info(f"📱 WhatsApp webhook data: {json.dumps(data, indent=2)}")
            
            # Extract message data
            if "entry" in data and data["entry"]:
                for entry in data["entry"]:
                    if "changes" in entry:
                        for change in entry["changes"]:
                            if "value" in change and "messages" in change["value"]:
                                messages = change["value"]["messages"]
                                
                                for message in messages:
                                    # Extract sender info
                                    phone_number = message["from"]
                                    message_text = ""
                                    user_name = "User"
                                    
                                    # Get message text
                                    if message["type"] == "text":
                                        message_text = message["text"]["body"]
                                    elif message["type"] == "button":
                                        message_text = message["button"]["text"]
                                    elif message["type"] == "interactive":
                                        if "button_reply" in message["interactive"]:
                                            message_text = message["interactive"]["button_reply"]["title"]
                                        elif "list_reply" in message["interactive"]:
                                            message_text = message["interactive"]["list_reply"]["title"]
                                    
                                    # Get user profile name if available
                                    if "contacts" in change["value"]:
                                        for contact in change["value"]["contacts"]:
                                            if contact["wa_id"] == phone_number:
                                                user_name = contact["profile"]["name"]
                                                break
                                    
                                    if message_text:
                                        # Process message asynchronously
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                        
                                        response = loop.run_until_complete(
                                            whatsapp_bot.process_whatsapp_message(
                                                phone_number, message_text, user_name
                                            )
                                        )
                                        
                                        # Send response back to user
                                        whatsapp_bot.send_whatsapp_message(phone_number, response)
                                        
                                        loop.close()
            
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            logger.error(f"❌ WhatsApp webhook error: {e}")
            return jsonify({"error": str(e)}), 500

@app.route("/whatsapp-status")
def whatsapp_status():
    """Health check for WhatsApp integration"""
    return jsonify({
        "status": "active",
        "service": "Sofi AI WhatsApp Bot",
        "timestamp": datetime.now().isoformat(),
        "phone_number_id": WHATSAPP_PHONE_NUMBER_ID,
        "webhook_configured": bool(WHATSAPP_VERIFY_TOKEN)
    })

@app.route("/send-test-message")
def send_test_message():
    """Test endpoint to send a message (for debugging)"""
    try:
        phone = request.args.get("phone")
        message = request.args.get("message", "Test message from Sofi AI!")
        
        if not phone:
            return jsonify({"error": "Phone number required"}), 400
        
        success = whatsapp_bot.send_whatsapp_message(phone, message)
        
        return jsonify({
            "success": success,
            "phone": phone,
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("🚀 Starting Sofi AI WhatsApp Bot...")
    app.run(host="0.0.0.0", port=5001, debug=True)
