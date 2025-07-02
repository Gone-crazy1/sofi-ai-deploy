#!/usr/bin/env python3
"""
Test Complete Fixed Onboarding System
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from utils.user_onboarding import onboarding_service
import json

async def test_complete_onboarding():
    """Test the complete fixed onboarding system"""
    try:
        print("🔄 Testing Complete Fixed Onboarding System...")
        
        # Test user data - realistic data
        test_user = {
            'telegram_id': '123456789',
            'full_name': 'Test Complete User',
            'phone': '+2348012345681',
            'email': 'test.complete@example.com',
            'address': 'Lagos, Nigeria',
            'bvn': '12345678901'  # Include BVN for verification
        }
        
        print(f"Creating account for: {test_user['full_name']}")
        print(f"Email: {test_user['email']}")
        print(f"Phone: {test_user['phone']}")
        
        result = await onboarding_service.create_new_user(test_user)
        
        print("\n📋 Onboarding Result:")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            account_details = result.get('account_details', {})
            print("\n✅ ONBOARDING SUCCESSFUL!")
            print("=" * 50)
            print(f"👤 User: {result['full_name']}")
            print(f"📧 Customer ID: {result['customer_id']}")
            print(f"🔢 Account Number: {account_details['account_number']}")
            print(f"👤 Account Name: {account_details['account_name']}")
            print(f"🏦 Bank: {account_details['bank_name']}")
            print(f"💰 Status: {'✅ Verified' if result.get('is_verified') else '⚠️ Unverified'}")
            
            print("\n🎯 Account Ready for Users!")
            print(f"Users can now transfer money to: {account_details['account_number']} ({account_details['bank_name']})")
            
        else:
            print(f"❌ Onboarding failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_complete_onboarding())
