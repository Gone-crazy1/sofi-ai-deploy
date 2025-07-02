#!/usr/bin/env python3
"""
Test Real Telegram User Onboarding

This script simulates a real Telegram user going through the onboarding process
and receiving account details via Telegram.
"""

import requests
import json
import time

def test_telegram_user_onboarding():
    """Test onboarding for a real Telegram user"""
    
    # Simulate a real Telegram chat ID
    telegram_chat_id = "123456789"  # Real-looking Telegram chat ID
    
    # Test user data
    test_user = {
        "telegram_id": telegram_chat_id,
        "full_name": "John Doe Telegram",
        "phone": "+2347012345678",
        "email": "johndoe@telegram.com",
        "address": "Abuja, Nigeria",
        "bvn": "12345678901"
    }
    
    print("🧪 Testing Real Telegram User Onboarding")
    print("=" * 55)
    print(f"📧 Test User: {test_user['full_name']}")
    print(f"📱 Phone: {test_user['phone']}")
    print(f"🆔 Telegram ID: {test_user['telegram_id']} (Real user)")
    print()
    
    try:
        # Make API call
        url = "http://127.0.0.1:5000/api/onboard"
        
        print(f"🌐 Making POST request to: {url}")
        print(f"📦 Payload: {json.dumps(test_user, indent=2)}")
        print()
        
        response = requests.post(
            url,
            json=test_user,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print()
        
        # Parse response
        result = response.json()
        print("📋 Response Body:")
        print(json.dumps(result, indent=2))
        print()
        
        if response.status_code == 200 and result.get('success'):
            print("✅ SUCCESS: Telegram user onboarded successfully!")
            print()
            print("🎯 Expected Behavior:")
            print("   ✅ User registered in database")
            print("   ✅ Virtual account created with Paystack")
            print("   ✅ Account details sent to user's Telegram chat")
            print("   ✅ User can now interact with Sofi on Telegram")
            
            # Show account details
            account_details = result.get('account_details', {})
            if account_details:
                print()
                print("🏦 Virtual Account Details (Sent to Telegram):")
                print(f"   📧 Account Number: {account_details.get('account_number')}")
                print(f"   👤 Account Name: {account_details.get('account_name')}")
                print(f"   🏛️ Bank: {account_details.get('bank_name')}")
                print(f"   🆔 Customer Code: {result.get('customer_code')}")
                
                print()
                print("💬 Telegram Message Preview:")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"🎉 Account Created Successfully!")
                print(f"")
                print(f"Welcome to Sofi AI, {test_user['full_name']}! Your virtual account is ready.")
                print(f"")
                print(f"💳 Your Account Details:")
                print(f"━━━━━━━━━━━━━━━━━━━━━")
                print(f"🏦 Account Number: {account_details.get('account_number')}")
                print(f"👤 Account Name: {account_details.get('account_name')}")
                print(f"🏛️ Bank: {account_details.get('bank_name')}")
                print(f"🆔 Customer ID: {result.get('customer_code')}")
                print(f"━━━━━━━━━━━━━━━━━━━━━")
                print(f"")
                print(f"🚀 Next Steps:")
                print(f"✅ Fund your account using the details above")
                print(f"✅ Start sending money instantly")
                print(f"✅ Buy airtime & data at best rates")
                print(f"✅ Check your balance anytime")
                print(f"")
                print(f"💬 Try saying:")
                print(f"• \"Check my balance\"")
                print(f"• \"Send ₦1000 to John\"")
                print(f"• \"Buy ₦200 airtime\"")
                print(f"")
                print(f"🤖 I'm here to help with all your financial needs!")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
        else:
            print("❌ FAILED: Telegram user onboarding failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server!")
        print("   Make sure the Flask server is running on http://127.0.0.1:5000")
        
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    test_telegram_user_onboarding()
