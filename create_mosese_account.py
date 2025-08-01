#!/usr/bin/env python3
"""
Create New 9PSB Virtual Account - Fresh Test
"""

import os
import uuid
from dotenv import load_dotenv

load_dotenv()

def create_fresh_virtual_account():
    """Create a completely new virtual account with unique details"""
    print("🏦 Creating Fresh 9PSB Virtual Account...")
    
    try:
        from utils.ninepsb_api import NINEPSBApi
        
        # Generate unique user ID
        unique_id = f"mosese_{uuid.uuid4().hex[:8]}"
        
        api_key = os.getenv("NINEPSB_API_KEY")
        secret_key = os.getenv("NINEPSB_SECRET_KEY")
        base_url = os.getenv("NINEPSB_BASE_URL")
        
        print(f"🔑 Using API Key: {api_key[:20]}..." if api_key else "❌ No API Key")
        print(f"🌐 Base URL: {base_url}")
        print(f"👤 User ID: {unique_id}")
        
        psb = NINEPSBApi(api_key, secret_key, base_url)
        
        # Create virtual account with new user details
        # Generate valid Nigerian phone number (080XXXXXXXX format)
        import random
        phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        user_data = {
            "first_name": "Mosese",
            "last_name": "Smart Ayobami", 
            "email": f"mosese.smart.{uuid.uuid4().hex[:6]}@test.com",
            "phone": f"080{phone_suffix}"  # Valid Nigerian format: 08012345678
        }
        
        print(f"📝 User Data: {user_data}")
        
        response = psb.create_virtual_account(unique_id, user_data)
        
        print("🎯 Virtual Account Creation Response:")
        print("=" * 50)
        print(f"Response: {response}")
        
        if isinstance(response, dict):
            if response.get("success") or response.get("status") == "success":
                print("✅ Virtual Account Created Successfully!")
                
                # Extract account details if available
                if "data" in response:
                    data = response["data"]
                    print(f"🏦 Account Number: {data.get('account_number', 'N/A')}")
                    print(f"🏛️ Bank Name: {data.get('bank_name', 'N/A')}")
                    print(f"👤 Account Name: {data.get('account_name', 'N/A')}")
                
            elif "error" in response:
                print(f"❌ Error: {response['error']}")
                if "already exists" in str(response.get('error', '')).lower():
                    print("💡 Try with a different email or phone number")
            else:
                print("⚠️ Unexpected response format")
        else:
            print(f"📄 Raw Response: {response}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error creating virtual account: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_authentication_first():
    """Test authentication before creating account"""
    print("🔐 Testing Authentication First...")
    
    try:
        from utils.waas_auth import get_access_token
        token = get_access_token()
        
        if token:
            print(f"✅ Auth Success! Token: {token[:50]}...")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Fresh 9PSB Virtual Account Creation")
    print("👤 Name: Mosese Smart Ayobami")
    print("=" * 50)
    
    # Test auth first
    if test_authentication_first():
        print("\n" + "=" * 50)
        create_fresh_virtual_account()
    else:
        print("❌ Cannot proceed without authentication")
    
    print("\n✅ Test completed!")
