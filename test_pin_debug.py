#!/usr/bin/env python3
"""
Test to debug the PIN entry flow step by step
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_pin_flow_debug():
    """Debug the exact PIN entry flow"""
    print("🔍 Debugging PIN Entry Flow...")
    
    test_chat_id = "5495194750"  # Your actual chat ID
    
    try:
        # Test 1: Direct assistant function call
        print("\n📱 Test 1: Direct Assistant Function Call")
        from assistant import SofiAssistant
        
        assistant = SofiAssistant()
        
        # Simulate the exact function call that would happen
        function_args = {
            "amount": 100,
            "account_number": "8104965538", 
            "bank_name": "Opay",
            "narration": "Test transfer"
        }
        
        print(f"🔧 Calling send_money directly: {json.dumps(function_args, indent=2)}")
        
        result = await assistant._execute_function("send_money", function_args, test_chat_id)
        
        print(f"📊 Direct function result: {json.dumps(result, indent=2)}")
        
        if result.get("requires_pin"):
            print(f"✅ PIN entry triggered correctly!")
            print(f"💬 Message: {result.get('message')}")
            
            # Test 2: Check PIN keyboard creation
            print(f"\n⌨️  Test 2: PIN Keyboard Creation")
            from utils.pin_entry_system import create_pin_entry_keyboard
            keyboard = create_pin_entry_keyboard()
            print(f"✅ Keyboard created: {len(keyboard['inline_keyboard'])} rows")
            
            # Test 3: Check what message should be sent
            pin_message = f"🔐 **Enter your 4-digit PIN**\n\n{result.get('message')}\n\n*Use the keypad below:*"
            print(f"\n💬 Test 3: Full PIN Message")
            print(f"Message to user:")
            print(pin_message)
            print(f"\nKeyboard: {json.dumps(keyboard, indent=2)}")
            
        else:
            print(f"❌ PIN entry NOT triggered")
            print(f"   Result: {result}")
            
        # Test 4: Test the full assistant conversation
        print(f"\n🤖 Test 4: Full Assistant Conversation")
        
        test_message = "Send 100 to 8104965538 Opay"
        response, function_data = await assistant.process_message(test_chat_id, test_message)
        
        print(f"Assistant response: {response}")
        print(f"Function data: {json.dumps(function_data, indent=2, default=str)}")
        
        # Check if any function returned requires_pin
        if function_data:
            for func_name, func_result in function_data.items():
                if isinstance(func_result, dict) and func_result.get("requires_pin"):
                    print(f"✅ Function {func_name} correctly triggered PIN entry!")
                    return func_result
        
        print(f"❌ No function triggered PIN entry in full conversation")
            
    except Exception as e:
        print(f"\n❌ Error in debug test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pin_flow_debug())
