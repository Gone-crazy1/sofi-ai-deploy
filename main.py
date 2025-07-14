from flask import Flask, request, jsonify, url_for, render_template
from flask_cors import CORS
import os, requests, hashlib, logging, json, asyncio, tempfile, re, threading
from datetime import datetime
from supabase import create_client
import openai
from openai import OpenAI
from typing import Dict, Optional, Any
import time
from utils.bank_api import BankAPI
from utils.secure_transfer_handler import SecureTransferHandler
from utils.balance_helper import get_user_balance as get_balance_secure, check_virtual_account as check_virtual_account_secure
# Paystack Integration - Banking Partner
from paystack import get_paystack_service
from paystack.paystack_webhook import handle_paystack_webhook
# AI Assistant Integration - Powered by Pip install AI Technologies
from assistant import get_assistant
from dotenv import load_dotenv
import random
from PIL import Image
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from utils.memory import save_memory, list_memories, save_chat_message, get_chat_history
from utils.conversation_state import conversation_state
from utils.nigerian_expressions import enhance_nigerian_message, get_response_guidance
from utils.prompt_schemas import get_image_prompt, validate_image_result
from unittest.mock import MagicMock

# 🔒 SECURITY SYSTEM IMPORTS
from utils.security import init_security
from utils.security_monitor import log_security_event, AlertLevel, get_security_stats
from utils.security_config import get_security_config, TELEGRAM_SECURITY

# 🔒 SECURITY ENDPOINTS
from utils.security_endpoints import init_security_endpoints

# Load environment variables from .env file
load_dotenv()

# Import admin handler AFTER environment loading
from utils.admin_command_handler import AdminCommandHandler
admin_handler = AdminCommandHandler()

# Import user onboarding system
from utils.user_onboarding import SofiUserOnboarding
onboarding_service = SofiUserOnboarding()

# Import beneficiary management system
from utils.beneficiary_manager import beneficiary_manager

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

# Initialize required variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NELLOBYTES_USERID = os.getenv("NELLOBYTES_USERID")
NELLOBYTES_APIKEY = os.getenv("NELLOBYTES_APIKEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize AI client with API key - Powered by Pip install AI Technologies
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set the path to the ffmpeg executable for pydub
AudioSegment.converter = which("ffmpeg")

def send_typing_action(chat_id):
    """Send 'typing...' action to Telegram chat"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Failed to send typing action: {e}")


def send_reply(chat_id, message, reply_markup=None):
    """Send reply message to Telegram chat with optional inline keyboard"""
    send_typing_action(chat_id)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": message,
        "parse_mode": "Markdown"
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    response = requests.post(url, json=payload)
    return response.json() if response.status_code == 200 else None

def send_photo_to_telegram(chat_id, photo_data, caption=None):
    """Send photo to Telegram chat"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        files = {'photo': photo_data}
        data = {'chat_id': chat_id}
        
        if caption:
            data['caption'] = caption
            
        response = requests.post(url, files=files, data=data)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        return None

def detect_intent(message):
    """Enhanced intent detector using AI with chatgpt-4o-latest and Nigerian expressions support - Powered by Pip install AI Technologies"""
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
            model="chatgpt-4o-latest",
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

async def get_user_balance(chat_id):
    """Get user's current balance using enhanced helper with force sync"""
    try:
        from utils.balance_helper import get_user_balance as get_balance_secure
        return await get_balance_secure(str(chat_id), force_sync=True)
    except Exception as e:
        logger.error(f"Error getting user balance: {e}")
        return 0.0

async def check_virtual_account(chat_id):
    """Check if user has a virtual account using enhanced helper"""
    try:
        from utils.balance_helper import check_virtual_account as check_virtual_account_secure
        return await check_virtual_account_secure(str(chat_id))
    except Exception as e:
        logger.error(f"Error checking virtual account: {e}")
        return None

async def generate_ai_reply(chat_id: str, message: str):
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
New users: Direct to https://pipinstallsofi.com/onboard
Keep responses short (2-3 lines max). Use Nigerian style but stay professional.
Proudly powered by Pip install AI Technologies - the future of AI banking."""

    try:
        # Check if user has a virtual account
        virtual_account = await check_virtual_account(chat_id)
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
                    user_profile = await onboarding_service.get_user_profile(str(chat_id))
                    
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
                # New user - send web app button instead of naked link
                reply = (
                    "🚀 *Create Your Sofi Account*\n\n"
                    "Get instant virtual account for:\n"
                    "💸 Money transfers\n"
                    "📱 Airtime purchases\n"
                    "💰 Balance management\n\n"
                    "Tap the button below to get started!"
                )
                
                # Create web app button
                keyboard = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🚀 Create Account",
                                "web_app": {"url": "https://pipinstallsofi.com/onboard"}
                            }
                        ]
                    ]
                }
                
                save_chat_message(chat_id, "assistant", reply)
                return send_reply(chat_id, reply, keyboard)

        # Get conversation history
        messages = get_chat_history(chat_id)
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
            model="chatgpt-4o-latest",
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
            save_chat_message(chat_id, "user", message)
            save_chat_message(chat_id, "assistant", ai_reply)
        else:
            logger.warning(f"Not saving non-string ai_reply to chat history: {type(ai_reply)}")
        return ai_reply
        
    except Exception as e:
        logger.error(f"Error generating AI reply: {e}")
        return "Sorry, I'm having trouble thinking right now. Please try again later."

def download_file(file_id):
    """Download file from Telegram"""
    # Get file path
    file_info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    file_info = requests.get(file_info_url).json()
    file_path = file_info["result"]["file_path"]

    # Download file
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    file_data = requests.get(file_url).content
    return file_data

def process_photo(file_id):
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
            model="chatgpt-4o-latest",
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
                         "✅ Buy airtime and data\n"
                         "✅ Basic account management\n"
                         "✅ Transaction history\n\n"
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

def process_voice(file_id):
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

async def handle_transfer_flow(chat_id: str, message: str, user_data: dict = None, media_data: dict = None) -> str:
    """Handle the transfer conversation flow with enhanced natural language processing"""
    from utils.enhanced_intent_detection import enhanced_intent_detector
    
    state = conversation_state.get_state(chat_id)
    
    # Check if user wants to exit transfer flow
    if state and enhanced_intent_detector.detect_intent_change(message):
        conversation_state.clear_state(chat_id)
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
                    
                    conversation_state.set_state(chat_id, state)
                    
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
        
        conversation_state.set_state(chat_id, state)
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
        
        conversation_state.set_state(chat_id, state)
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
        
        conversation_state.set_state(chat_id, state)
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
            
            # Store transaction for secure verification
            from utils.secure_pin_verification import secure_pin_verification
            secure_pin_verification.store_pending_transaction(transaction_id, {
                'chat_id': chat_id,
                'user_data': user_data,
                'transfer_data': transfer,
                'amount': amount
            })
            
            # Create secure PIN verification message with inline keyboard
            msg = (
                f"✅ *Account verified!*\n"
                f"Click the button below to complete transfer of ₦{amount:,.2f} to:\n\n"
                f"👤 *{transfer['recipient_name']}*\n"
                f"🏦 *{transfer['bank']}* ({transfer['account_number']})\n\n"
                f"🔐 *Secure PIN verification required*"
            )
            
            # Create inline keyboard for secure PIN verification
            pin_keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "🔐 Verify Transaction",
                        "url": f"https://pipinstallsofi.com/verify-pin?txn_id={transaction_id}"
                    }
                ]]
            }
            
            conversation_state.set_state(chat_id, state)            # Send message with secure PIN button
            send_reply(chat_id, msg, pin_keyboard)
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
            
            # Store transaction for secure verification
            from utils.secure_pin_verification import secure_pin_verification
            secure_pin_verification.store_pending_transaction(transaction_id, {
                'chat_id': chat_id,
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
            
            # Create inline keyboard for secure PIN verification
            pin_keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "🔐 Verify Transaction",
                        "url": f"https://pipinstallsofi.com/verify-pin?txn_id={transaction_id}"
                    }
                ]]
            }
            
            conversation_state.set_state(chat_id, state)
            send_reply(chat_id, msg, pin_keyboard)
            return None  # Don't send additional message
            
        elif response_lower in ['no', 'n', 'cancel', 'stop']:
            # User cancelled
            conversation_state.clear_state(chat_id)
            
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

async def handle_airtime_commands(chat_id: str, message: str, user_data: dict, virtual_account: dict = None) -> Optional[str]:
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
        response = await airtime_handler.handle_airtime_request(chat_id, message, user_data, virtual_account)
        return response
    except Exception as e:
        logger.error(f"Error handling airtime command: {e}")
        # Only return error message if it was actually an airtime request
        airtime_keywords = ['airtime', 'data', 'recharge', 'mtn', 'glo', 'airtel', '9mobile', 'buy credit']
        if any(keyword in message.lower() for keyword in airtime_keywords):
            return "Sorry, I'm having trouble with airtime services right now. Please try again later."
        return None

async def handle_crypto_commands(chat_id: str, message: str, user_data: dict) -> Optional[str]:
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
        response = await crypto_handler.handle_crypto_request(chat_id, message, user_data)
        return response
    except Exception as e:
        logger.error(f"Error handling crypto command: {e}")
        # Only return error message if it was actually a crypto request
        crypto_keywords = ['wallet', 'bitcoin', 'btc', 'ethereum', 'eth', 'usdt', 'crypto', 'cryptocurrency']
        if any(keyword in message.lower() for keyword in crypto_keywords):
            return "Sorry, I'm having trouble with crypto services right now. Please try again later."
        return None

async def handle_message(chat_id: str, message: str, user_data: dict = None, virtual_account: dict = None) -> str:
    """Main message handler with AI Assistant integration - Powered by Pip install AI Technologies"""
    try:
        # Check for admin commands first (highest priority)
        admin_command = await admin_handler.detect_admin_command(message, chat_id)
        if admin_command:
            admin_response = await admin_handler.handle_admin_command(admin_command, message, chat_id)
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
            response, function_data = await assistant.process_message(chat_id, message, context_data)
            
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
                            send_reply(chat_id, pin_message, pin_keyboard)
                            
                            # Return special marker to prevent duplicate message sending
                            return "PIN_ALREADY_SENT"
                        

                        
                        # Only web PIN is supported now - inline PIN system removed
                    
                                        # Check if any function returned a successful transfer with balance message
                    if isinstance(func_result, dict) and func_result.get("success") and func_result.get("balance_message"):
                        logger.info(f"💰 Function {func_name} completed transfer - sending balance message")
                        
                        # Send the main transfer completion message
                        transfer_message = func_result.get("message", "Transfer completed successfully!")
                        send_reply(chat_id, transfer_message)
                        
                        # Send the automatic balance message immediately after
                        balance_message = func_result.get("balance_message")
                        send_reply(chat_id, balance_message)
                        
                        # Return special marker to prevent duplicate message sending
                        return "BALANCE_MESSAGE_SENT"
                    
                        
                        # Generate and send beautiful HTML receipt
                        receipt_data = func_result.get("receipt_data", {})
                        if receipt_data:
                            await send_beautiful_receipt(chat_id, receipt_data, func_result)
                        
                        # Return the receipt message directly
                        return func_result.get("message", "Transfer completed successfully!")
            
            # If assistant handled it successfully, return the response
            if response and not response.startswith("Sorry, I encountered an error"):
                logger.info(f"✅ AI Assistant handled message from {chat_id}")
                return response
            else:
                logger.info(f"⚠️ AI Assistant failed, falling back to legacy handlers")
        
        except Exception as assistant_error:
            logger.error(f"❌ AI Assistant error: {str(assistant_error)}")
            logger.info("🔄 Falling back to legacy message handlers")
        
        # Fallback to legacy handlers if assistant fails
        # Check for beneficiary commands first (before other handlers)
        beneficiary_response = await beneficiary_manager.handle_beneficiary_command(chat_id, message, user_data or {})
        if beneficiary_response:
            return beneficiary_response
        
        # Check for transaction history queries
        history_response = await handle_transaction_history_query(chat_id, message, user_data)
        if history_response:
            return history_response
        
        # Check for 2-month summary requests
        summary_keywords = ['2 month', 'two month', 'monthly summary', 'financial summary', 'spending summary', 
                           'transaction summary', 'summarize my transactions', 'past 2 months', 'last 2 months']
        if any(keyword in message.lower() for keyword in summary_keywords):
            summary_response = await transaction_summarizer.get_2_month_summary(chat_id, user_data)
            return summary_response
        
        # Check for balance inquiry
        balance_response = await handle_balance_inquiry(chat_id, message, user_data, virtual_account)
        if balance_response:
            return balance_response
        
        # Check for transfer intent
        transfer_response = await handle_transfer_flow(chat_id, message, user_data)
        if transfer_response:
            return transfer_response
        
        # Check for airtime/data commands
        airtime_response = await handle_airtime_commands(chat_id, message, user_data, virtual_account)
        if airtime_response:
            return airtime_response
        
        # Check for crypto commands
        crypto_response = await handle_crypto_commands(chat_id, message, user_data)
        if crypto_response:
            return crypto_response
        
        # Fall back to general AI conversation
        ai_response = await generate_ai_reply(chat_id, message)
        return ai_response
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return "Sorry, I encountered an error. Please try again."

async def handle_balance_inquiry(chat_id: str, message: str, user_data: dict = None, virtual_account: dict = None) -> str:
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
            virtual_account = await check_virtual_account(chat_id)
        
        if not virtual_account:
            return (
                "🏦 You don't have a virtual account yet.\n\n"
                "Create one by tapping the button below to get started with Sofi AI!"
            )
            # Note: This should trigger a web app button but we're returning text here
            # The main handler should catch this and send the web app button
        
        # Get current balance
        current_balance = await get_user_balance(chat_id)
        
        # Get user's full name from Supabase
        from utils.user_onboarding import onboarding_service
        user_profile = await onboarding_service.get_user_profile(str(chat_id))
        
        # Safe access to account details
        account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number", "Not available")
        bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Paystack Bank")
        display_name = user_profile.get('full_name') if user_profile else virtual_account.get("accountName", "Not available")
        
        # Get recent transactions from Supabase
        recent_transactions = []
        try:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # First get the user UUID from telegram_chat_id
            user_result = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
            
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

        # Fallback to ChatGPT 4o latest model
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-latest",
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

# 🔒 SECURITY MONITORING ROUTES
@app.route("/security/stats")
def security_stats():
    """Get security statistics (admin only)"""
    try:
        # Basic admin check (implement proper admin authentication)
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('ADMIN_API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        
        stats = get_security_stats()
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

@app.route("/webhook", methods=["POST"])
async def webhook_incoming():
    """Handle incoming Telegram messages and callback queries"""
    try:
        # 🔒 Security monitoring for webhook
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Log webhook access
        log_security_event("webhook_access", AlertLevel.LOW, client_ip, user_agent, "/webhook", "POST")
        
        # Validate Telegram webhook (basic check)
        if not user_agent or 'telegram' not in user_agent.lower():
            log_security_event("suspicious_webhook", AlertLevel.MEDIUM, client_ip, user_agent, "/webhook", "POST", 
                             reason="Non-Telegram user agent")
        
        data = request.get_json()
        
        if not data:
            log_security_event("invalid_webhook_payload", AlertLevel.MEDIUM, client_ip, user_agent, "/webhook", "POST")
            return jsonify({"error": "Invalid update payload", "response": None}), 400
        
        # Handle callback queries (inline keyboard button presses)
        if "callback_query" in data:
            return await handle_callback_query(data["callback_query"])
        
        # Handle regular messages
        if "message" not in data:
            return jsonify({"error": "Invalid message payload", "response": None}), 400
        
        message_data = data["message"]
        chat_id = str(message_data["chat"]["id"])
        
        # Extract user information
        user_data = message_data.get("from", {})
        
        # Check if user exists in database
        user_resp = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        user_exists = len(user_resp.data) > 0
        
        # Handle photo messages
        if "photo" in message_data:
            file_id = message_data["photo"][-1]["file_id"]  # Get the highest quality photo
            success, response = process_photo(file_id)
            
            if success:
                ai_response = await generate_ai_reply(chat_id, response)
                send_reply(chat_id, ai_response)
            else:
                send_reply(chat_id, response)
        
        # Handle voice messages
        elif "voice" in message_data:
            file_id = message_data["voice"]["file_id"]
            
            # Check if user is in PIN verification mode
            state = conversation_state.get_state(chat_id)
            if state and state.get('step') == 'secure_pin_verification':
                # Process voice PIN
                from utils.voice_pin_processor import VoicePinProcessor
                
                voice_processor = VoicePinProcessor()
                result = await voice_processor.process_voice_pin(file_id, chat_id)
                
                if result['success']:
                    extracted_pin = result['pin']
                    
                    # Process the PIN using the secure transfer system
                    from utils.secure_transfer_handler import handle_secure_transfer_confirmation
                    transfer_data = state.get('transfer', {})
                    
                    # Handle the PIN as if it was typed
                    response = await handle_secure_transfer_confirmation(
                        chat_id=chat_id,
                        message=extracted_pin,
                        user_data=user_data,
                        transfer_data=transfer_data
                    )
                    send_reply(chat_id, response)
                else:
                    send_reply(chat_id, result['error'])
                    
            else:
                # Normal voice processing for general conversation
                success, response = process_voice(file_id)
                
                if success:
                    # Process the transcribed text as a regular message
                    user_message = response
                    ai_response = await handle_message(chat_id, user_message, user_data)
                    send_reply(chat_id, ai_response)
                else:
                    send_reply(chat_id, response)
        
        # Handle text messages
        elif "text" in message_data:
            user_message = message_data.get("text", "").strip()
            
            if not user_message:
                return jsonify({"success": True}), 200
            
            # Check if user exists and handle onboarding flow intelligently
            if not user_exists:
                # Check if message suggests they already know they need an account
                skip_onboarding_keywords = [
                    "already registered", "i have account", "just created", "completed registration",
                    "just signed up", "thanks", "thank you", "okay", "ok", "got it", "understood",
                    "will do", "sure", "alright", "fine", "done", "yes", "no problem"
                ]
                
                # Don't send onboarding if they seem to acknowledge or are just being polite
                if any(keyword in user_message.lower() for keyword in skip_onboarding_keywords):
                    # Give a brief helpful response with web app button
                    brief_response = (
                        "Ready to help! Complete your registration by tapping the button below:"
                    )
                    
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "🚀 Complete Registration",
                                    "web_app": {"url": "https://pipinstallsofi.com/onboard"}
                                }
                            ]
                        ]
                    }
                    
                    send_reply(chat_id, brief_response, keyboard)
                    return jsonify({"success": True}), 200
                
                # Only show full onboarding for substantial messages or clear requests
                substantial_message = len(user_message.split()) > 2 or any(
                    keyword in user_message.lower() for keyword in [
                        "account", "register", "sign up", "create", "start", "begin", "help",
                        "transfer", "send money", "balance", "airtime", "data"
                    ]
                )
                
                if substantial_message:
                    # Force onboarding for new users with inline keyboard
                    onboarding_message = (
                        f"👋 *Welcome to Sofi AI!* I'm your intelligent financial assistant powered by Pip install AI Technologies.\n\n"
                        f"🔐 *To get started, I need to create your secure virtual account:*\n\n"
                        f"📋 *You'll need:*\n"
                        f"• Your BVN (Bank Verification Number)\n"
                        f"• Phone number\n"
                        f"• Basic personal details\n\n"
                        f"✅ *Once done, you can:*\n"
                        f"• Send money to any bank instantly\n"
                        f"• Buy airtime & data at best rates\n"
                        f"• Receive money from anywhere\n"
                        f"• Chat with me for intelligent financial advice\n\n"
                        f"🚀 *Click the button below to start your registration!*"
                    )
                    
                    # Create inline keyboard with web app button
                    inline_keyboard = {
                        "inline_keyboard": [[
                            {
                                "text": "🚀 Complete Registration",
                                "web_app": {"url": "https://pipinstallsofi.com/onboard"}
                            }
                        ]]
                    }
                    
                    send_reply(chat_id, onboarding_message, inline_keyboard)
                    return jsonify({"success": True}), 200
                else:
                    # For very brief messages, give a gentle nudge with web app button
                    brief_nudge = (
                        "Hi! I'm Sofi AI. Tap below to get started:"
                    )
                    
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "🚀 Get Started",
                                    "web_app": {"url": "https://pipinstallsofi.com/onboard"}
                                }
                            ]
                        ]
                    }
                    
                    send_reply(chat_id, brief_nudge, keyboard)
                    return jsonify({"success": True}), 200
            
            # Handle existing user messages
            try:
                # Check if user has virtual account
                virtual_account = await check_virtual_account(chat_id)
                
                # Generate AI reply with conversation context
                ai_response = await handle_message(chat_id, user_message, user_resp.data[0] if user_resp.data else None, virtual_account)
                
                # Only send reply if it's not a PIN requirement (PIN messages are already sent in handle_message)
                if ai_response and not ai_response.startswith("PIN_ALREADY_SENT") and not ai_response.startswith("BALANCE_MESSAGE_SENT"):
                    send_reply(chat_id, ai_response)
            except Exception as e:
                logger.error(f"Error in AI reply: {str(e)}")
                send_reply(chat_id, "Sorry, I encountered an error processing your request. Please try again.")

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
            
            # Generate a temporary telegram_id if not provided (for web form users)
            if not data.get('telegram_id'):
                import uuid
                data['telegram_id'] = f"web_user_{uuid.uuid4().hex[:8]}"
        
        onboarding = SofiUserOnboarding()
        result = onboarding.create_virtual_account(data)
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creating virtual account: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

# Removed duplicate onboard route - now using templates/onboarding.html (WORKING VERSION)

@app.route("/onboard")
def onboard_page():
    """Serve beautiful onboarding page"""
    try:
        with open('web_onboarding.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content, 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return "Onboarding page not found", 404
    except Exception as e:
        logger.error(f"Error serving onboarding page: {e}")
        return "Internal server error", 500

@app.route("/verify-pin")
def pin_verification_page():
    """Serve secure PIN verification page"""
    transaction_id = request.args.get('txn_id')
    
    if not transaction_id:
        return "Invalid transaction", 400
    
    # Get transaction data from temporary storage
    if not hasattr(app, 'temp_transfers'):
        app.temp_transfers = {}
    
    transaction = app.temp_transfers.get(transaction_id)
    if not transaction:
        return "Transaction expired or invalid", 400
    
    # Check if transaction is expired (5 minutes)
    from datetime import datetime, timedelta
    created_at = datetime.fromisoformat(transaction['created_at'])
    if datetime.now() - created_at > timedelta(minutes=5):
        # Remove expired transaction
        del app.temp_transfers[transaction_id]
        return "Transaction expired", 400
    # Render the PIN entry page with transaction details
    return render_template("pin-entry.html", 
                         transaction_id=transaction_id,
                         transfer_data={
                             'amount': transaction['amount'],
                             'recipient_name': transaction['recipient_name'],
                             'bank': transaction['bank_name'],
                             'account_number': transaction['account_number']
                         })

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
    # Create a sample transaction for testing
    sample_transaction = {
        'amount': 5000.00,
        'recipient_name': 'John Doe',
        'bank': 'GTBank',
        'account_number': '0123456789'
    }
    
    return render_template("pin-entry.html", 
                         transaction_id="test_demo",
                         transfer_data=sample_transaction)



@app.route("/api/verify-pin", methods=["POST"])
async def verify_pin_api():
    """API endpoint for PIN verification with security monitoring"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        pin = data.get('pin')
        
        # Get client IP for security monitoring
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if not transaction_id or not pin:
            # Monitor failed PIN attempts
            from utils.security_monitor import security_monitor
            security_monitor.monitor_pin_attempts(client_ip, False)
            
            return jsonify({
                'success': False,
                'error': 'Missing transaction ID or PIN'
            }), 400
        
        # Get transaction data from temporary storage
        if not hasattr(app, 'temp_transfers'):
            app.temp_transfers = {}
        
        transaction = app.temp_transfers.get(transaction_id)
        if not transaction:
            # Monitor failed PIN attempts
            from utils.security_monitor import security_monitor
            security_monitor.monitor_pin_attempts(client_ip, False)
            
            return jsonify({
                'success': False,
                'error': 'Transaction expired or invalid'
            }), 400
        
        # Check if transaction is expired (5 minutes)
        from datetime import datetime, timedelta
        created_at = datetime.fromisoformat(transaction['created_at'])
        if datetime.now() - created_at > timedelta(minutes=5):
            # Remove expired transaction
            del app.temp_transfers[transaction_id]
            
            # Monitor failed PIN attempts
            from utils.security_monitor import security_monitor
            security_monitor.monitor_pin_attempts(client_ip, False)
            
            return jsonify({
                'success': False,
                'error': 'Transaction expired'
            }), 400
        # Verify PIN
        from functions.security_functions import verify_pin
        pin_result = await verify_pin(chat_id=transaction['chat_id'], pin=pin)
        
        # Monitor PIN attempt
        from utils.security_monitor import security_monitor
        security_monitor.monitor_pin_attempts(client_ip, pin_result.get("valid", False))
        
        if not pin_result.get("valid"):
            return jsonify({
                'success': False,
                'error': 'Invalid PIN'
            }), 400
        
        # ✅ IMMEDIATE RESPONSE: Create success page URL first
        from urllib.parse import urlencode
        from datetime import datetime
        
        success_params = {
            'amount': transaction['amount'],
            'recipient_name': transaction['recipient_name'],
            'bank': transaction['bank_name'],
            'account_number': transaction['account_number'],
            'reference': f"TX{transaction_id[-8:]}",  # Use transaction ID as temporary reference
            'fee': transaction.get('fee', 20),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        redirect_url = f"/success?{urlencode(success_params)}"
        
        # ⚡ BACKGROUND PROCESSING: Execute transfer and notifications async
        import threading
        
        def process_transfer_background():
            """Process transfer and send notifications in background"""
            try:
                # Execute the transfer
                from functions.transfer_functions import send_money
                import asyncio
                
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(send_money(
                    chat_id=transaction['chat_id'],
                    account_number=transaction['account_number'],
                    bank_name=transaction['bank_name'],
                    amount=transaction['amount'],
                    pin=pin,
                    narration=transaction['narration']
                ))
                
                if result.get('success'):
                    # Generate and send Telegram notifications
                    receipt = f"""🧾 **SOFI AI TRANSFER RECEIPT**
═══════════════════════════════

📋 **TRANSACTION DETAILS**
Reference: {result.get('reference', 'N/A')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: COMPLETED ✅

💸 **TRANSFER SUMMARY**
Amount: ₦{transaction['amount']:,.2f}
Fee: ₦{transaction.get('fee', 20):,.2f}
Total: ₦{transaction['amount'] + transaction.get('fee', 20):,.2f}

👤 **RECIPIENT DETAILS**
Name: {transaction['recipient_name']}
Account: {transaction['account_number']}
Bank: {transaction['bank_name']}

═══════════════════════════════
⚡ Powered by Sofi AI
🔒 Secured by Paystack
═══════════════════════════════

Thank you for using Sofi! 💙"""
                    
                    send_reply(transaction['chat_id'], receipt)
                    
                    # Generate and send beautiful receipt
                    try:
                        from beautiful_receipt_generator import SofiReceiptGenerator
                        receipt_gen = SofiReceiptGenerator()
                        
                        receipt_data = {
                            'user_name': 'Sofi User',
                            'amount': transaction['amount'],
                            'recipient_name': transaction['recipient_name'],
                            'recipient_account': transaction['account_number'],
                            'recipient_bank': transaction['bank_name'],
                            'transfer_fee': transaction.get('fee', 20),
                            'new_balance': result.get('balance_after', 0),
                            'reference': result.get('reference', 'N/A')
                        }
                        
                        beautiful_receipt = receipt_gen.create_bank_transfer_receipt(receipt_data)
                        if beautiful_receipt:
                            send_reply(transaction['chat_id'], beautiful_receipt)
                            logger.info(f"📧 Beautiful receipt sent to {transaction['chat_id']}")
                    except Exception as e:
                        logger.error(f"Failed to generate beautiful receipt: {e}")
                    
                    # Send Sofi's acknowledgment
                    from utils.bank_name_converter import get_bank_name_from_code
                    friendly_bank_name = get_bank_name_from_code(transaction.get('bank_code', ''))
                    display_bank_name = friendly_bank_name if friendly_bank_name != "Unknown Bank" else transaction['bank_name']
                    
                    sofi_response = f"""Transfer completed successfully! ✅

I've sent ₦{transaction['amount']:,.2f} to {transaction['recipient_name']} at {display_bank_name}.

Is there anything else I can help you with today?"""
                    
                    send_reply(transaction['chat_id'], sofi_response)
                    logger.info(f"✅ Transfer completed successfully for {transaction['chat_id']}")
                    
                else:
                    # Send error notification
                    error_message = f"""❌ Transfer Failed

{result.get('error', 'Unknown error occurred')}

Please try again or contact support if the issue persists."""
                    
                    send_reply(transaction['chat_id'], error_message)
                    logger.error(f"❌ Transfer failed for {transaction['chat_id']}: {result.get('error')}")
                
                loop.close()
                
            except Exception as e:
                logger.error(f"❌ Background transfer processing error: {e}")
                # Send error notification to user
                try:
                    send_reply(transaction['chat_id'], "❌ Transfer processing error. Please contact support.")
                except:
                    pass
        
        # Start background processing
        background_thread = threading.Thread(target=process_transfer_background)
        background_thread.daemon = True
        background_thread.start()
        
        # Remove transaction from temporary storage immediately
        del app.temp_transfers[transaction_id]
        
        # ⚡ IMMEDIATE RESPONSE: Return success page instantly
        return jsonify({
            'success': True,
            'message': 'Transfer initiated successfully',
            'reference': f"TX{transaction_id[-8:]}",
            'redirect_url': redirect_url
        }), 200
            
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
    """API endpoint for web onboarding"""
    try:
        # Get user data from request
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'No user data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['telegram_id', 'full_name', 'phone']
        missing_fields = [field for field in required_fields if not user_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Run the onboarding process
        logger.info(f"Starting web onboarding for user: {user_data.get('full_name')}")
        
        import asyncio
        # Use asyncio.run to safely run the async onboarding function
        result = asyncio.run(onboarding_service.create_new_user(user_data))
        
        if result.get('success'):
            logger.info(f"Successfully onboarded web user: {user_data.get('full_name')}")
            
            # Send account details to user via Telegram if telegram_id is provided
            telegram_id = user_data.get('telegram_id')
            if telegram_id and not telegram_id.startswith('web_user_'):
                try:
                    asyncio.run(send_account_details_to_user(telegram_id, result))
                    logger.info(f"Account details sent to Telegram user {telegram_id}")
                except Exception as e:
                    logger.error(f"Failed to send account details to {telegram_id}: {e}")
            
            return jsonify(result), 200
        else:
            logger.warning(f"Onboarding failed for web user: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in web onboarding API: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

async def send_account_details_to_user(chat_id: str, onboarding_result: dict):
    """Send account details to user via Telegram after successful onboarding"""
    try:
        account_details = onboarding_result.get('account_details', {})
        full_name = onboarding_result.get('full_name', '')
        customer_code = onboarding_result.get('customer_code', '')
        
        # Create concise welcome message
        welcome_message = (
            f"🎉 *Account Created!*\n\n"
            f"🏦 *Account:* `{account_details.get('account_number', 'N/A')}`\n"
            f"👤 *Name:* {account_details.get('account_name', 'N/A')}\n"
            f"🏛️ *Bank:* {account_details.get('bank_name', 'N/A')}\n\n"
            f"� Fund your account, then try:\n"
            f"\"Check new balance\" or \"Send money\""
        )
        
        # Send message to user
        send_reply(chat_id, welcome_message)
        logger.info(f"Account details sent to user {chat_id}")
        
    except Exception as e:
        logger.error(f"Error sending account details to user {chat_id}: {e}")

@app.route("/api/notify-onboarding", methods=["POST"])
def notify_onboarding_complete():
    """Webhook endpoint for onboarding completion notifications"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        onboarding_result = data.get('result', {})
        
        if telegram_id and not telegram_id.startswith('web_user_'):
            # Send account details to the user
            import asyncio
            asyncio.run(send_account_details_to_user(telegram_id, onboarding_result))
            
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error in onboarding notification: {e}")
        return jsonify({'success': False}), 500

# Removed duplicate onboard route - using the working templates/onboarding.html above

# Note: Old PIN entry web routes removed - now using inline keyboards

def edit_message(chat_id, message_id, text, reply_markup=None):
    """Edit a message in Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"✅ Message edited successfully for chat {chat_id}")
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
        chat_id = str(callback_query["from"]["id"])
        callback_data = callback_query.get("data", "")
        message_id = callback_query.get("message", {}).get("message_id")
        
        logger.info(f"📱 Callback query from {chat_id}: {callback_data}")
        
        # Define answer_callback_query helper
        async def answer_callback_query(query_id: str, text: str = ""):
            """Answer a callback query to remove loading state"""
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
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

async def send_beautiful_receipt(chat_id, receipt_data, transfer_result):
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
        send_reply(chat_id, receipt_text)
        logger.info(f"📧 Beautiful receipt sent to {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending beautiful receipt: {str(e)}")
        # Fallback to simple reply
        txn_id = receipt_data.get('transaction_id', 'N/A') if receipt_data else 'N/A'
        send_reply(chat_id, f"✅ Transfer completed successfully!\nTransaction ID: {txn_id}")

