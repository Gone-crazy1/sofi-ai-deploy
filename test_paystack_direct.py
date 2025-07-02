#!/usr/bin/env python3
"""
Test Paystack DVA API Directly
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_paystack_dva_direct():
    """Test Paystack DVA API directly to understand the response"""
    try:
        secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        base_url = "https://api.paystack.co"
        
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Create customer first
        print("🔄 Step 1: Creating customer...")
        customer_url = f"{base_url}/customer"
        customer_payload = {
            "email": "direct.test@example.com",
            "first_name": "Direct",
            "last_name": "Test",
            "phone": "+2348012345680"
        }
        
        customer_response = requests.post(customer_url, json=customer_payload, headers=headers)
        customer_result = customer_response.json()
        
        print("Customer Creation Response:")
        print(json.dumps(customer_result, indent=2))
        
        if customer_result.get("status"):
            customer_code = customer_result["data"]["customer_code"]
            customer_id = customer_result["data"]["id"]
            
            print(f"\n✅ Customer created: {customer_code}")
            
            # Test 2: Create DVA for customer
            print("\n🔄 Step 2: Creating dedicated virtual account...")
            dva_url = f"{base_url}/dedicated_account"
            dva_payload = {
                "customer": customer_code,
                "preferred_bank": "wema-bank"
            }
            
            dva_response = requests.post(dva_url, json=dva_payload, headers=headers)
            dva_result = dva_response.json()
            
            print("DVA Creation Response:")
            print(json.dumps(dva_result, indent=2))
            
            if dva_result.get("status"):
                dva_data = dva_result["data"]
                print(f"\n✅ DVA Created!")
                print(f"Account Number: {dva_data.get('account_number')}")
                print(f"Account Name: {dva_data.get('account_name')}")
                print(f"Bank: {dva_data.get('bank', {}).get('name')}")
                print(f"Bank Code: {dva_data.get('bank', {}).get('code')}")
            else:
                print(f"❌ DVA creation failed: {dva_result}")
        else:
            print(f"❌ Customer creation failed: {customer_result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_paystack_dva_direct()
