#!/usr/bin/env python3
"""
Test Virtual Account Creation Process
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_create_virtual_account():
    """Test the virtual account creation process"""
    print("🏦 TESTING VIRTUAL ACCOUNT CREATION")
    print("=" * 50)
    
    try:
        # Import necessary modules
        from main import check_virtual_account, handle_message
        from utils.user_onboarding import onboarding_service
        
        # Test with a new chat ID (not your admin ID)
        test_chat_id = "1234567890"  # Fake ID for testing
        
        print(f"📱 Testing with chat ID: {test_chat_id}")
        
        # Test 1: Check if user has existing account
        print("\n🔍 Test 1: Checking for existing virtual account...")
        virtual_account = await check_virtual_account(test_chat_id)
        if virtual_account:
            print(f"✅ User has existing account: {virtual_account}")
        else:
            print("❌ No existing account found (expected for new user)")
        
        # Test 2: Test account creation request
        print("\n🏦 Test 2: Testing account creation request...")
        response = await handle_message(test_chat_id, "I want to create an account")
        print(f"📝 Sofi's response:")
        print(response)
        
        # Test 3: Test account status check
        print("\n📊 Test 3: Testing account status check...")
        response = await handle_message(test_chat_id, "check my account status")
        print(f"📝 Sofi's response:")
        print(response)
        
        print("\n✅ Virtual account tests completed!")
        
    except Exception as e:
        print(f"❌ Error in virtual account test: {e}")
        import traceback
        traceback.print_exc()

async def test_onboarding_flow():
    """Test the complete onboarding flow"""
    print("\n🚀 TESTING ONBOARDING FLOW")
    print("=" * 50)
    
    try:
        from monnify.monnify_api import MonnifyAPI
        
        # Initialize Monnify API
        monnify = MonnifyAPI()
        
        # Test data
        test_data = {
            'full_name': 'John Test User',
            'phone': '08012345678',
            'email': 'test@example.com',
            'bvn': '12345678901',
            'telegram_chat_id': '1234567890'
        }
        
        print("🔧 Test data prepared:")
        for key, value in test_data.items():
            if key != 'bvn':  # Don't show BVN in logs
                print(f"   {key}: {value}")
        
        # Test virtual account creation (this would normally be done via the web form)
        print("\n🏦 Testing virtual account creation with Monnify...")
        print("(This simulates what happens after user fills the onboarding form)")
          # Create virtual account
        account_result = monnify.create_virtual_account({
            'email': test_data['email'],
            'first_name': test_data['full_name'].split()[0],
            'last_name': ' '.join(test_data['full_name'].split()[1:]),
            'phone': test_data['phone'],
            'user_id': test_data['telegram_chat_id']
        })
        
        print(f"📊 Account creation result: {account_result}")
        
        if account_result.get('success'):
            print("✅ Virtual account creation successful!")
            account_details = account_result.get('data', {})
            print(f"   Account Number: {account_details.get('accountNumber')}")
            print(f"   Bank Name: {account_details.get('bankName')}")
            print(f"   Account Name: {account_details.get('accountName')}")
        else:
            print(f"❌ Virtual account creation failed: {account_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Error in onboarding flow test: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all account creation tests"""
    print("🧪 SOFI AI - VIRTUAL ACCOUNT CREATION TESTS")
    print("=" * 60)
    
    await test_create_virtual_account()
    await test_onboarding_flow()
    
    print("\n🎉 ALL ACCOUNT CREATION TESTS COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())
