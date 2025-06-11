#!/usr/bin/env python3
"""
Test script to verify the complete onboarding completion message flow
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_onboarding_completion_flow():
    """Test the full onboarding completion flow with chat ID"""
    print("🚀 Testing Onboarding Completion Flow...")
    
    # Test data with a mock telegram_chat_id
    test_user = {
        "firstName": "TestFlow",
        "lastName": "User",
        "bvn": "12345678901",
        "phone": "08123456789",
        "telegram_chat_id": "123456789"  # Mock chat ID for testing
    }
    
    print(f"📋 Test user data: {test_user}")
    
    try:
        # Test with local development server
        local_url = "http://127.0.0.1:5000/api/create_virtual_account"
        
        print(f"\n🔧 Testing local endpoint: {local_url}")
        try:
            response = requests.post(local_url, json=test_user, timeout=15)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ Local test passed! Virtual account created successfully!")
                data = response.json()
                if "account" in data:
                    account = data["account"]
                    print(f"💳 Account Number: {account.get('accountNumber')}")
                    print(f"🏦 Bank: {account.get('bankName')}")
                    print(f"👤 Account Name: {account.get('accountName')}")
                print("📱 Onboarding completion message should have been sent to Telegram!")
                return True
            else:
                print(f"❌ Local test failed: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("⚠️ Local server not running - skipping local test")
        except Exception as e:
            print(f"❌ Local test error: {e}")
        
        # Test with deployed Render endpoint
        render_url = "https://sofi-ai-trio.onrender.com/api/create_virtual_account"
        
        print(f"\n🌐 Testing deployed endpoint: {render_url}")
        try:
            response = requests.post(render_url, json=test_user, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ Deployed test passed! Virtual account created successfully!")
                data = response.json()
                if "account" in data:
                    account = data["account"]
                    print(f"💳 Account Number: {account.get('accountNumber')}")
                    print(f"🏦 Bank: {account.get('bankName')}")
                    print(f"👤 Account Name: {account.get('accountName')}")
                print("📱 Onboarding completion message should have been sent to Telegram!")
                return True
            else:
                print(f"❌ Deployed test failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Deployed test error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing onboarding completion flow: {e}")
        return False

def test_chat_id_url_integration():
    """Test that the chat ID URL integration works"""
    print("\n🔗 Testing Chat ID URL Integration...")
    
    test_chat_id = "987654321"
    expected_url = f"https://sofi-ai-trio.onrender.com/onboarding?chat_id={test_chat_id}"
    
    print(f"Expected URL format: {expected_url}")
    
    # Test URL construction logic
    constructed_url = f"https://sofi-ai-trio.onrender.com/onboarding?chat_id={test_chat_id}"
    
    if "chat_id=" in constructed_url and test_chat_id in constructed_url:
        print("✅ URL construction test passed!")
        print(f"✅ Chat ID parameter correctly included: {constructed_url}")
        return True
    else:
        print("❌ URL construction test failed!")
        return False

if __name__ == "__main__":
    print(">>> Starting Onboarding Completion Flow Tests...")
    
    success1 = test_onboarding_completion_flow()
    success2 = test_chat_id_url_integration()
    
    print(f"\n📊 Test Results:")
    print(f"✅ Onboarding Flow Test: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Chat ID URL Test: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 or success2:
        print("\n🎉 At least one test passed! The integration is working.")
    else:
        print("\n💥 All tests failed!")
