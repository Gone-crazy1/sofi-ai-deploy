#!/usr/bin/env python3
"""Test real money transfer with assistant to ensure verification is called"""

import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

async def test_transfer_with_verification():
    """Test money transfer that should trigger account verification"""
    try:
        from assistant.sofi_assistant import get_assistant
        
        print("💰 Testing money transfer with account verification...")
        
        assistant = get_assistant()
        
        # Test a transfer request that should trigger verification
        test_message = "Send ₦100 to account 0123456789 at Access Bank"
        chat_id = "test_user_transfer"
        
        print(f"📤 Transfer Request: {test_message}")
        
        # Process the message
        response, function_data = await assistant.process_message(chat_id, test_message)
        
        print(f"📥 Assistant Response: {response}")
        
        if function_data:
            print(f"🔧 Functions Called: {list(function_data.keys())}")
            for func_name, func_result in function_data.items():
                print(f"   {func_name}: {func_result}")
        else:
            print("⚠️ No functions were called")
        
        # Check if verification was called
        if function_data and 'verify_account_name' in function_data:
            print("✅ Account verification function was called!")
            verify_result = function_data['verify_account_name']
            if verify_result.get('verified'):
                print(f"   ✅ Account verified: {verify_result.get('account_name')}")
            else:
                print(f"   ❌ Verification failed: {verify_result.get('error')}")
        else:
            print("❌ Account verification function was NOT called")
        
        # Check if send_money was called
        if function_data and 'send_money' in function_data:
            print("💰 Send money function was called!")
            transfer_result = function_data['send_money']
            print(f"   Result: {transfer_result}")
        else:
            print("⚠️ Send money function was NOT called")
        
    except Exception as e:
        print(f"❌ Error testing transfer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_transfer_with_verification())
