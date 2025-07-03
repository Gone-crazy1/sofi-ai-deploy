#!/usr/bin/env python3
"""
Test the improved transfer flow
"""

import requests
import json
import time
import sys
import os

# Configuration
WEBHOOK_URL = "http://localhost:5000/webhook"
TEST_CHAT_ID = "5495194750"  # Use your actual test chat ID
TEST_ACCOUNT = "8104965538"  # Test account number
TEST_BANK = "Opay"  # Test bank
TEST_AMOUNT = "100"  # Test amount

def simulate_message(chat_id, text):
    """Simulate a Telegram message"""
    print(f"\n📤 Sending message: '{text}'")
    
    payload = {
        "update_id": int(time.time()),
        "message": {
            "message_id": int(time.time()),
            "from": {
                "id": int(chat_id),
                "is_bot": False,
                "first_name": "Test",
                "username": "test_user"
            },
            "chat": {
                "id": int(chat_id),
                "first_name": "Test",
                "type": "private"
            },
            "date": int(time.time()),
            "text": text
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"🔄 Response status: {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return None

def simulate_callback_query(chat_id, callback_data):
    """Simulate a Telegram callback query"""
    print(f"\n📤 Sending callback query: '{callback_data}'")
    
    payload = {
        "update_id": int(time.time()),
        "callback_query": {
            "id": str(int(time.time())),
            "from": {
                "id": int(chat_id),
                "is_bot": False,
                "first_name": "Test",
                "username": "test_user"
            },
            "message": {
                "message_id": int(time.time()),
                "from": {
                    "id": 123456789,
                    "is_bot": True,
                    "first_name": "SofiAI",
                    "username": "sofi_ai_bot"
                },
                "chat": {
                    "id": int(chat_id),
                    "first_name": "Test",
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "Test message"
            },
            "chat_instance": str(int(time.time())),
            "data": callback_data
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"🔄 Response status: {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ Error sending callback query: {e}")
        return None

def run_test():
    """Test the improved transfer flow"""
    print("🧪 TESTING IMPROVED TRANSFER FLOW")
    print("=" * 50)
    
    # Step 1: Send Xara-style transfer command
    print("\n1️⃣ Testing Xara-style transfer command...")
    xara_command = f"{TEST_ACCOUNT} {TEST_BANK} send {TEST_AMOUNT}"
    simulate_message(TEST_CHAT_ID, xara_command)
    
    # Wait for response
    time.sleep(2)
    
    print("\nCheck that you received:")
    print("- Account Verified message")
    print("- Professional confirmation with bank and account holder name")
    print("- 'Enter My PIN' button instead of PIN keyboard")
    
    print("\nNow click the 'Enter My PIN' button in Telegram to continue testing")
    print("=" * 50)
    print("Test complete! If everything works correctly, you should see:")
    print("1. Account verification message (not 'Verifying account...')")
    print("2. Proper account holder name and bank display")
    print("3. 'Enter My PIN' button (not a PIN keyboard)")
    print("4. When PIN button is clicked, a secure PIN entry keyboard should appear")
    print("=" * 50)

if __name__ == "__main__":
    run_test()
