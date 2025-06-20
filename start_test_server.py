#!/usr/bin/env python3
"""
Start Sofi AI Flask App for Testing
Run this to test the onboarding form in Chrome
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import app
    
    if __name__ == "__main__":
        print("🚀 Starting Sofi AI Flask App for Testing")
        print("=" * 50)
        print("📱 Telegram Bot: Running in background")
        print("🌐 Web Server: Starting on http://localhost:5000")
        print("📋 Onboarding Form: http://localhost:5000/onboarding")
        print("⚙️  Admin Dashboard: http://localhost:5000/admin") 
        print("-" * 50)
        print("💡 Open Chrome and navigate to: http://localhost:5000/onboarding")
        print("🧪 Test account creation with fake data")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run Flask app in debug mode for testing
        app.run(
            debug=True,
            host="0.0.0.0",
            port=5000,
            use_reloader=False  # Avoid double startup in debug mode
        )
        
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install flask python-telegram-bot supabase python-dotenv requests")
except Exception as e:
    print(f"❌ Failed to start Flask app: {e}")
    print("Check your .env file and make sure all credentials are set correctly.")
