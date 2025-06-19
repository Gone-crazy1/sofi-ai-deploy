#!/usr/bin/env python3
"""Test script to verify the improved transfer help response"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function
from main import generate_ai_reply

# Mock environment variables and dependencies
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test_key"
os.environ["OPENAI_API_KEY"] = "test_key"

async def test_transfer_help_responses():
    """Test various transfer help requests"""
    
    # Mock the dependencies
    with patch('main.get_supabase_client') as mock_supabase, \
         patch('main.check_virtual_account') as mock_check_account, \
         patch('main.save_chat_message') as mock_save_message:
        
        # Set up mocks to simulate onboarded user
        mock_check_account.return_value = {
            "accountnumber": "1234567890",
            "accountname": "Test User",
            "bankname": "Monnify MFB",
            "balance": 5000.00
        }
        
        # Mock Supabase client
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            "id": "test_user_id",
            "telegram_chat_id": "12345",
            "first_name": "Test",
            "last_name": "User"
        }]
        mock_supabase.return_value = mock_client
        
        # Mock save_chat_message to avoid database calls
        mock_save_message.return_value = True
        
        test_chat_id = "12345"
        
        # Test cases for transfer help requests
        test_messages = [
            "example of how to send money",
            "how to send money",
            "how do i send money",
            "show me how to transfer",
            "how to transfer money",
            "transfer example",
            "send money example",
            "how can i send money",
            "guide to send money",
            "help with sending money",
            "help with transfer",
            "how does transfer work"
        ]
        
        print("🧪 Testing Transfer Help Response Improvements")
        print("=" * 60)
        
        success_count = 0
        for i, message in enumerate(test_messages, 1):
            try:
                print(f"\n{i}. Testing: '{message}'")
                response = await generate_ai_reply(test_chat_id, message)
                
                # Check if response contains the key elements we want
                expected_elements = [
                    "To send money, you can provide the recipient's account number and bank name",
                    "if you have saved the recipient as a beneficiary",
                    "Examples:",
                    "What I'll do:"
                ]
                
                has_all_elements = all(element in response for element in expected_elements)
                
                if has_all_elements:
                    print("✅ SUCCESS: Response contains all expected instructional elements")
                    success_count += 1
                else:
                    print("❌ FAIL: Response missing expected elements")
                    print(f"Response: {response[:200]}...")
                    
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
        
        print(f"\n📊 RESULTS: {success_count}/{len(test_messages)} tests passed")
        
        # Test one specific case in detail
        print("\n" + "=" * 60)
        print("📋 DETAILED TEST: 'example of how to send money'")
        print("=" * 60)
        
        try:
            detailed_response = await generate_ai_reply(test_chat_id, "example of how to send money")
            print("Full Response:")
            print("-" * 40)
            print(detailed_response)
            print("-" * 40)
            
            # Check if it's human and instructional (not bot-like)
            bot_like_phrases = [
                "I'm an AI", "I am programmed", "as an AI assistant",
                "Please provide bank name, account number, amount",
                "I cannot process", "system error"
            ]
            
            human_like_elements = [
                "you can provide", "you can simply mention", "Just tell me",
                "What I'll do:", "Examples:"
            ]
            
            is_bot_like = any(phrase in detailed_response for phrase in bot_like_phrases)
            is_human_like = any(element in detailed_response for element in human_like_elements)
            
            print(f"\n🤖 Bot-like indicators: {'Found' if is_bot_like else 'None detected'}")
            print(f"👤 Human-like elements: {'Found' if is_human_like else 'Missing'}")
            
            if not is_bot_like and is_human_like:
                print("✅ RESPONSE QUALITY: Human, instructional, and clear!")
            else:
                print("❌ RESPONSE QUALITY: Still too bot-like or unclear")
                
        except Exception as e:
            print(f"❌ DETAILED TEST ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_transfer_help_responses())
