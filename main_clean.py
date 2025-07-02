from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for required environment variables
required_vars = [
    "TELEGRAM_BOT_TOKEN",
    "SUPABASE_URL", 
    "SUPABASE_SERVICE_ROLE_KEY",
    "OPENAI_API_KEY",
    "PAYSTACK_SECRET_KEY"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.warning(f"⚠️ Missing environment variables: {missing_vars}")

# Import components after environment setup
try:
    from utils.fee_calculator import get_fee_calculator
    logger.info("✅ Fee calculator loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Fee calculator issue: {e}")

# Health check route
@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": "2025-01-02T00:00:00Z",
        "message": "Sofi AI is running"
    })

# Basic webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    """Basic webhook handler"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook: {data}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# Basic route
@app.route("/")
def index():
    """Basic index route"""
    return jsonify({
        "message": "Sofi AI Backend Running",
        "status": "healthy",
        "endpoints": ["/health", "/webhook"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
