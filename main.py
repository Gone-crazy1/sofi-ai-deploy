from flask import Flask, request, jsonify, url_for, render_template
from flask_cors import CORS
import os, requests, hashlib, logging
from datetime import datetime
from supabase import create_client
import openai
from dotenv import load_dotenv
import random
from PIL import Image
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from utils.memory import save_memory, list_memories

# Load environment variables from .env file
load_dotenv()

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
SUPABASE_URL = "https://qbxherpwkxckwlkwjhpm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFieGhlcnB3a3hja3dsa3dqaHBtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNDQ1MzYsImV4cCI6MjA2NDcyMDUzNn0._YOyoxWVoaOD7VMl_OwP1t-duw6s4qWmtNZm2rrcskM"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NELLOBYTES_USERID = os.getenv("NELLOBYTES_USERID")
NELLOBYTES_APIKEY = os.getenv("NELLOBYTES_APIKEY")
MONNIFY_BASE_URL = os.getenv("MONNIFY_BASE_URL")
MONNIFY_API_KEY = os.getenv("MONNIFY_API_KEY")
MONNIFY_SECRET_KEY = os.getenv("MONNIFY_SECRET_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)  # CSRF Disabled globally
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure your .env has this key

NELLOBYTES_USERID = os.getenv("NELLOBYTES_USERID")
NELLOBYTES_APIKEY = os.getenv("NELLOBYTES_APIKEY")

# Set the path to the ffmpeg executable for pydub
AudioSegment.converter = which("ffmpeg")

def send_reply(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})

def detect_intent(message):
    """Refined intent detector using OpenAI API with gpt-3.5-turbo"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intent classification assistant. Respond with only one of the following intents: 'greeting', 'inquiry', or 'unknown'."},
                {"role": "user", "content": f"Classify the intent of this message: '{message}'"}
            ],
            max_tokens=10
        )
        with open("api_logs.txt", "a") as log_file:
            log_file.write(f"Message: {message}\nResponse: {response}\n\n")
        intent = response['choices'][0]['message']['content'].strip().lower()
        intent = intent.strip("'")  # Remove extra quotes if present
        if intent not in ["greeting", "inquiry", "unknown"]:
            intent = "unknown"
        return {"intent": intent}
    except Exception as e:
        logger.error(f"Error detecting intent: {e}")
        return {"intent": "unknown"}

def create_virtual_account(first_name, last_name, bvn):
    """Create a virtual account using Monnify API."""
    monnify_base_url = os.getenv("MONNIFY_BASE_URL")
    monnify_api_key = os.getenv("MONNIFY_API_KEY")
    monnify_secret_key = os.getenv("MONNIFY_SECRET_KEY")

    # Generate authentication token
    auth_url = f"{monnify_base_url}/api/v1/auth/login"
    auth_response = requests.post(auth_url, auth=(monnify_api_key, monnify_secret_key))

    if auth_response.status_code != 200:
        logger.error("Failed to authenticate with Monnify API.")
        return {}

    auth_token = auth_response.json().get("responseBody", {}).get("accessToken")
    if not auth_token:
        logger.error("Authentication token not found in Monnify response.")
        return {}

    # Create virtual account
    create_account_url = f"{monnify_base_url}/api/v2/bank-transfer/reserved-accounts"
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "accountReference": f"{first_name}_{last_name}_{random.randint(1000, 9999)}",
        "accountName": f"{first_name} {last_name}",
        "currencyCode": "NGN",
        "customerEmail": f"{first_name.lower()}.{last_name.lower()}@example.com",
        "bvn": bvn,
        "customerName": f"{first_name} {last_name}",
        "getAllAvailableBanks": False
    }

    logger.info(f"Payload sent to Monnify: {payload}")  # Log the payload being sent

    response = requests.post(create_account_url, json=payload, headers=headers)

    if response.status_code != 201:
        logger.error(f"Failed to create virtual account: {response.text}")
        return {}

    account_data = response.json().get("responseBody", {})
    return {
        "accountNumber": account_data.get("accountNumber"),
        "accountName": account_data.get("accountName"),
        "bankName": account_data.get("bankName"),
        "accountReference": account_data.get("accountReference")
    }
# Enhanced response mapping with varied responses
INTENT_RESPONSES = {
    "greeting": [
        "Hello! How can I assist you today?",
        "Hi there! What can I do for you?",
        "Hey! Need help with something?"
    ],
    "inquiry": [
        "I'm just a bot, but I'm here to help! What can I do for you?",
        "I'm here to assist you. Feel free to ask anything!",
        "How can I help you today?"
    ],
    "unknown": [
        "I'm sorry, I didn't quite understand that. Could you rephrase?",
        "Hmm, I couldn't catch that. Could you try again?",
        "I'm not sure I understand. Could you clarify?"
    ]
}

def generate_ai_reply(message):
    system_prompt = """
    You are Sofi AI — a friendly, smart, and helpful Nigerian virtual assistant.
    You help users send and receive money, buy airtime/data, check balance, view transaction history, and do daily banking tasks easily.
    You reply in a warm, conversational way like a real human.
    If the user asks non-finance stuff, you politely help or reply as a general assistant.
    If the user asks about you, introduce yourself as Sofi AI, explain your capabilities, and assure them you are here to assist.
    You also have knowledge about Monnify, PayPal, and other financial platforms. For example:
    - Monnify is a payment gateway that enables businesses to accept payments securely and efficiently.
    - PayPal is an online payment system for sending and receiving money electronically.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        ai_reply = response['choices'][0]['message']['content'].strip()
        return ai_reply
    except Exception as e:
        return "Sorry, I'm having trouble thinking right now. Please try again later."

def download_file(file_id):
    # Get file path
    file_info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    file_info = requests.get(file_info_url).json()
    file_path = file_info["result"]["file_path"]

    # Download file
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    file_data = requests.get(file_url).content
    return file_data

def process_photo(file_id):
    try:
        file_data = download_file(file_id)
        image = Image.open(BytesIO(file_data))
        # Example: Resize image
        image = image.resize((200, 200))
        processed_file = "processed_image.jpg"
        image.save(processed_file)
        
        # Cleanup after processing
        if os.path.exists(processed_file):
            os.remove(processed_file)
            
        return True
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        return False

def process_voice(file_id):
    try:
        file_data = download_file(file_id)
        voice_ogg = "voice.ogg"
        voice_mp3 = "voice.mp3"
        
        with open(voice_ogg, "wb") as f:
            f.write(file_data)
            
        # Convert OGG to MP3 using pydub
        audio = AudioSegment.from_file(voice_ogg, format="ogg")
        audio.export(voice_mp3, format="mp3")
        
        # Cleanup after processing
        for file in [voice_ogg, voice_mp3]:
            if os.path.exists(file):
                os.remove(file)
                
        return True
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        return False

@app.route("/webhook_incoming", methods=["POST"])
def handle_incoming_message():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid update payload", "response": None}), 400

        chat_id = data["message"]["chat"]["id"]
        telegram_username = data["message"]["chat"].get("username", "there")

        if "photo" in data["message"]:
            photo = data["message"]["photo"][-1]
            if process_photo(photo["file_id"]):
                ai_reply = generate_ai_reply(f"Thanks for sharing the image! I've processed it successfully.")
            else:
                ai_reply = "I'm sorry, I had trouble processing that image. Could you try sending it again or describe what you wanted to show me?"
            send_reply(chat_id, ai_reply)
            return jsonify({"status": "ok", "response": ai_reply})

        if "voice" in data["message"]:
            voice = data["message"]["voice"]
            if process_voice(voice["file_id"]):
                ai_reply = generate_ai_reply(f"Thanks for the voice message! I've processed it successfully.")
            else:
                ai_reply = "I'm sorry, I had trouble processing that voice message. Could you try sending it again or type your message instead?"
            send_reply(chat_id, ai_reply)
            return jsonify({"status": "ok", "response": ai_reply})

        user_message = data["message"].get("text", "").strip()
        if not user_message:
            send_reply(chat_id, "Please send a valid message!")
            return jsonify({"error": "No message provided"}), 400

        # Generate AI reply for text messages
        ai_reply = generate_ai_reply(user_message)
        send_reply(chat_id, ai_reply)
        return jsonify({"status": "ok", "response": ai_reply})
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

def handle_telegram_update(update):
    if not update or "message" not in update:
        return
    chat_id = update["message"]["chat"]["id"]
    user_message = update["message"].get("text", "").strip()
    telegram_username = update["message"]["chat"].get("username", "there")

    user_resp = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
    if not user_resp.data:
        welcome_message = (
            f"Hello {telegram_username}!\n\n"
            "I'm Sofi — your Personal Account Manager AI from Sofi Technologies.\n\n"
            "I can help you:\n"
            "• Send and receive money instantly\n"
            "• Buy airtime and data at the best rates\n"
            "• Analyze and manage your spending\n"
            "• Schedule bills and transfers\n"
            "• Fund betting wallets ⚽️\n"
            "• Earn cashback and bonuses\n\n"
            "Quick tip: Lock your Telegram to keep your account safe.\n\n"
            "Let’s begin your onboarding 👉\n[Start Onboarding](https://sofi-ai-trio.onrender.com/onboarding)"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "Complete Onboarding", "url": "https://t.me/getsofi_bot"}]
            ]
        }
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": welcome_message, "reply_markup": keyboard}
        )
        return

    ai_response = detect_intent(user_message)
    if isinstance(ai_response, str) and ai_response.startswith("Error"):
        send_reply(chat_id, "Sorry, I couldn't process that. Please try again or type /start_onboarding to begin.")
    else:
        send_reply(chat_id, f"Here's what I understood: {ai_response}")

@app.route('/transfer', methods=['POST'])
def transfer_money():
    data = request.json
    sender_name = data.get('sender_name')
    amount = data.get('amount')
    recipient_name = data.get('recipient_name')
    recipient_account = data.get('recipient_account')
    recipient_bank = data.get('recipient_bank')

    monnify_base_url = os.getenv("MONNIFY_BASE_URL")
    monnify_api_key = os.getenv("MONNIFY_API_KEY")
    monnify_secret_key = os.getenv("MONNIFY_SECRET_KEY")

    # Generate authentication token
    auth_url = f"{monnify_base_url}/api/v1/auth/login"
    auth_response = requests.post(auth_url, auth=(monnify_api_key, monnify_secret_key))

    if auth_response.status_code != 200:
        logger.error("Failed to authenticate with Monnify API.")
        return jsonify({"status": "error", "message": "Authentication failed."}), 500

    auth_token = auth_response.json().get("responseBody", {}).get("accessToken")
    if not auth_token:
        logger.error("Authentication token not found in Monnify response.")
        return jsonify({"status": "error", "message": "Authentication token missing."}), 500

    # Perform transfer
    transfer_url = f"{monnify_base_url}/api/v2/disbursements/single"
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "amount": amount,
        "reference": f"transfer_{random.randint(1000, 9999)}",
        "narration": f"Transfer to {recipient_name}",
        "destinationBankCode": recipient_bank,
        "destinationAccountNumber": recipient_account,
        "currency": "NGN",
        "sourceAccountNumber": "1234567890"  # Replace with actual source account
    }

    logger.info(f"Payload sent to Monnify: {payload}")  # Log the payload being sent

    response = requests.post(transfer_url, json=payload, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to complete transfer: {response.text}")
        return jsonify({"status": "error", "message": "Transfer failed."}), 500

    logger.info(f"Transfer successful: {response.json()}")
    return jsonify({"status": "success", "message": "Transfer completed successfully."})

@app.route('/buy_airtime', methods=['POST'])
def buy_airtime():
    data = request.json
    mobile_network = data.get('MobileNetwork')
    amount = data.get('Amount')
    mobile_number = data.get('MobileNumber')
    request_id = data.get('RequestID')
    callback_url = data.get('CallBackURL')

    if not all([mobile_network, amount, mobile_number, request_id, callback_url]):
        return jsonify({"error": "Missing required parameters"}), 400

    url = f"https://www.nellobytesystems.com/APIAirtimeV1.asp?UserID={NELLOBYTES_USERID}&APIKey={NELLOBYTES_APIKEY}&MobileNetwork={mobile_network}&Amount={amount}&MobileNumber={mobile_number}&RequestID={request_id}&CallBackURL={callback_url}"

    response = requests.get(url)
    return jsonify(response.json()), response.status_code

@app.route('/buy_databundle', methods=['POST'])
def buy_databundle():
    data = request.json
    mobile_network = data.get('MobileNetwork')
    data_plan = data.get('DataPlan')
    mobile_number = data.get('MobileNumber')
    request_id = data.get('RequestID')
    callback_url = data.get('CallBackURL')

    if not all([mobile_network, data_plan, mobile_number, request_id, callback_url]):
        return jsonify({"error": "Missing required parameters"}), 400

    url = f"https://www.nellobytesystems.com/APIDatabundleV1.asp?UserID={NELLOBYTES_USERID}&APIKey={NELLOBYTES_APIKEY}&MobileNetwork={mobile_network}&DataPlan={data_plan}&MobileNumber={mobile_number}&RequestID={request_id}&CallBackURL={callback_url}"

    response = requests.get(url)
    return jsonify(response.json()), response.status_code

@app.route('/query_transaction', methods=['POST'])
def query_transaction():
    data = request.json
    order_id = data.get('OrderID')
    request_id = data.get('RequestID')

    if not (order_id or request_id):
        return jsonify({"error": "Either OrderID or RequestID is required"}), 400

    if order_id:
        url = f"https://www.nellobytesystems.com/APIQueryV1.asp?UserID={NELLOBYTES_USERID}&APIKey={NELLOBYTES_APIKEY}&OrderID={order_id}"
    else:
        url = f"https://www.nellobytesystems.com/APIQueryV1.asp?UserID={NELLOBYTES_USERID}&APIKey={NELLOBYTES_APIKEY}&RequestID={request_id}"

    response = requests.get(url)
    return jsonify(response.json()), response.status_code

@app.before_request
def log_request_info():
    logger.info(f"Headers: {request.headers}")
    logger.info(f"Body: {request.get_data()}")

# Clear memory logic for webhook
@app.route("/clear_memory", methods=["POST"])
def clear_memory():
    chat_id = request.json.get("chat_id")
    if not chat_id:
        return jsonify({"error": "chat_id is required"}), 400

    # Clear memory for the specific chat_id using utils.memory
    save_memory(chat_id, None)  # Assuming None clears memory
    return jsonify({"status": "success", "message": f"Memory cleared for chat_id: {chat_id}"})

if __name__ == "__main__":
    app.run(debug=True)
