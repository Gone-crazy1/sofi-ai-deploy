from flask import Flask, render_template, request, jsonify
from supabase import create_client
from monnify.Auth import get_monnify_token
from monnify.Transfers import create_virtual_account
from telegram import Bot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-key")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

app = Flask(__name__, template_folder="templates")

@app.route("/onboarding", methods=["GET"])
def onboarding_form():
    """Serve the onboarding form."""
    return render_template("onboarding_form.html")

@app.route("/submit_onboarding", methods=["POST"])
def submit_onboarding():
    """Handle form submission and send account details via Telegram."""
    user_data = {
        "first_name": request.form.get("first_name"),
        "last_name": request.form.get("last_name"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "state": request.form.get("state"),
        "bvn": request.form.get("bvn"),
        "pin": request.form.get("pin"),
        "chat_id": request.form.get("chat_id"),  # Collect chat_id from the form
    }

    try:
        # Create Monnify virtual account
        token = get_monnify_token()
        account_details = create_virtual_account(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            bvn=user_data["bvn"],
            token=token
        )

        # Save user data and account details to Supabase
        user_data.update({
            "account_number": account_details.get("accountNumber"),
            "bank_name": account_details.get("bankName"),
        })
        supabase.table("users").insert(user_data).execute()

        # Send account details via Telegram
        message = (
            f"🎉 Hello {user_data['first_name']} {user_data['last_name']}!\n"
            f"Your account has been successfully created.\n\n"
            f"🏦 Bank Name: {account_details.get('bankName')}\n"
            f"💳 Account Number: {account_details.get('accountNumber')}\n"
            f"📍 Address: {user_data['address']}, {user_data['city']}, {user_data['state']}"
        )
        bot.send_message(chat_id=user_data["chat_id"], text=message)

        return jsonify({"message": "Onboarding successful!"})
    except Exception as e:
        return jsonify({"message": "Onboarding failed!", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001)
