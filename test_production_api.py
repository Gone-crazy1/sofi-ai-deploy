#!/usr/bin/env python3
"""
Simple test for virtual account creation API
"""
import requests
import json

def test_production_api():
    """Test the production virtual account API"""
    
    # Test data
    test_user = {
        "firstName": "Test",
        "lastName": "User", 
        "bvn": "12345678901",
        "phone": "08123456789"
    }
    
    print("Testing production virtual account API...")
    print(f"Test data: {test_user}")
    
    try:
        # Test production endpoint
        url = "https://sofi-ai-trio.onrender.com/api/create_virtual_account"
        
        print(f"\nTesting: {url}")
        response = requests.post(url, json=test_user, timeout=60)
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            if data.get("success"):
                print("\n✅ SUCCESS: Virtual account created!")
                account = data.get("account", {})
                if account:
                    print(f"Account Number: {account.get('accountNumber', 'N/A')}")
                    print(f"Bank: {account.get('bankName', 'N/A')}")
                    print(f"Account Name: {account.get('accountName', 'N/A')}")
                return True
            else:
                print(f"\n❌ FAILED: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_production_api()
