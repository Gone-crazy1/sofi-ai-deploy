"""
Test Paystack Authentication
Verify that your secret key is properly configured
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_paystack_auth():
    """Test Paystack authentication with secret key"""
    
    print("🔐 Testing Paystack Authentication...")
    print("=" * 50)
    
    # Check if secret key exists
    secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    
    if not secret_key:
        print("❌ PAYSTACK_SECRET_KEY not found in environment!")
        print("📝 Add this to your .env file:")
        print("PAYSTACK_SECRET_KEY=sk_test_your_secret_key_here")
        return False
    
    # Mask the key for display
    masked_key = secret_key[:7] + "*" * (len(secret_key) - 11) + secret_key[-4:]
    print(f"✅ Secret key found: {masked_key}")
    
    # Test API call
    try:
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        # Test with banks endpoint (simple, no side effects)
        response = requests.get(
            "https://api.paystack.co/bank",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                banks_count = len(data.get("data", []))
                print(f"✅ Authentication successful!")
                print(f"📱 Found {banks_count} supported banks")
                return True
            else:
                print(f"❌ API Error: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_paystack_auth()
    
    if success:
        print("\n🎉 Paystack integration is ready!")
        print("✅ You can now:")
        print("  • Create virtual accounts")
        print("  • Process transfers") 
        print("  • Verify account numbers")
        print("  • Handle webhooks")
    else:
        print("\n❌ Please fix the authentication issues above")
