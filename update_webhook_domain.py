"""
Update Telegram Bot Webhook to use new domain
Run this script to set the webhook to your new domain
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def set_telegram_webhook():
    """Set Telegram webhook to new domain"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    new_domain = "https://pipinstallsofi.com"
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return False
    
    # Set webhook URL
    webhook_url = f"{new_domain}/webhook"
    
    # Telegram API endpoint to set webhook
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    payload = {
        "url": webhook_url,
        "allowed_updates": ["message", "callback_query", "inline_query"]
    }
    
    try:
        print(f"🔗 Setting Telegram webhook to: {webhook_url}")
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Telegram webhook set successfully!")
            print(f"📍 Webhook URL: {webhook_url}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {str(e)}")
        return False

def get_webhook_info():
    """Get current webhook information"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            current_url = webhook_info.get("url", "Not set")
            pending_updates = webhook_info.get("pending_update_count", 0)
            last_error = webhook_info.get("last_error_message", "None")
            
            print(f"📊 Current Webhook Info:")
            print(f"   URL: {current_url}")
            print(f"   Pending Updates: {pending_updates}")
            print(f"   Last Error: {last_error}")
        else:
            print(f"❌ Failed to get webhook info: {result.get('description')}")
            
    except Exception as e:
        print(f"❌ Error getting webhook info: {str(e)}")

if __name__ == "__main__":
    print("🚀 Sofi AI - Telegram Webhook Updater")
    print("=" * 50)
    
    # Show current webhook info
    print("\n📊 Current webhook status:")
    get_webhook_info()
    
    # Set new webhook
    print(f"\n🔄 Updating webhook to new domain...")
    success = set_telegram_webhook()
    
    if success:
        print("\n✅ Webhook update completed!")
        print("\n📊 Updated webhook status:")
        get_webhook_info()
        
        print(f"\n🎉 Your Sofi AI bot is now configured for:")
        print(f"   🌐 Domain: https://pipinstallsofi.com")
        print(f"   📱 Telegram: @getsofi_bot")
        print(f"   🔗 Webhook: https://pipinstallsofi.com/webhook")
        print(f"   💳 Paystack: https://pipinstallsofi.com/api/paystack/webhook")
        
    else:
        print("\n❌ Webhook update failed!")
        print("Please check your TELEGRAM_BOT_TOKEN and try again.")
        
    print("\n" + "=" * 50)
