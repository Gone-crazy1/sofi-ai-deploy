#!/usr/bin/env python3
"""
Test the PIN entry system integration with Sofi AI
Tests the full flow: message -> assistant -> PIN keyboard -> transfer
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assistant import SofiAssistant
from utils.pin_entry_system import pin_manager, create_pin_entry_keyboard

async def test_pin_entry_flow():
    """Test the complete PIN entry flow"""
    print("🧪 Testing PIN Entry Flow...")
    
    # Test user
    test_chat_id = "TEST_PIN_USER"
    
    try:
        # Initialize assistant
        assistant = SofiAssistant()
        
        # Test transfer message that should trigger PIN entry
        test_message = "Use send_money function to send 1000 naira to account 1234567890 at Access Bank"
        
        print(f"\n📱 User message: {test_message}")
        
        # Process message with assistant
        response, function_data = await assistant.process_message(test_chat_id, test_message)
        
        print(f"\n🤖 Assistant response: {response}")
        print(f"📊 Function data: {json.dumps(function_data, indent=2)}")
        
        # Check if PIN entry was triggered
        pin_required = False
        if function_data:
            for func_name, func_result in function_data.items():
                if isinstance(func_result, dict) and func_result.get("requires_pin"):
                    pin_required = True
                    print(f"\n🔐 PIN entry triggered by function: {func_name}")
                    print(f"💬 PIN message: {func_result.get('message')}")
                    
                    # Test PIN keyboard creation
                    keyboard = create_pin_entry_keyboard()
                    print(f"⌨️ PIN keyboard: {json.dumps(keyboard, indent=2)}")
                    
                    # Test PIN entry simulation
                    print(f"\n🔢 Simulating PIN entry: 1234")
                    
                    # Add PIN digits
                    for digit in "1234":
                        result = pin_manager.add_pin_digit(test_chat_id, digit)
                        print(f"   Digit {digit}: {result}")
                    
                    # Get completed PIN
                    session = pin_manager.get_session(test_chat_id)
                    print(f"\n📋 Session data: {json.dumps(session, indent=2, default=str)}")
                    
                    completed_pin = session.get("pin_digits") if session else None
                    print(f"🔐 Completed PIN: {completed_pin}")
                    
                    # Clear session
                    pin_manager.clear_session(test_chat_id)
                    print(f"🧹 Session cleared")
                    
                    break
        else:
            print(f"\n⚠️ No function data returned - assistant didn't call any functions")
        
        if not pin_required:
            print(f"\n❌ PIN entry was NOT triggered - this might be an issue")
            print(f"   Check if the message was processed correctly")
        else:
            print(f"\n✅ PIN entry flow test completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Error in PIN entry test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_keyboard_structure():
    """Test PIN keyboard structure"""
    print("\n🧪 Testing PIN Keyboard Structure...")
    
    keyboard = create_pin_entry_keyboard()
    
    # Verify structure
    assert "inline_keyboard" in keyboard
    assert len(keyboard["inline_keyboard"]) == 5  # 5 rows
    
    # Check digit buttons
    digits_found = set()
    for row in keyboard["inline_keyboard"][:4]:  # First 4 rows contain digits
        for button in row:
            if button["callback_data"].startswith("pin_") and button["callback_data"][4:].isdigit():
                digits_found.add(button["callback_data"][4:])
    
    expected_digits = set("0123456789")
    assert digits_found == expected_digits, f"Missing digits: {expected_digits - digits_found}"
    
    print("✅ PIN keyboard structure is correct")

if __name__ == "__main__":
    asyncio.run(test_keyboard_structure())
    asyncio.run(test_pin_entry_flow())
