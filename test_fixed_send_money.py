#!/usr/bin/env python3
"""
Test the fixed send_money function with correct parameter names
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assistant import SofiAssistant

async def test_fixed_send_money():
    """Test send_money with the exact parameters that OpenAI Assistant sends"""
    print("🧪 Testing Fixed send_money Function...")
    
    test_chat_id = "TEST_FIXED_USER"
    
    try:
        # Initialize assistant
        assistant = SofiAssistant()
        
        # Use the exact parameters that OpenAI Assistant sent (from the log)
        function_args = {
            "amount": 100,
            "account_number": "0252948419",
            "bank_name": "Wema Bank"
        }
        
        print(f"\n🔧 Calling send_money with OpenAI format: {json.dumps(function_args, indent=2)}")
        
        # Execute function directly
        result = await assistant._execute_function("send_money", function_args, test_chat_id)
        
        print(f"\n📊 Function result: {json.dumps(result, indent=2, default=str)}")
        
        if result.get("requires_pin"):
            print(f"\n✅ SUCCESS! PIN entry triggered correctly!")
            print(f"💬 Message: {result.get('message')}")
            print(f"📋 Transfer data: {result.get('transfer_data')}")
            
            # Check if PIN session was created
            from utils.pin_entry_system import pin_manager
            session = pin_manager.get_session(test_chat_id)
            if session:
                print(f"✅ PIN session created successfully")
                print(f"   Account: {session['transfer_data']['recipient_account']}")
                print(f"   Bank: {session['transfer_data']['recipient_bank']}")
                print(f"   Amount: ₦{session['transfer_data']['amount']}")
                
                # Clear session
                pin_manager.clear_session(test_chat_id)
                print(f"🧹 Session cleared")
            else:
                print(f"❌ No PIN session found")
        else:
            print(f"\n❌ PIN entry was NOT triggered")
            print(f"   Error: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_send_money())
