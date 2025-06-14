#!/usr/bin/env python3
"""
Fix Bitnob API integration to create real Bitcoin wallets
"""

import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append('.')

# Load environment variables
load_dotenv()

def test_bitnob_api_endpoints():
    """Test all possible Bitnob API endpoints to find the correct one"""
    
    api_key = os.getenv("BITNOB_SECRET_KEY")
    if not api_key:
        print("❌ BITNOB_SECRET_KEY not found in environment")
        return None
    
    base_url = "https://api.bitnob.co"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test user data
    test_user_id = f"test_api_fix_{int(datetime.now().timestamp())}"
    customer_email = f"{test_user_id}@sofiwallet.com"
    
    data = {
        "customerEmail": customer_email,
        "label": f"Sofi Wallet - User {test_user_id}",
        "currency": "NGN"
    }
    
    # Try different endpoints
    endpoints_to_test = [
        "/api/v1/customers/wallets",
        "/api/v1/wallets",
        "/api/v1/wallet", 
        "/api/v2/wallets",
        "/wallets",
        "/customer/wallets",
        "/api/wallets",
        "/v1/wallets"
    ]
    
    print("🧪 Testing Bitnob API Endpoints")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing: {url}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ SUCCESS! Response: {json.dumps(result, indent=2)}")
                return endpoint, result
            else:
                print(f"   ❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Exception: {str(e)}")
    
    print("\n⚠️ All endpoints failed - checking documentation...")
    return test_bitnob_documentation()

def test_bitnob_documentation():
    """Try to get information from Bitnob API documentation"""
    
    api_key = os.getenv("BITNOB_SECRET_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try to get API info or list existing wallets
    info_endpoints = [
        "https://api.bitnob.co/api/v1/wallets",  # GET request to list wallets
        "https://api.bitnob.co/api/v1/customers",
        "https://api.bitnob.co/api/v1/users",
        "https://api.bitnob.co/api/info",
        "https://api.bitnob.co/api/v1/info"
    ]
    
    print("\n📚 Checking API Documentation/Info")
    print("=" * 50)
    
    for url in info_endpoints:
        print(f"\n🔍 GET {url}")
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Response: {json.dumps(result, indent=2)}")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Exception: {str(e)}")
    
    return None

def create_bitnob_customer_first():
    """Try creating a customer first, then wallet"""
    
    api_key = os.getenv("BITNOB_SECRET_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    test_user_id = f"test_customer_{int(datetime.now().timestamp())}"
    customer_email = f"{test_user_id}@sofiwallet.com"
    
    print("\n👤 Testing Customer Creation First")
    print("=" * 50)
    
    # Step 1: Create customer
    customer_data = {
        "email": customer_email,
        "firstName": "Test",
        "lastName": "User"
    }
    
    customer_endpoints = [
        "https://api.bitnob.co/api/v1/customers",
        "https://api.bitnob.co/api/v1/customer",
        "https://api.bitnob.co/customers"
    ]
    
    customer_id = None
    
    for endpoint in customer_endpoints:
        print(f"\n🔍 Creating customer at: {endpoint}")
        try:
            response = requests.post(endpoint, headers=headers, json=customer_data, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Customer created: {json.dumps(result, indent=2)}")
                customer_id = result.get("data", {}).get("id") or result.get("id")
                break
            else:
                print(f"   ❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Exception: {str(e)}")
    
    # Step 2: Create wallet for customer
    if customer_id:
        print(f"\n💰 Creating wallet for customer: {customer_id}")
        
        wallet_data = {
            "customerId": customer_id,
            "label": f"Sofi Wallet - {test_user_id}",
            "currency": "NGN"
        }
        
        wallet_endpoints = [
            "https://api.bitnob.co/api/v1/wallets",
            f"https://api.bitnob.co/api/v1/customers/{customer_id}/wallets"
        ]
        
        for endpoint in wallet_endpoints:
            print(f"\n🔍 Creating wallet at: {endpoint}")
            try:
                response = requests.post(endpoint, headers=headers, json=wallet_data, timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"   ✅ Wallet created: {json.dumps(result, indent=2)}")
                    return endpoint, result
                else:
                    print(f"   ❌ Error: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   💥 Exception: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("🚀 Starting Bitnob API Integration Fix")
    print("=" * 60)
    
    # Test direct wallet creation
    result = test_bitnob_api_endpoints()
    
    if not result:
        # Try customer-first approach
        result = create_bitnob_customer_first()
    
    if result:
        endpoint, response = result
        print(f"\n🎉 SUCCESS! Working endpoint: {endpoint}")
        print("✅ Real Bitcoin addresses will now be generated!")
    else:
        print("\n⚠️ All tests failed. You may need to:")
        print("1. Check Bitnob API documentation")
        print("2. Verify API key permissions")
        print("3. Contact Bitnob support")
        print("4. For now, mock wallets will be used")
