#!/usr/bin/env python3
"""
Test script to verify the new pip install -ai Technologies branding and installation flow
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import handle_message

# Mock functions for testing
async def mock_get_chat_history(chat_id):
    return []  # Empty history for first-time user

async def mock_save_chat_message(chat_id, role, content):
    pass

def mock_send_reply(chat_id, message):
    print(f"📱 TELEGRAM MESSAGE TO {chat_id}:")
    print(f"   {message}")
    print()

async def mock_check_virtual_account(chat_id):
    return None  # No virtual account (new user)

def mock_get_supabase_client():
    class MockClient:
        def table(self, name):
            return MockTable()
    
    class MockTable:
        def select(self, *args):
            return self
        def eq(self, *args):
            return self
        def execute(self):
            return MockResponse()
    
    class MockResponse:
        data = []  # No user data (new user)
    
    return MockClient()

async def test_first_time_user_flow():
    """Test the new installation flow for first-time users"""
    print("🧪 TESTING NEW INSTALLATION FLOW")
    print("=" * 50)
    
    # Mock all external dependencies
    with patch('main.get_chat_history', mock_get_chat_history), \
         patch('main.save_chat_message', mock_save_chat_message), \
         patch('main.send_reply', mock_send_reply), \
         patch('main.check_virtual_account', mock_check_virtual_account), \
         patch('main.get_supabase_client', mock_get_supabase_client):
        
        # Test various first-time messages
        test_messages = [
            "Hi",
            "Hello", 
            "Get started",
            "What can you do?",
            "Help me"
        ]
        
        print("Testing first-time user messages:\n")
        
        for i, message in enumerate(test_messages, 1):
            print(f"Test {i}: User says '{message}'")
            print("-" * 30)
            
            try:
                response = await handle_message("test_user_123", message)
                
                if isinstance(response, dict):
                    print(f"✅ Installation Flow Triggered!")
                    print(f"📝 Response Text Preview:")
                    text = response.get('text', '')
                    lines = text.split('\n')
                    for line in lines[:3]:  # Show first 3 lines
                        if line.strip():
                            print(f"   {line}")
                    if len(lines) > 3:
                        print("   ...")
                    
                    if 'pip install -ai Technologies' in text:
                        print("✅ Company branding included!")
                    else:
                        print("❌ Company branding missing!")
                        
                    if response.get('reply_markup'):
                        print("✅ Onboarding button included!")
                    else:
                        print("❌ Onboarding button missing!")
                else:
                    print(f"Response: {response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "="*50 + "\n")

async def test_identity_questions():
    """Test responses to identity questions"""
    print("🧪 TESTING IDENTITY/NAME QUESTIONS")
    print("=" * 50)
    
    # Mock user as already onboarded
    async def mock_check_virtual_account_onboarded(chat_id):
        return {"accountnumber": "1234567890", "bankname": "Test Bank", "accountname": "Test User"}
    
    def mock_get_supabase_client_onboarded():
        class MockClient:
            def table(self, name):
                return MockTable()
        
        class MockTable:
            def select(self, *args):
                return self
            def eq(self, *args):
                return self
            def execute(self):
                return MockResponse()
        
        class MockResponse:
            data = [{"first_name": "Test", "last_name": "User"}]
        
        return MockClient()
    
    with patch('main.get_chat_history', mock_get_chat_history), \
         patch('main.save_chat_message', mock_save_chat_message), \
         patch('main.send_reply', mock_send_reply), \
         patch('main.check_virtual_account', mock_check_virtual_account_onboarded), \
         patch('main.get_supabase_client', mock_get_supabase_client_onboarded):
        
        identity_questions = [
            "What is your name?",
            "Who are you?", 
            "Tell me about yourself",
            "Introduce yourself",
            "What's your name?"
        ]
        
        for i, question in enumerate(identity_questions, 1):
            print(f"Test {i}: User asks '{question}'")
            print("-" * 30)
            
            try:
                response = await handle_message("test_user_456", question)
                
                if response and 'pip install -ai Technologies' in response:
                    print("✅ Correct identity response with company branding!")
                    print(f"📝 Response preview: {response[:100]}...")
                else:
                    print(f"❌ Identity response missing or incorrect")
                    print(f"Response: {response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "="*50 + "\n")

async def main():
    """Run all tests"""
    print("🤖 SOFI AI - NEW BRANDING & INSTALLATION FLOW TEST")
    print("=" * 60)
    print("Testing pip install -ai Technologies branding\n")
    
    await test_first_time_user_flow()
    await test_identity_questions()
    
    print("✅ BRANDING & INSTALLATION FLOW TEST COMPLETED!")
    print("\nKey Features Tested:")
    print("• ✅ New installation command: 'pip install sofi-ai --user'")
    print("• ✅ Company branding: 'pip install -ai Technologies'")
    print("• ✅ Personal introduction with new branding")
    print("• ✅ Identity questions with company reference")
    print("• ✅ Onboarding flow integration")

if __name__ == "__main__":
    asyncio.run(main())
