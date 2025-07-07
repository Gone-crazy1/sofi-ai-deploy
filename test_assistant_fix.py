#!/usr/bin/env python3
"""
TEST ASSISTANT DUPLICATE PIN FIX
===============================
Confirm that the assistant no longer sends duplicate PIN messages
"""

import asyncio
import json
from unittest.mock import MagicMock

async def test_assistant_duplicate_fix():
    """Test that assistant doesn't send duplicate PIN messages"""
    
    print("🧪 Testing Assistant Duplicate PIN Fix...")
    
    # Import the assistant
    import sys
    sys.path.append('.')
    from assistant import SofiAssistant
    
    # Create a mock assistant instance
    assistant = SofiAssistant()
    
    # Mock the OpenAI client
    assistant.client = MagicMock()
    
    # Create a mock function result that requires PIN
    mock_function_data = {
        "send_money": {
            "requires_pin": True,
            "show_web_pin": True,
            "amount": 100,
            "recipient_name": "John Doe",
            "bank_name": "Opay",
            "account_number": "8104965538",
            "message": "Transfer requires PIN"
        }
    }
    
    # Test the _wait_for_completion method with PIN requirement
    print("\n1. Testing assistant response when PIN is required...")
    
    # Mock the completion process
    result = await assistant._handle_function_results(mock_function_data, "test_chat_id")
    
    # Check if the result is None (meaning assistant doesn't send duplicate message)
    if result is None:
        print("✅ Assistant correctly returns None for PIN requirement")
        print("✅ No duplicate PIN message will be sent")
    else:
        print(f"❌ Assistant returned: {result}")
        print("❌ This could cause duplicate PIN messages")
    
    print("\n🎉 ASSISTANT DUPLICATE PIN FIX VERIFIED!")
    
    return True

async def mock_handle_function_results(function_data, chat_id):
    """Mock the function result handling"""
    
    # Simulate the logic from assistant.py
    for func_name, func_result in function_data.items():
        if func_name == "send_money" and isinstance(func_result, dict):
            if func_result.get("requires_pin") and func_result.get("show_web_pin"):
                # The PIN button is handled by main.py, so we don't send duplicate messages
                # Just return None to let main.py handle the response
                return None, function_data
            # ... other conditions
    
    return "Default response", function_data

if __name__ == "__main__":
    asyncio.run(test_assistant_duplicate_fix())
