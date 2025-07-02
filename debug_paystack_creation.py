#!/usr/bin/env python3
"""
Debug the Fixed Paystack Account Creation
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

async def debug_paystack_account_creation():
    """Debug what the Paystack service is returning"""
    try:
        print("🔄 Debugging Paystack Account Creation...")
        
        service = PaystackService()
        
        # Test user data
        test_user = {
            'email': 'debug.test@example.com',
            'first_name': 'Debug',
            'last_name': 'Test',
            'phone': '+2348012345682'
        }
        
        print(f"Creating account for: {test_user['email']}")
        
        result = service.create_user_account(test_user)
        
        print("\n📋 Full Paystack Service Response:")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
        print("\n🔍 Analyzing Response Structure:")
        print("=" * 50)
        
        if result.get("success"):
            print("✅ Account creation successful")
            
            # Check for account_info
            account_info = result.get('account_info')
            if account_info:
                print(f"✅ Account info found: {list(account_info.keys())}")
                print(f"Account Number: {account_info.get('account_number')}")
                print(f"Account Name: {account_info.get('account_name')}")
                print(f"Bank Name: {account_info.get('bank_name')}")
            else:
                print("❌ No account_info in response")
                
            # Check data structure
            data = result.get('data', {})
            print(f"Data keys: {list(data.keys())}")
            
        else:
            print(f"❌ Account creation failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(debug_paystack_account_creation())
