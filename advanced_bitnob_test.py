#!/usr/bin/env python3
"""
Implement working Bitnob API integration based on discovered endpoints
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

def create_customer_wallet_addresses():
    """Create wallet addresses for customers using the correct Bitnob API flow"""
    
    api_key = os.getenv("BITNOB_SECRET_KEY")
    if not api_key:
        print("❌ BITNOB_SECRET_KEY not found")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    base_url = "https://api.bitnob.co"
    
    print("🧪 Testing Customer Wallet Address Creation")
    print("=" * 50)
    
    # Step 1: Create a customer
    test_user_id = f"wallet_test_{int(datetime.now().timestamp())}"
    customer_email = f"{test_user_id}@sofiwallet.com"
    
    customer_data = {
        "email": customer_email,
        "firstName": "Test",
        "lastName": "Wallet"
    }
    
    print(f"👤 Creating customer: {customer_email}")
    
    try:
        response = requests.post(f"{base_url}/api/v1/customers", headers=headers, json=customer_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            customer_id = result.get("data", {}).get("id")
            print(f"✅ Customer created: {customer_id}")
            
            # Step 2: Try to generate wallet addresses for the customer
            return generate_wallet_addresses_for_customer(customer_id, headers, base_url)
            
        else:
            print(f"❌ Customer creation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return None

def generate_wallet_addresses_for_customer(customer_id, headers, base_url):
    """Try different methods to generate wallet addresses for a customer"""
    
    print(f"\n💰 Generating wallet addresses for customer: {customer_id}")
    
    # Method 1: Try address generation endpoints
    address_endpoints = [
        f"/api/v1/customers/{customer_id}/addresses",
        f"/api/v1/customers/{customer_id}/address",
        f"/api/v1/addresses",
        f"/api/v1/generateAddress",
        f"/api/v1/customer/addresses"
    ]
    
    address_data = {
        "customerId": customer_id,
        "currency": "BTC"
    }
    
    for endpoint in address_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing address generation: {endpoint}")
        
        try:
            response = requests.post(url, headers=headers, json=address_data, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ SUCCESS! Response: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
    
    # Method 2: Try wallet creation with different data structure
    print(f"\n🏦 Trying alternative wallet creation methods...")
    
    wallet_endpoints = [
        f"/api/v1/customer/{customer_id}/wallet",
        f"/api/v1/customers/{customer_id}/wallet",
        f"/api/v1/wallets/create"
    ]
    
    wallet_data_variations = [
        {
            "customerId": customer_id,
            "type": "bitcoin",
            "currency": "BTC"
        },
        {
            "customerId": customer_id,
            "walletType": "crypto",
            "currencies": ["BTC", "USDT"]
        },
        {
            "customer": customer_id,
            "generateAddresses": ["BTC", "USDT", "ETH"]
        }
    ]
    
    for endpoint in wallet_endpoints:
        for wallet_data in wallet_data_variations:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 Testing: {endpoint} with data: {wallet_data}")
            
            try:
                response = requests.post(url, headers=headers, json=wallet_data, timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"   ✅ SUCCESS! Response: {json.dumps(result, indent=2)}")
                    return result
                else:
                    print(f"   ❌ Error: {response.text}")
                    
            except Exception as e:
                print(f"   💥 Exception: {str(e)}")
    
    return None

def check_existing_customer_addresses():
    """Check if existing customers have wallet addresses"""
    
    api_key = os.getenv("BITNOB_SECRET_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    base_url = "https://api.bitnob.co"
    
    print(f"\n🔍 Checking existing customers for wallet addresses...")
    
    try:
        # Get customers
        response = requests.get(f"{base_url}/api/v1/customers", headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            customers = result.get("data", {}).get("customers", [])
            
            print(f"Found {len(customers)} customers")
            
            # Check first few customers for addresses
            for customer in customers[:3]:
                customer_id = customer.get("id")
                email = customer.get("email")
                
                print(f"\n👤 Customer: {email} ({customer_id})")
                
                # Try to get addresses for this customer
                address_endpoints = [
                    f"/api/v1/customers/{customer_id}/addresses",
                    f"/api/v1/customers/{customer_id}/wallets",
                    f"/api/v1/customers/{customer_id}"
                ]
                
                for endpoint in address_endpoints:
                    url = f"{base_url}{endpoint}"
                    try:
                        addr_response = requests.get(url, headers=headers, timeout=30)
                        if addr_response.status_code == 200:
                            addr_result = addr_response.json()
                            print(f"   ✅ {endpoint}: {json.dumps(addr_result, indent=4)}")
                        else:
                            print(f"   ❌ {endpoint}: {addr_response.status_code}")
                    except Exception as e:
                        print(f"   💥 {endpoint}: {str(e)}")
                        
    except Exception as e:
        print(f"💥 Error checking customers: {str(e)}")

if __name__ == "__main__":
    print("🚀 Advanced Bitnob API Integration Test")
    print("=" * 60)
    
    # Test wallet address creation
    result = create_customer_wallet_addresses()
    
    if not result:
        # Check existing customers
        check_existing_customer_addresses()
        
        print("\n🔧 RECOMMENDATION:")
        print("1. The Bitnob API may require a different flow")
        print("2. Check Bitnob documentation for address generation")
        print("3. Contact Bitnob support for correct endpoints")
        print("4. Consider using existing wallet addresses shown above")
