#!/usr/bin/env python3
"""Fix PIN storage and test transfer again"""

import asyncio
import os
import sys
import hashlib
from dotenv import load_dotenv
from supabase import create_client

sys.path.append('.')
load_dotenv()

async def fix_pin_and_test():
    """Fix PIN storage and test transfer"""
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        chat_id = "real_user_test"
        pin = "1998"
        
        print(f"🔧 Fixing PIN storage for user {chat_id}")
        
        # Get current user
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", chat_id).execute()
        if not user_result.data:
            print("❌ User not found")
            return
        
        user_data = user_result.data[0]
        print(f"Current user data: {user_data}")
        
        # Create proper PIN hash
        pin_hash = hashlib.pbkdf2_hmac('sha256', 
                                     pin.encode('utf-8'), 
                                     chat_id.encode('utf-8'), 
                                     100000)  # 100,000 iterations
        pin_hash_hex = pin_hash.hex()
        
        print(f"Setting PIN hash: {pin_hash_hex[:20]}...")
        
        # Update user with proper PIN hash
        update_result = supabase.table("users").update({
            "pin_hash": pin_hash_hex,
            "transaction_pin": pin,  # Keep for reference
            "has_pin": True
        }).eq("telegram_chat_id", chat_id).execute()
        
        if update_result.data:
            print("✅ PIN hash updated successfully")
        else:
            print("❌ Failed to update PIN hash")
            return
        
        # Test PIN verification
        print(f"\n🔐 Testing PIN verification...")
        from functions.security_functions import verify_pin
        
        pin_result = await verify_pin(chat_id, pin)
        print(f"PIN verification result: {pin_result}")
        
        if not pin_result.get('valid'):
            print("❌ PIN verification still failing")
            return
        
        print("✅ PIN verification working!")
        
        # Test real money transfer
        print(f"\n💰 Testing real money transfer...")
        from functions.transfer_functions import send_money
        
        transfer_result = await send_money(
            chat_id=chat_id,
            account_number="9325047112",
            bank_name="Wema Bank",
            amount=100.0,
            pin=pin,
            narration="Real Sofi AI transfer with correct PIN"
        )
        
        print(f"Transfer result: {transfer_result}")
        
        if transfer_result.get('success'):
            print("🎉 REAL MONEY TRANSFER SUCCESSFUL!")
            print(f"Message: {transfer_result.get('message')}")
        else:
            print("❌ Transfer failed")
            print(f"Error: {transfer_result.get('error')}")
        
        # Test OpenAI Assistant integration
        print(f"\n🤖 Testing OpenAI Assistant integration...")
        from assistant.sofi_assistant import get_assistant
        
        assistant = get_assistant()
        
        # Test with full transfer command
        transfer_message = "Send ₦100 to account 9325047112 at Wema Bank"
        print(f"Assistant message: {transfer_message}")
        
        response, function_data = await assistant.process_message(chat_id, transfer_message)
        print(f"Assistant response: {response}")
        
        if function_data:
            print(f"Functions called: {list(function_data.keys())}")
            for func_name, func_result in function_data.items():
                print(f"  {func_name}: {func_result}")
                if func_name == "send_money" and func_result.get("success"):
                    print("🎉 ASSISTANT MONEY TRANSFER SUCCESSFUL!")
        
        print("\n✅ ALL TESTS COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_pin_and_test())
