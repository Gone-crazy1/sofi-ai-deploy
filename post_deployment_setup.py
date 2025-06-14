#!/usr/bin/env python3
"""
🔗 POST-DEPLOYMENT WEBHOOK SETUP
Run this AFTER your Render deployment is live
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def setup_telegram_webhook():
    """Set up Telegram webhook after Render deployment"""
    
    # UPDATE THIS WITH YOUR RENDER URL
    RENDER_URL = "https://your-app-name.onrender.com"  # CHANGE THIS!
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    webhook_url = f"{RENDER_URL}/webhook"
    telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    
    print(f"🔗 Setting Telegram webhook to: {webhook_url}")
    
    try:
        response = requests.post(telegram_api_url, json={
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"]
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Telegram webhook configured successfully!")
                print(f"📝 Webhook URL: {webhook_url}")
                return True
            else:
                print(f"❌ Telegram API error: {result}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def test_deployment():
    """Test your live deployment"""
    
    # UPDATE THIS WITH YOUR RENDER URL
    RENDER_URL = "https://your-app-name.onrender.com"  # CHANGE THIS!
    
    print(f"🧪 Testing deployment at: {RENDER_URL}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Deployment is live and healthy!")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment test failed: {e}")
        return False

def main():
    """Main post-deployment setup"""
    print("🚀 POST-DEPLOYMENT SETUP")
    print("=" * 50)
    print("Run this AFTER your Render deployment is live!")
    print()
    
    # Instructions
    print("📋 STEP 1: Update RENDER_URL in this script")
    print("   - Replace 'your-app-name' with your actual Render service name")
    print()
    
    print("📋 STEP 2: Test deployment")
    deployment_ok = test_deployment()
    
    if deployment_ok:
        print("\n📋 STEP 3: Configure Telegram webhook")
        webhook_ok = setup_telegram_webhook()
        
        if webhook_ok:
            print("\n🎉 POST-DEPLOYMENT SETUP COMPLETE!")
            print("✅ Your Sofi AI bot is now live!")
            print("\n📱 Test your bot:")
            print("   - Send a message to your Telegram bot")
            print("   - Try: 'Hello', 'Check balance', 'Send money'")
        else:
            print("\n⚠️ Webhook setup failed - configure manually")
    else:
        print("\n❌ Deployment not ready - check Render logs")

if __name__ == "__main__":
    main()
