#!/usr/bin/env python3
"""
Test Paystack DVA Response Structure
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from paystack.paystack_service import PaystackService
import json

async def test_paystack_dva_response():
    """Test what the actual Paystack DVA response looks like"""
    try:
        print("🔄 Testing Paystack DVA Response Structure...")
        
        service = PaystackService()
        
        # Test user data
        test_user = {
            'email': 'test.dva.response@example.com',
            'first_name': 'DVA',
            'last_name': 'Response',
            'phone': '+2348012345679'
        }
        
        print(f"Creating account for: {test_user['email']}")
        
        result = service.create_user_account(test_user)
        
        print("📋 Full Paystack Response:")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            data = result.get("data", {})
            print("\n🔍 Response Structure Analysis:")
            print("=" * 50)
            print(f"Top level keys: {list(data.keys())}")
            
            if 'customer' in data:
                customer = data['customer']
                print(f"Customer keys: {list(customer.keys())}")
                print(f"Customer ID: {customer.get('id')}")
                print(f"Customer Code: {customer.get('customer_code')}")
            
            if 'dedicated_account' in data:
                dva = data['dedicated_account']
                print(f"DVA keys: {list(dva.keys())}")
                print(f"Account Number: {dva.get('account_number')}")
                print(f"Account Name: {dva.get('account_name')}")
                
                if 'bank' in dva:
                    bank = dva['bank']
                    print(f"Bank keys: {list(bank.keys())}")
                    print(f"Bank Name: {bank.get('name')}")
                    print(f"Bank Code: {bank.get('code')}")
        else:
            print(f"❌ Account creation failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_paystack_dva_response())
