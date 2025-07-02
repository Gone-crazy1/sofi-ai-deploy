#!/usr/bin/env python3
"""
Test Web Onboarding API

This script tests the web onboarding endpoint by making a POST request
to /api/onboard with sample user data.
"""

import requests
import json
import time

def test_web_onboarding():
    """Test the web onboarding API endpoint"""
    
    # Test user data
    test_user = {
        "telegram_id": f"web_user_{int(time.time())}",  # Unique ID for web users
        "full_name": "Test Web User",
        "phone": "+2348123456789",
        "email": "testweb@example.com",
        "address": "Lagos, Nigeria",
        "bvn": ""
    }
    
    print("🧪 Testing Web Onboarding API")
    print("=" * 50)
    print(f"📧 Test User: {test_user['full_name']}")
    print(f"📱 Phone: {test_user['phone']}")
    print(f"🆔 Telegram ID: {test_user['telegram_id']}")
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
        print(f"📄 Response Headers: {dict(response.headers)}")
        print()
        
        # Parse response
        result = response.json()
        print("📋 Response Body:")
        print(json.dumps(result, indent=2))
        print()
        
        if response.status_code == 200 and result.get('success'):
            print("✅ SUCCESS: User onboarded successfully!")
            
            # Show account details
            account_details = result.get('account_details', {})
            if account_details:
                print()
                print("🏦 Virtual Account Details:")
                print(f"   Account Number: {account_details.get('account_number')}")
                print(f"   Account Name: {account_details.get('account_name')}")
                print(f"   Bank: {account_details.get('bank_name')}")
                print(f"   Bank Code: {account_details.get('bank_code')}")
                
            print(f"   Customer Code: {result.get('customer_code')}")
            print(f"   Customer ID: {result.get('customer_id')}")
            
        else:
            print("❌ FAILED: User onboarding failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
            if result.get('pending_dva'):
                print("⏳ DVA creation is still pending - try again in a few moments")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server!")
        print("   Make sure the Flask server is running on http://127.0.0.1:5000")
        
    except requests.exceptions.Timeout:
        print("⏰ ERROR: Request timed out!")
        print("   The onboarding process may be taking longer than expected")
        
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    test_web_onboarding()
