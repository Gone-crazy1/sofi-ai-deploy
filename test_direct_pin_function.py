#!/usr/bin/env python3
"""
Direct test of PIN entry flow by calling assistant functions directly
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assistant import SofiAssistant
from utils.pin_entry_system import pin_manager, create_pin_entry_keyboard

async def test_direct_send_money():
    """Test sending money function directly to trigger PIN entry"""
    print("🧪 Testing Direct send_money Function Call...")
    
    test_chat_id = "TEST_DIRECT_USER"
    
    try:
        # Initialize assistant
        assistant = SofiAssistant()
        
        # Call send_money function directly through assistant
        function_args = {
            "recipient_account": "1234567890",
            "recipient_bank": "access bank",
            "amount": 1000,
            "reason": "Test transfer"
        }
        
        print(f"\n🔧 Calling send_money with args: {json.dumps(function_args, indent=2)}")
        
        # Execute function directly
        result = await assistant._execute_function("send_money", function_args, test_chat_id)
        
        print(f"\n📊 Function result: {json.dumps(result, indent=2)}")
        
        if result.get("requires_pin"):
            print(f"\n✅ PIN entry triggered successfully!")
            print(f"💬 Message: {result.get('message')}")
            
            # Test PIN keyboard
            keyboard = create_pin_entry_keyboard()
            print(f"\n⌨️ PIN keyboard created successfully")
            
            # Test PIN session
            session = pin_manager.get_session(test_chat_id)
            if session:
                print(f"📋 PIN session data: {json.dumps(session, indent=2, default=str)}")
                
                # Clear session
                pin_manager.clear_session(test_chat_id)
                print(f"🧹 Session cleared")
            else:
                print(f"❌ No PIN session found")
        else:
            print(f"\n❌ PIN entry was NOT triggered")
            print(f"   Result: {result}")
            
    except Exception as e:
        print(f"\n❌ Error in direct function test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_send_money())
