#!/usr/bin/env python3
"""
Test the CORRECT Paystack DVA Flow
Using the GET method to fetch DVA details
"""

import os
import sys
import importlib
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Force reload modules
if 'paystack.paystack_dva_api' in sys.modules:
    del sys.modules['paystack.paystack_dva_api']

from paystack.paystack_dva_api import PaystackDVAAPI
import json

def test_correct_dva_flow():
    """Test the correct DVA flow with GET endpoint"""
    try:
        print("🔄 Testing CORRECT Paystack DVA Flow...")
        
        dva_api = PaystackDVAAPI()
        
        # Test user data
        test_user = {
            'email': 'correct.flow.test@example.com',
            'first_name': 'Correct',
            'last_name': 'Flow',
            'phone': '+2348012345685'
        }
        
        print(f"Creating DVA for: {test_user['email']}")
        print("Using the correct 3-step flow...")
        
        # Use the corrected method
        result = dva_api.create_customer_with_dva(test_user)
        
        print("\n📋 CORRECT DVA Flow Result:")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            if result.get("account_number"):
                print("\n✅ COMPLETE SUCCESS!")
                print("=" * 50)
                print(f"👤 Customer Code: {result.get('customer_code')}")
                print(f"👤 Customer ID: {result.get('customer_id')}")
                print(f"🔢 Account Number: {result.get('account_number')}")
                print(f"👤 Account Name: {result.get('account_name')}")
                print(f"🏦 Bank: {result.get('bank_name')}")
                print(f"💳 DVA ID: {result.get('dva_id')}")
                print(f"💱 Currency: NGN")
                
                print("\n🎯 THIS IS WHAT USERS WILL GET!")
                print(f"Account Number: {result.get('account_number')}")
                print(f"Bank: {result.get('bank_name')}")
                
            elif result.get("pending_dva"):
                print("\n⚠️ DVA CREATION IN PROGRESS")
                print("=" * 50)
                print(f"Customer created: {result.get('customer_code')}")
                print("DVA assignment in progress...")
                print(f"Retry with: {result.get('retry_instructions')}")
                
                # Let's try to fetch it manually
                print("\n🔄 Attempting manual fetch...")
                fetch_result = dva_api.fetch_dva_by_customer(result.get('customer_code'))
                print("Manual fetch result:")
                print(json.dumps(fetch_result, indent=2))
        else:
            print(f"❌ DVA creation failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_correct_dva_flow()
