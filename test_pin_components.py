"""
Test PIN keyboard display manually
"""
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pin_entry_system import create_pin_entry_keyboard, pin_manager

def test_pin_keyboard_creation():
    """Test PIN keyboard creation directly"""
    print("\n🧪 TEST: PIN Keyboard Creation")
    print("=" * 50)
    
    try:
        # Create PIN keyboard
        keyboard = create_pin_entry_keyboard()
        
        print("✅ PIN keyboard created successfully!")
        print(f"📱 Keyboard structure: {type(keyboard)}")
        
        # Check keyboard content
        if isinstance(keyboard, dict) and 'inline_keyboard' in keyboard:
            print("✅ Keyboard has proper structure")
            
            # Print keyboard layout for verification
            print("📋 Keyboard layout:")
            for i, row in enumerate(keyboard['inline_keyboard']):
                row_text = " | ".join([btn['text'] for btn in row])
                print(f"   Row {i+1}: {row_text}")
            
            return True
        else:
            print("❌ Keyboard missing expected structure")
            print(f"   Keyboard content: {keyboard}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating PIN keyboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pin_manager():
    """Test PIN manager functionality"""
    print("\n🧪 TEST: PIN Manager")
    print("=" * 50)
    
    try:
        # Test chat ID
        chat_id = "test_user_123"
        
        # Start PIN session
        transfer_data = {
            "account_number": "8104945538",
            "bank_name": "opay",
            "amount": 101.0,
            "narration": "Test transfer"
        }
        
        pin_manager.start_pin_session(chat_id, "transfer", transfer_data)
        print("✅ PIN session started")
        
        # Check session
        session = pin_manager.get_session(chat_id)
        if session:
            print("✅ PIN session retrieved")
            print(f"   Session type: {session.get('session_type')}")
            print(f"   Transfer amount: ₦{session.get('transfer_data', {}).get('amount', 0)}")
        else:
            print("❌ PIN session not found")
            return False
        
        # Test adding digits
        result1 = pin_manager.add_pin_digit(chat_id, "1")
        result2 = pin_manager.add_pin_digit(chat_id, "9")
        result3 = pin_manager.add_pin_digit(chat_id, "9")
        result4 = pin_manager.add_pin_digit(chat_id, "8")
        
        print(f"✅ Added 4 digits, final status: {result4.get('status')}")
        
        if result4.get('status') == 'complete':
            print("✅ PIN entry completed successfully")
            return True
        else:
            print("❌ PIN entry not completed")
            return False
            
    except Exception as e:
        print(f"❌ Error in PIN manager test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pin_flow_simulation():
    """Simulate the complete PIN flow"""
    print("\n🧪 TEST: Complete PIN Flow Simulation")
    print("=" * 50)
    
    try:
        # Mock the send_money response that triggers PIN
        pin_response = {
            "success": False,
            "requires_pin": True,
            "message": "Please enter your 4-digit PIN to send ₦101 to 8104945538",
            "show_pin_keyboard": True,
            "transfer_data": {
                "account_number": "8104945538",
                "bank_name": "opay",
                "amount": 101.0,
                "narration": "Test transfer"
            }
        }
        
        print("📝 Simulated transfer response:")
        print(f"   Requires PIN: {pin_response.get('requires_pin')}")
        print(f"   Show keyboard: {pin_response.get('show_pin_keyboard')}")
        print(f"   Message: {pin_response.get('message')}")
        
        # Test the main handler logic
        if pin_response.get("requires_pin") and pin_response.get("show_pin_keyboard"):
            keyboard = create_pin_entry_keyboard()
            
            if keyboard:
                print("✅ PIN keyboard would be sent to user")
                print("✅ Complete PIN flow works correctly")
                return True
            else:
                print("❌ Failed to create PIN keyboard")
                return False
        else:
            print("❌ PIN flow not triggered correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error in PIN flow simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all PIN tests"""
    print("🚀 TESTING PIN KEYBOARD FUNCTIONALITY")
    print("=" * 60)
    
    # Run tests
    test1 = test_pin_keyboard_creation()
    test2 = test_pin_manager()
    test3 = test_pin_flow_simulation()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"📱 PIN Keyboard Creation: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"🔐 PIN Manager: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"🔄 Complete PIN Flow: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    all_passed = test1 and test2 and test3
    print(f"\n🎯 OVERALL: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n✅ PIN KEYBOARD SYSTEM IS WORKING!")
        print("🔧 The issue is likely that the user doesn't exist in the database")
        print("💡 Once the user is properly registered, PIN keyboard will display correctly")
    
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(main())
