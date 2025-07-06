#!/usr/bin/env python3
"""
Test Telegram Integration
=========================
Test if Sofi AI assistant responds properly now
"""

import requests
import json
import time

def test_telegram_webhook():
    """Test Telegram webhook functionality"""
    
    print("🤖 Testing Telegram Webhook Integration...")
    
    # Test webhook with a sample message
    webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": int(time.time()),
            "text": "hi"
        }
    }
    
    try:
        response = requests.post(
            "https://pipinstallsofi.com/webhook",
            json=webhook_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TelegramBot (like TwitterBot)"
            },
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ PASS: Webhook processed successfully")
            try:
                result = response.json()
                print(f"Response Data: {result}")
            except:
                print("Response is not JSON")
        else:
            print(f"❌ FAIL: Webhook returned {response.status_code}")
            print(f"Response Text: {response.text}")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n🎯 Telegram integration test completed!")

if __name__ == "__main__":
    test_telegram_webhook()
