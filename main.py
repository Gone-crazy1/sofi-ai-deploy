import os
import sys
import logging
from flask import Flask, request, jsonify, render_template, render_template_string, redirect, url_for
from telegram import Update, Bot
import openai
from supabase import create_client, Client
import uuid
from flask_wtf import CSRFProtect
from wtforms import Form, StringField, PasswordField, validators
import requests
import time
import json
from datetime import datetime
import hashlib
import hmac

# Load environment variables from .env at the very top
from dotenv import load_dotenv
load_dotenv()

# Configure logging at the top
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Security: CSRF Protection ===
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or uuid.uuid4().hex  # Use env or random fallback
csrf = CSRFProtect(app)

# === Security: HTTPS enforcement ===
@app.before_request
def enforce_https():
    # Only enforce HTTPS in production, not in development
    if not request.is_secure and os.getenv("FLASK_ENV") == "production":
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)

# === Config / Keys ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MONNIFY_API_KEY = os.getenv("MONNIFY_API_KEY")
MONNIFY_SECRET_KEY = os.getenv("MONNIFY_SECRET_KEY")
MONNIFY_CONTRACT_CODE = os.getenv("MONNIFY_CONTRACT_CODE")

REQUIRED_ENV_VARS = [
    "TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY",
    "MONNIFY_API_KEY", "MONNIFY_SECRET_KEY", "MONNIFY_CONTRACT_CODE"
]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Initialize Supabase and OpenAI
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# --- Flask App Setup ---
from werkzeug.middleware.proxy_fix import ProxyFix

# Use ProxyFix if behind a proxy (e.g., on Heroku)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# === Input Validation: WTForms for onboarding ===
class OnboardingForm(Form):
    first_name = StringField('First Name', [validators.InputRequired(), validators.Length(min=2, max=50)])
    last_name = StringField('Last Name', [validators.InputRequired(), validators.Length(min=2, max=50)])
    address = StringField('Address', [validators.InputRequired(), validators.Length(min=2, max=100)])
    city = StringField('City', [validators.InputRequired(), validators.Length(min=2, max=50)])
    state = StringField('State', [validators.InputRequired(), validators.Length(min=2, max=50)])
    bvn = StringField('BVN', [validators.InputRequired(), validators.Regexp(r'^\d{11}$', message="BVN must be 11 digits")])
    pin = PasswordField('PIN', [validators.InputRequired(), validators.Regexp(r'^\d{4}$', message="PIN must be 4 digits")])
    chat_id = StringField('Chat ID', [validators.Optional()])

# Global utility function
def return_status_ok(message="✅ Done"):
    return {"status": "ok", "message": message}

# === Monnify Setup ===
# Removed hardcoded Monnify keys. Only use environment variables loaded above.

# === HTML Form ===
# Updated HTML Form with modern design
onboarding_form = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sofi AI Onboarding</title>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .form-container {
            background: #ffffff;
            padding: 20px 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
        }
        .form-container h2 {
            text-align: center;
            color: #333333;
            margin-bottom: 20px;
        }
        .form-container input[type="text"],
        .form-container input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #cccccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .form-container input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
        }
        .form-container input[type="submit"]:hover {
            background-color: #45a049;
        }
        .form-container label {
            font-size: 14px;
            color: #555555;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>🧠 Sofi AI - Open Your Virtual Account</h2>
        <form method="post">
            <label for="first_name">First Name:</label>
            <input type="text" id="first_name" name="first_name" placeholder="Enter your first name" required>

            <label for="last_name">Last Name:</label>
            <input type="text" id="last_name" name="last_name" placeholder="Enter your last name" required>

            <label for="address">Address:</label>
            <input type="text" id="address" name="address" placeholder="Enter your address" required>

            <label for="city">City:</label>
            <input type="text" id="city" name="city" placeholder="Enter your city" required>

            <label for="state">State:</label>
            <input type="text" id="state" name="state" placeholder="Enter your state" required>

            <label for="bvn">BVN:</label>
            <input type="text" id="bvn" name="bvn" placeholder="Enter your BVN" required>

            <label for="pin">Choose Transaction PIN:</label>
            <input type="password" id="pin" name="pin" placeholder="Enter a 4-digit PIN" required>

            <input type="submit" value="Submit">
        </form>
    </div>
</body>
</html>
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
        "getAllAvailableBanks": True  # Allow Monnify to select the best bank
    }

    res = requests.post(url, headers=headers, json=data)
    response = res.json()

    if res.status_code == 200 and "responseBody" in response:
        return response["responseBody"]
    else:
        raise Exception(f"Failed to create virtual account: {response.get('responseMessage', 'Unknown error')}")

# === Intent Detection Prompt ===
system_prompt = """
You are Sofi AI, a smart Nigerian assistant that helps users with transfers, airtime, and more.
If a user says something like "Send ₦500 to John at Access Bank, 0123456789", reply ONLY with this JSON format:

{
  "intent": "transfer",
  "amount": 500,
  "recipient_name": "John",
  "account_number": "0123456789",
  "bank_name": "Access Bank"
}

If some information is missing, just include what you understood. Do not make up data.

Examples:
User: "I want to send ₦1000 to Uche"
Reply:
{"intent": "transfer", "amount": 1000, "recipient_name": "Uche"}

User: "Send 2k to 0098765432 at Zenith"
Reply:
{"intent": "transfer", "amount": 2000, "account_number": "0098765432", "bank_name": "Zenith"}

Always respond with just the JSON, no extra text.
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
    """
    Sends a message to a Telegram chat using the bot's API.

    Args:
        chat_id (int): The Telegram chat ID to send the message to.
        message (str): The message text to send.
    """
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to chat_id {chat_id}: {e}")

# Global dictionary to track onboarding state
onboarding_state = {}  # key: chat_id, value: dict of user responses

# Global dictionary to track user intents and states
user_state = {}  # key: chat_id, value: dict with keys like "intent", "step", "transfer_data", etc.

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

def generate_pos_style_receipt(sender_name, amount, recipient_name, recipient_account, recipient_bank, balance, transaction_id):
    """
    Generate a beautiful POS-style receipt for a transfer.
    """
    return f"""
┌───────────────────────────────┐
│         SOFI TRANSFER         │
├───────────────────────────────┤
│  FROM: {sender_name}          │
│  TO:   {recipient_name}       │
│  ACCT: {recipient_account}    │
│  BANK: {recipient_bank}       │
├───────────────────────────────┤
│  AMOUNT:   ₦{amount:,.2f}     │
│  BALANCE:  ₦{balance:,.2f}    │
│  TXN ID:   {transaction_id}   │
├───────────────────────────────┤
│      ✅ TRANSFER SUCCESSFUL    │
│      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   │
└───────────────────────────────┘
"""

@app.route(f"/webhook_telegram", methods=["POST"])
def telegram_webhook():
    """
    Handle incoming Telegram updates.
    """
    try:
        update = request.get_json()
        if not update:
            return jsonify({"error": "No update received"}), 400

        # Log the update for debugging
        logger.info(f"Received Telegram update: {update}")

        # Process the update (e.g., handle messages, commands, etc.)
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            user_message = update["message"].get("text", "").strip()

            # Example: Echo the received message back to the user
            bot.send_message(chat_id=chat_id, text=f"You said: {user_message}")

        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error handling Telegram update: {e}")
        return jsonify({"error": "Internal server error"}), 500

def handle_update(update):
    """
    Process incoming Telegram updates.
    """
    if update.message:
        chat_id = update.message.chat_id
        user_message = update.message.text

        # Example: Respond to a simple text message
        if user_message.lower() == "/start":
            send_reply(chat_id, "Welcome! How can I assist you today?")
        else:
            ai_response = detect_intent(user_message)
            send_reply(chat_id, ai_response)

    elif update.callback_query:
        # Handle callback queries if needed
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f"Selected option: {query.data}")

# === Routes ===
@app.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    logger.info(f"Received request at /onboarding with method: {request.method}")
    form = OnboardingForm(request.form)
    if request.method == "POST" and form.validate():
        first = form.first_name.data
        last = form.last_name.data
        address = form.address.data
        city = form.city.data
        state = form.state.data
        bvn = form.bvn.data
        pin = form.pin.data
        chat_id = form.chat_id.data
        try:
            hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
            existing_user_bvn = supabase.table("users").select("account_number").eq("bvn", bvn).execute()
            if existing_user_bvn.data:
                logger.warning(f"Duplicate BVN detected: {bvn}")
                return f"<h3>❌ Account already exists for BVN: {bvn}</h3>"
            result = create_virtual_account(first, last, bvn)
            acct_no = result.get("accountNumber", "")
            acct_name = result.get("accountName", "")
            bank_name = result.get("bankName", "")
            account_reference = result.get("accountReference", "")
            supabase.table("users").insert({
                "telegram_chat_id": chat_id,
                "first_name": first,
                "last_name": last,
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
            logger.info("Account successfully created.")
            return f"""
            <h3>🎉 Account Created!</h3>
            <p><b>Acct Name:</b> {acct_name}<br><b>Acct No:</b> {acct_no}<br><b>Bank:</b> {bank_name}</p>
            <a href='https://t.me/your_bot_username' target='_blank'>
                <button>Go back to Telegram</button>
            </a>
            """
        except Exception as e:
            logger.error(f"Error during onboarding: {e}")
            return f"<h3>❌ Onboarding failed!</h3><p>{str(e)}</p>"
    elif request.method == "POST":
        logger.warning(f"Onboarding form validation failed: {form.errors}")
        return f"<h3>❌ Invalid input:</h3><p>{form.errors}</p>"
    return render_template_string(onboarding_form)

@app.route("/onboard", methods=["GET", "POST"])
def onboard():
    logger.info(f"Received request at /onboard with method: {request.method}")
    form = OnboardingForm(request.form)
    if request.method == "POST" and form.validate():
        first = form.first_name.data
        last = form.last_name.data
        address = form.address.data
        city = form.city.data
        state = form.state.data
        bvn = form.bvn.data
        pin = form.pin.data
        chat_id = form.chat_id.data
        try:
            hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
            existing_user_bvn = supabase.table("users").select("account_number").eq("bvn", bvn).execute()
            if existing_user_bvn.data:
                logger.warning(f"Duplicate BVN detected: {bvn}")
                return f"<h3>❌ Account already exists for BVN: {bvn}</h3>"
            result = create_virtual_account(first, last, bvn)
            acct_no = result.get("accountNumber", "")
            acct_name = result.get("accountName", "")
            bank_name = result.get("bankName", "")
            account_reference = result.get("accountReference", "")
            supabase.table("users").insert({
                "telegram_chat_id": chat_id,
                "first_name": first,
                "last_name": last,
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
            logger.info("Account successfully created.")
            return f"""
            <h3>🎉 Account Created!</h3>
            <p><b>Acct Name:</b> {acct_name}<br><b>Acct No:</b> {acct_no}<br><b>Bank:</b> {bank_name}</p>
            <a href='https://t.me/your_bot_username' target='_blank'>
                <button>Go back to Telegram</button>
            </a>
            """
        except Exception as e:
            logger.error(f"Error during onboarding: {e}")
            return f"<h3>❌ Onboarding failed!</h3><p>{str(e)}</p>"
    elif request.method == "POST":
        logger.warning(f"Onboarding form validation failed: {form.errors}")
        return f"<h3>❌ Invalid input:</h3><p>{form.errors}</p>"
    return render_template("onboarding_form.html")

# Update PIN verification logic
@app.route("/verify_pin", methods=["POST"])
def verify_pin():
    data = request.get_json()
    chat_id = data.get("chat_id")
    entered_pin = data.get("pin")

    try:
        # Fetch stored hashed PIN from Supabase
        response = supabase.table("users").select("pin").eq("telegram_chat_id", str(chat_id)).single().execute()
        stored_hashed_pin = response.data['pin'] if response.data else None

        if stored_hashed_pin:
            # Hash the entered PIN and compare
            hashed_entered_pin = hashlib.sha256(entered_pin.encode()).hexdigest()
            if hashed_entered_pin == stored_hashed_pin:
                return jsonify({"status": "success", "message": "PIN verified successfully."})
            else:
                return jsonify({"status": "failure", "message": "Incorrect PIN."})
        else:
            return jsonify({"status": "failure", "message": "PIN not found for user."})
    except Exception as e:
        logger.error(f"Error during PIN verification: {e}")
        return jsonify({"status": "error", "message": "An error occurred during PIN verification."})

def summarize_spending(chat_id, period="last month"):
    try:
        user = supabase.table("users").select("id", "first_name").eq("telegram_chat_id", str(chat_id)).single().execute().data
        if not user:
            send_reply(chat_id, "User not found.")
            return

        # Fetch transactions for the user
        res = supabase.table("transactions").select("*").eq("user_id", user["id"]).order("timestamp", desc=True).execute()
        txns = res.data or []

        if not txns:
            send_reply(chat_id, "No transactions found for that period.")
            return

        # Group transactions by category and calculate totals
        category_totals = {}
        for txn in txns:
            category = txn.get("category", "uncategorized")
            amount = txn.get("amount", 0)
            category_totals[category] = category_totals.get(category, 0) + amount

        # Calculate total spending and average daily/weekly spending
        total_spent = sum(category_totals.values())
        days_in_period = 30  # Assuming "last month" is 30 days
        avg_daily_spend = total_spent / days_in_period
        avg_weekly_spend = avg_daily_spend * 7

        # Sort categories by spending and get the top 3
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top_categories = sorted_categories[:3]

        # Prepare summary input for GPT
        summary_input = "\n".join([f"{cat}: ₦{amt:,.2f}" for cat, amt in sorted_categories])

        # Enhanced prompt for GPT
        narration_prompt = f"""
        You are Sofi AI, a smart Nigerian assistant. Summarize this user's spending activity based on the data below. Be concise but insightful.

        User: {user['first_name']}
        Total Spent: ₦{total_spent:,.2f}
        Average Daily Spend: ₦{avg_daily_spend:,.2f}
        Average Weekly Spend: ₦{avg_weekly_spend:,.2f}

        Top 3 Spending Categories:
        {', '.join([f'{cat} (₦{amt:,.2f})' for cat, amt in top_categories])}

        Data:
        {summary_input}

        Highlight any unusual patterns or significant insights.
        """

        narration = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": narration_prompt}],
            temperature=0.4
        )["choices"][0]["message"]["content"]

        send_reply(chat_id, narration)

    except Exception as e:
        send_reply(chat_id, f"Spending summary failed: {e}")

@app.route('/webhook_monnify', methods=['POST'])
def monnify_webhook():
    data = request.json

    # Verify Monnify signature
    signature_header = request.headers.get('monnify-signature')
    secret_key = os.getenv("MONNIFY_SECRET_KEY")  # Keep secret

    calculated_signature = hmac.new(
        secret_key.encode(),
        msg=json.dumps(data).encode(),
        digestmod=hashlib.sha512
    ).hexdigest()

    if signature_header != calculated_signature:
        logger.warning("Invalid Monnify signature received.")
        return "Invalid signature", 400

    if data["eventType"] == "SUCCESSFUL_TRANSACTION":
        acct_ref = data["eventData"]["product"]["reference"]
        user = supabase.table("users").select("*").eq("account_reference", acct_ref).single().execute()
        if user.data:
            user_id = user.data["id"]
            deposit_amount = data["eventData"]["amount"]

            # Fetch the current wallet balance from the wallets table
            wallet = supabase.table("wallets").select("balance").eq("user_id", user_id).single().execute()

            if not wallet.data:
                # Create a new wallet if it doesn't exist
                supabase.table("wallets").insert({
                    "user_id": user_id,
                    "balance": deposit_amount
                }).execute()
                logger.info(f"New wallet created for user_id {user_id} with initial balance {deposit_amount}.")
            else:
                # Update the existing wallet balance
                current_balance = wallet.data["balance"]
                new_balance = current_balance + deposit_amount
                supabase.table("wallets").update({"balance": new_balance}).eq("user_id", user_id).execute()
                logger.info(f"Wallet updated for user_id {user_id}: Previous balance {current_balance}, Deposit {deposit_amount}, New balance {new_balance}.")

            # Insert deposit record
            supabase.table("deposits").insert({
                "user_id": user_id,
                "amount": deposit_amount,
                "transaction_reference": data["eventData"]["transactionReference"],
                "timestamp": data["eventData"]["paymentDate"]
            }).execute()
            logger.info(f"Deposit record created for user_id {user_id}: Amount {deposit_amount}, Transaction Reference {data['eventData']['transactionReference']}.")

            # Notify user via Telegram
            chat_id = user.data.get("telegram_chat_id")
            if chat_id:
                message = (
                    f"💰 Deposit Alert!\n\n"
                    f"Amount: ₦{deposit_amount:,.2f}\n"
                    f"Transaction Reference: {data['eventData']['transactionReference']}\n"
                    f"New Wallet Balance: ₦{new_balance:,.2f}"
                )
                bot.send_message(chat_id=chat_id, text=message)
                logger.info(f"Deposit notification sent to chat_id {chat_id}.")

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
        "bankCode": transfer.get("bank_code", ""),  # Ensure bank_code is stored in the database
        "accountNumber": transfer.get("account_number", ""),
        "currency": "NGN",
        "sourceAccountNumber": "YOUR_SOURCE_ACCOUNT_NUMBER"  # Replace with actual source account number
    }

    # Make API call
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("requestSuccessful"):
            # Generate and log/send receipt
            receipt = generate_receipt(transfer["recipient_name"], transfer["amount"], "debit", "Monnify")
            print(receipt)  # For debugging or logging purposes
            return True, f"₦{transfer['amount']} sent to {transfer['recipient_name']} ({transfer['bank_code']})."
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
        logger.error(f"Categorization failed: {e}")
        try:
            # Retry once in case of transient issues
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10,
            )
            category = completion.choices[0].message.content.strip().lower()
            return category
        except Exception as retry_error:
            logger.error(f"Retry categorization failed: {retry_error}")
            return "uncategorized"

# === Handle Incoming Messages ===
@app.route("/webhook_incoming", methods=["POST"])
def handle_incoming_message():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "").strip()

        # Check if user is in the middle of a transfer
        if chat_id in user_state and user_state[chat_id].get("intent") == "transfer":
            transfer_data = user_state[chat_id].get("transfer_data", {})

            # Handle based on the current step
            if user_state[chat_id]["step"] == "collecting_transfer_data":
                # Check and ask for each required field
                if not transfer_data.get("amount"):
                    send_reply(chat_id, "How much do you want to send?")
                    user_state[chat_id]["transfer_data"]["amount"] = user_message  # Temporarily store the response
                elif not transfer_data.get("recipient_name"):
                    send_reply(chat_id, "Who are you sending the money to?")
                    user_state[chat_id]["transfer_data"]["recipient_name"] = user_message
                elif not transfer_data.get("account_number"):
                    send_reply(chat_id, "What is the recipient's account number?")
                    user_state[chat_id]["transfer_data"]["account_number"] = user_message
                elif not transfer_data.get("bank_name"):
                    send_reply(chat_id, "What bank is the recipient using?")
                    user_state[chat_id]["transfer_data"]["bank_name"] = user_message
                else:
                    # All data collected, confirm the transfer
                    amount = transfer_data["amount"]
                    recipient_name = transfer_data["recipient_name"]
                    account_number = transfer_data["account_number"]
                    bank_name = transfer_data["bank_name"]

                    send_reply(chat_id, f"Alright! You're sending ₦{amount} to {recipient_name} at {bank_name}, {account_number}.")
                    send_reply(chat_id, "\n\nPlease enter your 4-digit PIN to confirm.")
                    user_state[chat_id]["step"] = "awaiting_pin"  # Move to the next step
            elif user_state[chat_id]["step"] == "awaiting_pin":
                pin = user_message
                # Call verify_pin endpoint
                verify_resp = requests.post(
                    url_for('verify_pin', _external=True),
                    json={"chat_id": chat_id, "pin": pin}
                )
                verify_result = verify_resp.json()
                if verify_result.get("status") == "success":
                    # Proceed with transfer logic (call Monnify, update DB, etc.)
                    send_reply(chat_id, "Transfer successful!")
                else:
                    send_reply(chat_id, f"PIN verification failed: {verify_result.get('message')}")
                del user_state[chat_id]  # Clear the user state after completing the transfer
            return "OK"

        # Default processing for other messages
        ai_response = detect_intent(user_message)
        if isinstance(ai_response, str) and ai_response.startswith("Error"):
            send_reply(chat_id, "Sorry, I couldn't process that. Please try again or type /start_onboarding to begin.")
        else:
            send_reply(chat_id, f"🤖 Here's what I understood: {ai_response}")

    return "OK"

# --- Test Coverage: Ensure all routes are tested ---
# (Assume tests/test_transfer_flow.py exists and covers all routes. If not, add tests.)

def handle_telegram_update(update):
    """
    Process Telegram updates inline for onboarding, intent detection, and user flows.
    """
    if not update or "message" not in update:
        return
    chat_id = update["message"]["chat"]["id"]
    user_message = update["message"].get("text", "").strip()
    telegram_username = update["message"]["chat"].get("username", "there")

    # Check if user exists
    user_resp = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
    if not user_resp.data:
        base_url = os.getenv("BASE_URL", "http://127.0.0.1:5001")
        onboarding_url = f"{base_url}/onboarding"
        welcome_message = f"""
👋 Hello {telegram_username}!\n\nI'm Sofi, your Personal Account Manager AI from Sofi Technologies. I can handle transactions, schedule payments, and even analyze your spending!\n\n🔐 Quick tip: Lock down your Telegram for extra security!\n\nReady to get started? Let's begin your onboarding! ✨
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
        return

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
                        f"🎉 Success! Your account has been created.\n\nAccount Number: {acct_no}\nBank Name: {bank_name}"
                    )
                else:
                    send_reply(chat_id, "❌ Failed to create your account. Please try again later.")
            except Exception as e:
                send_reply(chat_id, "⚠️ Something went wrong during onboarding. Please try again.")
                onboarding_state.pop(chat_id, None)
            onboarding_state.pop(chat_id, None)
        return

    # Start onboarding if user sends a specific command
    if user_message.lower() == "/start_onboarding":
        onboarding_state[chat_id] = {}
        send_reply(chat_id, "Welcome to Sofi AI! Let's get started. What's your first name?")
        return

    # Default behavior for other messages
    ai_response = detect_intent(user_message)
    if isinstance(ai_response, str) and ai_response.startswith("Error"):
        send_reply(chat_id, "Sorry, I couldn't process that. Please try again or type /start_onboarding to begin.")
    else:
        send_reply(chat_id, f"🤖 Here's what I understood: {ai_response}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle Telegram webhook updates.
    """
    try:
        json_data = request.get_json()
        update = Update.de_json(json_data, bot)
        handle_update(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("\n--- Flask Routes ---")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
    print("--- End Routes ---\n")
    # Run without SSL context for local HTTP testing
    app.run(port=5000)
