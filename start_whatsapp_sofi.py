#!/usr/bin/env python3
"""
Sofi AI WhatsApp-Only Startup Script
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_whatsapp_config():
    """Check if WhatsApp configuration is complete"""
    required_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID', 
        'WHATSAPP_VERIFY_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif 'your_' in value.lower() or '_here' in value.lower():
            placeholder_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        return False
    
    if placeholder_vars:
        print("❌ Environment variables have placeholder values:")
        for var in placeholder_vars:
            print(f"   • {var} = {os.getenv(var)}")
        print("\n💡 Please update your .env file with real credentials")
        return False
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file with WhatsApp credentials.")
        return False
    
    print("✅ WhatsApp configuration complete!")
    return True

def start_sofi():
    """Start Sofi AI WhatsApp service"""
    if not check_whatsapp_config():
        sys.exit(1)
    
    print("🚀 Starting Sofi AI WhatsApp Service...")
    print("📱 WhatsApp-only mode activated")
    print("🔗 Webhook endpoint: /webhook")
    
    # Import and start the Flask app
    from main import app
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    start_sofi()
