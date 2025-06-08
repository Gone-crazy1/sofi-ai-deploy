import os
import uuid
import logging
from flask import Flask, request, jsonify, render_template
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, filters
from dotenv import load_dotenv

# --- Init ---
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or uuid.uuid4().hex

# Disable CSRF globally
app.config['WTF_CSRF_ENABLED'] = False
csrf = CSRFProtect(app)

# Load environment variables from .env file
load_dotenv()

# --- Telegram Bot ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set. Please check your .env file.")

application = Application.builder().token(TELEGRAM_TOKEN).build()

# --- Webhook Handler ---
@app.route('/webhook', methods=['POST'])
@csrf.exempt  # CRUCIAL for Telegram webhook
async def webhook():
    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Telegram Message Handler ---
def handle_message(update, context):
    user = update.effective_user
    first_name = user.first_name or user.username or "there"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"👋 Hello {first_name}, I’m Sofi!\nI'm your Personal Account Manager AI from Sofi Technologies.\n\nReady to get started? Let’s begin your onboarding! ✨",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Begin Onboarding", url=os.getenv("ONBOARDING_FORM_URL"))]
        ])
    )

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Web Form Handler ---
@app.route('/onboard', methods=['GET', 'POST'])
def onboard():
    if request.method == 'POST':
        return jsonify({"message": "Account created successfully!"})
    return render_template('onboard.html')

# --- Error Handler for CSRF ---
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({"error": "CSRF token missing or invalid"}), 400

# --- App Entry Point ---
if __name__ == '__main__':
    app.run(debug=True)