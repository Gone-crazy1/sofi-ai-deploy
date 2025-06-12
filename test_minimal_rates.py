#!/usr/bin/env python3
"""
Test minimal crypto rates module
"""

print("🔍 Testing rates module specifically...")

try:
    import requests
    print("✅ Requests imported")
    
    import os
    print("✅ OS imported")
    
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded")
    
    # Test the rates function directly
    def test_get_crypto_rates():
        """Test crypto rates API directly"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,tether',
                'vs_currencies': 'ngn'
            }
            
            print(f"🌐 Making request to: {url}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Response: {data}")
                return data
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None
    
    # Test the API call
    rates = test_get_crypto_rates()
    if rates:
        print("✅ Crypto rates API test successful!")
    else:
        print("❌ Crypto rates API test failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
