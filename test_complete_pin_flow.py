#!/usr/bin/env python3
"""
Comprehensive test of the PIN entry system integration
Tests the exact flow that happens in production
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pin_entry_system import pin_manager, create_pin_entry_keyboard

async def test_pin_integration_flow():
    """Test the complete PIN integration flow"""
    print("🧪 Testing Complete PIN Integration Flow...")
    
    test_chat_id = "TEST_COMPLETE_FLOW"
    
    try:
        # Step 1: Assistant determines that send_money function should be called
        print("\n📱 Step 1: User wants to send money")
        user_message = "Send 1000 naira to 1234567890 at Access Bank"
        print(f"   User message: {user_message}")
        
        # Step 2: Assistant extracts transfer details
        print("\n🔧 Step 2: Assistant processes transfer request")
        transfer_args = {
            "recipient_account": "1234567890",
            "recipient_bank": "access bank",
            "amount": 1000,
            "reason": "Test transfer"
        }
        print(f"   Transfer details: {json.dumps(transfer_args, indent=2)}")
        
        # Step 3: send_money function is called WITHOUT PIN
        print("\n🔒 Step 3: PIN entry is required")
        
        # Simulate what happens in assistant._execute_function when PIN is not provided
        # Start PIN entry session
        transfer_data = {
            "recipient_account": transfer_args["recipient_account"],
            "recipient_bank": transfer_args["recipient_bank"],
            "amount": float(transfer_args["amount"]),
            "narration": transfer_args.get("reason", "Transfer via Sofi AI"),
            "temp_id": f"transfer_{test_chat_id}_{int(12345678)}"
        }
        
        pin_manager.start_pin_session(test_chat_id, "transfer", transfer_data)
        
        # Return special response indicating PIN entry is needed
        pin_response = {
            "success": False,
            "requires_pin": True,
            "message": f"Please enter your 4-digit PIN to send ₦{transfer_args['amount']:,.0f} to {transfer_args['recipient_account']}",
            "show_pin_keyboard": True,
            "transfer_data": transfer_data
        }
        
        print(f"   PIN response: {json.dumps(pin_response, indent=2)}")
        
        # Step 4: Webhook detects requires_pin and sends keyboard
        print("\n⌨️ Step 4: PIN keyboard is sent to user")
        if pin_response.get("requires_pin"):
            keyboard = create_pin_entry_keyboard()
            pin_message = f"🔐 **Enter your 4-digit PIN**\n\n{pin_response.get('message')}\n\n*Use the keypad below:*"
            
            print(f"   PIN message: {pin_message}")
            print(f"   Keyboard buttons: {len(keyboard['inline_keyboard'])} rows")
            
            # Verify session was created
            session = pin_manager.get_session(test_chat_id)
            if session:
                print(f"✅ PIN session created successfully")
                print(f"   Session type: {session.get('type')}")
                print(f"   Transfer amount: ₦{session['transfer_data']['amount']}")
            else:
                print(f"❌ PIN session NOT created")
                return
        
        # Step 5: User clicks PIN digits (simulate callback queries)
        print("\n🔢 Step 5: User enters PIN via keyboard")
        pin_digits = "1234"
        
        for i, digit in enumerate(pin_digits, 1):
            # Simulate callback query: pin_1, pin_2, etc.
            callback_data = f"pin_{digit}"
            print(f"   Button press {i}: {callback_data}")
            
            # This is what happens in handle_callback_query
            result = pin_manager.add_pin_digit(test_chat_id, digit)
            pin_display = "•" * result["length"]
            print(f"      Display: {pin_display}")
            
            if result["status"] == "complete":
                print(f"      PIN complete! Auto-submitting...")
                break
        
        # Step 6: PIN submission and transfer execution
        print("\n💸 Step 6: PIN submitted and transfer executed")
        
        # Get session for transfer
        session = pin_manager.get_session(test_chat_id)
        pin = session.get("pin_digits", "")
        transfer_data = session.get("transfer_data", {})
        
        print(f"   PIN entered: {pin}")
        print(f"   Transfer data: {json.dumps(transfer_data, indent=2)}")
        
        # Simulate transfer execution (without actually calling Paystack)
        print(f"   Simulating transfer execution...")
        print(f"   ✅ Transfer would be executed with:")
        print(f"      Amount: ₦{transfer_data['amount']}")
        print(f"      To: {transfer_data['recipient_account']}")
        print(f"      Bank: {transfer_data['recipient_bank']}")
        print(f"      PIN: {'*' * len(pin)}")
        
        # Clear session
        pin_manager.clear_session(test_chat_id)
        print(f"   🧹 PIN session cleared")
        
        print(f"\n✅ Complete PIN integration flow test SUCCESS!")
        print(f"   All steps completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error in PIN integration test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_error_scenarios():
    """Test error handling scenarios"""
    print(f"\n🧪 Testing Error Scenarios...")
    
    test_chat_id = "TEST_ERRORS"
    
    # Test 1: No active session
    print(f"\n🔍 Test 1: No active PIN session")
    session = pin_manager.get_session(test_chat_id)
    if not session:
        print(f"✅ Correctly returns None for non-existent session")
    
    # Test 2: Add digit without session
    result = pin_manager.add_pin_digit(test_chat_id, "1")
    if not result.get("success"):
        print(f"✅ Correctly rejects digit entry without session: {result.get('error')}")
    
    # Test 3: Session creation and management
    transfer_data = {"amount": 500, "recipient_account": "1111111111"}
    session_id = pin_manager.start_pin_session(test_chat_id, "transfer", transfer_data)
    print(f"✅ Session created: {session_id}")
    
    # Test 4: Clear PIN
    pin_manager.add_pin_digit(test_chat_id, "1")
    pin_manager.add_pin_digit(test_chat_id, "2")
    result = pin_manager.clear_pin(test_chat_id)
    print(f"✅ PIN cleared: {result}")
    
    # Test 5: Session cleanup
    pin_manager.clear_session(test_chat_id)
    session_after = pin_manager.get_session(test_chat_id)
    if not session_after:
        print(f"✅ Session properly cleared")
    
    print(f"✅ Error scenario tests completed")

if __name__ == "__main__":
    asyncio.run(test_pin_integration_flow())
    asyncio.run(test_error_scenarios())
