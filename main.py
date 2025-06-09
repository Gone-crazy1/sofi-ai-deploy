from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
import os, requests, hashlib, logging
from supabase import create_client
import openai
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # CSRF Disabled globally
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

user_state = {}
onboarding_state = {}

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure your .env has this key

def send_reply(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})

def detect_intent(message):
    """Refined intent detector using OpenAI API with gpt-3.5-turbo"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intent classification assistant. Respond with only the intent label, such as 'greeting', 'inquiry', or 'unknown'."},
                {"role": "user", "content": f"Classify the intent of this message: '{message}'"}
            ],
            max_tokens=10
        )
        intent = response['choices'][0]['message']['content'].strip().lower()
        return intent
    except Exception as e:
        logger.error(f"Error detecting intent: {e}")
        return "unknown"

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

@app.route("/webhook_incoming", methods=["POST"])
def handle_incoming_message():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "").strip()

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Use GPT AI for all replies
        ai_reply = generate_ai_reply(user_message)
        send_reply(chat_id, ai_reply)

        return jsonify({"response": ai_reply})

def handle_telegram_update(update):
    if not update or "message" not in update:
        return
    chat_id = update["message"]["chat"]["id"]
    user_message = update["message"].get("text", "").strip()
    telegram_username = update["message"]["chat"].get("username", "there")

    user_resp = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
    if not user_resp.data:
        onboarding_url = "https://sofi-ai-trio.onrender.com/onboarding_form.html"
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
            f"Let’s begin your onboarding 👉\n[Start Onboarding]({onboarding_url})"
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

    if chat_id in onboarding_state:
        user_data = onboarding_state[chat_id]
        if "first_name" not in user_data:
            user_data["first_name"] = user_message
            send_reply(chat_id, "Great! Now, please tell me your last name.")
        elif "last_name" not in user_data:
            user_data["last_name"] = user_message
            send_reply(chat_id, "Got it! What's your BVN?")
        elif "bvn" not in user_data:
            user_data["bvn"] = user_message
            send_reply(chat_id, "Almost done! Choose a transaction PIN.")
        elif "pin" not in user_data:
            user_data["pin"] = user_message
            try:
                result = create_virtual_account(
                    user_data["first_name"], user_data["last_name"], user_data["bvn"]
                )
                acct_no = result.get("accountNumber", "")
                bank_name = result.get("bankName", "")
                if acct_no and bank_name:
                    supabase.table("users").upsert({
                        "telegram_chat_id": chat_id,
                        "first_name": user_data["first_name"],
                        "last_name": user_data["last_name"],
                        "bvn": user_data["bvn"],
                        "pin": user_data["pin"],
                        "account_number": acct_no,
                        "bank_name": bank_name,
                        "address": user_data.get("address", ""),
                        "city": user_data.get("city", ""),
                        "state": user_data.get("state", "")
                    }, on_conflict=["telegram_chat_id"]).execute()
                    send_reply(
                        chat_id,
                        f"Success! Your account has been created.\n\nAccount Number: {acct_no}\nBank Name: {bank_name}"
                    )
                else:
                    send_reply(chat_id, "Failed to create your account. Please try again later.")
            except Exception:
                send_reply(chat_id, "Something went wrong during onboarding. Please try again.")
            onboarding_state.pop(chat_id, None)
        return

    if user_message.lower() == "/start_onboarding":
        onboarding_state[chat_id] = {}
        send_reply(chat_id, "Welcome to Sofi AI! Let's get started. What's your first name?")
        return

    if "my name is" in user_message.lower():
        # Extract and save the name
        user_name = user_message.split("my name is")[-1].strip().capitalize()
        save_user_memory(chat_id, "name", user_name)
        send_reply(chat_id, f"Nice to meet you, {user_name}!")
        return

    if "what's my name" in user_message.lower() or "what is my name" in user_message.lower():
        name = get_user_memory(chat_id, "name")
        if name:
            send_reply(chat_id, f"Your name is {name}!")
        else:
            send_reply(chat_id, "I don't know your name yet. What's your name?")
        return

    if user_message.lower().startswith("remember"):
        # Example: "Remember my API key is sk-12345"
        key_value = user_message.replace("remember", "").strip()
        if "is" in key_value:
            parts = key_value.split("is")
            key = parts[0].strip()
            value = parts[1].strip()
            save_user_memory(chat_id, key, value)
            send_reply(chat_id, f"Got it! I'll remember that your {key} is {value}.")
        else:
            send_reply(chat_id, "Please tell me what to remember in the format: 'Remember [thing] is [value]'.")
        return

    if user_message.lower().startswith("what is"):
        # Example: "What is my API key"
        key = user_message.replace("what is", "").replace("my", "").strip()
        value = get_user_memory(chat_id, key)
        if value:
            send_reply(chat_id, f"Your {key} is {value}.")
        else:
            send_reply(chat_id, f"I don't remember your {key}.")
        return

    ai_response = detect_intent(user_message)
    if isinstance(ai_response, str) and ai_response.startswith("Error"):
        send_reply(chat_id, "Sorry, I couldn't process that. Please try again or type /start_onboarding to begin.")
    else:
        send_reply(chat_id, f"Here's what I understood: {ai_response}")

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json or {}
    chat_id = data.get("chat_id")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    bvn = data.get("bvn")
    pin = data.get("pin")

    if not all([chat_id, first_name, last_name, address, city, state, bvn, pin]):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    try:
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        result = create_virtual_account(first_name, last_name, bvn)
        acct_no = result.get("accountNumber", "")
        acct_name = result.get("accountName", "")
        bank_name = result.get("bankName", "")
        account_reference = result.get("accountReference", "")

        supabase.table("users").insert({
            "telegram_chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "city": city,
            "state": state,
            "bvn": bvn,
            "pin": hashed_pin,
            "account_number": acct_no,
            "account_name": acct_name,
            "bank_name": bank_name,
            "account_reference": account_reference
        }).execute()

        return jsonify({
            "status": "success",
            "message": "Onboarding successful!",
            "account_number": acct_no,
            "bank_name": bank_name
        }), 201
    except Exception:
        return jsonify({"status": "error", "message": "Onboarding failed. Please try again later."}), 500

@app.route('/onboard', methods=['POST'])
def onboard():
    data = request.form
    chat_id = data.get("chat_id")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    address = data.get("address")
    city = data.get("city")
    state = data.get("state")
    bvn = data.get("bvn")
    pin = data.get("pin")

    if not all([chat_id, first_name, last_name, address, city, state, bvn, pin]):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    try:
        result = create_virtual_account(first_name, last_name, bvn)
        acct_no = result.get("accountNumber", "")
        acct_name = result.get("accountName", "")
        bank_name = result.get("bankName", "")
        account_reference = result.get("accountReference", "")

        if not all([acct_no, acct_name, bank_name]):
            return jsonify({"status": "error", "message": "Failed to create virtual account."}), 500

        supabase.table("users").insert({
            "telegram_chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "city": city,
            "state": state,
            "bvn": bvn,
            "pin": pin,
            "account_number": acct_no,
            "account_name": acct_name,
            "bank_name": bank_name,
            "account_reference": account_reference
        }).execute()

        return jsonify({
            "status": "success",
            "message": "Onboarding successful!",
            "account_number": acct_no,
            "bank_name": bank_name
        }), 201
    except Exception as e:
        logger.error(f"Error during onboarding: {e}")
        return jsonify({"status": "error", "message": "Onboarding failed. Please try again later."}), 500

def generate_pos_style_receipt(sender_name, amount, recipient_name, recipient_account, recipient_bank, balance, transaction_id):
    return f"""
    Transaction Receipt
    --------------------
    Sender: {sender_name}
    Amount: ₦{amount:.2f}
    Recipient: {recipient_name}
    Account: {recipient_account}
    Bank: {recipient_bank}
    Balance: ₦{balance:.2f}
    Transaction ID: {transaction_id}
    --------------------
    Thank you for using Sofi AI!
    """

def send_money(chat_id, amount, recipient_name, account_number, bank_name):
    """Simulate sending money."""
    # Log the transaction (mocked for now)
    logger.info(f"Sending ₦{amount} to {recipient_name} at {bank_name}, {account_number}.")
    return {"status": "success", "message": "Transfer completed successfully."}

def save_user_memory(chat_id, key, value):
    try:
        supabase.table("memory").insert({
            "telegram_chat_id": str(chat_id),
            "key": key,
            "value": value
        }).execute()
        logger.info(f"Memory saved for {chat_id}: {key} = {value}")
    except Exception as e:
        logger.error(f"Error saving memory: {e}")
        logger.debug(f"Failed data: chat_id={chat_id}, key={key}, value={value}")

def get_user_memory(chat_id, key):
    try:
        result = supabase.table("memory").select("value").eq("telegram_chat_id", str(chat_id)).eq("key", key).execute()
        if result.data and len(result.data) > 0:
            logger.info(f"Memory retrieved for {chat_id}: {key} = {result.data[0]['value']}")
            return result.data[0]["value"]
        logger.info(f"No memory found for {chat_id} with key: {key}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        logger.debug(f"Failed retrieval: chat_id={chat_id}, key={key}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
