#!/usr/bin/env python3
"""Test the verify_account_name function integration"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append('.')

load_dotenv()

async def test_verify_account_function():
    """Test the verify_account_name function with OpenAI Assistant"""
    try:
        # Import the assistant
        from assistant.sofi_assistant import get_assistant
        
        print("🔍 Testing verify_account_name function with OpenAI Assistant...")
        
        # Initialize assistant
        assistant = get_assistant()
        
        # Test message that should trigger account verification
        test_message = "Please verify account 6115491450 at OPay"
        chat_id = "test_user_123"
        
        print(f"📤 Sending test message: {test_message}")
        
        # Process the message
        response, function_data = await assistant.process_message(chat_id, test_message)
        
        print(f"📥 Assistant Response: {response}")
        
        if function_data:
            print(f"🔧 Function Data: {function_data}")
        
        # Test direct function call
        print("\n🔧 Testing direct function call...")
        from functions.verification_functions import verify_account_name
        
        direct_result = await verify_account_name(
            account_number="6115491450",
            bank_name="OPay"
        )
        
        print(f"✅ Direct Function Result: {direct_result}")
        
    except Exception as e:
        print(f"❌ Error testing verify_account_name: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_verify_account_function())
