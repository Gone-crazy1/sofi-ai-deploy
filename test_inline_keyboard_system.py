"""
Test the new inline keyboard PIN entry system for Sofi AI
"""

import asyncio
import json
from utils.inline_pin_keyboard import (
    inline_pin_manager,
    create_inline_pin_keyboard,
    handle_pin_button
)

def test_inline_keyboard_creation():
    """Test inline keyboard creation"""
    print("🧪 Testing inline keyboard creation...")
    
    keyboard = create_inline_pin_keyboard()
    print(f"✅ Keyboard created: {json.dumps(keyboard, indent=2)}")
    
    # Verify keyboard structure
    assert "inline_keyboard" in keyboard
    assert len(keyboard["inline_keyboard"]) == 5  # 5 rows
    assert len(keyboard["inline_keyboard"][0]) == 3  # First row has 3 buttons (1,2,3)
    assert len(keyboard["inline_keyboard"][3]) == 3  # Fourth row has 3 buttons (Clear, 0, Submit)
    assert len(keyboard["inline_keyboard"][4]) == 1  # Fifth row has 1 button (Cancel)
    
    print("✅ Keyboard structure validation passed")

def test_pin_session():
    """Test PIN session management"""
    print("\n🧪 Testing PIN session management...")
    
    chat_id = "test_chat_123"
    transfer_data = {
        "amount": 5000,
        "account_number": "1234567890",
        "bank_name": "Access Bank",
        "recipient_name": "John Doe",
        "fee": 20
    }
    
    # Start session
    session_id = inline_pin_manager.start_pin_session(chat_id, transfer_data)
    print(f"✅ Session started: {session_id}")
    
    # Test PIN display
    display = inline_pin_manager.create_pin_display(0)
    print(f"✅ Empty PIN display: '{display}'")
    assert display == "_ _ _ _"
    
    display = inline_pin_manager.create_pin_display(2)
    print(f"✅ Partial PIN display: '{display}'")
    assert display == "● ● _ _"
    
    display = inline_pin_manager.create_pin_display(4)
    print(f"✅ Full PIN display: '{display}'")
    assert display == "● ● ● ●"
    
    # Test transfer confirmation message
    message = inline_pin_manager.create_transfer_confirmation_message(transfer_data)
    print(f"✅ Transfer confirmation message created")
    print(f"Message preview: {message[:100]}...")
    
    # End session
    inline_pin_manager.end_session(chat_id)
    print("✅ Session ended")

def test_pin_button_handling():
    """Test PIN button handling"""
    print("\n🧪 Testing PIN button handling...")
    
    chat_id = "test_chat_456"
    transfer_data = {
        "amount": 2000,
        "account_number": "0987654321",
        "bank_name": "GTBank",
        "recipient_name": "Jane Smith",
        "fee": 15
    }
    
    # Start session
    inline_pin_manager.start_pin_session(chat_id, transfer_data)
    
    # Test adding digits
    result = handle_pin_button(chat_id, "pin_1")
    print(f"✅ Added digit 1: {result}")
    assert result["success"] == True
    assert result["length"] == 1
    assert result["display"] == "● _ _ _"
    
    result = handle_pin_button(chat_id, "pin_2")
    print(f"✅ Added digit 2: {result}")
    assert result["length"] == 2
    assert result["display"] == "● ● _ _"
    
    result = handle_pin_button(chat_id, "pin_3")
    result = handle_pin_button(chat_id, "pin_4")
    print(f"✅ Added digits 3,4: {result}")
    assert result["length"] == 4
    assert result["display"] == "● ● ● ●"
    assert result["can_submit"] == True
    
    # Test clear
    result = handle_pin_button(chat_id, "pin_clear")
    print(f"✅ Cleared PIN: {result}")
    assert result["success"] == True
    assert result["length"] == 0
    assert result["display"] == "_ _ _ _"
    
    # Test submit with incomplete PIN
    result = handle_pin_button(chat_id, "pin_submit")
    print(f"✅ Submit with incomplete PIN: {result}")
    assert result["success"] == False
    assert "not complete" in result["error"]
    
    # Complete PIN and submit
    handle_pin_button(chat_id, "pin_1")
    handle_pin_button(chat_id, "pin_2")
    handle_pin_button(chat_id, "pin_3")
    handle_pin_button(chat_id, "pin_4")
    
    result = handle_pin_button(chat_id, "pin_submit")
    print(f"✅ Submit with complete PIN: {result}")
    assert result["success"] == True
    assert result["action"] == "submit"
    assert result["pin"] == "1234"
    assert result["transfer_data"]["amount"] == 2000
    
    # Test cancel
    inline_pin_manager.start_pin_session(chat_id, transfer_data)
    result = handle_pin_button(chat_id, "pin_cancel")
    print(f"✅ Cancel PIN: {result}")
    assert result["success"] == True
    assert result["action"] == "cancel"

def test_message_creation():
    """Test message creation functions"""
    print("\n🧪 Testing message creation...")
    
    transfer_data = {
        "amount": 10000,
        "account_number": "1122334455",
        "bank_name": "Zenith Bank",
        "recipient_name": "Alice Johnson",
        "fee": 25
    }
    
    # Test confirmation message
    message = inline_pin_manager.create_transfer_confirmation_message(transfer_data)
    print("✅ Confirmation message created:")
    print(message)
    
    # Verify message contains key information
    assert "₦10,000" in message
    assert "Alice Johnson" in message
    assert "Zenith Bank" in message
    assert "1122334455" in message
    assert "₦25" in message  # Fee
    assert "₦10,025" in message  # Total
    assert "_ _ _ _" in message  # Empty PIN display
    
    # Test progress message
    progress_message = inline_pin_manager.create_pin_progress_message(transfer_data, 2)
    print("\n✅ Progress message created:")
    print(progress_message)
    assert "● ● _ _" in progress_message

def main():
    """Run all tests"""
    print("🧪 Testing Sofi AI Inline Keyboard PIN Entry System")
    print("=" * 60)
    
    try:
        test_inline_keyboard_creation()
        test_pin_session()
        test_pin_button_handling()
        test_message_creation()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Inline keyboard PIN system is working correctly.")
        print("🚀 Ready to deploy the new PIN entry system!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
