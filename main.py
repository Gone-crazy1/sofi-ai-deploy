from flask import Flask, request, jsonify, url_for, render_template
from flask_cors import CORS
import os, requests, hashlib, logging, json, asyncio, tempfile, re
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

# Load environment variables from .env file
load_dotenv()

# Import admin handler AFTER environment loading
from utils.admin_command_handler import AdminCommandHandler
admin_handler = AdminCommandHandler()

# Import user onboarding system
from utils.user_onboarding import SofiUserOnboarding
onboarding_service = SofiUserOnboarding()

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

# Initialize AI client with API key - Powered by Pip install AI Technologies
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
                
                # Get user's full name from Supabase instead of truncated bank name
                from utils.user_onboarding import onboarding_service
                user_profile = await onboarding_service.get_user_profile(str(chat_id))
                
                # Safe access to account details with fallbacks
                account_number = virtual_account.get("accountNumber") or virtual_account.get("account_number", "Not available")
                bank_name = virtual_account.get("bankName") or virtual_account.get("bank_name", "Not available")
                
                # Use full name from Supabase, not truncated bank account name
                display_name = user_profile.get('full_name') if user_profile else virtual_account.get("accountName", "Not available")
                
                reply = (
                    f"✅ You have an account:\n"
                    f"🏦 {account_number} ({bank_name})\n"
                    f"👤 {display_name}\n\n"
                    f"What do you need?"
                )
            else:
                reply = (
                    "Create account: https://pipinstallsofi.com/onboard\n"
                    "Need: BVN + phone number\n"
                    "Get instant virtual account for transfers & airtime!"
                )
            save_chat_message(chat_id, "assistant", reply)
            return reply

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
                for func_name, func_result in function_data.items():
                    if isinstance(func_result, dict) and func_result.get("requires_pin"):
                        logger.info(f"🔐 Function {func_name} requires PIN entry - sending inline keyboard")
                        
                        # Check if it's the new inline keyboard system
                        if func_result.get("show_inline_keyboard"):
                            from utils.inline_pin_keyboard import inline_pin_manager
                            
                            # Send the PIN entry message with inline keyboard
                            pin_message = func_result.get("message", "Please enter your PIN")
                            keyboard = func_result.get("keyboard", {})
                            
                            # Send message with inline keyboard
                            message_response = send_reply(chat_id, pin_message, keyboard)
                            
                            # Store the message ID for editing later
                            if message_response and message_response.get("result"):
                                message_id = message_response["result"]["message_id"]
                                inline_pin_manager.set_message_id(chat_id, message_id)
                            
                            return "PIN keyboard sent"  # Prevent further processing
                        
                        # Legacy PIN handling (fallback)
                        else:
                            from utils.pin_entry_system import create_pin_entry_keyboard
                            
                            pin_message = f"""🔐 *Please enter your PIN*

To complete your transaction

*Click the button below to enter your PIN securely:*"""
                            pin_keyboard = create_pin_entry_keyboard()
                            
                            # Send PIN keyboard immediately
                            send_reply(chat_id, pin_message, pin_keyboard)
                            return "PIN keyboard sent"  # Prevent further processing
                    
                    # Check if any function returned a successful transfer with auto receipt
                    if isinstance(func_result, dict) and func_result.get("auto_send_receipt") and func_result.get("success"):
                        logger.info(f"📧 Function {func_name} completed transfer - auto-sending receipt")
                        
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
                "https://pipinstallsofi.com/onboard\n\n"
                "Once you have an account, I can show you your balance and transaction history!"
            )
        
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

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/webhook", methods=["POST"])
async def webhook_incoming():
    """Handle incoming Telegram messages and callback queries"""
    try:
        data = request.get_json()
        
        if not data:
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
                    # Give a brief helpful response instead of onboarding
                    brief_response = (
                        "Ready to help! Once you complete your registration at "
                        "https://pipinstallsofi.com/onboard, you'll be all set. "
                        "Need help with anything else?"
                    )
                    send_reply(chat_id, brief_response)
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
                    # For very brief messages, give a gentle nudge
                    brief_nudge = (
                        "Hi! I'm Sofi AI. To use my services, please register at "
                        "https://pipinstallsofi.com/onboard"
                    )
                    send_reply(chat_id, brief_nudge)
                    return jsonify({"success": True}), 200
            
            # Handle existing user messages
            try:
                # Check if user has virtual account
                virtual_account = await check_virtual_account(chat_id)
                
                # Generate AI reply with conversation context
                ai_response = await handle_message(chat_id, user_message, user_resp.data[0] if user_resp.data else None, virtual_account)
                
                # Check if response is a special PIN entry request
                if isinstance(ai_response, dict) and ai_response.get("requires_pin"):
                    # This is a PIN entry request - send PIN keyboard
                    from utils.pin_entry_system import create_pin_entry_keyboard
                    
                    # Get transfer details from the response
                    transfer_data = ai_response.get("transfer_data", {})
                    amount = transfer_data.get("amount", 0)
                    verified_name = transfer_data.get("recipient_name", "recipient")
                    
                    pin_message = f"""🔐 *Please enter your PIN*

To complete transfer of ₦{amount:,.2f} to {verified_name}

*Click the button below to enter your PIN securely:*"""
                    pin_keyboard = create_pin_entry_keyboard()
                    
                    send_reply(chat_id, pin_message, pin_keyboard)
                else:
                    # Regular response
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
        data = request.get_json()
        
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

@app.route("/onboard")
def onboard_page():
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
        
        # Since onboarding is async, we need to run it in an event loop
        import asyncio
        
        # Create new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the onboarding process
        result = loop.run_until_complete(onboarding_service.create_new_user(user_data))
        
        if result.get('success'):
            logger.info(f"Successfully onboarded web user: {user_data.get('full_name')}")
            
            # Send account details to user via Telegram if telegram_id is provided
            telegram_id = user_data.get('telegram_id')
            if telegram_id and not telegram_id.startswith('web_user_'):
                # This is a real Telegram user, send them their account details
                asyncio.run(send_account_details_to_user(telegram_id, result))
            
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
            f"\"Check balance\" or \"Send ₦500\""
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

@app.route("/onboard", methods=["GET"])
def serve_onboarding_form():
    """Serve the web onboarding form"""
    try:
        with open('web_onboarding.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content, 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({
            'error': 'Onboarding form not found'
        }), 404
    except Exception as e:
        logger.error(f"Error serving onboarding form: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

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
        
        # Handle inline PIN keyboard callbacks
        if callback_data.startswith("pin_"):
            try:
                from utils.inline_pin_keyboard import handle_pin_button, inline_pin_manager
                
                # Process the PIN button press
                result = handle_pin_button(chat_id, callback_data)
                
                if result["success"]:
                    if result.get("action") == "submit":
                        # PIN submitted - execute transfer
                        await answer_callback_query(query_id, "🔐 Processing transfer...")
                        
                        pin = result["pin"]
                        transfer_data = result["transfer_data"]
                        
                        # STEP 1: Remove the inline keyboard immediately
                        remove_keyboard_message = f"""💸 You're about to send ₦{transfer_data['amount']:,.0f} to:
👤 Name: *{transfer_data['recipient_name']}*
🏦 Bank: {transfer_data['bank_name']}
🔢 Account: {transfer_data['account_number']}

🔐 PIN submitted! Processing transfer..."""
                        
                        # Remove keyboard by editing message without reply_markup
                        edit_message(chat_id, message_id, remove_keyboard_message)
                        
                        # STEP 2: Execute the transfer
                        from functions.transfer_functions import send_money
                        transfer_result = await send_money(
                            chat_id=chat_id,
                            amount=transfer_data["amount"],
                            account_number=transfer_data["account_number"],
                            bank_name=transfer_data["bank_name"],
                            recipient_name=transfer_data["recipient_name"],
                            pin=pin,
                            narration=transfer_data.get("narration", "Sofi AI Transfer")
                        )
                        
                        # End the PIN session
                        inline_pin_manager.end_session(chat_id)
                        
                        # STEP 3: Update the message with final result and send receipt
                        if transfer_result and transfer_result.get("success"):
                            # Show success message with real receiver name
                            success_message = f"""✅ Transfer Successful!

💰 ₦{transfer_data['amount']:,.0f} sent to:
👤 *{transfer_data['recipient_name']}*
🏦 {transfer_data['bank_name']}
🔢 {transfer_data['account_number']}

🧾 Receipt is being prepared..."""
                            
                            edit_message(chat_id, message_id, success_message)
                            
                            # Send receipt as a separate message
                            receipt_data = transfer_result.get("receipt_data", {})
                            if receipt_data:
                                await send_beautiful_receipt(chat_id, receipt_data, transfer_result)
                            
                            # Send a clean summary message
                            summary_message = f"💸 ₦{transfer_data['amount']:,.0f} sent to {transfer_data['bank_name']} ({transfer_data['account_number']}) {transfer_data['recipient_name']} ✅"
                            send_reply(chat_id, summary_message)
                            
                        else:
                            # Show error message
                            error_message = f"""❌ Transfer Failed

{transfer_result.get('message', 'Transfer could not be completed. Please try again.')}"""
                            edit_message(chat_id, message_id, error_message)
                            
                    elif result.get("action") == "cancel":
                        # PIN cancelled - remove keyboard
                        await answer_callback_query(query_id, "❌ Transfer cancelled")
                        
                        # Remove keyboard and show cancellation message
                        cancel_message = "❌ Transfer cancelled by user.\n\nYou can start a new transfer anytime by sending me transfer details."
                        edit_message(chat_id, message_id, cancel_message)
                        
                    else:
                        # PIN digit added or cleared
                        await answer_callback_query(query_id, "")
                        
                        # Update the PIN display
                        transfer_data = inline_pin_manager.get_transfer_data(chat_id)
                        if transfer_data:
                            pin_length = result.get("length", 0)
                            updated_message = inline_pin_manager.create_pin_progress_message(transfer_data, pin_length)
                            keyboard = inline_pin_manager.create_pin_keyboard()
                            
                            # Update the message with new PIN display
                            edit_message(chat_id, message_id, updated_message, keyboard)
                else:
                    # Error handling PIN button
                    await answer_callback_query(query_id, f"❌ {result.get('error', 'PIN entry error')}")
                    
            except Exception as e:
                logger.error(f"❌ Error handling PIN callback: {str(e)}")
                await answer_callback_query(query_id, "❌ PIN entry failed")
                
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
        from beautiful_receipt_generator import generate_pos_style_receipt
        
        # Extract receipt data
        sender_name = receipt_data.get('sender_name', 'Sofi User')
        amount = receipt_data.get('amount', 0)
        recipient_name = receipt_data.get('recipient_name', 'Unknown')
        recipient_account = receipt_data.get('recipient_account', 'Unknown')
        recipient_bank = receipt_data.get('recipient_bank', 'Unknown')
        balance = receipt_data.get('new_balance', 0)
        transaction_id = receipt_data.get('transaction_id', 'N/A')
        
        # Generate the receipt
        receipt_text = generate_pos_style_receipt(
            sender_name, amount, recipient_name, 
            recipient_account, recipient_bank, balance, transaction_id
        )
        
        # Send the receipt
        send_reply(chat_id, f"🧾 **Your Transfer Receipt**\n\n```\n{receipt_text}\n```")
        
        logger.info(f"📧 Beautiful receipt sent to {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending beautiful receipt: {str(e)}")
        # Fallback to simple message
        send_reply(chat_id, f"✅ Transfer completed successfully! Transaction ID: {receipt_data.get('transaction_id', 'N/A')}")
