#!/usr/bin/env python3
"""
Test Deposit Notification System

This script simulates a Paystack webhook for a successful payment
to test if Sofi sends deposit notifications to users.
"""

import requests
import json
import time

def test_deposit_notification():
    """Test deposit notification via webhook simulation"""
    
    # Simulate a Paystack charge.success webhook
    webhook_payload = {
        "event": "charge.success",
        "data": {
            "id": 123456789,
            "domain": "live",
            "status": "success",
            "reference": f"sofi_test_deposit_{int(time.time())}",
            "amount": 500000,  # ₦5,000 in kobo
            "message": "Payment successful",
            "gateway_response": "Successful",
            "paid_at": "2025-07-02T14:30:45.000Z",
            "created_at": "2025-07-02T14:30:40.000Z",
            "channel": "dedicated_nuban",
            "currency": "NGN",
            "customer": {
                "id": 289200041,
                "first_name": "John",
                "last_name": "Doe Telegram",
                "email": "johndoe@telegram.com",
                "customer_code": "CUS_qvu63vm5o3t59do",
                "phone": "+2347012345678"
            },
            "authorization": {
                "receiver_bank_account_number": "9325041701",
                "receiver_bank": "035"
            }
        }
    }
    
    print("🧪 Testing Deposit Notification System")
    print("=" * 50)
    print(f"💰 Simulating deposit: ₦5,000")
    print(f"👤 User: John Doe Telegram")
    print(f"🏦 Account: 9325041701")
    print(f"🆔 Customer: CUS_qvu63vm5o3t59do")
    print()
    
    try:
        # Send webhook to local server
        url = "http://127.0.0.1:5000/api/paystack/webhook"
        
        print(f"🌐 Sending webhook to: {url}")
        print(f"📦 Payload: {json.dumps(webhook_payload, indent=2)}")
        print()
        
        response = requests.post(
            url,
            json=webhook_payload,
            headers={
                'Content-Type': 'application/json'
                # Removed X-Paystack-Signature for testing without verification
            },
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ SUCCESS: Webhook processed successfully!")
                print()
                print("🎯 Expected Results:")
                print("   ✅ User balance updated to ₦5,000")
                print("   ✅ Transaction recorded in database")
                print("   ✅ Beautiful notification sent to Telegram")
                print()
                print("📱 Expected Telegram Message:")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("💰 Payment Received!")
                print("")
                print("━━━━━━━━━━━━━━━━━━━━━")
                print("💵 Amount: ₦5,000.00")
                print("💳 New Balance: ₦5,000.00")
                print("🕒 Time: 02/07/2025 2:30 PM")
                print("━━━━━━━━━━━━━━━━━━━━━")
                print("")
                print("🎉 Your account has been funded successfully!")
                print("")
                print("💬 Try saying:")
                print("• \"Check my balance\"")
                print("• \"Send money to John\"")
                print("• \"Buy airtime\"")
                print("")
                print("Thank you for using Sofi AI! 🤖")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            else:
                print("❌ FAILED: Webhook processing failed!")
                print(f"   Error: {result}")
        else:
            print("❌ FAILED: Webhook request failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server!")
        print("   Make sure the Flask server is running on http://127.0.0.1:5000")
        
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    test_deposit_notification()
