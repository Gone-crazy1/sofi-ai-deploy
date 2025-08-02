"""
Minimal WhatsApp API Test Server
==============================
This creates a simple API endpoint for testing
"""

from flask import Flask, request, jsonify, render_template
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    return "✅ WhatsApp API Test Server Running"

@app.route("/whatsapp-onboard")
def whatsapp_onboard_page():
    """Serve WhatsApp-style onboarding page"""
    try:
        whatsapp_number = request.args.get('whatsapp', '')
        logger.info(f"📱 Onboarding request for: {whatsapp_number}")
        return render_template('whatsapp_onboarding.html', whatsapp_number=whatsapp_number)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"Error loading onboarding page: {e}", 500

@app.route("/api/whatsapp_create_account", methods=["POST"])
def whatsapp_create_account():
    """WhatsApp account creation API endpoint"""
    try:
        data = request.get_json()
        logger.info(f"🎯 API Request: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Extract required fields
        whatsapp_number = data.get('whatsapp_number', '').strip()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        
        if not full_name:
            return jsonify({"success": False, "error": "Full name is required"}), 400
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        logger.info(f"✅ Creating account for: {full_name} ({whatsapp_number})")
        
        # Import and use the WhatsApp account manager
        try:
            import asyncio
            from utils.whatsapp_account_manager_simple import whatsapp_account_manager
            
            # Create account
            result = asyncio.run(whatsapp_account_manager.create_whatsapp_account(data))
            
            if result['success']:
                logger.info(f"✅ Account created successfully: {result.get('account_number')}")
                
                # Try to send WhatsApp notification
                try:
                    account_message = whatsapp_account_manager.format_account_message(result)
                    # You can add WhatsApp sending here if needed
                    logger.info("📱 Account details ready for WhatsApp")
                except Exception as e:
                    logger.error(f"Notification error: {e}")
                
                return jsonify(result), 201
            else:
                logger.error(f"❌ Account creation failed: {result.get('error')}")
                return jsonify(result), 400
                
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            return jsonify({
                "success": False, 
                "error": "Account creation service not available"
            }), 500
            
        except Exception as e:
            logger.error(f"❌ Account creation error: {e}")
            return jsonify({
                "success": False, 
                "error": str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"❌ API Error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route("/api/test")
def test_api():
    """Simple test endpoint"""
    return jsonify({
        "success": True,
        "message": "API is working",
        "timestamp": "2025-08-02",
        "service": "WhatsApp Banking"
    })

if __name__ == "__main__":
    print("🚀 Starting WhatsApp API Test Server")
    print("📍 Visit: http://localhost:5002/whatsapp-onboard")
    print("🧪 API: http://localhost:5002/api/whatsapp_create_account")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(debug=True, port=5002, host='0.0.0.0')
