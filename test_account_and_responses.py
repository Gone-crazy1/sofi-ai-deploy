#!/usr/bin/env python3
"""
Test Account Creation and Basic Sofi Responses
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_account_creation():
    """Test virtual account creation process"""
    print("🏦 TESTING ACCOUNT CREATION")
    print("=" * 50)
    
    try:
        # Import the necessary modules
        from main import handle_message
        from utils.user_onboarding import onboarding_service
        
        # Test chat ID (use your admin ID for testing)
        test_chat_id = "5495194750"
        
        print(f"📱 Testing with chat ID: {test_chat_id}")
        
        # Test 1: Check if user already has account
        print("\n🔍 Test 1: Checking existing account...")
        virtual_account = await onboarding_service.check_virtual_account(test_chat_id)
        if virtual_account:
            print(f"✅ User already has account: {virtual_account.get('accountNumber', 'N/A')}")
        else:
            print("❌ No existing account found")
        
        # Test 2: Test "hello" message
        print("\n💬 Test 2: Testing 'hello' message...")
        response = await handle_message(test_chat_id, "hello")
        print(f"📝 Sofi's response to 'hello': {response[:200]}...")
        
        # Test 3: Test "create account" message
        print("\n🏦 Test 3: Testing 'create account' message...")
        response = await handle_message(test_chat_id, "create account")
        print(f"📝 Sofi's response to 'create account': {response[:200]}...")
        
        # Test 4: Test balance inquiry
        print("\n💰 Test 4: Testing balance inquiry...")
        response = await handle_message(test_chat_id, "check my balance")
        print(f"📝 Sofi's response to balance inquiry: {response[:200]}...")
        
        print("\n✅ Account creation tests completed!")
        
    except Exception as e:
        print(f"❌ Error in account creation test: {e}")
        import traceback
        traceback.print_exc()

async def test_basic_responses():
    """Test basic Sofi responses to common messages"""
    print("\n🤖 TESTING BASIC SOFI RESPONSES")
    print("=" * 50)
    
    test_messages = [
        "hello",
        "hi",
        "how are you",
        "what can you do",
        "help",
        "who are you"
    ]
    
    test_chat_id = "5495194750"
    
    try:
        from main import handle_message
        
        for message in test_messages:
            print(f"\n💬 Message: '{message}'")
            response = await handle_message(test_chat_id, message)
            print(f"📝 Response: {response[:150]}...")
            
    except Exception as e:
        print(f"❌ Error in basic response test: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("🧪 SOFI AI - ACCOUNT CREATION & RESPONSE TESTS")
    print("=" * 60)
    
    await test_account_creation()
    await test_basic_responses()
    
    print("\n🎉 ALL TESTS COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())
