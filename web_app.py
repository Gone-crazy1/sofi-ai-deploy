from flask import Flask
from supabase import create_client
from telegram import Bot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "your-supabase-key")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

supabase = None

def get_supabase_client():
    global supabase
    if supabase is None:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
bot = Bot(token=TELEGRAM_BOT_TOKEN)

app = Flask(__name__, template_folder="templates")

if __name__ == "__main__":
    app.run(port=5001)
