#!/usr/bin/env python3
"""
Start Sofi AI Flask App for Testing
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

if __name__ == "__main__":
    print("🚀 Starting Sofi AI Flask App...")
    print("📱 WhatsApp webhook available at: /whatsapp-webhook")
    print("🔗 Webhook URL: http://localhost:5000/whatsapp-webhook")
    print("=" * 50)
    
    # Import and run the Flask app
    try:
        from main import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        import traceback
        traceback.print_exc()
