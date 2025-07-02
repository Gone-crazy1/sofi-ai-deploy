#!/usr/bin/env python3
"""
Fresh Test of Fixed DVA System
"""

import os
import sys
import importlib
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Force reload all modules
if 'paystack.paystack_dva_api' in sys.modules:
    del sys.modules['paystack.paystack_dva_api']
if 'paystack.paystack_service' in sys.modules:
    del sys.modules['paystack.paystack_service']

from paystack.paystack_dva_api import PaystackDVAAPI
import json

def test_fresh_dva_creation():
    """Test DVA creation with fresh module import"""
    try:
        print("🔄 Testing Fresh DVA Creation...")
        
        dva_api = PaystackDVAAPI()
        
        # Test user data
        test_user = {
            'email': 'fresh.dva.test@example.com',
            'first_name': 'Fresh',
            'last_name': 'DVA',
            'phone': '+2348012345684'
        }
        
        print(f"Creating DVA for: {test_user['email']}")
        
        result = dva_api.create_customer_with_dva(test_user)
        
        print("\n📋 Fresh DVA API Response:")
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
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_fresh_dva_creation()
