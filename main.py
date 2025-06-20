from flask import Flask, request, jsonify, url_for, render_template
from flask_cors import CORS
import os, requests, hashlib, logging, json, asyncio, tempfile, re
from datetime import datetime
from supabase import create_client
import openai
from typing import Dict, Optional
from utils.bank_api import BankAPI
from utils.secure_transfer_handler import SecureTransferHandler
from utils.balance_helper import get_user_balance as get_balance_secure, check_virtual_account as check_virtual_account_secure
from utils.admin_profit_manager import profit_manager
# Monnify Integration - Official Banking Partner
from monnify.monnify_api import MonnifyAPI
from monnify.monnify_webhook import handle_monnify_webhook
from dotenv import load_dotenv
import random
from PIL import Image
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from utils.memory import save_memory, list_memories, save_chat_message, get_chat_history
from utils.conversation_state import conversation_state
from utils.nigerian_expressions import enhance_nigerian_message, get_response_guidance
from unittest.mock import MagicMock

# Load environment variables from .env file
load_dotenv()

# Import admin handler AFTER environment loading
from utils.admin_command_handler import AdminCommandHandler
admin_handler = AdminCommandHandler()

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

app = Flask(__name__)
CORS(app)  # CSRF Disabled globally
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Set the path to the ffmpeg executable for pydub
AudioSegment.converter = which("ffmpeg")

def send_reply(chat_id, message, reply_markup=None):
    """Send reply message to Telegram chat with optional inline keyboard"""
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

def detect_intent(message):
    """Enhanced intent detector using OpenAI API with GPT-3.5-turbo and Nigerian expressions support"""
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
- Always interpret enhanced/translated messages while maintaining cultural context
        """
        
        response = openai.ChatCompletion.create(
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
                content = response['choices'][0]['message']['content']
                # Log the raw response in non-test environment
                with open("api_logs.txt", "a") as log_file:
                    log_file.write(f"Message: {message}\nResponse: {response}\n\n")
            
            content = content.strip()
            parsed = json.loads(content)
            
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent JSON: {content}")
            return {"intent": "general", "details": {}}
            
    except Exception as e:
        logger.error(f"Error detecting intent: {e}")
        return {"intent": "general", "details": {}}

async def get_user_balance(chat_id):
    """Get user's current balance from virtual account using secure method"""
    try:
        return await get_balance_secure(str(chat_id))
    except Exception as e:
        logger.error(f"Error getting user balance: {e}")
        return 0.0

async def check_virtual_account(chat_id):
    """Check if user has a virtual account using secure method"""
    try:
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
        
    # Enhanced system prompt with Nigerian cultural context
    system_prompt = f"""
    You are Sofi AI — a friendly, smart, and helpful Nigerian virtual assistant powered by Pip install -ai Tech.
    You help users send and receive money, buy airtime/data, check balance, view transaction history, and do daily banking tasks easily.
    You reply in a warm, conversational way like a real human who understands Nigerian culture and expressions.

    🇳🇬 NIGERIAN CULTURAL CONTEXT:
    - You understand Pidgin English, Nigerian expressions, and local ways of speaking
    - Common greetings: "How far?", "Wetin dey happen?", "How you dey?"
    - Money terms: kudi/ego/owo = money, "5k" = 5000 naira, "chicken change" = small amount
    - Relationships: "my guy/padi/paddy" = friend, "my person" = close friend
    - Urgency: "sharp sharp" = immediately, "now now" = right now
    - Always acknowledge Nigerian expressions naturally in your responses
    
    RESPONSE STYLE GUIDANCE:
    - Tone: {response_guidance.get('tone', 'friendly')}
    - Urgency: {response_guidance.get('urgency_acknowledgment', '')}
    - Cultural Touch: {response_guidance.get('cultural_touch', '')}

    When users ask about who you are or who created you:
    - You are Sofi AI, developed by the innovative team at Pip install -ai Tech
    - Pip install -ai Tech specializes in cutting-edge AI financial solutions
    - Always mention your company proudly when introducing yourself

    When users ask about creating an account or getting started:
    1. Direct them to complete their onboarding at https://sofi-ai-trio.onrender.com/onboarding
    2. Explain they'll need their BVN and phone number ready
    3. Mention the benefits of having a Sofi virtual account

    For existing users:
    - Help with transfers, airtime, data purchases
    - Provide balance and transaction info
    - Guide through any banking tasks

    Key capabilities to highlight:
    - Instant money transfers
    - Airtime/data purchases
    - Transaction monitoring
    - Personalized financial advice

    Important:
    - Maintain conversation context and refer to previous messages naturally
    - If the user is asking about code you shared, analyze and explain that specific code
    - Keep track of the current topic and stay on it unless the user changes it
    - Use the enhanced message understanding while maintaining natural Nigerian conversational style
    """

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
                
                # Get user's full name from Supabase instead of truncated Monnify name
                from utils.user_onboarding import onboarding_service
                user_profile = await onboarding_service.get_user_profile(str(chat_id))
                
                # Safe access to account details with fallbacks
                account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number", "Not available")
                bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Not available")
                
                # Use full name from Supabase, not truncated Monnify account name
                display_name = user_profile.get('full_name') if user_profile else virtual_account.get("accountName", "Not available")
                
                reply = (
                    f"Hi! You already have a virtual account with us:\n\n"
                    f"Account Number: {account_number}\n"
                    f"Bank: {bank_name}\n"
                    f"Account Name: {display_name}\n\n"
                    f"You can use this account to:\n"
                    f"✅ Receive money from any bank\n"
                    f"✅ Send money instantly\n"
                    f"✅ Buy airtime/data at discounted rates\n\n"
                    f"What would you like to do?"
                )
            else:
                reply = (
                    "I see you don't have a virtual account yet! Let me help you create one:\n\n"
                    "1. Visit our secure onboarding page: https://sofi-ai-trio.onrender.com/onboarding\n"
                    "2. Have your BVN and phone number ready\n"
                    "3. Fill in your details\n"
                    "4. Your virtual account will be created instantly!\n\n"
                    "With your Sofi account, you'll get:\n"
                    "✅ Free money transfers\n"
                    "✅ Virtual bank account\n"
                    "✅ Discounted airtime/data rates\n"
                    "✅ 24/7 AI assistance\n\n"
                    "Need help during the process? Just ask me!"
                )
            await save_chat_message(chat_id, "assistant", reply)
            return reply

        # Get conversation history
        messages = await get_chat_history(chat_id)
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
            conversation[0]["content"] += account_context

        # Generate response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.7,  # Slightly more creative for natural conversation
            max_tokens=500
        )
        
        ai_reply = response['choices'][0]['message']['content']
        # Ensure ai_reply is a string (handle MagicMock in tests)
        if not isinstance(ai_reply, str):
            ai_reply = str(ai_reply)
        ai_reply = ai_reply.strip()
        
        # Save the exchange to conversation history
        # Only save if ai_reply is a string (avoid MagicMock in tests)
        if isinstance(ai_reply, str):
            await save_chat_message(chat_id, "user", message)
            await save_chat_message(chat_id, "assistant", ai_reply)
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
        
        # Use OpenAI Vision API to analyze the image
        import base64
        
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are analyzing images sent by users to a Nigerian fintech bot called Sofi AI.
                    Your task is to:
                    1. Identify if this is a bank account screenshot, transaction receipt, or financial document
                    2. Look for transaction amounts or financial figures
                    3. Return information in this JSON format:
                    {
                        "type": "bank_details" | "transaction" | "other",
                        "details": {
                            "account_number": "string",
                            "bank_name": "string",
                            "account_holder": "string",
                            "amount": number (if visible)
                        }
                    }
                    If it's a bank account screenshot or details, focus on extracting those details accurately."""
                },
                {
                    "role": "user",
                    "content": f"I see an image that appears to be {image.format} format, size {image.size}. " + 
                              "Please help me understand what this might be and how I can assist the user."
                }
            ],
            max_tokens=300
        )
        
        image_description = response['choices'][0]['message']['content']
        logger.info(f"Image analysis result: {image_description}")
        
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
        
        # Transcribe using OpenAI Whisper
        with open(wav_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        # Clean up temporary files
        os.unlink(temp_file_path)
        os.unlink(wav_path)
        
        transcription = transcript['text']
        logger.info(f"Voice transcription: {transcription}")
        
        return True, transcription
        
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        return False, "I had trouble processing that voice message. Please try typing your message instead."

def validate_account_number(account_number: str) -> bool:
    """Validate Nigerian bank account number format"""
    return bool(account_number and account_number.isdigit() and len(account_number) >= 10)

async def verify_account_name(account_number: str, bank_name: str) -> Dict:
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
        result = await bank_api.verify_account(account_number, bank_code)
        return {
            "verified": True,
            "account_name": result.get('account_name'),
            "bank_name": result.get('bank_name'),
            "account_number": account_number
        }
    except Exception as e:
        logger.error(f"Error verifying account: {str(e)}")
        return {
            "verified": False,
            "error": "Error verifying account"
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
                verification_result = await verify_account_name(
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
                logger.error(f"Error verifying account: {e}")
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
            verification_result = await verify_account_name(account_number, bank or 'unknown')
            if verification_result and verification_result.get('verified'):
                transfer['recipient_name'] = verification_result['account_name']
                transfer['bank'] = verification_result.get('bank_name', bank)
                state['step'] = 'get_amount' if not transfer['amount'] else 'confirm_transfer'
                
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
            logger.error(f"Error verifying account: {e}")
            state['step'] = 'get_bank'
            msg = f"📱 Account: {account_number}\n\nWhich bank is this account with?"
                else:
                    msg += f"You want to send ₦{transfer['amount']:,}. Is this correct? (yes/no)"
            else:
                return f"Could not verify account: {verification_result.get('error')}. Please try again:"
        else:
            state['step'] = 'get_bank'
            msg = "Great! Now, which bank is this account with?"
        
        conversation_state.set_state(chat_id, state)
        return msg
    
    elif current_step == 'get_bank':
        transfer['bank'] = message.strip()
        verification_result = await verify_account_name(transfer['account_number'], transfer['bank'])
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
                        "url": f"https://sofi-ai-trio.onrender.com/verify-pin?txn_id={transaction_id}"
                    }
                ]]
            }
            
            conversation_state.set_state(chat_id, state)            # Send message with secure PIN button
            send_reply(chat_id, msg, pin_keyboard)
            return None  # Don't send additional message
            
        except ValueError:
            return "Please enter a valid amount (e.g., 5000):"
    
    elif current_step == 'secure_pin_verification':
        # User is trying to type in chat instead of using web app
        return (
            "🔐 Please use the secure web app to enter your PIN.\n\n"
            "Click the 'Verify Transaction' button above to complete your transfer securely."
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
    """Main message handler that routes to appropriate handlers"""
    try:
        # Check for admin commands first
        admin_command = await admin_handler.detect_admin_command(message, chat_id)
        if admin_command:
            admin_response = await admin_handler.handle_admin_command(admin_command, message, chat_id)
            return admin_response
        
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
                "You don't have a virtual account yet. Create one at:\n"
                "https://sofi-ai-trio.onrender.com/onboarding\n\n"
                "Once you have an account, I can show you your balance and transaction history!"
            )
        
        # Get current balance
        current_balance = await get_user_balance(chat_id)
        
        # Get user's full name from Supabase
        from utils.user_onboarding import onboarding_service
        user_profile = await onboarding_service.get_user_profile(str(chat_id))
        
        # Safe access to account details
        account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number", "Not available")
        bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Monnify MFB")
        display_name = user_profile.get('full_name') if user_profile else virtual_account.get("accountName", "Not available")
        
        # Get recent transactions from Supabase
        recent_transactions = []
        try:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # Get recent bank transactions
            transactions_result = supabase.table("bank_transactions")\
                .select("*")\
                .eq("user_id", chat_id)\
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
        
        # Build response
        response = f"""
💳 **Your Account Summary**

👤 **Account Name:** {display_name}
📱 **Account Number:** {account_number}
🏦 **Bank:** {bank_name}
💰 **Available Balance:** ₦{current_balance:,.2f}

📊 **Recent Activity:**
"""
        
        if recent_transactions:
            response += "\n".join(recent_transactions)
        else:
            response += "• No recent transactions"
        
        response += "\n\nNeed to send money, buy airtime, or check anything else?"
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling balance inquiry: {e}")
        return None

# Flask Routes
@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/webhook", methods=["POST"])
async def webhook_incoming():
    """Handle incoming Telegram messages with conversation memory"""
    try:
        data = request.get_json()
        
        if not data or "message" not in data:
            return jsonify({"error": "Invalid update payload", "response": None}), 400
        
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
            success, response = process_voice(file_id)
            
            if success:
                # Process the transcribed text as a regular message
                user_message = response
                ai_response = await handle_message(chat_id, user_message, user_data)
                send_reply(chat_id, ai_response)
            else:                send_reply(chat_id, response)
        
        # Handle text messages
        elif "text" in message_data:
            user_message = message_data.get("text", "").strip()
            
            if not user_message:
                return jsonify({"success": True}), 200
              # Check if user exists and force onboarding for new users
            if not user_exists:
                # Force onboarding for new users with inline keyboard
                onboarding_message = (
                    f"👋 *Welcome to Sofi AI!* I'm your personal financial assistant.\n\n"
                    f"🔐 *To get started, I need to create your secure virtual account:*\n\n"
                    f"📋 *You'll need:*\n"
                    f"• Your BVN (Bank Verification Number)\n"
                    f"• Phone number\n"
                    f"• Basic personal details\n\n"
                    f"✅ *Once done, you can:*\n"
                    f"• Send money to any bank instantly\n"
                    f"• Buy airtime & data at best rates\n"
                    f"• Receive money from anywhere\n"
                    f"• Chat with me for financial advice\n\n"
                    f"🚀 *Click the button below to start your registration!*"
                )
                
                # Create inline keyboard with registration button
                inline_keyboard = {
                    "inline_keyboard": [[
                        {
                            "text": "🚀 Complete Registration",
                            "url": "https://sofi-ai-trio.onrender.com/onboarding"
                        }
                    ]]
                }
                
                send_reply(chat_id, onboarding_message, inline_keyboard)
                return jsonify({"success": True}), 200
            
            # Handle existing user messages
            try:
                # Check if user has virtual account
                virtual_account = await check_virtual_account(chat_id)
                
                # Generate AI reply with conversation context
                ai_response = await handle_message(chat_id, user_message, user_resp.data[0] if user_resp.data else None, virtual_account)
                send_reply(chat_id, ai_response)
            except Exception as e:
                logger.error(f"Error in AI reply: {str(e)}")
                send_reply(chat_id, "Sorry, I encountered an error processing your request. Please try again.")

        return jsonify({"success": True}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error", "response": None}), 500

@app.route("/monnify_webhook", methods=["POST"])
def handle_monnify_webhook_route():
    """Handle Monnify webhook notifications for payments and transfers"""
    try:
        data = request.get_json()
        
        # Get signature from headers if available
        signature = request.headers.get('Monnify-Signature')
        
        # Log incoming webhook for debugging
        logger.info(f"Monnify webhook received: {data}")
        
        # Process the webhook using imported handler
        result = handle_monnify_webhook(data, signature)
        
        if result.get('success'):
            return jsonify({"status": "success", "message": "Webhook processed"}), 200
        else:
            return jsonify({"status": "error", "message": result.get('error', 'Unknown error')}), 400
            
    except Exception as e:
        logger.error(f"Error processing Monnify webhook: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

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

@app.route("/onboarding")
def onboarding_page():
    """Serve onboarding page"""
    return render_template("onboarding.html")

@app.route("/verify-pin")
def pin_verification_page():
    """Serve secure PIN verification page"""
    transaction_id = request.args.get('txn_id')
    
    if not transaction_id:
        return "Invalid transaction", 400
      # Get transaction data
    from utils.secure_pin_verification import secure_pin_verification
    
    transaction = secure_pin_verification.get_pending_transaction(transaction_id)
    if not transaction:
        return "Transaction expired or invalid", 400
    
    transfer_data = transaction['transfer_data']
    
    return render_template("secure_pin_verification.html", 
                         transaction_id=transaction_id,
                         amount=f"{transfer_data['amount']:,.2f}",
                         recipient_name=transfer_data['recipient_name'],
                         bank_name=transfer_data['bank'],
                         account_number=transfer_data['account_number'])

@app.route("/api/verify-pin", methods=["POST"])
async def verify_pin_api():
    """API endpoint for PIN verification"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        pin = data.get('pin')
        
        if not transaction_id or not pin:
            return jsonify({
                'success': False,
                'error': 'Missing transaction ID or PIN'
            }), 400
        
        from utils.secure_pin_verification import secure_pin_verification
        
        result = await secure_pin_verification.verify_pin_and_process_transfer(
            transaction_id, pin
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
