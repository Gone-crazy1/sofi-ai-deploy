#!/usr/bin/env python3
"""
🧪 DIRECT VIRTUAL ACCOUNT CREATION TEST
=====================================

Test the create_virtual_account function directly
"""

import os
import sys
from datetime import datetime

def test_direct_account_creation():
    """Test account creation function directly"""
    print("🧪 TESTING DIRECT ACCOUNT CREATION")
    print("=" * 50)
    
    # Import the function
    try:
        sys.path.append('.')
        from main import create_virtual_account
        print("✅ create_virtual_account function imported successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test data
    test_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'bvn': '12345678901',
        'chat_id': 'test_user_123'
    }
    
    print(f"\n📋 Test Data:")
    print(f"   Name: {test_data['first_name']} {test_data['last_name']}")
    print(f"   BVN: {test_data['bvn']}")
    print(f"   Chat ID: {test_data['chat_id']}")
    
    # Check environment variables
    print(f"\n🔧 Checking Environment Variables:")
    env_vars = ['MONNIFY_BASE_URL', 'MONNIFY_API_KEY', 'MONNIFY_SECRET_KEY', 'MONNIFY_CONTRACT_CODE']
    missing_vars = []
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Present")
        else:
            print(f"   ❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("🔧 Add these to your .env file to test account creation")
        return False
    
    # Test the function
    print(f"\n🚀 Testing account creation...")
    try:
        result = create_virtual_account(
            first_name=test_data['first_name'],
            last_name=test_data['last_name'],
            bvn=test_data['bvn'],
            chat_id=test_data['chat_id']
        )
        
        print(f"\n📨 Result: {result}")
        
        if result and result.get('status') == 'success':
            print("✅ ACCOUNT CREATION SUCCESSFUL!")
            
            account_data = result.get('data', {})
            if account_data:
                print(f"\n💳 Virtual Account Details:")
                print(f"   Account Number: {account_data.get('accountNumber', 'N/A')}")
                print(f"   Account Name: {account_data.get('accountName', 'N/A')}")
                print(f"   Bank: {account_data.get('bankName', 'N/A')}")
                print(f"   Bank Code: {account_data.get('bankCode', 'N/A')}")
                print(f"   Reference: {account_data.get('accountReference', 'N/A')}")
            
            return True
            
        elif result and result.get('status') == 'error':
            print(f"❌ ACCOUNT CREATION FAILED")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False
            
        else:
            print(f"❌ UNEXPECTED RESULT: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during account creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monnify_auth():
    """Test Monnify authentication separately"""
    print(f"\n🔑 TESTING MONNIFY AUTHENTICATION")
    print("=" * 50)
    
    try:
        import requests
        
        monnify_base_url = os.getenv("MONNIFY_BASE_URL")
        monnify_api_key = os.getenv("MONNIFY_API_KEY") 
        monnify_secret_key = os.getenv("MONNIFY_SECRET_KEY")
        
        if not all([monnify_base_url, monnify_api_key, monnify_secret_key]):
            print("❌ Missing Monnify credentials")
            return False
        
        print(f"🔗 Base URL: {monnify_base_url}")
        print(f"🔑 API Key: {monnify_api_key[:10]}...")
        
        # Test authentication
        auth_url = f"{monnify_base_url}/api/v1/auth/login"
        
        print(f"\n📤 Testing authentication...")
        auth_response = requests.post(auth_url, auth=(monnify_api_key, monnify_secret_key), timeout=10)
        
        print(f"📨 Auth Response Status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            if auth_data.get("requestSuccessful"):
                token = auth_data.get("responseBody", {}).get("accessToken")
                if token:
                    print(f"✅ Authentication successful!")
                    print(f"🔑 Token: {token[:20]}...")
                    return True
                else:
                    print("❌ No access token in response")
                    return False
            else:
                print(f"❌ Auth unsuccessful: {auth_data}")
                return False
        else:
            print(f"❌ Auth failed: {auth_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SOFI AI ACCOUNT CREATION TEST")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # Test 1: Monnify authentication
    auth_success = test_monnify_auth()
    
    # Test 2: Direct account creation
    if auth_success:
        creation_success = test_direct_account_creation()
    else:
        print("\n⚠️  Skipping account creation test due to auth failure")
        creation_success = False
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"Account Creation: {'✅ PASS' if creation_success else '❌ FAIL'}")
    
    if auth_success and creation_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Virtual account creation system is working")
        print(f"🚀 Ready for production use")
    else:
        print(f"\n⚠️  Some tests failed")
        print(f"🔧 Check environment variables and Monnify configuration")
    
    print(f"\n🏁 Test completed!")
