#!/usr/bin/env python3
"""
TEST TOKEN EXTRACTION IN FRONTEND
==================================
Create a test transfer and verify the token extraction works
"""

import requests
import time
from utils.secure_pin_verification import secure_pin_verification

def test_token_extraction():
    """Test that frontend can extract tokens properly"""
    
    print("🧪 Testing Token Extraction...")
    
    # 1. Generate a test token
    test_data = {
        'chat_id': '5495194750',
        'transfer_data': {
            'amount': 100,
            'recipient_name': 'Test User',
            'account_number': '1234567890',
            'bank': 'Test Bank'
        }
    }
    
    token = secure_pin_verification.store_pending_transaction('TEST_TOKEN_123', test_data)
    
    print(f"✅ Generated test token: {token}")
    print(f"   Token length: {len(token)}")
    print(f"   Token chars: {set(token)}")
    
    # 2. Build the PIN verification URL
    pin_url = f"https://pipinstallsofi.com/verify-pin?token={token}"
    print(f"📱 PIN URL: {pin_url}")
    
    # 3. Test that the URL loads properly
    try:
        print(f"\n🌐 Testing PIN page load...")
        response = requests.get(pin_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ PIN page loads successfully")
            
            # Check if the token is in the page content
            if token in response.text:
                print("✅ Token found in page HTML")
            else:
                print("❌ Token NOT found in page HTML")
                
            # Check for React app
            if 'react' in response.text.lower():
                print("✅ React app detected in page")
            else:
                print("❌ React app NOT detected")
                
        else:
            print(f"❌ PIN page failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing PIN page: {e}")
    
    # 4. Show what the frontend should extract
    print(f"\n📋 Frontend should extract:")
    print(f"   URL: {pin_url}")
    print(f"   Token parameter: token={token}")
    print(f"   Token value: {token}")
    print(f"   Expected length: {len(token)}")
    
    print(f"\n✅ Test completed!")
    print(f"💡 Now test by:")
    print(f"   1. Opening the PIN URL in browser")
    print(f"   2. Checking browser console for token extraction logs")
    print(f"   3. Entering PIN '1998' and checking if secure_token is included")

if __name__ == "__main__":
    test_token_extraction()
