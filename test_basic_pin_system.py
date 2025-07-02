#!/usr/bin/env python3
"""
Simple test to check if PIN entry works at basic level
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pin_entry_system import pin_manager, create_pin_entry_keyboard

def test_basic_pin_system():
    """Test basic PIN system functionality"""
    print("🧪 Testing Basic PIN System...")
    
    test_chat_id = "TEST_BASIC"
    
    # Test keyboard creation
    keyboard = create_pin_entry_keyboard()
    print(f"✅ PIN keyboard created: {len(keyboard['inline_keyboard'])} rows")
    
    # Test PIN session
    transfer_data = {
        "recipient_account": "1234567890",
        "recipient_bank": "access bank",
        "amount": 1000,
        "narration": "Test transfer"
    }
    
    session_id = pin_manager.start_pin_session(test_chat_id, "transfer", transfer_data)
    print(f"✅ PIN session started: {session_id}")
    
    # Test PIN entry
    for digit in "1234":
        result = pin_manager.add_pin_digit(test_chat_id, digit)
        print(f"   Digit {digit}: length={result.get('length')}, status={result.get('status')}")
    
    # Check session
    session = pin_manager.get_session(test_chat_id)
    print(f"✅ Session PIN: {session['pin_digits']}")
    print(f"✅ Transfer data: {session['transfer_data']['amount']}")
    
    # Clear session
    pin_manager.clear_session(test_chat_id)
    print(f"✅ Session cleared")
    
    print(f"\n✅ Basic PIN system test completed successfully!")

if __name__ == "__main__":
    test_basic_pin_system()
