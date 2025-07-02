#!/usr/bin/env python3
"""
Test DVA Creation Directly
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from paystack.paystack_dva_api import PaystackDVAAPI
import json

def test_dva_creation_directly():
    """Test DVA creation directly"""
    try:
        print("🔄 Testing DVA Creation Directly...")
        
        dva_api = PaystackDVAAPI()
        
        # Test user data
        test_user = {
            'email': 'dva.direct.test@example.com',
            'first_name': 'DVA',
            'last_name': 'Direct',
            'phone': '+2348012345683'
        }
        
        print(f"Creating DVA for: {test_user['email']}")
        
        result = dva_api.create_customer_with_dva(test_user)
        
        print("\n📋 DVA API Response:")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print("\n✅ DVA Creation Successful!")
            print(f"Account Number: {result.get('account_number')}")
            print(f"Account Name: {result.get('account_name')}")
            print(f"Bank Name: {result.get('bank_name')}")
            print(f"Customer Code: {result.get('customer_code')}")
            print(f"Customer ID: {result.get('customer_id')}")
        else:
            print(f"❌ DVA creation failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_dva_creation_directly()
