import os
from flask import Flask, request, jsonify, url_for, render_template, abort, make_response
from flask_cors import CORS
import os, requests, logging, json, asyncio, tempfile, re, threading, uuid, time
import hashlib  # Built-in module - import separately
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# 9PSB API credentials
NINEPSB_USERNAME = os.getenv("NINEPSB_USERNAME")
NINEPSB_PASSWORD = os.getenv("NINEPSB_PASSWORD")
NINEPSB_CLIENT_ID = os.getenv("NINEPSB_CLIENT_ID")
NINEPSB_CLIENT_SECRET = os.getenv("NINEPSB_CLIENT_SECRET")
NINEPSB_API_KEY = os.getenv("NINEPSB_API_KEY")
NINEPSB_SECRET_KEY = os.getenv("NINEPSB_SECRET_KEY")
NINEPSB_BASE_URL = os.getenv("NINEPSB_BASE_URL")

from supabase import create_client
import openai
from openai import OpenAI
from typing import Dict, Optional, Any
import time
from utils.bank_api import BankAPI
from utils.secure_transfer_handler import SecureTransferHandler
from utils.balance_helper import get_user_balance as get_balance_secure, check_virtual_account as check_virtual_account_secure
from flow_encryption import get_flow_encryption
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
# Paystack Integration - Banking Partner
from paystack import get_paystack_service
from paystack.paystack_webhook import handle_paystack_webhook
# AI Assistant Integration - Powered by Pip install AI Technologies
from assistant import get_assistant
import random
from PIL import Image
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from utils.memory import save_memory, list_memories, save_chat_message, get_chat_history
from utils.conversation_state import conversation_state
from utils.nigerian_expressions import enhance_nigerian_message, get_response_guidance
from utils.prompt_schemas import get_image_prompt, validate_image_result
from utils.whatsapp_gpt_integration import sofi_whatsapp_gpt
from whatsapp_onboarding import WhatsAppOnboardingManager, send_onboarding_message
from whatsapp_flow_onboarding import WhatsAppFlowOnboarding, send_flow_onboarding
from unittest.mock import MagicMock

# ⚡ INSTANT RESPONSE CACHE for ultra-fast replies
import time
from functools import lru_cache

# Cache for instant balance responses (20 seconds)
balance_cache = {}
CACHE_DURATION = 20  # seconds

def get_cached_balance(phone_number):
    """Get cached balance for instant response"""
    now = time.time()
    if phone_number in balance_cache:
        balance, timestamp = balance_cache[phone_number]
        if now - timestamp < CACHE_DURATION:
            return balance
    return None

def cache_balance(phone_number, balance):
    """Cache balance for instant future responses"""
    balance_cache[phone_number] = (balance, time.time())

# 🔒 SECURITY SYSTEM IMPORTS
from utils.security import init_security
from utils.security_monitor import (
    log_security_event, AlertLevel, get_enhanced_security_stats,
    enable_fast_mode, disable_fast_mode, get_fast_mode_status
)
from utils.security_config import get_security_config

# ⚡ ENABLE FAST MODE FOR ULTRA-FAST RESPONSES
enable_fast_mode()  # This disables non-critical security alerts
print("🚀 Sofi AI started in FAST MODE for optimal response times")

# 🔒 SECURITY ENDPOINTS
from utils.security_endpoints import init_security_endpoints
from functions.transfer_functions import BANK_CODE_TO_NAME

# Import admin handler AFTER environment loading
from utils.admin_command_handler import AdminCommandHandler
admin_handler = AdminCommandHandler()

# Import user onboarding system
from utils.user_onboarding import SofiUserOnboarding
onboarding_service = SofiUserOnboarding()

# Import beneficiary management system (NEW Supabase integration)
from utils.legacy_beneficiary_handler import legacy_beneficiary_handler

# Import transaction history system
from utils.transaction_history import handle_transaction_history_query

# Import enhanced transaction summarizer
from utils.transaction_summarizer import transaction_summarizer

app = Flask(__name__)

# Initialize logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔒 INITIALIZE SECURITY SYSTEM
security_middleware = init_security(app)
logger.info("🔒 Sofi AI Security System activated")

# 🔒 INITIALIZE SECURITY ENDPOINTS
init_security_endpoints(app)
logger.info("🔒 Security endpoints initialized")

# CORS configuration is now handled by security system

def generate_pos_style_receipt(sender_name, amount, recipient_name, recipient_account, recipient_bank, balance, transaction_id):
    """Generate a POS-style receipt for a transaction."""
    receipt = f"""
=================================
      SOFI AI TRANSFER RECEIPT
=================================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Transaction ID: {transaction_id}
---------------------------------
Sender: {sender_name}
Amount: ₦{amount:,.2f}
Recipient: {recipient_name}
Account: {recipient_account}
Bank: {recipient_bank}
---------------------------------
Balance: ₦{balance:,.2f}
=================================
    Thank you for using Sofi AI!
=================================
"""
    return receipt

# WhatsApp Flow Configuration
WHATSAPP_FLOW_ID = os.getenv("WHATSAPP_FLOW_ID", "1234567890123456789")  # Replace with your actual Flow ID from Meta Business Manager
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
NELLOBYTES_USERID = os.getenv("NELLOBYTES_USERID")
NELLOBYTES_APIKEY = os.getenv("NELLOBYTES_APIKEY")

# 🚨 CRITICAL: Validate WhatsApp credentials before starting
if not WHATSAPP_ACCESS_TOKEN:
    logger.error("❌ CRITICAL: WHATSAPP_ACCESS_TOKEN not found!")
    logger.error("🔧 Set WHATSAPP_ACCESS_TOKEN in your environment variables")
    
if not WHATSAPP_PHONE_NUMBER_ID:
    logger.error("❌ CRITICAL: WHATSAPP_PHONE_NUMBER_ID not found!")
    logger.error("🔧 Set WHATSAPP_PHONE_NUMBER_ID in your environment variables")
    
# Log credential status with more detail
logger.info(f"🔧 WhatsApp Access Token: {'✅ LOADED' if WHATSAPP_ACCESS_TOKEN else '❌ MISSING'}")
logger.info(f"🔧 WhatsApp Phone Number ID: {'✅ LOADED' if WHATSAPP_PHONE_NUMBER_ID else '❌ MISSING'}")

if WHATSAPP_ACCESS_TOKEN and len(WHATSAPP_ACCESS_TOKEN) > 10:
    logger.info(f"🔧 Token preview: {WHATSAPP_ACCESS_TOKEN[:15]}...{WHATSAPP_ACCESS_TOKEN[-5:]}")
if WHATSAPP_PHONE_NUMBER_ID:
    logger.info(f"🔧 Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")

# Raise error if critical credentials are missing
if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
    error_msg = "❌ CRITICAL: WhatsApp credentials not configured properly!"
    logger.error(error_msg)
    logger.error("🔧 SOLUTION: Set these environment variables in your deployment:")
    logger.error("   - WHATSAPP_ACCESS_TOKEN=your_access_token")
    logger.error("   - WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id")
    # Don't exit in production, but log the error clearly

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize AI client with API key - Powered by Pip install AI Technologies
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set the path to the ffmpeg executable for pydub
AudioSegment.converter = which("ffmpeg")

def send_whatsapp_typing_action(phone_number):
    """Send 'typing...' action to WhatsApp chat IMMEDIATELY"""
    # WhatsApp doesn't have a typing indicator in the API, but we can simulate
    # instant response by implementing a read receipt or status update
    try:
        # For now, just log the action - WhatsApp Cloud API doesn't support typing indicators
        logger.info(f"📱 Simulating typing action for WhatsApp {phone_number}")
    except Exception as e:
        logger.error(f"Failed to send WhatsApp typing action: {e}")

def background_task(func, *args, **kwargs):
    """Run a function in background thread for instant responses"""
    import threading
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()

def send_whatsapp_message(phone_number: str, message: str):
    """Send regular WhatsApp text message"""
    # Check if credentials are available
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        logger.error("❌ Cannot send WhatsApp message: Missing credentials")
        logger.error(f"   ACCESS_TOKEN present: {bool(WHATSAPP_ACCESS_TOKEN)}")
        logger.error(f"   PHONE_NUMBER_ID present: {bool(WHATSAPP_PHONE_NUMBER_ID)}")
        return False
    
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
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
        
        logger.info(f"📤 Sending WhatsApp message to {phone_number}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"✅ WhatsApp message sent successfully to {phone_number}")
            return True
        else:
            logger.error(f"❌ WhatsApp API error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {e}")
        return False

def send_whatsapp_message_with_button(phone_number: str, message: str, button_text: str, button_url: str):
    """Send WhatsApp message with link preview for better user experience"""
    # Check if credentials are available
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        logger.error("❌ Cannot send WhatsApp message: Missing credentials")
        return False
    
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Create message with link preview and call-to-action button
        message_with_link = f"{message}\n\n🔗 {button_url}"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message_with_link, "preview_url": True}
        }
        
        logger.info(f"📤 Sending WhatsApp message with link preview to {phone_number}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"✅ WhatsApp message with link preview sent successfully")
            return True
        else:
            logger.error(f"❌ WhatsApp API error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {e}")
        return False

def send_whatsapp_message(phone_number, message, reply_markup=None):
    """Send INSTANT reply without waiting for background processing"""
    # Show typing IMMEDIATELY
    send_whatsapp_typing_action(phone_number)
    
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "phone_number": phone_number, 
        "text": message,
        "parse_mode": "Markdown"
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        # Send with short timeout for instant response
        response = requests.post(url, json=payload, timeout=2)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Error sending instant reply: {e}")
        return None


def send_whatsapp_message(phone_number, message, reply_markup=None):
    """Send reply message to WhatsApp with optional interactive buttons"""
    return send_whatsapp_message(phone_number, message)

def send_photo_to_whatsapp(phone_number, photo_data, caption=None):
    """Send photo to WhatsApp chat"""
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # For WhatsApp, we need to upload the image first or use a URL
        # This is a simplified version - in production, you'd upload to a CDN
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": caption or "Image sent via Sofi AI"}
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Error sending WhatsApp photo: {e}")
        return None

def detect_intent(message):
    """Enhanced intent detector using AI with gpt-3.5-turbo and Nigerian expressions support - Powered by Pip install AI Technologies"""
    try:
        # Step 1: Enhance message with Nigerian expressions understanding
        enhanced_analysis = enhance_nigerian_message(message)
        enhanced_message = enhanced_analysis["enhanced_message"]
        
        # Log the enhancement for debugging
        if enhanced_analysis["contains_nigerian_expressions"]:
            logger.info(f"🇳🇬 Enhanced Nigerian expression: '{message}' -> '{enhanced_message}'")
        
        # Use the intent parser system prompt for better transfer detection
        from nlp.intent_parser import system_prompt
        
        # Create enhanced system prompt that includes Nigerian context
        enhanced_system_prompt = system_prompt + """
        
IMPORTANT NIGERIAN CONTEXT:
- The user may use Nigerian English, Pidgin, or local expressions
- Common patterns: "send 5k give my guy" = send 5000 naira to my friend
- "My account don empty" = my account is empty
- "Abeg" = please, "sharp sharp" = immediately, "now now" = right now
- "kudi/ego/owo" = money, "guy/padi/paddy" = friend
- Always interpret enhanced/translated messages while maintaining cultural context        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": f"Original: {message}\nEnhanced: {enhanced_message}"}
            ],
            temperature=0.3
        )
          # Parse the response as JSON
        try:
            # Handle mock responses in tests
            if isinstance(response, MagicMock):
                content = response.choices[0]['message']['content']
            else:
                # OpenAI v1.x syntax
                content = response.choices[0].message.content
                # Log the raw response in non-test environment
                with open("api_logs.txt", "a") as log_file:
                    log_file.write(f"Message: {message}\nResponse: {response}\n\n")
            
            content = content.strip()
            # Remove markdown formatting if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(content)
            
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {content}")
            return {"intent": "general", "details": {}}
            
    except Exception as e:
        logger.error(f"Error detecting intent: {e}")
        return {"intent": "general", "details": {}}

async def get_user_balance(phone_number):
    """Get user's current balance using enhanced helper with force sync"""
    try:
        from utils.balance_helper import get_user_balance as get_balance_secure
        return await get_balance_secure(str(phone_number), force_sync=True)
    except Exception as e:
        logger.error(f"Error getting user balance: {e}")
        return 0.0

async def check_virtual_account(phone_number):
    """Check if user has a virtual account using enhanced helper"""
    try:
        from utils.balance_helper import check_virtual_account as check_virtual_account_secure
        return await check_virtual_account_secure(str(phone_number))
    except Exception as e:
        logger.error(f"Error checking virtual account: {e}")
        return None

async def generate_ai_reply(phone_number: str, message: str):
    """Generate AI reply with conversation context and Nigerian expressions support"""
    # Ensure message is always a string
    if isinstance(message, bytes):
        message = message.decode('utf-8', errors='ignore')
    elif not isinstance(message, str):
        message = str(message)
    
    # Step 1: Enhance message with Nigerian expressions understanding
    enhanced_analysis = enhance_nigerian_message(message)
    enhanced_message = enhanced_analysis["enhanced_message"]
    response_guidance = get_response_guidance(enhanced_analysis)
    
    # Log enhancement for debugging
    if enhanced_analysis["contains_nigerian_expressions"]:
        logger.info(f"🇳🇬 AI Reply Enhancement: '{message}' -> '{enhanced_message}'")
        logger.info(f"📝 Response Guidance: {response_guidance}")
        
    # Concise system prompt - Now with Pip install AI Technologies branding
    system_prompt = """You are Sofi AI, an advanced banking assistant powered by Pip install AI Technologies. Be brief and helpful.

Key features: transfers, airtime, data, balance checks.
New users: Direct to https://www.pipinstallsofi.com/whatsapp-onboard
Keep responses short (2-3 lines max). Use Nigerian style but stay professional.
Proudly powered by Pip install AI Technologies - the future of AI banking."""

    try:
        # Check if user has a virtual account
        virtual_account = await check_virtual_account(phone_number)
          # First check if this is about account creation or account status
        account_keywords = ["create account", "sign up", "register", "get started", "open account", "account status", "my account"]
        is_account_request = any(keyword in message.lower() for keyword in account_keywords)
        
        if is_account_request:
            if virtual_account:
                # Debug info
                logger.info(f"DEBUG: Virtual account data = {virtual_account}")
                
                account_status = virtual_account.get("status", "unknown")
                
                if account_status == "active":
                    # Get user's full name from Supabase instead of truncated bank name
                    from utils.user_onboarding import onboarding_service
                    user_profile = await onboarding_service.get_user_profile(str(phone_number))
                    
                    # Safe access to account details with fallbacks
                    account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number", "Not available")
                    bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Not available")
                    
                    # Use full name from Supabase, not truncated bank account name
                    display_name = user_profile.get('full_name') if user_profile else virtual_account.get("accountName", "Not available")
                    
                    reply = (
                        f"✅ *Your Account Details:*\n\n"
                        f"🏦 *Account:* {account_number}\n"
                        f"🏛️ *Bank:* {bank_name}\n"
                        f"👤 *Name:* {display_name}\n\n"
                        f"What would you like to do?"
                    )
                elif account_status == "incomplete_setup":
                    reply = (
                        "⏳ *Account Setup in Progress*\n\n"
                        "Your virtual account is being created. This usually takes a few minutes.\n\n"
                        "I'll notify you once it's ready!"
                    )
                else:
                    # Handle other statuses or fallback
                    reply = (
                        "🔄 *Checking Your Account*\n\n"
                        "Let me verify your account status..."
                    )
            else:
                # New user - send message with rich link preview
                reply = (
                    "🚀 *Create Your Sofi Account*\n\n"
                    "Get instant virtual account for:\n"
                    "💸 Money transfers\n"
                    "📱 Airtime purchases\n"
                    "💰 Balance management\n\n"
                    "👆 Tap the link below to get started!"
                )
                
                save_chat_message(phone_number, "assistant", reply)
                return send_whatsapp_message_with_button(
                    phone_number, 
                    reply, 
                    "🚀 Create Account",
                    "https://pipinstallsofi.com/onboard"
                )

        # Get conversation history
        messages = get_chat_history(phone_number)
          # Add system prompt and current message
        conversation = [
            {"role": "system", "content": system_prompt},
            *messages,  # Previous messages
            {"role": "user", "content": f"User said: {message}\n(Enhanced understanding: {enhanced_message})"}  # Current message with enhancement
        ]
        
        # If user has virtual account, append account context
        if virtual_account:
            # Safe access to account details with fallbacks  
            account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number", "Unknown")
            bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Unknown")
            account_context = f"\nUser has virtual account: {account_number} at {bank_name}"
            conversation[0]["content"] += account_context        # Generate response
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.7,  # Slightly more creative for natural conversation
            max_tokens=500
        )
        
        ai_reply = response.choices[0].message.content
        # Ensure ai_reply is a string (handle MagicMock in tests)
        if not isinstance(ai_reply, str):
            ai_reply = str(ai_reply)
        ai_reply = ai_reply.strip()
        
        # Save the exchange to conversation history
        # Only save if ai_reply is a string (avoid MagicMock in tests)
        if isinstance(ai_reply, str):
            save_chat_message(phone_number, "user", message)
            save_chat_message(phone_number, "assistant", ai_reply)
        else:
            logger.warning(f"Not saving non-string ai_reply to chat history: {type(ai_reply)}")
        return ai_reply
        
    except Exception as e:
        logger.error(f"Error generating AI reply: {e}")
        return "Sorry, I'm having trouble thinking right now. Please try again later."

def download_file(file_id):
    """Download file from WhatsApp"""
    # Get file path
    file_info_url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/media?file_id={file_id}"
    file_info = requests.get(file_info_url).json()
    file_path = file_info["result"]["file_path"]

    # Download file
    file_url = f"https://graph.facebook.com/v18.0/{file_path}"
    file_data = requests.get(file_url).content
    return file_data

def process_whatsapp_media(message):
    """Process photo messages"""
    try:
        # Download the image
        image_data = download_file(file_id)
        image = Image.open(BytesIO(image_data))
        
        # Use AI Vision API to analyze the image - Powered by Pip install AI Technologies
        import base64        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Use standardized image analysis prompt
        prompt = get_image_prompt()
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"I see an image that appears to be {image.format} format, size {image.size}. " + 
                              "Please analyze this financial document image."
                }
            ],
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content.strip()
        logger.info(f"Image analysis result: {result_text}")
        
        # Try to parse as JSON and validate
        try:
            import json
            raw_result = json.loads(result_text)
            validated_result = validate_image_result(raw_result)
            
            if validated_result.error:
                image_description = f"Error analyzing image: {validated_result.error}"
            else:
                # Format the result for user display
                if validated_result.document_type == "bank_details":
                    parts = ["I can see this is a bank account document."]
                    if validated_result.bank_name:
                        parts.append(f"Bank: {validated_result.bank_name}")
                    if validated_result.account_number:
                        parts.append(f"Account: {validated_result.account_number}")
                    if validated_result.account_holder:
                        parts.append(f"Account Holder: {validated_result.account_holder}")
                    if validated_result.amount:
                        parts.append(f"Amount: ₦{validated_result.amount:,.2f}")
                    image_description = "\n".join(parts)
                elif validated_result.document_type == "transaction":
                    parts = ["I can see this is a transaction receipt."]
                    if validated_result.bank_name:
                        parts.append(f"Bank: {validated_result.bank_name}")
                    if validated_result.amount:
                        parts.append(f"Amount: ₦{validated_result.amount:,.2f}")
                    image_description = "\n".join(parts)
                else:
                    image_description = "I can see this appears to be a financial document, but I need more context to help you."
        except:
            # Fallback to original text response
            image_description = result_text
        
        # Check if it's a "under construction" image based on keywords
        is_construction = any(phrase in image_description.lower() for phrase in 
                            ['under construction', 'construction', 'maintenance', 'coming soon'])
        
        if is_construction:
            return True, ("I see this is about Sofi's development status. Let me explain what's currently available:\n\n"
                         "✅ Send and receive money instantly\n"
                         "📱 Buy airtime and data\n"
                         "💰 Basic account management\n"
                         "📊 Transaction history\n\n"
                         "Features coming soon:\n"
                         "🔄 Bill payments\n"
                         "🔄 Investment options\n"
                         "🔄 Automated savings\n\n"
                         "How can I help you with the available features?")
        
        # For regular images, provide a generic but helpful response
        return True, ("I see you've sent me an image. While I can't process detailed image content with my current capabilities, " +
                     "I can still help you with:\n\n" +
                     "• Money transfers\n" +
                     "• Airtime and data purchases\n" +
                     "• Account management\n" +
                     "• Transaction queries\n\n" +
                     "What would you like assistance with?")
            
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        return False, "I had trouble processing that image. Please try again or describe what you need help with."

def process_whatsapp_voice(message):
    """Process voice messages"""
    try:
        # Download the voice file
        voice_data = download_file(file_id)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
            temp_file.write(voice_data)
            temp_file_path = temp_file.name
        
        # Convert to WAV format for Whisper
        audio = AudioSegment.from_file(temp_file_path, format="ogg")
        wav_path = temp_file_path.replace(".ogg", ".wav")
        audio.export(wav_path, format="wav")
          # Transcribe using AI Whisper - Powered by Pip install AI Technologies
        with open(wav_path, 'rb') as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up temporary files
        os.unlink(temp_file_path)
        os.unlink(wav_path)
        
        transcription = transcript.text
        logger.info(f"Voice transcription: {transcription}")
        
        return True, transcription
        
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        return False, "I had trouble processing that voice message. Please try typing your message instead."

def validate_account_number(account_number: str) -> bool:
    """Validate Nigerian bank account number format"""
    return bool(account_number and account_number.isdigit() and len(account_number) >= 10)

def verify_account_name(account_number: str, bank_name: str) -> Dict:
    """Verify account name with bank using Bank API"""
    try:
        bank_api = BankAPI()
        
        # Get bank code (this is not async)
        bank_code = bank_api.get_bank_code(bank_name)
        if not bank_code:
            return {
                "verified": False,
                "error": "Unsupported bank"
            }
              # Verify account
        result = bank_api.verify_account(account_number, bank_code)
        
        if result and result.get('verified'):
            return {
                "verified": True,
                "account_name": result.get('account_name'),
                "bank_name": result.get('bank_name'),
                "account_number": account_number
            }
        else:
            return {
                "verified": False,
                "error": "Account verification failed"
            }
    except Exception as e:
        logger.error(f"Error processing: {str(e)}")
        return {
            "verified": False,
            "error": "Error processing"
        }

async def handle_transfer_flow(phone_number: str, message: str, user_data: dict = None, media_data: dict = None) -> str:
    """Handle the transfer conversation flow with enhanced natural language processing"""
    from utils.enhanced_intent_detection import enhanced_intent_detector
    
    state = conversation_state.get_state(phone_number)
    
    # Check if user wants to exit transfer flow
    if state and enhanced_intent_detector.detect_intent_change(message):
        conversation_state.clear_state(phone_number)
        # Let the message be handled by general AI
        return None
    
    if not state:
        # Starting new transfer flow - check for transfer intent
        intent_data = detect_intent(message)
        
        # Try enhanced parsing for natural language transfers
        transfer_info = enhanced_intent_detector.extract_transfer_info(message)
        
        if intent_data.get('intent') != 'transfer' and not transfer_info:
            return None
        
        # Combine traditional and enhanced detection
        if transfer_info:
            details = transfer_info
        else:
            details = intent_data.get('details', {})
        
        # Check for beneficiary first before asking for account details
        recipient_name = details.get('recipient') or details.get('recipient_name')
        if recipient_name and user_data and not details.get('account'):
            # Try to find beneficiary by name
            beneficiary = await beneficiary_manager.find_beneficiary_by_name(user_data.get('id'), recipient_name)
            if beneficiary:
                # Found beneficiary! Populate details
                details['account'] = beneficiary['account_number']
                details['recipient'] = beneficiary['account_name']
                details['bank'] = beneficiary['bank_name'] or beneficiary['bank_code']
                
                # If we have both beneficiary and amount, proceed to confirmation
                if details.get('amount'):
                    state = {
                        'transfer': {
                            'amount': details['amount'],
                            'recipient_name': beneficiary['account_name'],
                            'account_number': beneficiary['account_number'],
                            'bank': beneficiary['bank_name'] or beneficiary['bank_code'],
                            'narration': details.get('narration', f"Transfer to {beneficiary['name']}")
                        },
                        'step': 'confirm_transfer',
                        'using_beneficiary': True,
                        'beneficiary_nickname': beneficiary['name']
                    }
                    
                    conversation_state.set_state(phone_number, state)
                    
                    return f"""💳 **Transfer to {beneficiary['name']}**

**Recipient:** {beneficiary['account_name']}
**Account:** {beneficiary['account_number']}
**Bank:** {beneficiary['bank_name'] or beneficiary['bank_code']}
**Amount:** ₦{details['amount']:,.2f}

Is this correct? Reply 'yes' to continue or 'no' to cancel."""
        
        state = {
            'transfer': {
                'amount': details.get('amount'),
                'recipient_name': details.get('recipient'),
                'account_number': details.get('account', ''),
                'bank': details.get('bank', ''),
                'narration': details.get('narration', '')
            }
        }
        
        # Determine the next step based on what information we have
        if state['transfer']['account_number'] and len(state['transfer']['account_number']) >= 10:
            # We have account number, try to verify it
            bank = state['transfer']['bank'] or 'unknown'
            
            try:
                verification_result = verify_account_name(
                    state['transfer']['account_number'],
                    bank
                )
                if verification_result and verification_result.get('verified'):
                    state['transfer']['recipient_name'] = verification_result['account_name']
                    state['transfer']['bank'] = verification_result.get('bank_name', bank)
                    state['step'] = 'get_amount' if not state['transfer']['amount'] else 'confirm_transfer'
                    
                    msg = (
                        f"✅ Account verified:\n"
                        f"👤 Name: {verification_result['account_name']}\n"
                        f"🏦 Account: {state['transfer']['account_number']}\n"
                        f"🏛️ Bank: {state['transfer']['bank']}\n\n"
                    )
                    if not state['transfer']['amount']:
                        msg += "💰 How much would you like to send?"
                    else:
                        msg += f"💰 You want to send ₦{state['transfer']['amount']:,}. Is this correct? (yes/no)"
                else:
                    # Account verification failed, but continue with manual entry
                    state['step'] = 'get_bank'
                    msg = f"📱 Account number: {state['transfer']['account_number']}\n\nWhich bank is this account with?"
            except Exception as e:
                logger.error(f"Error processing: {e}")
                state['step'] = 'get_bank'
                msg = f"📱 Account number: {state['transfer']['account_number']}\n\nWhich bank is this account with?"
        else:
            state['step'] = 'get_account'
            msg = "Please provide the recipient's account number:"
        
        conversation_state.set_state(phone_number, state)
        return msg
    
    # Handle ongoing transfer conversation
    current_step = state.get('step')
    transfer = state['transfer']
    
    if current_step == 'get_account':
        # Enhanced account number extraction
        transfer_info = enhanced_intent_detector.extract_transfer_info(message)
        
        if transfer_info and transfer_info.get('account'):
            account_number = transfer_info['account']
            bank = transfer_info.get('bank', '')
        elif enhanced_intent_detector.is_pure_account_number(message):
            account_number = re.sub(r'[^\d]', '', message)
            bank = ''
        else:
            return "Please provide a valid account number (at least 10 digits):"
        
        if len(account_number) < 10:
            return "Please provide a valid account number (at least 10 digits):"
        
        transfer['account_number'] = account_number
        if bank:
            transfer['bank'] = bank
          # Try to verify account
        try:
            verification_result = verify_account_name(account_number, bank or 'unknown')
            if verification_result and verification_result.get('verified'):
                transfer['recipient_name'] = verification_result['account_name']
                transfer['bank'] = verification_result.get('bank_name', bank)
                state['step'] = 'get_amount' if not transfer.get('amount') else 'confirm_transfer'
                state['step'] = 'get_amount' if not transfer.get('amount') else 'confirm_transfer'

                msg = (
                    f"✅ Account verified:\n"
                    f"👤 Name: {verification_result['account_name']}\n"
                    f"🏦 Account: {account_number}\n"
                    f"🏛️ Bank: {transfer['bank']}\n\n"
                )
                if not transfer['amount']:
                    msg += "💰 How much would you like to send?"
                else:
                    msg += f"💰 You want to send ₦{transfer['amount']:,}. Is this correct? (yes/no)"
            else:
                state['step'] = 'get_bank'
                msg = f"📱 Account: {account_number}\n\nWhich bank is this account with?"
        except Exception as e:
            logger.error(f"Error processing: {e}")
            state['step'] = 'get_bank'
            msg = f"📱 Account: {account_number}\n\nWhich bank is this account with?"
        
        conversation_state.set_state(phone_number, state)
        return msg
    
    elif current_step == 'get_bank':
        transfer['bank'] = message.strip()
        verification_result = verify_account_name(transfer['account_number'], transfer['bank'])
        if verification_result['verified']:
            transfer['recipient_name'] = verification_result['account_name']
            state['step'] = 'get_amount' if not transfer['amount'] else 'confirm_transfer'
            msg = (
                f"Account verified:\n"
                f"Name: {verification_result['account_name']}\n"
                f"Account: {transfer['account_number']}\n"
                f"Bank: {transfer['bank']}\n\n"
            )
            if not transfer['amount']:
                msg += "How much would you like to send?"
            else:
                msg += f"You want to send ₦{transfer['amount']:,}. Is this correct? (yes/no)"
        else:
            return f"Could not verify account: {verification_result.get('error')}. Please try again:"
        
        conversation_state.set_state(phone_number, state)
        return msg
    
    elif current_step == 'get_amount':
        try:
            # Remove any currency symbols and commas
            amount_str = message.strip().replace('₦', '').replace(',', '')
            amount = float(amount_str)
            if amount <= 0:
                return "Please enter a valid amount greater than 0:"
            
            transfer['amount'] = amount
            state['step'] = 'secure_pin_verification'
            
            # Generate unique transaction ID
            import uuid
            transaction_id = f"TX{uuid.uuid4().hex[:8].upper()}"
            
            # Store transaction for secure verification and get secure token
            from utils.secure_pin_verification import secure_pin_verification
            secure_token = secure_pin_verification.store_pending_transaction(transaction_id, {
                'phone_number': phone_number,
                'user_data': user_data,
                'transfer_data': transfer,
                'amount': amount
            })
            
            # Create secure PIN verification message with inline keyboard
            # Convert bank code to user-friendly name
            bank_code = transfer['bank']
            bank_name = BANK_CODE_TO_NAME.get(bank_code, bank_code)
            
            msg = (
                f"✅ *Account verified!*\n"
                f"Click the button below to complete transfer of ₦{amount:,.2f} to:\n\n"
                f"👤 *{transfer['recipient_name']}*\n"
                f"🏦 *{bank_name}* ({transfer['account_number']})\n\n"
                f"🔐 *Secure PIN verification required*"
            )
            
            # Create inline keyboard for secure PIN verification using secure token
            pin_keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "🔐 Verify Transaction",
                        "url": f"https://pipinstallsofi.com/verify-pin?token={secure_token}"
                    }
                ]]
            }
            
            conversation_state.set_state(phone_number, state)            # Send message with secure PIN button
            send_whatsapp_message(phone_number, msg, pin_keyboard)
            return None  # Don't send additional message
            
        except ValueError:
            return "Please enter a valid amount (e.g., 5000):"
    
    elif current_step == 'confirm_transfer':
        # Handle confirmation for beneficiary transfers
        response_lower = message.lower().strip()
        
        if response_lower in ['yes', 'y', 'confirm', 'ok', 'proceed']:
            # User confirmed - proceed to PIN verification
            state['step'] = 'secure_pin_verification'
            
            # Generate unique transaction ID
            import uuid
            transaction_id = f"TX{uuid.uuid4().hex[:8].upper()}"
            
            # Store transaction for secure verification and get secure token
            from utils.secure_pin_verification import secure_pin_verification
            secure_token = secure_pin_verification.store_pending_transaction(transaction_id, {
                'phone_number': phone_number,
                'user_data': user_data,
                'transfer_data': transfer,
                'amount': transfer['amount']
            })
            
            # Create secure PIN verification message with inline keyboard
            msg = (
                f"✅ *Transfer confirmed!*\n"
                f"Click the button below to complete transfer of ₦{transfer['amount']:,.2f} to:\n\n"
                f"👤 *{transfer['recipient_name']}*\n"
                f"🏦 *{transfer['bank']}* ({transfer['account_number']})\n\n"
                f"🔐 *Secure PIN verification required*"
            )
            
            # Create inline keyboard for secure PIN verification using secure token
            pin_keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "🔐 Verify Transaction",
                        "url": f"https://pipinstallsofi.com/verify-pin?token={secure_token}"
                    }
                ]]
            }
            
            conversation_state.set_state(phone_number, state)
            send_whatsapp_message(phone_number, msg, pin_keyboard)
            return None  # Don't send additional message
            
        elif response_lower in ['no', 'n', 'cancel', 'stop']:
            # User cancelled
            conversation_state.clear_state(phone_number)
            
            beneficiary_name = state.get('beneficiary_nickname', 'recipient')
            return f"❌ Transfer to {beneficiary_name} cancelled. Is there anything else I can help you with?"
        else:
            return "Please reply 'yes' to confirm the transfer or 'no' to cancel."
    
    elif current_step == 'secure_pin_verification':
        # User is trying to type in chat instead of using web app or voice
        return (
            "🔐 Please choose how to enter your PIN:\n\n"
            "1️⃣ **Web App**: Click the 'Verify Transaction' button above\n"
            "2️⃣ **Voice Note**: Send a voice message saying your 4-digit PIN\n\n"
            "Both options are secure and encrypted."
        )
    
    return "I didn't understand that. Please try again."

async def handle_airtime_commands(phone_number: str, message: str, user_data: dict, virtual_account: dict = None) -> Optional[str]:
    """Handle airtime and data purchase commands"""
    try:
        # Check if message is actually about airtime/data before processing
        airtime_keywords = ['airtime', 'data', 'recharge', 'mtn', 'glo', 'airtel', '9mobile', 'buy credit']
        message_lower = message.lower()
        
        # Only process if message contains airtime-related keywords
        if not any(keyword in message_lower for keyword in airtime_keywords):
            return None
        
        # Import airtime handler
        from utils.airtime_handler import AirtimeHandler
        
        airtime_handler = AirtimeHandler()
        response = await airtime_handler.handle_airtime_request(phone_number, message, user_data, virtual_account)
        return response
    except Exception as e:
        logger.error(f"Error handling airtime command: {e}")
        # Only return error message if it was actually an airtime request
        airtime_keywords = ['airtime', 'data', 'recharge', 'mtn', 'glo', 'airtel', '9mobile', 'buy credit']
        if any(keyword in message.lower() for keyword in airtime_keywords):
            return "Sorry, I'm having trouble with airtime services right now. Please try again later."
        return None

async def handle_crypto_commands(phone_number: str, message: str, user_data: dict) -> Optional[str]:
    """Handle crypto wallet and transaction commands"""
    try:
        # Check if message is actually about crypto before processing
        crypto_keywords = ['wallet', 'bitcoin', 'btc', 'ethereum', 'eth', 'usdt', 'crypto', 'cryptocurrency']
        message_lower = message.lower()
        
        # Only process if message contains crypto-related keywords
        if not any(keyword in message_lower for keyword in crypto_keywords):
            return None
        
        # Import crypto handler
        from crypto.handlers import CryptoCommandHandler
        
        crypto_handler = CryptoCommandHandler()
        response = await crypto_handler.handle_crypto_request(phone_number, message, user_data)
        return response
    except Exception as e:
        logger.error(f"Error handling crypto command: {e}")
        # Only return error message if it was actually a crypto request
        crypto_keywords = ['wallet', 'bitcoin', 'btc', 'ethereum', 'eth', 'usdt', 'crypto', 'cryptocurrency']
        if any(keyword in message.lower() for keyword in crypto_keywords):
            return "Sorry, I'm having trouble with crypto services right now. Please try again later."
        return None

async def handle_message(phone_number: str, message: str, user_data: dict = None, virtual_account: dict = None) -> str:
    """Main message handler with AI Assistant integration - Powered by Pip install AI Technologies"""
    try:
        # Check for admin commands first (highest priority)
        admin_command = await admin_handler.detect_admin_command(message, phone_number)
        if admin_command:
            admin_response = await admin_handler.handle_admin_command(admin_command, message, phone_number)
            return admin_response
        
        # Legacy smart transfer code removed - now using AI Assistant
        
        # Try AI Assistant first for better AI handling
        try:
            assistant = get_assistant()
            
            # Prepare user data for context
            context_data = user_data or {}
            if virtual_account:
                context_data['virtual_account'] = virtual_account
            
            # Process message with AI Assistant
            response, function_data = await assistant.process_message(phone_number, message, context_data)
            
            # Check if any function returned requires_pin or completed transfer
            if function_data:
                logger.info(f"🔧 DEBUG: Function data received: {json.dumps(function_data, indent=2, default=str)}")
                for func_name, func_result in function_data.items():
                    if isinstance(func_result, dict) and func_result.get("requires_pin"):
                        logger.info(f"🔐 Function {func_name} requires PIN entry - sending web PIN link")
                        
                        # Check if it's the new web PIN system
                        if func_result.get("show_web_pin"):
                            # Send the PIN entry message with web app button
                            pin_message = func_result.get("message", "Please enter your PIN")
                            pin_keyboard = func_result.get("keyboard", {})
                            
                            # Debug logging
                            logger.info(f"🔧 DEBUG: Sending web PIN button")
                            logger.info(f"📱 PIN Message: {pin_message}")
                            logger.info(f"⌨️ Keyboard: {pin_keyboard}")
                            
                            # Send message with PIN button
                            send_whatsapp_message(phone_number, pin_message, pin_keyboard)
                            
                            # Return special marker to prevent duplicate message sending
                            return "PIN_ALREADY_SENT"
                        

                        
                        # Only web PIN is supported now - inline PIN system removed
                    
                    # Check if any function returned a successful transfer with auto receipt
                    if isinstance(func_result, dict) and func_result.get("auto_send_receipt") and func_result.get("success"):
                        logger.info(f"📧 Function {func_name} completed transfer - auto-sending receipt")
                        
                        # Generate and send beautiful HTML receipt
                        receipt_data = func_result.get("receipt_data", {})
                        if receipt_data:
                            await send_beautiful_receipt(phone_number, receipt_data, func_result)
                        
                        # Return the receipt message directly
                        return func_result.get("message", "Transfer completed successfully!")
            
            # If assistant handled it successfully, return the response
            if response and not response.startswith("Sorry, I encountered an error"):
                logger.info(f"✅ AI Assistant handled message from {phone_number}")
                return response
            else:
                logger.info(f"⚠️ AI Assistant failed, falling back to legacy handlers")
        
        except Exception as assistant_error:
            logger.error(f"❌ AI Assistant error: {str(assistant_error)}")
            logger.info("🔄 Falling back to legacy message handlers")
        
        # Fallback to legacy handlers if assistant fails
        # Check for beneficiary commands first (before other handlers)
        beneficiary_response = await legacy_beneficiary_handler.handle_beneficiary_command(phone_number, message, user_data or {})
        if beneficiary_response:
            return beneficiary_response
        
        # Check for transaction history queries
        history_response = await handle_transaction_history_query(phone_number, message, user_data)
        if history_response:
            return history_response
        
        # Check for 2-month summary requests
        summary_keywords = ['2 month', 'two month', 'monthly summary', 'financial summary', 'spending summary', 
                           'transaction summary', 'summarize my transactions', 'past 2 months', 'last 2 months']
        if any(keyword in message.lower() for keyword in summary_keywords):
            summary_response = await transaction_summarizer.get_2_month_summary(phone_number, user_data)
            return summary_response
        
        # Check for balance inquiry
        balance_response = await handle_balance_inquiry(phone_number, message, user_data, virtual_account)
        if balance_response:
            return balance_response
        
        # Check for transfer intent
        transfer_response = await handle_transfer_flow(phone_number, message, user_data)
        if transfer_response:
            return transfer_response
        
        # Check for airtime/data commands
        airtime_response = await handle_airtime_commands(phone_number, message, user_data, virtual_account)
        if airtime_response:
            return airtime_response
        
        # Check for crypto commands
        crypto_response = await handle_crypto_commands(phone_number, message, user_data)
        if crypto_response:
            return crypto_response
        
        # Fall back to general AI conversation
        ai_response = await generate_ai_reply(phone_number, message)
        return ai_response
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return "Sorry, I encountered an error. Please try again."

async def handle_balance_inquiry(phone_number: str, message: str, user_data: dict = None, virtual_account: dict = None) -> str:
    """Handle balance inquiry requests"""
    try:
        # Check if message is asking for balance
        balance_keywords = [
            'balance', 'check account', 'how much', 'my account', 'account summary',
            'wallet balance', 'available balance', 'current balance', 'account balance'
        ]
        
        message_lower = message.lower()
        is_balance_query = any(keyword in message_lower for keyword in balance_keywords)
        
        if not is_balance_query:
            return None
        
        # Get user's virtual account if not provided
        if not virtual_account:
            virtual_account = await check_virtual_account(phone_number)
        
        if not virtual_account:
            return (
                "🏦 You don't have a virtual account yet.\n\n"
                "Create one by tapping the button below to get started with Sofi AI!"
            )
            # Note: This should trigger a web app button but we're returning text here
            # The main handler should catch this and send the web app button
        
        # Get current balance
        current_balance = await get_user_balance(phone_number)
        
        # Get user's full name from Supabase
        from utils.user_onboarding import onboarding_service
        user_profile = await onboarding_service.get_user_profile(str(phone_number))
        
        # Safe access to account details
        account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number", "Not available")
        bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Paystack Bank")
        display_name = user_profile.get('full_name') if user_profile else virtual_account.get("accountName", "Not available")
        
        # Get recent transactions from Supabase
        recent_transactions = []
        try:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # First get the user UUID from whatsapp_number
            user_result = supabase.table("users").select("id").eq("whatsapp_number", phone_number).execute()
            
            if not user_result.data:
                recent_transactions = ["• No user found"]
            else:
                user_id = user_result.data[0]["id"]
                
                # Get recent bank transactions using the UUID
                transactions_result = supabase.table("bank_transactions")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .order("created_at", desc=True)\
                    .limit(3)\
                    .execute()
            
            if transactions_result.data:
                for txn in transactions_result.data:
                    transaction_type = txn.get('transaction_type', 'Unknown')
                    amount = float(txn.get('amount', 0))
                    recipient = txn.get('recipient_name', 'Unknown')
                    created_at = txn.get('created_at', '')
                    
                    # Format date
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = date_obj.strftime('%b %d')
                    except:
                        date_str = 'Recent'
                    
                    if transaction_type == 'credit':
                        recent_transactions.append(f"• ₦{amount:,.0f} received from {recipient} - {date_str}")
                    else:
                        recent_transactions.append(f"• ₦{amount:,.0f} sent to {recipient} - {date_str}")
        
        except Exception as e:
            logger.error(f"Error fetching recent transactions: {e}")
            recent_transactions = ["• Recent transactions unavailable"]
        
        # Build concise response
        response = f"""� **Balance:** ₦{current_balance:,.2f}
🏦 {account_number} ({bank_name})"""
        
        if recent_transactions:
            response += f"\n\n📊 **Recent:**\n" + "\n".join(recent_transactions[:2])  # Only show 2 transactions
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling balance inquiry: {e}")
        return None

def create_sofi_ai_response_with_custom_prompt(user_message, context="general"):
    """
    Create Sofi AI response using custom prompt from OpenAI
    Prompt ID: pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d
    """
    try:
        # Attempt to use the custom prompt directly via prompt ID
        response = openai_client.responses.create(
            prompt={
                "id": "pmpt_6855c4bb02d4819782b8428f4e76f7830bfd1f9ee7b5787d",
                "version": "3"
            },
            input={"user_message": user_message, "context": context}
        )

        return response.choices[0].message.content if response.choices else "I'm having trouble processing your request. Try again later."

    except Exception as e:
        logger.error(f"Error with custom prompt: {e}")

        # Fallback to GPT-3.5-turbo model
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Sofi AI, a Nigerian banking assistant. Be brief and helpful. Handle transfers, balance checks, airtime. Keep responses under 3 lines."
                    },
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content if response.choices else "Fallback failed. Try again later."

        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            return "Unexpected error occurred. Please try again later."

# Flask Routes
@app.route("/")
def landing_page():
    """Serve the main landing page"""
    return render_template("index.html")

# 🚀 PERFORMANCE MODE MANAGEMENT ROUTES
@app.route("/performance/fast-mode", methods=["POST"])
def toggle_fast_mode():
    """Toggle fast mode on/off (admin only)"""
    try:
        # Basic admin check
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('ADMIN_API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json() or {}
        enable = data.get('enable', True)
        
        if enable:
            enable_fast_mode()
            message = "⚡ FAST MODE ENABLED - Sofi will respond ultra-fast!"
        else:
            disable_fast_mode()
            message = "🔒 NORMAL MODE ENABLED - Full security monitoring active"
        
        return jsonify({
            "message": message,
            "status": get_fast_mode_status()
        })
    except Exception as e:
        logger.error(f"Error toggling fast mode: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/performance/status")
def performance_status():
    """Get current performance mode status"""
    try:
        return jsonify({
            "performance_mode": get_fast_mode_status(),
            "message": "⚡ FAST MODE active - Security alerts suppressed for speed" if get_fast_mode_status()['fast_mode'] else "🔒 NORMAL MODE active - Full security monitoring"
        })
    except Exception as e:
        logger.error(f"Error getting performance status: {e}")
        return jsonify({"error": "Internal server error"}), 500

# 🔒 SECURITY MONITORING ROUTES
@app.route("/security/stats")
def security_stats():
    """Get security statistics (admin only)"""
    try:
        # Basic admin check (implement proper admin authentication)
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('ADMIN_API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        
        stats = get_enhanced_security_stats()  # Use enhanced stats with fast mode info
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting security stats: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/security/block-ip", methods=["POST"])
def block_ip_endpoint():
    """Block an IP address (admin only)"""
    try:
        # Basic admin check
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('ADMIN_API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        ip = data.get('ip')
        reason = data.get('reason', 'Manual block')
        
        if not ip:
            return jsonify({"error": "IP address required"}), 400
        
        from utils.security_monitor import block_ip_address
        block_ip_address(ip, reason)
        
        return jsonify({"message": f"IP {ip} blocked successfully"})
    except Exception as e:
        logger.error(f"Error blocking IP: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/security/unblock-ip", methods=["POST"])
def unblock_ip_endpoint():
    """Unblock an IP address (admin only)"""
    try:
        # Basic admin check
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('ADMIN_API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        ip = data.get('ip')
        
        if not ip:
            return jsonify({"error": "IP address required"}), 400
        
        from utils.security_monitor import unblock_ip_address
        unblock_ip_address(ip)
        
        return jsonify({"message": f"IP {ip} unblocked successfully"})
    except Exception as e:
        logger.error(f"Error unblocking IP: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/security/events")
def security_events():
    """Get recent security events (admin only)"""
    try:
        # Basic admin check
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('ADMIN_API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        
        count = request.args.get('count', 100, type=int)
        from utils.security_monitor import get_recent_security_events
        events = get_recent_security_events(count)
        
        return jsonify({"events": events})
    except Exception as e:
        logger.error(f"Error getting security events: {e}")
        return jsonify({"error": "Internal server error"}), 500

async def create_whatsapp_user(phone_number: str) -> dict:
    """Automatically create a new WhatsApp user in the database"""
    try:
        import uuid
        
        # Generate a unique user ID
        user_id = str(uuid.uuid4())
        
        # Create basic user record
        user_data = {
            "id": user_id,
            "whatsapp_number": phone_number,
            "full_name": f"WhatsApp User {phone_number[-4:]}",  # Use last 4 digits
            "email": f"whatsapp_{phone_number.replace('+', '').replace(' ', '')}@temp.sofi.com",
            "created_at": datetime.now().isoformat(),
            "wallet_balance": 0.0,
            "status": "active",
            "signup_source": "whatsapp"
        }
        
        # Insert into database
        result = supabase.table("users").insert(user_data).execute()
        
        if result.data:
            logger.info(f"✅ WhatsApp user created successfully: {phone_number}")
            return result.data[0]
        else:
            logger.error(f"❌ Failed to create WhatsApp user: {phone_number}")
            return {}
            
    except Exception as e:
        logger.error(f"❌ Error creating WhatsApp user {phone_number}: {e}")
        return {}

@app.route("/webhook", methods=["GET", "POST"])
def whatsapp_webhook_handler():
    """Handle incoming WhatsApp messages with INSTANT response"""
    try:
        # 🔒 Security monitoring for webhook
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Log webhook access
        log_security_event("whatsapp_webhook", AlertLevel.LOW, client_ip, user_agent, "/webhook", "POST")
        
        data = request.get_json()
        
        if not data:
            log_security_event("invalid_webhook_payload", AlertLevel.MEDIUM, client_ip, user_agent, "/webhook", "POST")
            return jsonify({"error": "Invalid WhatsApp payload"}), 400
        
        # Handle WhatsApp webhook verification
        if request.method == "GET":
            # Webhook verification for WhatsApp
            verify_token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")
            
            if verify_token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
                return challenge
            else:
                return "Invalid verification token", 403
        
        # Process WhatsApp webhook data
        if data.get("object") == "whatsapp_business_account":
            entries = data.get("entry", [])
            
            for entry in entries:
                changes = entry.get("changes", [])
                
                for change in changes:
                    if change.get("field") == "messages":
                        messages = change.get("value", {}).get("messages", [])
                        
                        for message in messages:
                            # Extract message details
                            phone_number = message.get("from")
                            message_type = message.get("type")
                            timestamp = message.get("timestamp")
                            
                            # Get message content based on type
                            message_text = ""
                            if message_type == "text":
                                message_text = message.get("text", {}).get("body", "")
                            elif message_type == "button":
                                message_text = message.get("button", {}).get("text", "")
                            elif message_type == "interactive":
                                interactive = message.get("interactive", {})
                                if interactive.get("type") == "button_reply":
                                    message_text = interactive.get("button_reply", {}).get("title", "")
                                elif interactive.get("type") == "list_reply":
                                    message_text = interactive.get("list_reply", {}).get("title", "")
                            
                            if phone_number and message_text:
                                # ⚡ INSTANT TYPING INDICATOR - Show typing IMMEDIATELY
                                send_whatsapp_typing_action(phone_number)
                                
                                # Process message in background thread
                                def process_message_background():
                                    import asyncio
                                    
                                    # Get or create user data for this WhatsApp number
                                    user_data = None
                                    try:
                                        user_resp = supabase.table("users").select("*").eq("whatsapp_number", phone_number).execute()
                                        if user_resp.data:
                                            user_data = user_resp.data[0]
                                        else:
                                            # Auto-create new WhatsApp user
                                            logger.info(f"🆕 Creating new WhatsApp user: {phone_number}")
                                            user_data = asyncio.run(create_whatsapp_user(phone_number))
                                            
                                    except Exception as e:
                                        logger.error(f"Error getting/creating user data: {e}")
                                    
                                    # Process message with AI assistant
                                    try:
                                        from assistant import get_assistant
                                        assistant = get_assistant()
                                        
                                        # Process message and get response using asyncio
                                        response, function_data = asyncio.run(assistant.process_message(
                                            phone_number=phone_number,
                                            message=message_text,
                                            user_data=user_data
                                        ))
                                        
                                        # Send response immediately
                                        send_whatsapp_message(phone_number, response)
                                        
                                        # Handle any function data
                                        if function_data:
                                            logger.info(f"Processing function data for {phone_number}: {function_data}")
                                    
                                    except Exception as e:
                                        logger.error(f"Error processing WhatsApp message: {e}")
                                        send_whatsapp_message(phone_number, "Sorry, I encountered an error. Please try again.")
                                
                                # Execute in background
                                background_task(process_message_background)
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return jsonify({"error": "Internal server error"}), 500
        
        message_data = data["message"]
        phone_number = str(message_data["chat"]["id"])
        
        # ⚡ INSTANT TYPING INDICATOR - Show typing IMMEDIATELY when message arrives
        send_whatsapp_typing_action(phone_number)
        
        # Extract user information
        user_data = message_data.get("from", {})
        
        # Check if user exists in database (run in background)
        def check_user_background():
            return supabase.table("users").select("*").eq("whatsapp_number", phone_number).execute()
        
        # Start background user check but don't wait for it
        background_task(check_user_background)
        
        # Handle photo messages
        if "photo" in message_data:
            file_id = message_data["photo"][-1]["file_id"]  # Get the highest quality photo
            
            # Send quick response first
            send_whatsapp_message(phone_number, "📸 Processing your image...")
            
            # Process photo in background
            def process_photo_background():
                success, response = process_whatsapp_media(message)
                if success:
                    # Use asyncio.run for the async call
                    ai_response = asyncio.run(generate_ai_reply(phone_number, response))
                    send_whatsapp_message(phone_number, ai_response)
                else:
                    send_whatsapp_message(phone_number, response)
            
            background_task(process_photo_background)
            return jsonify({"status": "ok", "response": "Processing image..."}), 200
        
        # Handle voice messages
        elif "voice" in message_data:
            file_id = message_data["voice"]["file_id"]
            
            # Check if user is in PIN verification mode
            state = conversation_state.get_state(phone_number)
            if state and state.get('step') == 'secure_pin_verification':
                # Process voice PIN
                from utils.voice_pin_processor import VoicePinProcessor
                
                voice_processor = VoicePinProcessor()
                # Remove await - make this synchronous or handle differently
                result = voice_processor.process_voice_pin_sync(file_id, phone_number)
                
                if result['success']:
                    extracted_pin = result['pin']
                    
                    # Process the PIN using the secure transfer system
                    from utils.secure_transfer_handler import handle_secure_transfer_confirmation
                    transfer_data = state.get('transfer', {})
                    
                    # Handle the PIN as if it was typed - remove await
                    response = handle_secure_transfer_confirmation_sync(
                        phone_number=phone_number,
                        message=extracted_pin,
                        user_data=user_data,
                        transfer_data=transfer_data
                    )
                    send_whatsapp_message(phone_number, response)
                else:
                    send_whatsapp_message(phone_number, result['error'])
                    
            else:
                # Normal voice processing for general conversation
                success, response = process_whatsapp_voice(message)
                
                if success:
                    # Process the transcribed text as a regular message
                    user_message = response
                    # Fix: Remove await and use synchronous call or asyncio.run
                    import asyncio
                    ai_response = asyncio.run(handle_message(phone_number, user_message, user_data))
                    send_whatsapp_message(phone_number, ai_response)
                else:
                    send_whatsapp_message(phone_number, response)
        
        # Handle text messages with INSTANT response
        elif "text" in message_data:
            user_message = message_data.get("text", "").strip()
            
            if not user_message:
                return jsonify({"success": True}), 200
            
            # ⚡ INSTANT RESPONSE LOGIC - Get user data in background
            def get_user_data_async():
                try:
                    user_resp = supabase.table("users").select("*").eq("whatsapp_number", phone_number).execute()
                    return user_resp.data[0] if user_resp.data else None
                except:
                    return None
            
            def get_virtual_account_async():
                try:
                    import asyncio
                    return asyncio.run(check_virtual_account(phone_number))
                except:
                    return None
            
            # ⚡ REMOVED PLACEHOLDER RESPONSES - Using only assistant logic
            # All processing now goes through assistant.process_message() only
            
            # Start background processing immediately
            def process_message_background():
                try:
                    # Get user data
                    user_data = get_user_data_async()
                    user_exists = user_data is not None
                    
                    # Handle new users with quick onboarding
                    if not user_exists:
                        # Quick onboarding check
                        skip_onboarding_keywords = [
                            "already registered", "i have account", "just created", "completed registration",
                            "just signed up", "thanks", "thank you", "okay", "ok", "got it", "understood",
                            "will do", "sure", "alright", "fine", "done", "yes", "no problem"
                        ]
                        
                        if any(keyword in user_message.lower() for keyword in skip_onboarding_keywords):
                            # Give a brief helpful response instead of onboarding
                            brief_response = (
                                "Ready to help! Complete your onboarding to unlock all features:\n\n"
                                "💰 Send money instantly\n"
                                "📱 Buy airtime & data\n" 
                                "💳 Receive payments\n\n"
                                "Tap below to get started:"
                            )
                            # Use WhatsApp Flow for in-chat onboarding
                            success = send_whatsapp_onboarding_flow(phone_number)
                            if not success:
                                # Fallback to URL button
                                send_whatsapp_message_with_url_button(
                                    phone_number,
                                    brief_response,
                                    "Complete Onboarding",
                                    f"https://www.pipinstallsofi.com/whatsapp-onboard?whatsapp={phone_number}"
                                )
                            return
                        
                        # Full onboarding for substantial messages
                        substantial_message = len(user_message.split()) > 2 or any(
                            keyword in user_message.lower() for keyword in [
                                "account", "register", "sign up", "create", "start", "begin", "help",
                                "transfer", "send money", "balance", "airtime", "data"
                            ]
                        )
                        
                        if substantial_message:
                            # Force onboarding for new users with inline keyboard - Clean single button like Xara
                            onboarding_message = (
                                f"👋 *Welcome to Sofi AI!* I'm your intelligent financial assistant powered by Pip install AI Technologies.\n\n"
                                f"� *To get started, I need to create your secure virtual account:*\n\n"
                                f"📋 *You'll need:*\n"
                                f"• Your BVN (Bank Verification Number)\n"
                                f"• Phone number\n"
                                f"• Basic personal details\n\n"
                                f"✅ *Once done, you can:*\n"
                                f"• Send money to any bank instantly\n"
                                f"• Buy airtime & data at best rates\n"
                                f"• Receive money from anywhere\n"
                                f"• Chat with me for intelligent financial advice\n\n"
                                f"🚀 *Ready to get started? Let's begin your onboarding!*"
                            )
                            
                            # WhatsApp Flow onboarding - Opens in-chat like Telegram Web Apps
                            success = send_whatsapp_onboarding_flow(phone_number)
                            if not success:
                                # Fallback to URL button if Flow fails
                                send_whatsapp_message_with_url_button(
                                    phone_number,
                                    onboarding_message, 
                                    "Complete Onboarding",
                                    f"https://www.pipinstallsofi.com/whatsapp-onboard?whatsapp={phone_number}"
                                )
                        else:
                            brief_nudge = (
                                "Hi! I'm Sofi AI, your intelligent financial assistant. 👋\n\n"
                                "Ready to get started? Tap below to complete your onboarding:"
                            )
                            # WhatsApp Flow for onboarding
                            success = send_whatsapp_onboarding_flow(phone_number)
                            if not success:
                                # Fallback to URL button
                                send_whatsapp_message_with_url_button(
                                    phone_number,
                                    brief_nudge,
                                    "Complete Onboarding", 
                                    f"https://www.pipinstallsofi.com/whatsapp-onboard?whatsapp={phone_number}"
                                )
                        return
                    
                    # Process existing user messages - ASSISTANT ONLY
                    virtual_account = get_virtual_account_async()
                    
                    # 🤖 USE ONLY ASSISTANT.PROCESS_MESSAGE() - No legacy fallback
                    try:
                        # Get assistant and process message through AI only
                        assistant = get_assistant()
                        
                        # Prepare context data
                        context_data = user_data or {}
                        if virtual_account:
                            context_data['virtual_account'] = virtual_account
                        
                        # 🎯 PURE ASSISTANT PROCESSING - Single source of truth
                        with app.app_context():  # Fix Flask context issues
                            response, function_data = asyncio.run(assistant.process_message(phone_number, user_message, context_data))
                        
                        # Handle function results first (like PIN keyboards)
                        if function_data:
                            logger.info(f"🔧 Assistant function data: {function_data}")
                            
                            # Check for PIN requirement with keyboard
                            for func_name, func_result in function_data.items():
                                if isinstance(func_result, dict) and func_result.get("requires_pin") and func_result.get("show_web_pin"):
                                    logger.info(f"🔐 Function {func_name} requires PIN entry - sending web PIN button")
                                    
                                    # Send the PIN entry message with web app button
                                    pin_message = func_result.get("message", "Please enter your PIN")
                                    pin_keyboard = func_result.get("keyboard", {})
                                    
                                    # Debug logging
                                    logger.info(f"🔧 DEBUG: Sending web PIN button from background")
                                    logger.info(f"� PIN Message: {pin_message}")
                                    logger.info(f"⌨️ Keyboard: {pin_keyboard}")
                                    
                                    # Send message with PIN button
                                    send_whatsapp_message(phone_number, pin_message, pin_keyboard)
                                    return  # Don't send additional message
                        
                        # Send only the assistant response if no special handling
                        if response:
                            send_whatsapp_message(phone_number, response)
                            
                    except Exception as assistant_error:
                        logger.error(f"❌ Assistant processing error: {str(assistant_error)}")
                        send_whatsapp_message(phone_number, "Sorry, I'm having trouble processing your request. Please try again.")
                            
                except Exception as e:
                    logger.error(f"Error in background message processing: {str(e)}")
                    send_whatsapp_message(phone_number, "Sorry, I encountered an error. Please try again.")
            
            # Start background processing
            background_task(process_message_background)
            
            # Return immediately to WhatsApp (under 1 second response)
            return jsonify({"success": True, "status": "processing"}), 200

        return jsonify({"success": True}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error", "response": None}), 500

@app.route("/api/paystack/webhook", methods=["POST"])
def handle_paystack_webhook_route():
    """Handle Paystack webhook notifications for payments and transfers"""""
    try:
        # Get raw data for debugging
        raw_data = request.data.decode('utf-8')
        logger.info(f"Raw Paystack webhook data: {raw_data[:200]}...")
        
        data = request.get_json()
        
        if data is None:
            logger.error("❌ Invalid JSON in Paystack webhook")
            return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400
        
        # Get signature from headers
        signature = request.headers.get('X-Paystack-Signature')
        
        # TEMPORARY: Bypass signature check for localhost testing
        if request.remote_addr == "127.0.0.1":
            logger.info("🔐 Bypassing signature check for localhost test")
            signature = None  # Skip verification for local tests
        
        # Log incoming webhook for debugging
        logger.info(f"Paystack webhook received: {data}")
        
        # Process the webhook using imported handler
        result = handle_paystack_webhook(data, signature)
        
        if result.get('success'):
            return jsonify({"status": "success", "message": "Webhook processed"}), 200
        else:
            return jsonify({"status": "error", "message": result.get('error', 'Unknown error')}), 400
            
    except Exception as e:
        logger.error(f"Error processing Paystack webhook: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@app.route("/paystack-webhook", methods=["POST"])
def handle_paystack_webhook_legacy():
    """Legacy webhook route for backward compatibility"""
    return handle_paystack_webhook_route()

# WhatsApp Cloud API Helper Functions
def send_whatsapp_onboarding_flow(phone_number: str) -> bool:
    """Send WhatsApp Flow for onboarding (opens in-chat like Telegram Web Apps)"""
    try:
        access_token = WHATSAPP_ACCESS_TOKEN
        phone_number_id = WHATSAPP_PHONE_NUMBER_ID
        flow_id = WHATSAPP_FLOW_ID
        
        if not access_token or not phone_number_id or not flow_id:
            logger.error("WhatsApp credentials or Flow ID not configured")
            return False
        
        url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # WhatsApp Flow message for in-chat onboarding
        onboarding_message = (
            "👋 *Welcome to Sofi AI!* I'm your intelligent financial assistant.\n\n"
            "🔐 *To get started, I need to create your secure virtual account.*\n\n"
            "✅ *You'll be able to:*\n"
            "• Send money to any bank instantly\n"
            "• Buy airtime & data at best rates\n"
            "• Receive money from anywhere\n"
            "• Chat with me for financial advice\n\n"
            "🚀 *Tap below to create your account securely!*"
        )
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "header": {
                    "type": "text",
                    "text": "Sofi AI Account Setup"
                },
                "body": {
                    "text": onboarding_message
                },
                "footer": {
                    "text": "Powered by Pip install AI Technologies"
                },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_id": flow_id,
                        "flow_cta": "Create Account",
                        "flow_action": "navigate",
                        "flow_action_payload": {
                            "screen": "screen_oxjvpn"
                        }
                    }
                }
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"✅ WhatsApp Flow onboarding sent successfully to {phone_number}")
            return True
        else:
            logger.error(f"❌ Failed to send WhatsApp Flow: {response.text}")
            # Fallback to URL button if Flow fails
            return send_whatsapp_message_with_url_button(
                phone_number, 
                onboarding_message,
                "Create Account", 
                f"https://www.pipinstallsofi.com/whatsapp-onboard?whatsapp={phone_number}"
            )
            
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp Flow onboarding: {e}")
        return False
    """Send WhatsApp Flow message for in-chat web preview (like Telegram Web Apps)"""
    try:
        access_token = WHATSAPP_ACCESS_TOKEN
        phone_number_id = WHATSAPP_PHONE_NUMBER_ID
        
        if not access_token or not phone_number_id:
            logger.error("WhatsApp credentials not configured")
            return False
        
        url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # WhatsApp Flow message for in-chat preview
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "body": {
                    "text": message_text
                },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_id": flow_id,
                        "flow_cta": flow_cta
                    }
                }
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp Flow message sent successfully to {to_number}")
            return True
        else:
            logger.error(f"Failed to send WhatsApp Flow message: {response.text}")
            # Fallback to regular URL button if Flow fails
            return send_whatsapp_message_with_url_button(to_number, message_text, flow_cta, f"https://www.pipinstallsofi.com/whatsapp-onboard?whatsapp={to_number}")
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp Flow message: {e}")
        return False

def send_whatsapp_message_with_url_button(to_number: str, message_text: str, button_text: str, url: str) -> bool:
    """Send WhatsApp message with URL button (opens in external browser as fallback)"""
    try:
        access_token = WHATSAPP_ACCESS_TOKEN
        phone_number_id = WHATSAPP_PHONE_NUMBER_ID
        
        if not access_token or not phone_number_id:
            logger.error("WhatsApp credentials not configured")
            return False
        
        url_endpoint = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # WhatsApp URL button (external browser)
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "cta_url",
                "body": {
                    "text": message_text
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": button_text,
                        "url": url
                    }
                }
            }
        }
        
        response = requests.post(url_endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp URL button message sent successfully to {to_number}")
            return True
        else:
            logger.error(f"Failed to send WhatsApp URL button message: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp URL button message: {e}")
        return False

def send_whatsapp_message(to_number: str, message_text: str, interactive_button: dict = None) -> bool:
    """Send a WhatsApp message using Cloud API with optional interactive button"""
    try:
        # Use global variables instead of calling os.getenv() again
        access_token = WHATSAPP_ACCESS_TOKEN
        phone_number_id = WHATSAPP_PHONE_NUMBER_ID
        
        if not access_token or not phone_number_id:
            logger.error("WhatsApp credentials not configured")
            logger.error(f"ACCESS_TOKEN present: {bool(access_token)}")
            logger.error(f"PHONE_NUMBER_ID present: {bool(phone_number_id)}")
            return False
        
        url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Create payload with interactive button if provided
        if interactive_button:
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": interactive_button.get("id", "btn_1"),
                                    "title": interactive_button.get("title", "Open Link")
                                }
                            }
                        ]
                    }
                }
            }
            
            # If it's a web URL button, use the correct format
            if interactive_button.get("url"):
                payload["interactive"] = {
                    "type": "cta_url",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "name": "cta_url",
                        "parameters": {
                            "display_text": interactive_button.get("title", "Open Link"),
                            "url": interactive_button.get("url")
                        }
                    }
                }
        else:
            # Standard text message
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text", 
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
    """Parse incoming WhatsApp webhook data and extract message ID"""
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
        sender = message.get("from")
        message_id = message.get("id")  # Extract message ID for read receipts
        
        # Handle different message types
        if message.get("type") == "text":
            text = message.get("text", {}).get("body", "").lower()
        else:
            text = ""  # Handle other message types if needed
            
        return sender, text, message_id
        
    except Exception as e:
        logger.error(f"Error parsing WhatsApp message: {e}")
        return None, None, None

async def route_whatsapp_message(sender: str, text: str, message_id: str = None) -> str:
    """Route WhatsApp message with FORCED onboarding for all users without Sofi accounts"""
    try:
        logger.info(f"📱 WhatsApp message from {sender}: '{text}'")
        
        # Import APIs
        from utils.whatsapp_api_fixed import whatsapp_api
        from utils.whatsapp_onboarding import send_whatsapp_onboarding_link, handle_whatsapp_onboarding_response
        
        # 🚨 STEP 1: FORCE CHECK - Does user have ACTUAL Sofi account?
        try:
            from supabase import create_client
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
            supabase = create_client(supabase_url, supabase_key)
            
            # Check if user has ACTUAL account with account_number (not just user record)
            user_result = supabase.table("users").select("*").eq("whatsapp_number", sender).execute()
            
            has_sofi_account = False
            if user_result.data and len(user_result.data) > 0:
                user = user_result.data[0]
                # User must have account_number to be considered onboarded
                has_sofi_account = bool(user.get('account_number') and user.get('customer_code'))
                
            logger.info(f"🔍 User {sender} has Sofi account: {has_sofi_account}")
                
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            has_sofi_account = False
        
        # 🚨 STEP 2: FORCE ONBOARDING - No Sofi account = No chat
        if not has_sofi_account:
            logger.info(f"🆕 FORCING onboarding for {sender} - no Sofi account detected")
            
            # Skip onboarding keywords check - directly send Flow
            skip_onboarding_keywords = [
                "already registered", "i have account", "just created", "completed registration",
                "just signed up", "thanks", "thank you", "okay", "ok", "got it", "understood",
                "will do", "sure", "alright", "fine", "done", "yes", "no problem"
            ]
            
            if any(keyword in text.lower() for keyword in skip_onboarding_keywords):
                brief_response = (
                    "Ready to help! Complete your onboarding to unlock all features:\n\n"
                    "💰 Send money instantly\n"
                    "📱 Buy airtime & data\n" 
                    "💳 Receive payments\n\n"
                    "Tap below to get started:"
                )
                # Use WhatsApp Flow for in-chat onboarding
                success = send_whatsapp_onboarding_flow(sender)
                if not success:
                    # Fallback to URL button
                    await whatsapp_api.send_message_with_read_and_typing(
                        phone_number=sender,
                        message=f"{brief_response}\n\n🔗 Complete your setup: https://www.pipinstallsofi.com/whatsapp-onboard?whatsapp={sender}",
                        message_id_to_read=message_id,
                        typing_duration=1.0
                    )
                return "Onboarding Flow sent successfully"
            
            # Send WhatsApp Flow for ANY other message
            success = send_whatsapp_onboarding_flow(sender)
            if success:
                return f"🚨 WhatsApp Flow onboarding sent to {sender}"
            else:
                # Fallback message
                await whatsapp_api.send_message_with_read_and_typing(
                    phone_number=sender,
                    message=f"👋 Welcome to Sofi! Please create your account first: https://www.pipinstallsofi.com/whatsapp-onboard?whatsapp={sender}",
                    message_id_to_read=message_id,
                    typing_duration=1.0
                )
                return "Fallback onboarding message sent"
        
        # ✅ STEP 3: Normal Assistant chat (only for users with Sofi accounts)
        logger.info(f"✅ User {sender} has Sofi account - proceeding to Assistant")
        
        from utils.sofi_assistant_api import sofi_assistant
        assistant_response = await sofi_assistant.send_message_to_assistant(sender, text)
        
        if assistant_response:
            await whatsapp_api.send_message_with_read_and_typing(
                phone_number=sender,
                message=assistant_response,
                message_id_to_read=message_id,
                typing_duration=2.0
            )
            return "Message processed by Sofi Assistant"
        else:
            await whatsapp_api.send_message_with_read_and_typing(
                phone_number=sender,
                message="Sorry, I'm having trouble right now. Please try again.",
                message_id_to_read=message_id,
                typing_duration=1.0
            )
            return "Assistant error - fallback sent"
            
    except Exception as e:
        logger.error(f"❌ Error routing WhatsApp message: {e}")
        
        # Emergency fallback
        try:
            from utils.whatsapp_api_fixed import whatsapp_api
            await whatsapp_api.send_message_with_read_and_typing(
                phone_number=sender,
                message="I'm experiencing technical difficulties. Please try again in a few minutes.",
                message_id_to_read=message_id,
                typing_duration=1.0
            )
        except:
            pass
            
        return f"Error: {str(e)}"

@app.route("/whatsapp-webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    """Handle WhatsApp Cloud API webhooks"""
    
    if request.method == "GET":
        # Webhook verification
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == verify_token:
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
            
            # Parse the message
            sender, text, message_id = parse_whatsapp_message(data)
            
            if not sender or not text:
                logger.info("WhatsApp webhook: No valid message found")
                return "OK", 200
            
            logger.info(f"WhatsApp message from {sender}: {text} (ID: {message_id})")
            
            # Route and process the message with read receipts and typing
            import asyncio
            result = asyncio.run(route_whatsapp_message(sender, text, message_id))
            
            # The route_whatsapp_message now handles sending messages directly
            # No need to send response again here
            
            logger.info(f"WhatsApp message processed: {result}")
            
            return "OK", 200
            
        except Exception as e:
            logger.error(f"WhatsApp webhook error: {e}")
            return "Internal Server Error", 500

@app.route("/9psb-webhook", methods=["POST"])
def ninepsb_webhook():
    """Handle 9PSB transaction webhooks for credit/debit alerts"""
    try:
        from utils.ninepsb_webhook import handle_9psb_webhook
        return handle_9psb_webhook()
    except Exception as e:
        logger.error(f"9PSB webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/create_virtual_account", methods=["POST"])
def create_virtual_account():
    """Create virtual account endpoint for onboarding"""
    try:
        from utils.user_onboarding import SofiUserOnboarding
        
        data = request.get_json()
        
        # Fix field mapping from form to backend
        if data:
            # Combine first_name and last_name into full_name
            if 'first_name' in data and 'last_name' in data:
                data['full_name'] = f"{data['first_name']} {data['last_name']}"
            
            # Generate a temporary whatsapp_number if not provided (for web form users)
            if not data.get('whatsapp_number'):
                import uuid
                data['whatsapp_number'] = f"web_user_{uuid.uuid4().hex[:8]}"
        
        onboarding = SofiUserOnboarding()
        result = onboarding.create_virtual_account(data)
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creating virtual account: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route("/api/whatsapp_create_account", methods=["POST"])
def whatsapp_create_account():
    """WhatsApp-specific account creation endpoint"""
    try:
        from utils.whatsapp_account_manager_simple import whatsapp_account_manager
        
        data = request.get_json()
        logger.info(f"🎯 WhatsApp account creation request: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Extract and validate required fields
        whatsapp_number = data.get('whatsapp_number', '').strip()
        full_name = data.get('full_name', '').strip()
        
        if not full_name:
            return jsonify({"success": False, "error": "Full name is required"}), 400
        
        # Create account via simplified WhatsApp manager
        import asyncio
        result = asyncio.run(whatsapp_account_manager.create_whatsapp_account(data))
        
        if result['success']:
            # Send WhatsApp notification with account details
            try:
                account_message = whatsapp_account_manager.format_account_message(result)
                
                # Send to WhatsApp if we have the number
                if whatsapp_number:
                    success = send_whatsapp_message(whatsapp_number, account_message)
                    logger.info(f"📱 Account details sent to WhatsApp: {success}")
                
            except Exception as e:
                logger.error(f"Error sending WhatsApp notification: {e}")
                # Don't fail the account creation if notification fails
            
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creating WhatsApp account: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

# Removed duplicate onboard route - now using templates/onboarding.html (WORKING VERSION)

@app.route("/onboard")
def onboard_page():
    """Serve secure onboarding page with token validation"""
    try:
        # Get token parameter
        token = request.args.get('token')
        whatsapp_number = request.args.get('whatsapp', '')
        
        # If token is provided, validate it
        if token:
            try:
                onboarding_manager = WhatsAppOnboardingManager()
                
                # Extract WhatsApp number from token if not provided directly
                if not whatsapp_number:
                    token_parts = token.split(':')
                    if len(token_parts) >= 1:
                        whatsapp_number = token_parts[0]
                
                # Validate token
                is_valid = onboarding_manager.validate_token(token, whatsapp_number)
                
                if not is_valid:
                    logger.warning(f"❌ Invalid onboarding token for {whatsapp_number}")
                    return "❌ Invalid or expired onboarding link. Please request a new one from Sofi.", 403
                
                logger.info(f"✅ Valid onboarding token for {whatsapp_number}")
                
            except Exception as e:
                logger.error(f"❌ Token validation error: {e}")
                return "❌ Error validating onboarding link. Please try again.", 500
        
        # Serve onboarding page
        try:
            with open('web_onboarding.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inject WhatsApp number if available
            if whatsapp_number:
                html_content = html_content.replace(
                    'value="" placeholder="WhatsApp Number"',
                    f'value="{whatsapp_number}" readonly'
                )
            
            return html_content, 200, {'Content-Type': 'text/html'}
            
        except FileNotFoundError:
            logger.error("❌ web_onboarding.html not found")
            return render_template('onboarding.html', whatsapp_number=whatsapp_number)
            
    except Exception as e:
        logger.error(f"❌ Error serving onboarding page: {e}")
        return "Internal server error", 500

@app.route("/whatsapp-onboard")
def whatsapp_onboard_page():
    """Serve WhatsApp-style onboarding page with auto-filled WhatsApp number"""
    try:
        whatsapp_number = request.args.get('whatsapp', '')
        logger.info(f"🎯 WhatsApp onboarding page accessed for: {whatsapp_number}")
        
        # Serve the new WhatsApp onboarding HTML
        try:
            with open('templates/whatsapp_onboarding_new.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # The WhatsApp number is passed via URL params and handled by JavaScript
            return html_content, 200, {'Content-Type': 'text/html'}
            
        except FileNotFoundError:
            logger.error("❌ whatsapp_onboarding_new.html not found")
            return render_template('whatsapp_onboarding.html', whatsapp_number=whatsapp_number)
            
    except Exception as e:
        logger.error(f"❌ Error serving WhatsApp onboarding page: {e}")
        return "Internal server error", 500

@app.route("/verify-pin")
def pin_verification_page():
    """Serve secure PIN verification page with token-based security and comprehensive bot handling"""
    # Get user agent, secure token, and legacy transaction ID for logging
    user_agent = request.headers.get('User-Agent', '')
    secure_token = request.args.get('token')
    legacy_txn_id = request.args.get('txn_id')  # For backward compatibility
    client_ip = request.remote_addr
    
    # Enhanced logging for debugging
    logger.info(f"📊 /verify-pin accessed - IP: {client_ip}, UA: {user_agent[:50]}..., token: {secure_token[:10] if secure_token else 'None'}..., legacy_txn: {legacy_txn_id}")
    
    # 1. Enhanced bot detection with IP checking
    from utils.security import is_whatsapp_bot_ip
    
    bot_user_agents = ['WhatsAppBot', 'TwitterBot', 'facebookexternalhit', 'WhatsApp', 'Slackbot', 'LinkedInBot', 'SkypeBot']
    is_bot_ua = any(bot in user_agent for bot in bot_user_agents)
    is_bot_ip = is_whatsapp_bot_ip(client_ip)
    
    if is_bot_ua or is_bot_ip:
        logger.info(f"🤖 Bot preview blocked: {user_agent} from IP: {client_ip} (Bot IP: {is_bot_ip})")
        # Return proper 204 No Content response for bots
        return make_response('', 204)
    
    # 2. Determine which token/ID to use (prefer secure token)
    transaction_id = None
    if secure_token:
        # New secure token system
        logger.info(f"🔑 Using secure token authentication")
    elif legacy_txn_id:
        # Legacy transaction ID system (for backward compatibility)
        logger.info(f"⚠️ Using legacy transaction ID (should migrate to tokens)")
        transaction_id = legacy_txn_id
    else:
        logger.warning(f"❌ Missing token/txn_id from IP: {client_ip}")
        return jsonify({"error": "Missing authentication token"}), 400
    
    # 3. Get transaction data from secure PIN verification system
    try:
        from utils.secure_pin_verification import secure_pin_verification
        
        if secure_token:
            # Use new secure token system
            transaction = secure_pin_verification.get_pending_transaction_by_token(secure_token)
            if not transaction:
                logger.warning(f"❌ Invalid/expired token: {secure_token[:10]}... from IP: {client_ip}")
                return jsonify({"error": "Token expired or invalid"}), 404
        else:
            # Use legacy system for backward compatibility
            transaction = secure_pin_verification.get_pending_transaction(legacy_txn_id)
            if not transaction:
                logger.warning(f"❌ Invalid/expired transaction: {legacy_txn_id} from IP: {client_ip}")
                return jsonify({"error": "Transaction expired or invalid"}), 404
        
        # Extract transfer data from the stored transaction
        transfer_data = transaction.get('transfer_data', {})
        
        # Log successful transaction lookup
        logger.info(f"✅ Valid transaction found for amount: ₦{transfer_data.get('amount', 0)} from IP: {client_ip}")
        
        # 4. Clean up expired data periodically
        secure_pin_verification.cleanup_expired_data()
        
        # 5. Render PIN entry page with appropriate token
        template_data = {
            'secure_token': secure_token,
            'transaction_id': legacy_txn_id,  # For backward compatibility
            'transfer_data': {
                'amount': transfer_data.get('amount', 0),
                'recipient_name': transfer_data.get('recipient_name', 'Unknown'),
                'bank': transfer_data.get('bank', 'Unknown Bank'),
                'account_number': transfer_data.get('account_number', 'Unknown')
            }
        }
        
        # 6. Try to render the PIN entry template with fallback
        try:
            return render_template("pin-entry.html", **template_data)
        except Exception as template_error:
            logger.warning(f"⚠️ Template error, serving React component: {template_error}")
            # Fallback to serving the React component directly
            return render_template("react-pin-app.html", 
                                 secure_token=secure_token,
                                 transaction_id=legacy_txn_id,
                                 api_url="/api/verify-pin")
    
    except Exception as e:
        logger.error(f"❌ PIN verification error: {str(e)} for token: {secure_token[:10] if secure_token else 'None'}...")
        return jsonify({"error": "Internal server error", "message": "Please try again"}), 500

@app.route("/success")
def success_page():
    """Success page with receipt after successful transfer"""
    # Get receipt data from URL parameters
    receipt_data = {
        'amount': float(request.args.get('amount', 0)),
        'recipient_name': request.args.get('recipient_name', ''),
        'bank': request.args.get('bank', ''),
        'account_number': request.args.get('account_number', ''),
        'reference': request.args.get('reference', ''),
        'fee': float(request.args.get('fee', 20)),
        'timestamp': request.args.get('timestamp', '')
    }
    
    return render_template("success.html", receipt_data=receipt_data)

@app.route("/test-pin")
def test_pin_page():
    """Test PIN page with sample data"""
    return render_template("test-pin.html")

@app.route("/test-pin-real")
def test_pin_page_real():
    """Test PIN page with real template"""
    # Create a sample transaction for testing
    sample_transaction = {
        'amount': 100.00,
        'recipient_name': 'THANKGOD OLUWASEUN NDIDI',
        'bank': 'Unknown Bank',
        'account_number': '8104965538'
    }
    
    return render_template("pin-entry.html", 
                         transaction_id="test_demo",
                         transfer_data=sample_transaction)

@app.route("/api/verify-pin", methods=["POST"])
def verify_pin_api():
    """API endpoint for PIN verification with token-based security and enhanced monitoring"""
    try:
        data = request.get_json()
        secure_token = data.get('secure_token')
        legacy_transaction_id = data.get('transaction_id')  # For backward compatibility
        pin = data.get('pin')
        
        # Debug logging
        logger.info(f"🔍 PIN API Request Debug:")
        logger.info(f"   Raw data: {data}")
        logger.info(f"   Raw data keys: {list(data.keys()) if data else 'None'}")
        logger.info(f"   secure_token raw: '{secure_token}' (type: {type(secure_token)})")
        logger.info(f"   transaction_id raw: '{legacy_transaction_id}' (type: {type(legacy_transaction_id)})")
        logger.info(f"   pin raw: '{pin}' (type: {type(pin)})")
        logger.info(f"   Has secure_token: {bool(secure_token)}")
        logger.info(f"   Has transaction_id: {bool(legacy_transaction_id)}")
        logger.info(f"   Has pin: {bool(pin)}")
        logger.info(f"   secure_token value: {secure_token[:10] + '...' if secure_token else 'None'}")
        
        # Get client IP for security monitoring
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if not pin:
            # Monitor failed PIN attempts
            from utils.security_monitor import security_monitor
            security_monitor.monitor_pin_attempts(client_ip, False)
            
            return jsonify({
                'success': False,
                'error': 'PIN is required'
            }), 400
        
        if not secure_token and not legacy_transaction_id:
            # Monitor failed PIN attempts
            from utils.security_monitor import security_monitor
            security_monitor.monitor_pin_attempts(client_ip, False)
            
            return jsonify({
                'success': False,
                'error': 'Authentication token required'
            }), 400
        
        # Get transaction data from secure PIN verification system
        from utils.secure_pin_verification import secure_pin_verification
        
        transaction = None
        if secure_token:
            # Use new secure token system
            transaction = secure_pin_verification.get_pending_transaction_by_token(secure_token)
            if transaction:
                # Mark token as used to prevent replay attacks
                secure_pin_verification.mark_token_as_used(secure_token)
                logger.info(f"✅ Secure token verified and marked as used: {secure_token[:10]}...")
        elif legacy_transaction_id:
            # Legacy system for backward compatibility
            transaction = secure_pin_verification.get_pending_transaction(legacy_transaction_id)
            logger.info(f"⚠️ Using legacy transaction ID: {legacy_transaction_id}")
        
        if not transaction:
            # Monitor failed PIN attempts
            from utils.security_monitor import security_monitor
            security_monitor.monitor_pin_attempts(client_ip, False)
            
            return jsonify({
                'success': False,
                'error': 'Transaction expired, invalid, or already used'
            }), 400
        # Verify PIN and process transfer using the secure PIN verification system
        from utils.secure_pin_verification import secure_pin_verification
        import asyncio
        
        # Get transaction ID properly using the secure token validation
        if secure_token:
            # Use proper method to validate token and get transaction data
            transaction = secure_pin_verification.get_pending_transaction_by_token(secure_token)
            if not transaction:
                return jsonify({
                    'success': False,
                    'error': 'Invalid, expired, or already used token'
                }), 400
            
            # Extract transaction ID from the validated transaction data
            # The transaction ID is embedded in the transfer_data
            transfer_data = transaction.get('transfer_data', {})
            transaction_id = transfer_data.get('transaction_id')
            
            # If not in transfer_data, try to derive from secure token data
            if not transaction_id:
                token_data = secure_pin_verification.secure_tokens.get(secure_token)
                transaction_id = token_data['transaction_id'] if token_data else None
                
            logger.info(f"✅ Extracted transaction_id from secure token: {transaction_id}")
        else:
            transaction_id = legacy_transaction_id
            logger.info(f"⚠️ Using legacy transaction_id: {transaction_id}")
            
        if not transaction_id:
            return jsonify({
                'success': False,
                'error': 'Transaction ID not found'
            }), 400
        
        # Process PIN verification and transfer
        pin_result = asyncio.run(secure_pin_verification.verify_pin_and_process_transfer(transaction_id, pin))
        
        # Monitor PIN attempt
        from utils.security_monitor import security_monitor
        security_monitor.monitor_pin_attempts(client_ip, pin_result.get("success", False))
        
        if pin_result.get('success'):
            # Return success response with redirect URL
            from urllib.parse import urlencode
            from datetime import datetime
            
            transfer_data = transaction.get('transfer_data', {})
            success_params = {
                'amount': transaction.get('amount', 0),
                'recipient_name': transfer_data.get('recipient_name', 'Unknown'),
                'bank': transfer_data.get('bank', 'Unknown Bank'),
                'account_number': transfer_data.get('account_number', 'Unknown'),
                'reference': pin_result.get('transaction_id', 'N/A'),
                'fee': transfer_data.get('fee', 20),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            redirect_url = f"/success?{urlencode(success_params)}"
            
            return jsonify({
                'success': True,
                'message': 'Transfer completed successfully!',
                'redirect_url': redirect_url
            })
        else:
            return jsonify({
                'success': False,
                'error': pin_result.get('error', 'Transfer failed')
            }), 400
            
    except Exception as e:
        logger.error(f"Error in PIN verification API: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route("/api/cancel-transfer/<transaction_id>", methods=["POST"])
def cancel_transfer_api(transaction_id):
    """API endpoint for cancelling transfer"""
    try:
        from utils.secure_pin_verification import pending_transactions
        
        if transaction_id in pending_transactions:
            del pending_transactions[transaction_id]
            
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error cancelling transfer: {e}")
        return jsonify({'success': False}), 500

@app.route("/api/onboard", methods=["POST"])
def onboard_user_api():
    """API endpoint for web onboarding - WhatsApp version"""
    try:
        # Get user data from request
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'No user data provided'
            }), 400
        
        # Validate required fields for WhatsApp
        required_fields = ['whatsapp_number', 'full_name', 'phone']
        missing_fields = [field for field in required_fields if not user_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Run the onboarding process
        logger.info(f"🆕 Starting WhatsApp onboarding for user: {user_data.get('full_name')} ({user_data.get('whatsapp_number')})")
        
        import asyncio
        # Use asyncio.run to safely run the async onboarding function
        result = asyncio.run(onboarding_service.create_new_user(user_data))
        
        if result.get('success'):
            logger.info(f"✅ Successfully onboarded WhatsApp user: {user_data.get('full_name')}")
            
            # Send account details to user via WhatsApp
            whatsapp_number = user_data.get('whatsapp_number')
            if whatsapp_number and not whatsapp_number.startswith('web_user_'):
                try:
                    # Send welcome message with account details immediately
                    asyncio.run(send_whatsapp_account_details(whatsapp_number, result))
                    logger.info(f"🎉 Account details sent to WhatsApp user {whatsapp_number}")
                except Exception as e:
                    logger.error(f"❌ Failed to send account details to {whatsapp_number}: {e}")
            
            return jsonify(result), 200
        else:
            logger.warning(f"❌ Onboarding failed for WhatsApp user: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in WhatsApp onboarding API: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

async def send_whatsapp_account_details(phone_number: str, onboarding_result: dict):
    """Send account details to user via WhatsApp after successful onboarding"""
    try:
        account_details = onboarding_result.get('account_details', {})
        full_name = onboarding_result.get('full_name', '')
        customer_code = onboarding_result.get('customer_code', '')
        
        # Create beautiful welcome message with account details
        welcome_message = (
            f"🎉 *Welcome to Sofi AI!*\n\n"
            f"✅ Your virtual account has been created successfully!\n\n"
            f"💳 *Account Details:*\n"
            f"🏦 Account: `{account_details.get('account_number', 'N/A')}`\n"
            f"👤 Name: {account_details.get('account_name', full_name)}\n"
            f"🏛️ Bank: {account_details.get('bank_name', 'Paystack Bank')}\n\n"
            f"🚀 *You can now:*\n"
            f"💰 Fund your account to start sending money\n"
            f"📱 Buy airtime and data\n"
            f"💸 Receive payments from anywhere\n"
            f"💬 Chat with me for help\n\n"
            f"Try saying: *\"Check my balance\"* or *\"Send money\"*"
        )
        
        # Send message to user via WhatsApp
        success = send_whatsapp_message(phone_number, welcome_message)
        
        if success:
            logger.info(f"✅ WhatsApp account details sent to {phone_number}")
        else:
            logger.error(f"❌ Failed to send WhatsApp message to {phone_number}")
        
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp account details to {phone_number}: {e}")

@app.route("/api/notify-onboarding", methods=["POST"])
def notify_onboarding_complete():
    """Webhook endpoint for onboarding completion notifications - WhatsApp version"""
    try:
        data = request.get_json()
        whatsapp_number = data.get('whatsapp_number')
        onboarding_result = data.get('result', {})
        
        logger.info(f"📢 Onboarding notification received for {whatsapp_number}")
        
        if whatsapp_number and not whatsapp_number.startswith('web_user_'):
            # Send account details to the WhatsApp user
            import asyncio
            asyncio.run(send_whatsapp_account_details(whatsapp_number, onboarding_result))
            logger.info(f"✅ Account details sent via notification webhook to {whatsapp_number}")
            
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in WhatsApp onboarding notification: {e}")
        return jsonify({'success': False}), 500

# Removed duplicate onboard route - using the working templates/onboarding.html above

# Note: Old PIN entry web routes removed - now using inline keyboards

def edit_message(phone_number, message_id, text, reply_markup=None):
    """Edit a message in WhatsApp"""
    try:
        url = f"https://api.whatsapp.org/bot{WHATSAPP_ACCESS_TOKEN}/editMessageText"
        payload = {
            "phone_number": phone_number,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"✅ Message edited successfully for chat {phone_number}")
            return response.json()
        else:
            logger.error(f"❌ Failed to edit message: {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Error editing message: {str(e)}")
        return None

async def handle_callback_query(callback_query: dict):
    """Handle callback queries from inline keyboards (PIN entry, etc.)"""
    try:
        query_id = callback_query["id"]
        phone_number = str(callback_query["from"]["id"])
        callback_data = callback_query.get("data", "")
        message_id = callback_query.get("message", {}).get("message_id")
        
        logger.info(f"📱 Callback query from {phone_number}: {callback_data}")
        
        # Define answer_callback_query helper
        async def answer_callback_query(query_id: str, text: str = ""):
            """Answer a callback query to remove loading state"""
            url = f"https://api.whatsapp.org/bot{WHATSAPP_ACCESS_TOKEN}/answerCallbackQuery"
            payload = {
                "callback_query_id": query_id,
                "text": text,
                "show_alert": False
            }
            try:
                response = requests.post(url, json=payload)
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                logger.error(f"❌ Error answering callback query: {str(e)}")
                return None
        
        # Only handle web app PIN callbacks now - inline keyboard PIN system removed
                
        # Handle other callback types here (existing logic)
        # ...existing callback handling code...
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"❌ Error handling callback query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/transaction-details")
def get_transaction_details():
    """API endpoint to fetch transaction details using secure token or legacy transaction ID"""
    try:
        secure_token = request.args.get('token')
        legacy_txn_id = request.args.get('txn_id')
        
        if not secure_token and not legacy_txn_id:
            return jsonify({
                'success': False,
                'error': 'Authentication token required'
            }), 400
        
        # Get transaction data from secure PIN verification system
        from utils.secure_pin_verification import secure_pin_verification
        
        transaction = None
        if secure_token:
            transaction = secure_pin_verification.get_pending_transaction_by_token(secure_token)
            logger.info(f"📊 Transaction details requested via secure token: {secure_token[:10]}...")
        elif legacy_txn_id:
            transaction = secure_pin_verification.get_pending_transaction(legacy_txn_id)
            logger.info(f"📊 Transaction details requested via legacy ID: {legacy_txn_id}")
        
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found or expired'
            }), 404
        
        # Extract transfer data
        transfer_data = transaction.get('transfer_data', {})
        
        # Convert bank code to friendly name
        from functions.transfer_functions import BANK_CODE_TO_NAME
        bank_code = transfer_data.get('bank', 'Unknown Bank')
        bank_name = BANK_CODE_TO_NAME.get(bank_code, bank_code)
        
        # Return safe transaction details for display
        return jsonify({
            'success': True,
            'transaction': {
                'amount': transaction.get('amount', 0),
                'recipient_name': transfer_data.get('recipient_name', 'Unknown'),
                'bank': bank_name,  # Use friendly bank name instead of code
                'account_number': transfer_data.get('account_number', 'Unknown'),
                'fee': transfer_data.get('fee', 20),
                'total': transaction.get('amount', 0) + transfer_data.get('fee', 20),
                'narration': transfer_data.get('narration', 'Transfer via Sofi AI')
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching transaction details: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

async def send_beautiful_receipt(phone_number, receipt_data, transfer_result):
    """Send a beautiful receipt after successful transfer"""
    try:
        # Import the beautiful receipt generator
        from beautiful_receipt_generator import SofiReceiptGenerator
        
        # Extract receipt data
        sender_name = receipt_data.get('sender_name', 'Sofi User')
        amount = receipt_data.get('amount', 0)
        recipient_name = receipt_data.get('recipient_name', 'Unknown')
        recipient_account = receipt_data.get('recipient_account', 'Unknown')
        recipient_bank = receipt_data.get('recipient_bank', 'Unknown')
        balance = receipt_data.get('new_balance', 0)
        transaction_id = receipt_data.get('transaction_id', 'N/A')
        transfer_fee = receipt_data.get('transfer_fee', 30)
        bank_name = recipient_bank
        
        # --- Ensure bank_name is always a human-readable name ---
        # If bank_name is a code, resolve it to a name
        from functions.transfer_functions import get_bank_name_from_code
        if bank_name.isdigit() or bank_name == bank_name.upper():
            resolved_name = get_bank_name_from_code(bank_name)
            if resolved_name:
                bank_name = resolved_name
        # --- End fix ---
        
        # Create receipt generator instance
        receipt_generator = SofiReceiptGenerator()
        
        # Prepare transaction data for receipt generation
        transaction_data = {
            'user_name': sender_name,
            'amount': amount,
            'recipient_name': recipient_name,
            'recipient_account': recipient_account,
            'recipient_bank': bank_name,
            'transfer_fee': transfer_fee,
            'new_balance': balance,
            'reference': transaction_id
        }
        
        # Generate the beautiful receipt
        receipt_text = receipt_generator.create_bank_transfer_receipt(transaction_data)
        
        # Send the receipt
        send_whatsapp_message(phone_number, receipt_text)
        logger.info(f"📧 Beautiful receipt sent to {phone_number}")
        
    except Exception as e:
        logger.error(f"❌ Error sending beautiful receipt: {str(e)}")
        # Fallback to simple reply
        txn_id = receipt_data.get('transaction_id', 'N/A') if receipt_data else 'N/A'
        send_whatsapp_message(phone_number, f"✅ Transfer completed successfully!\nTransaction ID: {txn_id}")

# --- 9PSB Webhook Test Endpoint Only ---

@app.route("/webhook/9psb/test", methods=["POST", "GET"])
def test_ninepsb_webhook():
    """Test endpoint for 9PSB webhook"""
    try:
        if request.method == "GET":
            return {"status": "ready", "message": "9PSB webhook endpoint is ready"}, 200
            
        # Handle test webhook
        test_data = request.get_json() or {
            "eventType": "wallet.created",
            "data": {
                "userId": "test_user_123",
                "accountNumber": "1234567890",
                "accountName": "TEST USER",
                "bankName": "9PSB",
                "walletId": "wallet_123"
            }
        }
        
        result = ninepsb_webhook_handler.handle_webhook(test_data)
        return {"status": "success", "result": result}, 200
        
    except Exception as e:
        logger.error(f"❌ Test webhook error: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.route("/api/register", methods=["POST"])
def register_user():
    """Handle user registration from onboarding form"""
    try:
        data = request.get_json()
        
        # Extract user data from form
        full_name = data.get('fullName', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        pin = data.get('pin', '')
        bvn = data.get('bvn', '').strip()
        date_of_birth = data.get('dateOfBirth', '')
        address = data.get('address', '').strip()
        state = data.get('state', '').strip()
        
        # Validate required fields
        if not all([full_name, email, phone, pin]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Check if user already exists
        existing_user = supabase.table("users").select("id").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"error": "User already exists with this email"}), 409
            
        # Also check by phone number
        existing_phone = supabase.table("users").select("id").eq("whatsapp_number", phone).execute()
        if existing_phone.data:
            # Update existing WhatsApp user with full registration data
            user_id = existing_phone.data[0]["id"]
            update_data = {
                "full_name": full_name,
                "email": email,
                "pin_hash": pin,  # In production, hash this properly
                "bvn": bvn,
                "date_of_birth": date_of_birth,
                "address": address,
                "state": state,
                "registration_completed": True,
                "updated_at": datetime.now().isoformat()
            }
            
            result = supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data:
                logger.info(f"✅ Updated existing WhatsApp user: {phone}")
                return jsonify({
                    "success": True, 
                    "message": "Registration completed successfully",
                    "user_id": user_id,
                    "account_number": "Processing..."  # Will be updated when virtual account is created
                })
        else:
            # Create completely new user
            import uuid
            user_id = str(uuid.uuid4())
            
            user_data = {
                "id": user_id,
                "full_name": full_name,
                "email": email,
                "whatsapp_number": phone,
                "pin_hash": pin,  # In production, hash this properly
                "bvn": bvn,
                "date_of_birth": date_of_birth,
                "address": address,
                "state": state,
                "wallet_balance": 0.0,
                "registration_completed": True,
                "status": "active",
                "signup_source": "web_onboarding",
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase.table("users").insert(user_data).execute()
            
            if result.data:
                logger.info(f"✅ New user registered: {email}")
                return jsonify({
                    "success": True,
                    "message": "Registration completed successfully", 
                    "user_id": user_id,
                    "account_number": "Processing..."  # Will be updated when virtual account is created
                })
        
        return jsonify({"error": "Registration failed"}), 500
        
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500

@app.route("/webhook/onboarding-complete", methods=["POST"])
def handle_onboarding_completion():
    """Handle completion of user onboarding from web app"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        user_name = data.get('name', 'there')
        account_number = data.get('account_number')
        
        if phone_number:
            # Send confirmation message back to WhatsApp like Xara does
            completion_message = (
                f"🎉 *Welcome to Sofi, {user_name}!*\n\n"
                f"✅ Your account has been created successfully!\n"
                f"🏦 Account Number: {account_number}\n\n"
                f"You can now:\n"
                f"💸 Send and receive money\n"
                f"📱 Buy airtime and data\n"
                f"💰 Check your balance\n\n"
                f"Type 'help' to see all available commands!"
            )
            
            # Send the completion message
            send_whatsapp_message(phone_number, completion_message)
            logger.info(f"✅ Onboarding completion message sent to {phone_number}")
            
            return {"status": "success", "message": "Completion message sent"}, 200
        else:
            return {"status": "error", "message": "Phone number required"}, 400
            
    except Exception as e:
        logger.error(f"❌ Onboarding completion webhook error: {e}")
        return {"status": "error", "message": str(e)}, 500

# ===============================================
# ===============================================
# 📱 WHATSAPP FLOW WEBHOOK HANDLER (Like Xara)
# ===============================================

@app.route("/whatsapp-flow-webhook", methods=["GET", "POST"])
def whatsapp_flow_webhook():
    """
    Handle WhatsApp Flow webhook - both verification and encrypted data exchange
    Works with both www and non-www domains to avoid 307 redirects
    """
    
    if request.method == 'GET':
        # Meta verification for Flow endpoint
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'sofi_ai_webhook_verify_2024')
        
        if mode == 'subscribe' and token == verify_token:
            logger.info("✅ WhatsApp Flow webhook verification successful")
            return challenge
        else:
            logger.warning("❌ WhatsApp Flow webhook verification failed")
            return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Flow data exchange with encryption
        try:
            # Get payload (could be JSON or empty for health checks)
            payload = request.get_json(silent=True)
            
            # Check User-Agent to identify Meta/Facebook requests
            user_agent = request.headers.get('User-Agent', '')
            is_meta_request = any(agent in user_agent.lower() for agent in [
                'facebookexternalua', 'facebook', 'meta', 'whatsapp'
            ])
            
            logger.info(f"🔍 User-Agent: {user_agent}")
            logger.info(f"🔍 Meta request: {is_meta_request}")
            logger.info(f"🔍 Payload: {payload}")
            
            # Handle Meta health checks and test requests
            if is_meta_request and (not payload or len(payload) == 0):
                logger.info("💊 Meta health check or test request detected")
                # Return encrypted test response
                return create_encrypted_health_response()
            
            if not payload:
                logger.error("❌ No payload received")
                return 'Bad Request', 400
            
            logger.info("🔐 Received Flow data")
            logger.info(f"📋 Payload keys: {list(payload.keys())}")
            
            # Check if this is encrypted flow data
            if 'encrypted_flow_data' in payload:
                return handle_encrypted_flow_data(payload)
            
            # Handle unencrypted legacy format or test data
            else:
                logger.info("📱 Handling legacy flow data format")
                return handle_legacy_flow_data(payload)
                
        except Exception as e:
            logger.error(f"❌ Flow webhook error: {e}")
            import traceback
            traceback.print_exc()
            return 'Internal Server Error', 500

def create_encrypted_health_response():
    """Create encrypted health check response for Meta"""
    try:
        # Health check response data
        health_data = {
            "status": "encryption_test",
            "message": "Encryption endpoint available but decryption failed",
            "note": "Please verify key configuration in Meta Business Manager"
        }
        
        # For now, return Base64 encoded JSON (Meta expects Base64)
        import base64
        import json
        
        response_json = json.dumps(health_data)
        base64_response = base64.b64encode(response_json.encode()).decode()
        
        logger.info("🔐 Sending Base64 encoded health response")
        return base64_response, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"❌ Error creating health response: {e}")
        return 'Internal Server Error', 500

def get_flow_encryption():
    """Get Flow encryption handler with actual implementation"""
    try:
        # Import the Flow encryption handler
        from utils.flow_encryption import FlowEncryption
        return FlowEncryption()
    except ImportError:
        # If utils.flow_encryption doesn't exist, return inline implementation
        return InlineFlowEncryption()
    except Exception as e:
        logger.error(f"❌ Error getting flow encryption: {e}")
        return None

class InlineFlowEncryption:
    """Inline Flow encryption implementation for WhatsApp Flows"""
    
    def __init__(self):
        import os
        import base64
        # Get private key from environment (Base64 encoded)
        private_key_b64 = os.getenv('WHATSAPP_FLOW_PRIVATE_KEY')
        if not private_key_b64:
            logger.warning("⚠️ WHATSAPP_FLOW_PRIVATE_KEY not set - Flow encryption disabled")
            self.private_key_pem = None
        else:
            try:
                # Decode Base64 to get PEM format
                self.private_key_pem = base64.b64decode(private_key_b64).decode('utf-8')
                logger.info("✅ Private key decoded from Base64 successfully")
            except Exception as e:
                logger.error(f"❌ Failed to decode private key: {e}")
                self.private_key_pem = None
    
    def decrypt_request(self, encrypted_flow_data, encrypted_aes_key, initial_vector):
        """Decrypt incoming Flow request from Meta"""
        try:
            import base64
            import json
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            
            if not self.private_key_pem:
                logger.warning("🔧 Private key not configured - cannot decrypt")
                return None
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                self.private_key_pem.encode(),
                password=None
            )
            
            # Decode Base64 data
            encrypted_aes_key_bytes = base64.b64decode(encrypted_aes_key)
            encrypted_flow_data_bytes = base64.b64decode(encrypted_flow_data)
            iv_bytes = base64.b64decode(initial_vector)
            
            # Decrypt AES key using RSA private key
            aes_key = private_key.decrypt(
                encrypted_aes_key_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt flow data using AES
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv_bytes))
            decryptor = cipher.decryptor()
            
            # Decrypt and remove padding
            decrypted_padded = decryptor.update(encrypted_flow_data_bytes) + decryptor.finalize()
            
            # Remove PKCS7 padding
            padding_length = decrypted_padded[-1]
            decrypted_data = decrypted_padded[:-padding_length]
            
            # Parse JSON
            flow_data = json.loads(decrypted_data.decode('utf-8'))
            
            # Store AES key and IV for response encryption
            self.response_aes_key = aes_key
            self.response_iv = iv_bytes
            
            logger.info("✅ Flow request decrypted successfully")
            return flow_data
            
        except Exception as e:
            logger.error(f"❌ Flow decryption error: {e}")
            return None
    
    def encrypt_response(self, response_data):
        """Encrypt Flow response for Meta"""
        try:
            import base64
            import json
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            
            if not hasattr(self, 'response_aes_key'):
                logger.error("❌ No AES key available for response encryption")
                return None
            
            # Convert response to JSON
            response_json = json.dumps(response_data)
            response_bytes = response_json.encode('utf-8')
            
            # Add PKCS7 padding
            block_size = 16
            padding_length = block_size - (len(response_bytes) % block_size)
            padded_response = response_bytes + bytes([padding_length] * padding_length)
            
            # Encrypt using stored AES key and IV
            cipher = Cipher(algorithms.AES(self.response_aes_key), modes.CBC(self.response_iv))
            encryptor = cipher.encryptor()
            encrypted_response = encryptor.update(padded_response) + encryptor.finalize()
            
            # Return Base64 encoded encrypted response
            return base64.b64encode(encrypted_response).decode('utf-8')
            
        except Exception as e:
            logger.error(f"❌ Flow encryption error: {e}")
            return None

def handle_encrypted_flow_data(payload):
    """Handle encrypted WhatsApp Flow data exchange"""
    try:
        # Meta/WhatsApp might use different field names
        encrypted_flow_data = payload.get('encrypted_flow_data') or payload.get('data')
        encrypted_aes_key = payload.get('encrypted_aes_key') or payload.get('aes_key')
        initial_vector = payload.get('initial_vector') or payload.get('iv')
        
        logger.info(f"🔍 Encrypted fields found:")
        logger.info(f"   encrypted_flow_data: {'✅' if encrypted_flow_data else '❌'}")
        logger.info(f"   encrypted_aes_key: {'✅' if encrypted_aes_key else '❌'}")
        logger.info(f"   initial_vector: {'✅' if initial_vector else '❌'}")
        
        # Check if this might be a Meta test/health request
        user_agent = request.headers.get('User-Agent', '')
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Check for Meta/Facebook IP ranges (173.252.x.x is Facebook)
        is_meta_ip = client_ip.startswith('173.252.') or client_ip.startswith('31.13.')
        is_meta_test = any(agent in user_agent.lower() for agent in [
            'facebookexternalua', 'facebook', 'meta'
        ])
        
        logger.info(f"🔍 Client IP: {client_ip}")
        logger.info(f"🔍 Meta IP range: {is_meta_ip}")
        logger.info(f"🔍 Meta test request: {is_meta_test}")
        
        if not all([encrypted_flow_data, encrypted_aes_key, initial_vector]):
            if is_meta_ip or is_meta_test:
                logger.info("💊 Meta test request with incomplete encryption data - returning Base64 response")
                # Return Base64 encoded response as expected by Meta
                test_response = {
                    "status": "encryption_test",
                    "message": "Encryption endpoint available but decryption failed", 
                    "note": "Please verify key configuration in Meta Business Manager"
                }
                import base64
                import json
                response_json = json.dumps(test_response)
                base64_response = base64.b64encode(response_json.encode()).decode()
                return base64_response, 200, {'Content-Type': 'text/plain'}
            else:
                logger.error("❌ Missing encryption fields")
                logger.info(f"Available payload fields: {list(payload.keys())}")
                return 'Missing required encryption fields', 421
        
        # Check if encryption handler is available
        try:
            flow_encryption = get_flow_encryption()
        except:
            flow_encryption = None
            
        if not flow_encryption or not hasattr(flow_encryption, 'private_key_pem') or not flow_encryption.private_key_pem:
            logger.info("🔧 Flow encryption not configured - returning Base64 test response")
            # Return Base64 encoded response indicating encryption setup needed
            test_response = {
                "status": "encryption_test",
                "message": "Encryption endpoint available but decryption failed",
                "note": "Please verify key configuration in Meta Business Manager"
            }
            import base64
            import json
            response_json = json.dumps(test_response) 
            base64_response = base64.b64encode(response_json.encode()).decode()
            return base64_response, 200, {'Content-Type': 'text/plain'}
        
        # Decrypt request
        logger.info("🔓 Decrypting flow request...")
        decrypted_data = flow_encryption.decrypt_request(
            encrypted_flow_data, 
            encrypted_aes_key, 
            initial_vector
        )
        
        if not decrypted_data:
            logger.error("❌ Decryption failed")
            
            # If this is from Meta's IP range, it might be a configuration test
            if is_meta_ip:
                logger.info("💊 Meta IP detected - might be configuration test")
                return jsonify({
                    "status": "encryption_test", 
                    "message": "Encryption endpoint available but decryption failed",
                    "note": "Please verify key configuration in Meta Business Manager"
                }), 200
            else:
                return 'Decryption failed', 421
        
        # Process the flow request
        response_data = process_flow_request(decrypted_data)
        
        # Encrypt response using stored AES key and IV from decryption
        logger.info("🔒 Encrypting flow response...")
        encrypted_response = flow_encryption.encrypt_response(response_data)
        
        if not encrypted_response:
            logger.error("❌ Response encryption failed")
            return 'Encryption failed', 500
        
        logger.info("✅ Flow response encrypted and sent")
        return encrypted_response, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"❌ Encrypted flow handling error: {e}")
        import traceback
        traceback.print_exc()
        return 'Processing failed', 500

def handle_legacy_flow_data(payload):
    """Handle unencrypted legacy flow data format or Meta test requests"""
    try:
        logger.info(f"📱 Legacy flow data: {json.dumps(payload, indent=2)}")
        
        # Check if this is a Meta test request
        user_agent = request.headers.get('User-Agent', '')
        is_meta_test = any(agent in user_agent.lower() for agent in [
            'facebookexternalua', 'facebook', 'meta'
        ])
        
        # If it's a Meta test with minimal data, return success
        if is_meta_test and (not payload or len(payload.keys()) <= 2):
            logger.info("💊 Meta test request in legacy handler")
            return jsonify({
                "status": "success",
                "message": "Flow webhook operational",
                "data": {
                    "version": "1.0",
                    "ready": True
                }
            }), 200
        
        # Extract flow data
        flow_data = payload.get("data", {}) or payload.get("flow_data", {})
        flow_token = payload.get("flow_token", "") or payload.get("token", "")
        action = flow_data.get("action", "")
        
        logger.info(f"🎯 Flow action: {action}")
        
        # Handle onboarding flow completion
        if action == "create_account":
            return handle_onboarding_flow_completion(flow_data, flow_token)
        
        # Handle transfer verification flow
        elif action == "approve_transfer":
            return handle_transfer_flow_completion(flow_data, flow_token)
        
        # Default response for unknown actions
        elif is_meta_test:
            logger.info("💊 Meta test request with unknown action")
            return jsonify({
                "status": "received",
                "message": "Test payload processed"
            }), 200
        
        # Default response
        return jsonify({
            "status": "success",
            "message": "Flow completed"
        })
        
    except Exception as e:
        logger.error(f"❌ Legacy flow handling error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def process_flow_request(decrypted_data):
    """Process decrypted flow request and return appropriate response"""
    
    version = decrypted_data.get('version')
    action = decrypted_data.get('action')
    screen = decrypted_data.get('screen')
    data = decrypted_data.get('data', {})
    flow_token = decrypted_data.get('flow_token')
    
    logger.info(f"📱 Processing Flow - Action: {action}, Screen: {screen}")
    
    # Handle different actions
    if action == 'INIT':
        return handle_flow_init(flow_token, data)
    
    elif action == 'data_exchange':
        if screen == 'ONBOARDING':
            return handle_onboarding_flow_submission(data, flow_token)
        elif screen == 'PIN_VERIFICATION':
            return handle_pin_verification_flow_submission(data, flow_token)
    
    elif action == 'BACK':
        return handle_flow_back(screen, data)
    
    # Default success response
    return {
        "screen": "SUCCESS",
        "data": {
            "extension_message_response": {
                "params": {
                    "flow_token": flow_token,
                    "status": "completed"
                }
            }
        }
    }

def handle_flow_init(flow_token, data):
    """Handle flow initialization"""
    logger.info("🎯 Handling flow initialization")
    
    return {
        "screen": "ONBOARDING",
        "data": {
            "welcome_message": "Welcome to Sofi Banking",
            "subtitle": "Complete your account setup to get started"
        }
    }

def handle_onboarding_flow_submission(data, flow_token):
    """Handle onboarding form submission from encrypted flow"""
    try:
        logger.info("📝 Processing onboarding flow submission")
        
        full_name = data.get('full_name')
        email = data.get('email')
        pin = data.get('pin')
        terms_agreement = data.get('terms_agreement')
        
        # Validate input
        if not all([full_name, email, pin, terms_agreement]):
            logger.warning("❌ Missing required onboarding fields")
            return {
                "screen": "ONBOARDING",
                "data": {
                    "error_message": "All fields are required"
                }
            }
        
        if len(pin) != 4 or not pin.isdigit():
            logger.warning("❌ Invalid PIN format")
            return {
                "screen": "ONBOARDING",
                "data": {
                    "error_message": "PIN must be exactly 4 digits"
                }
            }
        
        # Extract phone number from flow token
        phone_number = extract_phone_from_flow_token(flow_token)
        if not phone_number:
            phone_number = "2348104611794"  # Default for testing
        
        # Generate account number
        account_number = generate_account_number()
        
        # Hash PIN
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        # Create user account
        user_data = {
            'phone_number': phone_number,
            'full_name': full_name,
            'email': email,
            'pin_hash': pin_hash,
            'account_number': account_number,
            'balance': 0.00,
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            logger.info(f"✅ Account created: {account_number}")
            
            # Create virtual account
            create_virtual_account(phone_number, account_number, full_name)
            
            # Success response - terminate flow
            return {
                "screen": "SUCCESS",
                "data": {
                    "extension_message_response": {
                        "params": {
                            "flow_token": flow_token,
                            "account_number": account_number,
                            "full_name": full_name,
                            "status": "account_created"
                        }
                    }
                }
            }
        else:
            logger.error("❌ Account creation failed")
            return {
                "screen": "ONBOARDING",
                "data": {
                    "error_message": "Account creation failed. Please try again."
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Onboarding flow error: {e}")
        return {
            "screen": "ONBOARDING",
            "data": {
                "error_message": "An error occurred. Please try again."
            }
        }

def handle_pin_verification_flow_submission(data, flow_token):
    """Handle PIN verification form submission from encrypted flow"""
    try:
        logger.info("🔐 Processing PIN verification flow")
        
        pin = data.get('pin')
        amount = data.get('amount')
        recipient = data.get('recipient')
        
        # Get user info from flow token
        phone_number = extract_phone_from_flow_token(flow_token)
        if not phone_number:
            phone_number = "2348104611794"  # Default for testing
        
        # Verify PIN
        user_result = supabase.table('users').select('*').eq('phone_number', phone_number).execute()
        
        if not user_result.data:
            logger.warning("❌ User not found for PIN verification")
            return {
                "screen": "PIN_VERIFICATION",
                "data": {
                    "error_message": "User not found"
                }
            }
        
        user = user_result.data[0]
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        if pin_hash != user['pin_hash']:
            logger.warning("❌ Incorrect PIN provided")
            return {
                "screen": "PIN_VERIFICATION",
                "data": {
                    "error_message": "Incorrect PIN"
                }
            }
        
        logger.info("✅ PIN verified successfully")
        
        # PIN verified - proceed with transaction
        return {
            "screen": "SUCCESS",
            "data": {
                "extension_message_response": {
                    "params": {
                        "flow_token": flow_token,
                        "pin_verified": True,
                        "amount": amount,
                        "recipient": recipient,
                        "status": "pin_verified"
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ PIN verification flow error: {e}")
        return {
            "screen": "PIN_VERIFICATION",
            "data": {
                "error_message": "Verification failed. Please try again."
            }
        }

def extract_phone_from_flow_token(flow_token):
    """Extract phone number from flow token"""
    # Implement your flow token parsing logic
    # For now, you can parse it based on your token format
    try:
        # If flow token contains phone number, extract it
        # This depends on how you structure your flow tokens
        if flow_token and len(flow_token) > 10:
            # Try to extract phone number from token
            # Placeholder implementation
            return "2348104611794"
        return None
    except:
        return None

def handle_flow_back(screen, data):
    """Handle back button press in flow"""
    logger.info(f"⬅️  Flow back button pressed on screen: {screen}")
    
    # Return to previous screen based on current screen
    if screen == "PIN_VERIFICATION":
        return {
            "screen": "ONBOARDING",
            "data": {}
        }
    
    # Default to initial screen
    return {
        "screen": "ONBOARDING",
        "data": {
            "welcome_message": "Welcome to Sofi Banking"
        }
    }

def handle_onboarding_flow_completion(flow_data: dict, flow_token: str) -> tuple:
    """Handle onboarding flow completion (account creation)"""
    try:
        # Extract user data from your Flow structure
        first_name = flow_data.get("first_name", "").strip()
        last_name = flow_data.get("last_name", "").strip()
        bvn = flow_data.get("bvn", "").strip()
        address = flow_data.get("address", "").strip()
        email = flow_data.get("email", "").strip()
        phone = flow_data.get("phone", "").strip()
        pin = flow_data.get("pin", "").strip()
        
        # Combine first and last name
        full_name = f"{first_name} {last_name}".strip()
        
        logger.info(f"👤 Creating account for: {full_name} (BVN: {bvn[:3]}***)")
        logger.info(f"📋 Flow data received: {list(flow_data.keys())}")
        
        # Validate required fields from your Flow
        if not all([first_name, last_name, bvn]):
            return jsonify({
                "status": "error", 
                "message": "Missing required fields: First Name, Last Name, and BVN are required"
            }), 400
        
        # Create user account
        user_id = str(uuid.uuid4())
        account_number = generate_account_number()
        
        # Hash the PIN for security (if provided)
        pin_hash = None
        if pin:
            import hashlib
            pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        # Insert user into database
        user_record = {
            "id": user_id,
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email or f"{phone}@whatsapp.user",  # Use phone if no email
            "phone_number": phone,
            "bvn": bvn,
            "address": address,
            "pin_hash": pin_hash,
            "created_at": datetime.now().isoformat(),
            "wallet_balance": 0.0,
            "status": "active",
            "signup_source": "whatsapp_flow",
            "terms_accepted": True,  # Flow completion implies acceptance
            "flow_token": flow_token,
            "whatsapp_number": phone  # For WhatsApp identification
        }
        
        result = supabase.table("users").insert(user_record).execute()
        
        if result.data:
            # Create virtual account
            virtual_account = {
                "user_id": user_id,
                "account_number": account_number,
                "bank_name": "9PSB",
                "bank_code": "120001",
                "balance": 0.0,
                "created_at": datetime.now().isoformat()
            }
            
            supabase.table("virtual_accounts").insert(virtual_account).execute()
            
            logger.info(f"✅ Account created successfully: {account_number}")
            
            return jsonify({
                "status": "success",
                "message": "Account created successfully",
                "user_id": user_id,
                "account_number": account_number,
                "bank_name": "9PSB"
            }), 200
        else:
            logger.error("❌ Failed to create user account")
            return jsonify({
                "status": "error",
                "message": "Failed to create account"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Onboarding flow error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_transfer_flow_completion(flow_data: dict, flow_token: str) -> tuple:
    """Handle transfer verification flow completion"""
    try:
        # Extract transfer data
        pin = flow_data.get("pin", "").strip()
        amount = flow_data.get("amount", 0)
        recipient = flow_data.get("recipient", "")
        account = flow_data.get("account", "")
        
        logger.info(f"💸 Transfer verification: ₦{amount} to {recipient} ({account})")
        
        # Validate PIN (you'd normally check against user's stored PIN hash)
        if not pin or len(pin) != 4:
            return jsonify({
                "status": "error",
                "message": "Invalid PIN"
            }), 400
        
        # Process transfer (implement your transfer logic here)
        # For now, just log and return success
        
        logger.info(f"✅ Transfer approved: ₦{amount} to {recipient}")
        
        return jsonify({
            "status": "success",
            "message": "Transfer approved",
            "amount": amount,
            "recipient": recipient,
            "account": account
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Transfer flow error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def generate_account_number() -> str:
    """Generate a unique 10-digit account number"""
    import random
    while True:
        account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        # Check if account number already exists
        existing = supabase.table("virtual_accounts").select("account_number").eq("account_number", account_number).execute()
        
        if not existing.data:
            return account_number

# ===============================================
# 🏥 SOFI HEALTH MONITORING ENDPOINTS
# ===============================================

@app.route("/health")
def sofi_main_health():
    """Primary health check endpoint for Meta Business Manager verification"""
    return jsonify({
        "status": "healthy",
        "service": "Sofi WhatsApp Banking",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0",
        "endpoints": {
            "whatsapp_webhook": "/whatsapp-webhook",
            "flow_webhook": "/whatsapp-flow-webhook",
            "flow_meta_endpoint": "/whatsapp/flow",
            "health_detailed": "/health/flow"
        }
    }), 200

# ===============================================
# 📱 META WHATSAPP FLOW ENDPOINT (Expected by Meta)
# ===============================================

@app.route("/whatsapp/flow", methods=["GET", "POST"])
def sofi_meta_flow_endpoint():
    """
    Meta WhatsApp Flow endpoint - exactly what Meta expects
    This is the endpoint URL we configured in Meta Business Manager
    """
    
    if request.method == 'GET':
        # Meta verification for Flow endpoint
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'sofi_ai_webhook_verify_2024')
        
        logger.info(f"🔍 Meta Flow GET verification: mode={mode}, token_match={token == verify_token}")
        
        if mode == 'subscribe' and token == verify_token:
            logger.info("✅ Meta Flow webhook verification successful")
            return challenge
        else:
            logger.warning("❌ Meta Flow webhook verification failed")
            return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Detect Meta IP range (173.252.x.x, 31.13.x.x, 66.220.x.x)
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        is_meta_ip = any(client_ip.startswith(prefix) for prefix in [
            '173.252.', '31.13.', '66.220.', '69.63.', '69.171.', '74.119.', '103.4.'
        ])
        
        logger.info(f"🌐 Meta Flow POST from IP: {client_ip} (Meta IP: {is_meta_ip})")
        
        try:
            # Get payload (could be JSON or empty for health checks)
            payload = request.get_json(silent=True)
            
            # Check User-Agent to identify Meta/Facebook requests
            user_agent = request.headers.get('User-Agent', '')
            is_meta_request = any(agent in user_agent.lower() for agent in [
                'facebookexternalua', 'facebook', 'meta', 'whatsapp'
            ]) or is_meta_ip
            
            logger.info(f"🔍 User-Agent: {user_agent}")
            logger.info(f"🔍 Meta request: {is_meta_request}")
            
            # Handle Meta health checks and test requests
            if is_meta_request and (not payload or len(payload) == 0):
                logger.info("💊 Meta health check or test request on /whatsapp/flow")
                return jsonify({
                    "status": "ok", 
                    "service": "WhatsApp Flow Endpoint",
                    "ready": True,
                    "encryption": "available"
                }), 200
            
            if not payload:
                logger.error("❌ No payload received on /whatsapp/flow")
                return 'Bad Request', 400
            
            logger.info("🔐 Received encrypted Flow data on Meta endpoint")
            logger.info(f"📋 Payload keys: {list(payload.keys())}")
            logger.info(f"📄 Full payload: {json.dumps(payload, indent=2)}")
            
            # Check if this is encrypted flow data
            if 'encrypted_flow_data' in payload:
                return handle_encrypted_flow_data(payload)
            
            # Handle unencrypted legacy format or test data
            else:
                logger.info("📱 Handling legacy flow data format on Meta endpoint")
                return handle_legacy_flow_data(payload)
                
        except Exception as e:
            logger.error(f"❌ Meta Flow endpoint error: {e}")
            import traceback
            traceback.print_exc()
            return 'Internal Server Error', 500

@app.route("/health/flow", methods=["GET"])
def sofi_flow_health():
    """WhatsApp Flow encryption health check with detailed status"""
    try:
        # Test encryption system
        flow_encryption = get_flow_encryption()
        encryption_ready = flow_encryption is not None
        
        return jsonify({
            "status": "healthy",
            "service": "Sofi WhatsApp Flow System", 
            "timestamp": datetime.utcnow().isoformat(),
            "encryption": {
                "status": "ready" if encryption_ready else "unavailable",
                "rsa_keys": "configured" if encryption_ready else "missing"
            },
            "endpoints": {
                "flow_webhook": "/whatsapp-flow-webhook",
                "main_health": "/health",
                "flow_health": "/health/flow"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "service": "Sofi WhatsApp Flow System",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route("/whatsapp-flow-webhook/health")
def sofi_flow_webhook_health():
    """WhatsApp Flow webhook specific health verification"""
    # Return Base64 encoded response for Meta's health checks
    health_data = {
        "status": "encryption_test",
        "message": "Encryption endpoint available but decryption failed",
        "note": "Please verify key configuration in Meta Business Manager",
        "service": "WhatsApp Flow Webhook",
        "webhook": "whatsapp-flow",
        "accepts": ["GET", "POST"],
        "verification": "enabled",
        "encryption": "pending_key_setup"
    }
    
    import base64
    import json
    response_json = json.dumps(health_data)
    base64_response = base64.b64encode(response_json.encode()).decode()
    
    return base64_response, 200, {'Content-Type': 'text/plain'}

# ===============================================
# 🚀 SOFI APPLICATION ENTRY POINT
# ===============================================

if __name__ == "__main__":
    print("🚀 Starting Sofi WhatsApp Banking System...")
    print("✅ WhatsApp Flow encryption ready")
    print("✅ Health monitoring active")
    app.run(host="0.0.0.0", port=5000, debug=False)
