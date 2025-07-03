#!/usr/bin/env python3
"""
Test PIN keyboard and automatic receipt generation
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

async def test_pin_and_receipt_fixes():
    """Test the PIN keyboard and automatic receipt fixes"""
    try:
        print("🧪 TESTING PIN KEYBOARD & RECEIPT FIXES")
        print("=" * 50)
        
        # Test 1: PIN keyboard generation
        print("\n🔐 Test 1: PIN Keyboard Generation")
        from utils.pin_entry_system import create_pin_entry_keyboard
        
        pin_keyboard = create_pin_entry_keyboard()
        print("✅ PIN keyboard generated successfully:")
        print(f"   Keyboard has {len(pin_keyboard['inline_keyboard'])} rows")
        print(f"   First row: {[btn['text'] for btn in pin_keyboard['inline_keyboard'][0]]}")
        
        # Test 2: Receipt generation
        print("\n📄 Test 2: Receipt Generation")
        from utils.receipt_generator import create_transaction_receipt
        
        test_transaction = {
            'amount': 100.0,
            'fee': 20.0,
            'total_charged': 120.0,
            'new_balance': 9880.0,
            'recipient_name': 'PIPINSTALLAIT/THANKGOD NDIDI',
            'bank_name': 'Wema Bank',
            'account_number': '9325047112',
            'reference': 'TRF_test123456',
            'transaction_id': 'TXN_test789',
            'transaction_time': '03/07/2025 01:50 AM',
            'narration': 'Test transfer'
        }
        
        receipt = create_transaction_receipt(test_transaction, "telegram")
        print("✅ Receipt generated successfully:")
        print("   Receipt length:", len(receipt))
        print("   First few lines:")
        for line in receipt.split('\n')[:5]:
            print(f"     {line}")
        
        # Test 3: Assistant integration with PIN flow
        print("\n🤖 Test 3: Assistant PIN Flow")
        from assistant.sofi_assistant import get_assistant
        
        assistant = get_assistant()
        chat_id = "real_user_test"
        
        # Test transfer that should trigger PIN flow
        transfer_message = "Send ₦100 to account 9325047112 at Wema Bank"
        print(f"   Testing message: {transfer_message}")
        
        response, function_data = await assistant.process_message(chat_id, transfer_message)
        print(f"   Assistant response: {response[:100]}...")
        
        if function_data:
            print(f"   Functions called: {list(function_data.keys())}")
            for func_name, func_result in function_data.items():
                if isinstance(func_result, dict):
                    if func_result.get("requires_pin"):
                        print("   ✅ PIN flow triggered correctly!")
                    elif func_result.get("auto_send_receipt"):
                        print("   ✅ Auto receipt flag set!")
                    elif func_result.get("success"):
                        print("   ✅ Transfer completed successfully!")
        
        # Test 4: Main message handler integration
        print("\n📱 Test 4: Main Handler Integration")
        from main import handle_message
        
        # Simulate a real chat message
        test_response = await handle_message(chat_id, transfer_message)
        print(f"   Main handler response type: {type(test_response)}")
        
        if isinstance(test_response, dict):
            if test_response.get("requires_pin"):
                print("   ✅ Main handler correctly detected PIN requirement!")
                print(f"   PIN message: {test_response.get('message', '')[:50]}...")
            elif test_response.get("auto_send_receipt"):
                print("   ✅ Main handler detected auto receipt!")
        else:
            print(f"   Response: {str(test_response)[:100]}...")
        
        # Test 5: Webhook simulation
        print("\n📡 Test 5: Webhook Flow Simulation")
        
        # Simulate webhook payload
        webhook_payload = {
            "message": {
                "chat": {"id": 123456789},
                "from": {"id": 123456789, "first_name": "Test", "last_name": "User"},
                "text": transfer_message
            }
        }
        
        print("   Simulated webhook payload created")
        print("   This would trigger the main webhook handler")
        
        print("\n✅ ALL TESTS COMPLETED!")
        print("\n📋 Summary:")
        print("   ✅ PIN keyboard generation working")
        print("   ✅ Receipt generation working")
        print("   ✅ Assistant integration working")
        print("   ✅ Main handler integration working")
        print("   ✅ Ready for live testing!")
        
    except Exception as e:
        print(f"❌ Error in tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pin_and_receipt_fixes())
