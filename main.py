import os
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from supabase import create_client, Client
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
from utils.transaction_logger import save_transaction
from datetime import datetime, timedelta
import requests
import time
import json
import openai
import logging

load_dotenv()
# Config / Keys - replace with your actual keys or environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-key")

openai.api_key = OPENAI_API_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Monnify Setup ===
MONNIFY_API_KEY = "MK_TEST_2HZBPDH1ZA"
MONNIFY_SECRET_KEY = "KENV4DZB7QWE67LPX70L9Z3A30XDH8JY"
MONNIFY_CONTRACT_CODE = "0651597406"

# === Flask App Setup ===
app = Flask(__name__)

# === HTML Form ===
onboarding_form = '''
<!doctype html>
<title>Sofi AI Onboarding</title>
<h2>🧠 Sofi AI - Open Your Virtual Account</h2>
<form method=post>
  First Name: <input type=text name=first_name required><br><br>
  Last Name: <input type=text name=last_name required><br><br>
  Address: <input type=text name=address required><br><br>
  City: <input type=text name=city required><br><br>
  State: <input type=text name=state required><br><br>
  BVN: <input type=text name=bvn required><br><br>
  Choose Transaction PIN: <input type=password name=pin required><br><br>
  <input type=submit value=Submit>
</form>
'''

# === Monnify Auth ===
def get_monnify_token():
    url = "https://sandbox.monnify.com/api/v1/auth/login"
    res = requests.post(url, auth=(MONNIFY_API_KEY, MONNIFY_SECRET_KEY))
    return res.json()["responseBody"]["accessToken"]

# === Create Virtual Account ===
def create_virtual_account(first_name, last_name, bvn):
    token = get_monnify_token()
    url = "https://sandbox.monnify.com/api/v2/bank-transfer/reserved-accounts"
    headers = {"Authorization": f"Bearer {token}"}
    unique_reference = f"sofi_{first_name.lower()}_{last_name.lower()}_{int(time.time())}"  # Add timestamp for uniqueness
    data = {
        "accountReference": unique_reference,
        "accountName": f"{first_name} {last_name} Sofi",
        "bvn": bvn,
        "currencyCode": "NGN",
        "contractCode": MONNIFY_CONTRACT_CODE,
        "customerEmail": f"{first_name.lower()}.{last_name.lower()}@sofi.ng",
        "customerName": f"{first_name} {last_name}",
        "bankCode": "50515",  # Specify Moniepoint's bank code
        "getAllAvailableBanks": False  # Explicitly set to False to avoid generating multiple accounts
    }
    res = requests.post(url, headers=headers, json=data)
    response = res.json()

    # Fallback logic for unsupported bankCode
    if res.status_code != 200 or "responseBody" not in response:
        print("Error: Unsupported bankCode or other issue.")
        print(f"Response: {response}")

        # Retry with getAllAvailableBanks set to True
        data["getAllAvailableBanks"] = True
        data.pop("bankCode", None)  # Remove bankCode
        res = requests.post(url, headers=headers, json=data)
        response = res.json()

        if res.status_code != 200 or "responseBody" not in response:
            print("Error: Failed even with getAllAvailableBanks set to True.")
            print(f"Response: {response}")
            return {
                "error": "Failed to create account. Please try again later or contact support."
            }

    return response

# === Intent Detection Prompt ===
system_prompt = """
You are Sofi AI, an intelligent Nigerian assistant.

Your job is to detect user intent from their message and return a JSON.
If a user wants to send money, extract:
- amount
- recipient_name
- account_number (if mentioned)
- bank
- narration (if any)

Return:
{
  "intent": "send_money",
  "details": {
    "amount": 2000,
    "recipient_name": "Bumi Oladele",
    "account_number": "1234567890",
    "bank": "Opay",
    "narration": "For food"
  }
}

If the user asks about past spending, return:
{
  "intent": "spending_summary",
  "period": "last month"  // could be specific: "May 2025"
}

If it's just a chat, return:
{ "intent": "general_chat" }

Only respond with valid JSON. Do not include explanations.
"""

def detect_intent(user_message):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2
        )
        reply = response['choices'][0]['message']['content']
        return reply
    except Exception as e:
        return f"Error: {e}"

def send_reply(chat_id, message):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": message})

# Global dictionary to track users waiting for PIN verification
pending_pin_verification = {}  # key: chat_id, value: transfer_details dict

# Global dictionary to track onboarding state
onboarding_state = {}  # key: chat_id, value: dict of user responses

def extract_and_store_memory(chat_id, user_message):
    try:
        user_resp = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
        user = user_resp.data

        if not user:
            logger.warning(f"User profile not found for chat_id: {chat_id}")
            send_reply(chat_id, "I couldn't save your memory as your user profile was not found.")
            return

        # Ask GPT if this message is a memory
        prompt = f"""
        You are Sofi AI. Your user just sent: "{user_message}"

        Determine if this is a personal memory they want to store (like a fact or note about their life). If yes, return:
        {"store_memory": true, "memory_text": "..."}

        If not, return:
        {"store_memory": false}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3
        )
        reply = json.loads(response['choices'][0]['message']['content'])

        if reply.get("store_memory"):
            supabase.table("memories").insert({
                "user_id": user[0]["id"],
                "memory_text": reply["memory_text"]
            }).execute()
            send_reply(chat_id, "🧠 Got it. I’ll remember that.")
        else:
            logger.info(f"Message not identified as memory for chat_id: {chat_id}")

    except Exception as e:
        logger.error(f"Error while extracting and storing memory for chat_id {chat_id}: {e}")
        send_reply(chat_id, "An error occurred while processing your memory. Please try again later.")

def generate_receipt(user_name, amount, type, sender=""):
    if type == "credit":
        return f"💸 Hey {user_name}, you just received ₦{amount:,.2f} from {sender}."
    elif type == "debit":
        return f"🚀 {user_name}, ₦{amount:,.2f} was sent successfully to {sender}."

@app.route(f"/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "").strip()
        telegram_username = data["message"]["chat"].get("username", "there")

        # Check if user exists
        user_resp = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
        if not user_resp.data:
            # Send welcome message with inline keyboard for onboarding
            onboarding_url = "http://127.0.0.1:5001/onboarding"
            welcome_message = f"""
👋 Hello {telegram_username}! This is your username. Sofi will reply back with your Telegram username on your first message.

I'm Sofi, your Personal Account Manager AI from Sofi Technologies. I can handle transactions, schedule payments, and even analyze your spending!

🔐 Quick tip: Lock down your Telegram for extra security!

Ready to get started? Let's begin your onboarding! ✨
            """
            keyboard = {
                "inline_keyboard": [
                    [{"text": "Complete Onboarding", "url": onboarding_url}]
                ]
            }
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": welcome_message, "reply_markup": keyboard}
            )
            return "OK"

        # Check if user is in onboarding state
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

                # Create virtual account
                result = create_virtual_account(
                    user_data["first_name"], user_data["last_name"], user_data["bvn"]
                )

                if "responseBody" in result:
                    acct_info = result["responseBody"]
                    acct_no = acct_info.get("accountNumber", "")
                    bank_name = acct_info.get("bankName", "")

                    # Save user data in Supabase
                    supabase.table("users").insert({
                        "telegram_chat_id": chat_id,
                        "first_name": user_data["first_name"],
                        "last_name": user_data["last_name"],
                        "bvn": user_data["bvn"],
                        "pin": user_data["pin"],
                        "account_number": acct_no,
                        "bank_name": bank_name
                    }).execute()

                    send_reply(
                        chat_id,
                        f"🎉 Success! Your account has been created.\n\nAccount Number: {acct_no}\nBank Name: {bank_name}"
                    )
                else:
                    send_reply(chat_id, "❌ Failed to create your account. Please try again later.")

                # Clear onboarding state
                del onboarding_state[chat_id]
            return "OK"

        # Start onboarding if user sends a specific command
        if user_message.lower() == "/start_onboarding":
            onboarding_state[chat_id] = {}
            send_reply(chat_id, "Welcome to Sofi AI! Let's get started. What's your first name?")
            return "OK"

        # Default behavior for other messages
        send_reply(chat_id, "Sorry, I didn't understand that. Please type /start_onboarding to begin.")

    return "OK"

# === Routes ===
@app.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        first = request.form['first_name']
        last = request.form['last_name']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        bvn = request.form['bvn']
        pin = request.form['pin']

        # 1. Create Monnify virtual account
        result = create_virtual_account(first, last, bvn)
        print(result)  # For debugging

        if "responseBody" in result:
            acct_info = result["responseBody"]
            acct_no = acct_info.get("accountNumber", "")
            acct_name = acct_info.get("accountName", "")
            bank_name = acct_info.get("bankName", "")
            account_reference = acct_info.get("accountReference", "")

            # Save user with account_reference in Supabase
            supabase.table("users").insert({
                "first_name": first,
                "last_name": last,
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

            return f"<h3>🎉 Account Created!</h3><p><b>Acct Name:</b> {acct_name}<br><b>Acct No:</b> {acct_no}<br><b>Bank:</b> {bank_name}</p>"
        else:
            return f"<h3>❌ Failed to retrieve response body.</h3><p>{result}</p>"

    return render_template_string(onboarding_form)

def summarize_spending(chat_id, period="last month"):
    try:
        user = supabase.table("users").select("id", "first_name").eq("telegram_chat_id", str(chat_id)).single().execute().data
        if not user:
            send_reply(chat_id, "User not found.")
            return

        # You can adjust this date range logic
        res = supabase.table("transactions").select("*").eq("user_id", user["id"]).order("timestamp", desc=True).execute()
        txns = res.data or []

        if not txns:
            send_reply(chat_id, "No transactions found for that period.")
            return

        summary_input = "\n".join([f"{t['timestamp'][:10]}: ₦{t['amount']} for {t.get('category', 'unspecified')} ({t.get('narration', '')})" for t in txns])

        narration_prompt = f"""
        You are Sofi AI, a smart Nigerian assistant. Summarize this user's spending activity based on the data below. Be concise but insightful.

        User: {user['first_name']}
        Data:
        {summary_input}

        Respond as if you're explaining their habits and major categories of expenses.
        """
        narration = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": narration_prompt}],
            temperature=0.4
        )['choices'][0]['message']['content']

        send_reply(chat_id, narration)

    except Exception as e:
        send_reply(chat_id, f"Spending summary failed: {e}")

@app.route('/webhook', methods=['POST'])
def monnify_webhook():
    data = request.json
    if data["eventType"] == "SUCCESSFUL_TRANSACTION":
        acct_ref = data["eventData"]["product"]["reference"]
        user = supabase.table("users").select("*").eq("account_reference", acct_ref).single().execute()
        if user.data:
            user_id = user.data["id"]
            deposit_amount = data["eventData"]["amount"]
            new_balance = user.data["wallet_balance"] + deposit_amount

            # Insert deposit record
            supabase.table("deposits").insert({
                "user_id": user_id,
                "amount": deposit_amount,
                "transaction_reference": data["eventData"]["transactionReference"],
                "timestamp": data["eventData"]["paymentDate"]
            }).execute()

            # Update wallet balance
            supabase.table("wallets").update({"balance": new_balance}).eq("user_id", user_id).execute()

            # Generate receipt
            receipt = generate_receipt(user.data["first_name"], deposit_amount, "credit", "Monnify")
            print(receipt)  # For debugging or logging purposes

    return "Webhook processed", 200

def make_monnify_transfer(transfer_id):
    """
    - Query transfer details from DB using transfer_id
    - Use Monnify transfer API to send money
    - Return (success: bool, message: str)
    """
    transfer_res = supabase.table("transfers").select("*").eq("id", transfer_id).single().execute()
    if not transfer_res.data:
        return False, "Transfer record not found."

    transfer = transfer_res.data

    # Authenticate with Monnify
    token = get_monnify_token()
    if not token:
        return False, "Failed to authenticate with Monnify."

    # Prepare transfer request
    url = "https://sandbox.monnify.com/api/v2/disbursements/single"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "amount": transfer["amount"],
        "reference": f"transfer_{transfer_id}_{int(time.time())}",
        "narration": transfer.get("narration", ""),
        "bankCode": transfer.get("bank", ""),
        "accountNumber": transfer.get("account_number", ""),
        "currency": "NGN",
        "sourceAccountNumber": "YOUR_SOURCE_ACCOUNT_NUMBER"  # Replace with actual source account number
    }

    # Make API call
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("requestSuccessful"):
            return True, f"₦{transfer['amount']} sent to {transfer['recipient_name']} ({transfer['bank']})."
        else:
            error_message = response_data.get("responseMessage", "Unknown error occurred.")
            return False, f"Failed to send money: {error_message}"
    except Exception as e:
        return False, f"Error occurred during transfer: {str(e)}"

def save_memory(user_id, content):
    try:
        data = {
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        supabase.table("memories").insert(data).execute()
        logger.info(f"Memory saved successfully for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Error while saving memory for user_id {user_id}: {e}")

def categorize_transaction(narration):
    prompt = f"Please categorize this transaction description into categories like 'food', 'transport', 'shopping', 'bills', 'salary', 'deposit', etc: \"{narration}\""
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=10,
        )
        category = completion.choices[0].message.content.strip().lower()
        return category
    except Exception as e:
        return "uncategorized"

if __name__ == "__main__":
    app.run(port=5000)
