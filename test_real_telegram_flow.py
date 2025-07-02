#!/usr/bin/env python3
"""
Test the complete flow with real Telegram message format
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_real_telegram_flow():
    """Test the flow exactly as it would happen from Telegram"""
    print("🧪 Testing Real Telegram Message Flow...")
    
    # Use a realistic test user ID (would be the actual Telegram chat ID)
    test_chat_id = "5495194750"  # This matches the user from the logs
    
    try:
        # Simulate the exact message from Telegram user
        user_message = "Send 100 to 0252948419 Wema bank name: Ndidi ThankGod PIN 1998"
        
        print(f"\n📱 User message: {user_message}")
        
        # This simulates what the assistant parsing would extract
        # Based on the logs, the OpenAI Assistant correctly identified:
        function_args = {
            "amount": 100,
            "account_number": "0252948419",
            "bank_name": "Wema Bank"
        }
        
        print(f"\n🤖 Assistant extracted: {json.dumps(function_args, indent=2)}")
        
        # Now test the send_money function directly with this data
        from functions.transfer_functions import send_money
        
        result = await send_money(
            chat_id=test_chat_id,
            amount=function_args["amount"],
            account_number=function_args["account_number"],
            bank_name=function_args["bank_name"],
            narration="Transfer via Sofi AI"
        )
        
        print(f"\n📊 Function result: {json.dumps(result, indent=2, default=str)}")
        
        if result.get("requires_pin"):
            print(f"\n✅ SUCCESS! The flow now works correctly!")
            print(f"💬 User would see: {result.get('message')}")
            print(f"⌨️ PIN keyboard would be displayed")
            
            # Test PIN entry simulation
            from utils.pin_entry_system import pin_manager
            session = pin_manager.get_session(test_chat_id)
            
            if session:
                print(f"\n📋 PIN session created:")
                print(f"   Amount: ₦{session['transfer_data']['amount']}")
                print(f"   Account: {session['transfer_data']['account_number']}")
                print(f"   Bank: {session['transfer_data']['bank_name']}")
                
                # Simulate PIN entry (1998 from user message)
                print(f"\n🔢 Simulating PIN entry: 1998")
                for digit in "1998":
                    result = pin_manager.add_pin_digit(test_chat_id, digit)
                    print(f"   Digit {digit}: {result.get('display', '•')}")
                
                # Now simulate PIN submission (what happens when user clicks Submit)
                print(f"\n🚀 Simulating PIN submission...")
                
                # This would call handle_pin_submit from main.py
                from main import handle_pin_submit
                submit_result = await handle_pin_submit(test_chat_id)
                
                print(f"📊 Submit result: {json.dumps(submit_result, indent=2, default=str)}")
                
                if submit_result.get("success"):
                    print(f"\n🎉 COMPLETE SUCCESS! Transfer would be executed!")
                    print(f"💬 User would see: {submit_result.get('response')}")
                else:
                    print(f"\n⚠️ Transfer would fail: {submit_result.get('error')}")
                    if "User not found" in str(submit_result.get('error')):
                        print(f"   (This is expected for test user)")
                
            else:
                print(f"\n❌ No PIN session found")
        else:
            print(f"\n❌ PIN entry was not triggered")
            print(f"   Error: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Error in real flow test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_telegram_flow())
