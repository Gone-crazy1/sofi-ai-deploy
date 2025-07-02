#!/usr/bin/env python3
"""
Test PIN submission without importing main.py
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_pin_submission():
    """Test PIN submission directly"""
    print("🧪 Testing PIN Submission...")
    
    test_chat_id = "5495194750"
    
    try:
        # First create a PIN session with transfer data
        from utils.pin_entry_system import pin_manager
        
        transfer_data = {
            "account_number": "0252948419",
            "bank_name": "035",  # Wema Bank code
            "amount": 100,
            "narration": "Test transfer"
        }
        
        pin_manager.start_pin_session(test_chat_id, "transfer", transfer_data)
        
        # Enter PIN digits
        for digit in "1998":
            pin_manager.add_pin_digit(test_chat_id, digit)
        
        print(f"✅ PIN session ready with PIN: {pin_manager.get_session(test_chat_id)['pin_digits']}")
        
        # Now test PIN submission manually (without importing main.py)
        session = pin_manager.get_session(test_chat_id)
        pin = session.get("pin_digits", "")
        transfer_data = session.get("transfer_data", {})
        
        print(f"📋 Transfer details:")
        print(f"   Amount: ₦{transfer_data['amount']}")
        print(f"   Account: {transfer_data['account_number']}")
        print(f"   Bank: {transfer_data['bank_name']}")
        print(f"   PIN: {pin}")
        
        # Execute the transfer with PIN
        from functions.transfer_functions import send_money
        
        result = await send_money(
            chat_id=test_chat_id,
            account_number=transfer_data["account_number"],
            bank_name=transfer_data["bank_name"],
            amount=transfer_data["amount"],
            pin=pin,
            narration=transfer_data.get("narration", "Transfer via Sofi AI")
        )
        
        print(f"\n📊 Final transfer result: {json.dumps(result, indent=2, default=str)}")
        
        # Clear the session
        pin_manager.clear_session(test_chat_id)
        
        if result.get("success"):
            print(f"\n🎉 COMPLETE SUCCESS! Transfer executed!")
            print(f"💬 User would see: {result.get('message')}")
            print(f"📝 Reference: {result.get('reference')}")
        else:
            print(f"\n⚠️ Transfer failed: {result.get('error')}")
            if "User not found" in str(result.get('error')):
                print(f"   (This is expected for test user - real users would work)")
                
    except Exception as e:
        print(f"\n❌ Error in PIN submission test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pin_submission())
