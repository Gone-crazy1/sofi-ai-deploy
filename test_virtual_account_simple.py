#!/usr/bin/env python3
"""
Simple test script to create a virtual account using the production API
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_production_api():
    """Test the production virtual account creation API"""
    
    # Test data with email included
    test_user = {
        "firstName": "Test",
        "lastName": "User", 
        "bvn": "12345678901",
        "phone": "08123456789",
        "email": "test.user@example.com"  # Added missing email
    }
    
    url = "https://sofi-ai-trio.onrender.com/api/create_virtual_account"
    
    print("Testing production virtual account API...")
    print(f"Test data: {test_user}")
    print(f"\nTesting: {url}")
    
    try:
        response = requests.post(url, json=test_user, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            if data.get("success"):
                print("\n✅ SUCCESS: Virtual account created!")
                account = data.get("account", {})
                print(f"Account Number: {account.get('accountNumber')}")
                print(f"Bank: {account.get('bankName')}")
                print(f"Account Name: {account.get('accountName')}")
                return True
            else:
                print(f"\n❌ FAILED: {data.get('message')}")
                return False
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("https://sofi-ai-trio.onrender.com/health", timeout=10)
        print(f"\nHealth check - Status: {response.status_code}")
        print(f"Health response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"\nHealth check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Production API Tests...")
    
    # Test health first
    health_ok = test_health_endpoint()
    
    # Test virtual account creation
    success = test_production_api()
    
    if success:
        print("\n🎉 Production API test PASSED!")
    else:
        print("\n💥 Production API test FAILED!")
        if not health_ok:
            print("💡 Tip: Health check also failed - service might be down")
