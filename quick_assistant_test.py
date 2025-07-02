#!/usr/bin/env python3
"""
Quick Assistant Function Test
Test if assistant can call functions properly
"""

import asyncio
from assistant import get_assistant

async def quick_test():
    try:
        assistant = get_assistant()
        print("✅ Assistant initialized")
        
        # Test simple balance check
        response, function_data = await assistant.process_message(
            chat_id="test_money_user_123",
            message="Check my balance",
            user_data={"telegram_chat_id": "test_money_user_123"}
        )
        
        print(f"Response: {response}")
        print(f"Functions called: {list(function_data.keys()) if function_data else 'None'}")
        
        if function_data:
            for func_name, result in function_data.items():
                print(f"{func_name}: {result}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
