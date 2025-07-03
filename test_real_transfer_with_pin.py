#!/usr/bin/env python3
"""
COMPREHENSIVE REAL MONEY TRANSFER TEST
Test account verification and money transfer with PIN 1998
Account: 9325047112 (Wema Bank)
Amount: ₦100
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

async def test_complete_transfer_with_pin():
    """Test complete money transfer flow with real PIN"""
    try:
        print("🚀 COMPREHENSIVE REAL MONEY TRANSFER TEST")
        print("=" * 50)
        
        # Test parameters
        account_number = "9325047112"
        bank_name = "Wema Bank"
        amount = 100.0
        pin = "1998"
        test_chat_id = "real_user_test"
        
        print(f"📋 Test Parameters:")
        print(f"   Account: {account_number}")
        print(f"   Bank: {bank_name}")
        print(f"   Amount: ₦{amount}")
        print(f"   PIN: {pin}")
        
        # Step 1: Test account verification function
        print(f"\n🔍 STEP 1: Testing account verification...")
        from functions.verification_functions import verify_account_name
        
        verify_result = await verify_account_name(account_number, bank_name)
        print(f"   Verification Result: {verify_result}")
        
        if not verify_result.get('verified'):
            print("❌ Account verification failed - stopping test")
            return
        
        verified_name = verify_result.get('account_name')
        print(f"✅ Account verified: {verified_name}")
        
        # Step 2: Test OpenAI Assistant integration
        print(f"\n🤖 STEP 2: Testing OpenAI Assistant integration...")
        from assistant.sofi_assistant import get_assistant
        
        assistant = get_assistant()
        
        # Test verification through assistant
        verify_message = f"Verify account {account_number} at {bank_name}"
        print(f"   Assistant Message: {verify_message}")
        
        response, function_data = await assistant.process_message(test_chat_id, verify_message)
        print(f"   Assistant Response: {response}")
        
        if function_data and 'verify_account_name' in function_data:
            print(f"✅ Assistant verification worked: {function_data['verify_account_name']}")
        else:
            print("⚠️ Assistant verification function not called")
        
        # Step 3: Check if we have a test user or create one
        print(f"\n👤 STEP 3: Setting up test user...")
        from supabase import create_client
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Check for existing test user
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", test_chat_id).execute()
        
        if user_result.data:
            user_data = user_result.data[0]
            print(f"✅ Found test user: {user_data.get('full_name', 'Unknown')}")
            print(f"   Balance: ₦{user_data.get('wallet_balance', 0):,.2f}")
        else:
            print("❌ No test user found - creating one...")
            
            # Create a test user with sufficient balance
            test_user_data = {
                "telegram_chat_id": test_chat_id,
                "full_name": "Test User",
                "phone": "+2348000000000",
                "email": "test@sofi.ai",
                "wallet_balance": 10000.0,  # ₦10,000 balance
                "transaction_pin": "1998",  # Your PIN
                "is_verified": True,
                "created_at": "now()"
            }
            
            create_result = supabase.table("users").insert(test_user_data).execute()
            if create_result.data:
                print("✅ Test user created successfully")
                user_data = create_result.data[0]
            else:
                print("❌ Failed to create test user")
                return
        
        # Step 4: Test direct money transfer function
        print(f"\n💰 STEP 4: Testing direct money transfer...")
        from functions.transfer_functions import send_money
        
        transfer_result = await send_money(
            chat_id=test_chat_id,
            account_number=account_number,
            bank_name=bank_name,
            amount=amount,
            pin=pin,
            narration="Test transfer via Sofi AI"
        )
        
        print(f"   Transfer Result: {transfer_result}")
        
        if transfer_result.get('success'):
            print("✅ DIRECT TRANSFER SUCCESSFUL!")
            print(f"   {transfer_result.get('message', 'Transfer completed')}")
        else:
            print("❌ Direct transfer failed")
            print(f"   Error: {transfer_result.get('error')}")
        
        # Step 5: Test through OpenAI Assistant
        print(f"\n🤖 STEP 5: Testing transfer through OpenAI Assistant...")
        
        transfer_message = f"Send ₦{amount} to account {account_number} at {bank_name}"
        print(f"   Assistant Message: {transfer_message}")
        
        response, function_data = await assistant.process_message(test_chat_id, transfer_message)
        print(f"   Assistant Response: {response}")
        
        if function_data:
            print(f"   Functions Called: {list(function_data.keys())}")
            for func_name, func_result in function_data.items():
                print(f"     {func_name}: {func_result}")
        
        # Step 6: Test complete Telegram flow simulation
        print(f"\n📱 STEP 6: Testing Telegram webhook simulation...")
        
        # Simulate a Telegram message
        telegram_message = {
            "message": {
                "chat": {"id": int(test_chat_id.replace("real_user_test", "123456789"))},
                "from": {"id": 123456789, "first_name": "Test", "last_name": "User"},
                "text": f"Send ₦{amount} to {account_number} at {bank_name}"
            }
        }
        
        # Test the main message handler
        from main import handle_message
        
        chat_id_numeric = str(telegram_message["message"]["chat"]["id"])
        message_text = telegram_message["message"]["text"]
        user_context = telegram_message["message"]["from"]
        
        print(f"   Simulating Telegram message from {chat_id_numeric}: {message_text}")
        
        # Get user data
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", chat_id_numeric).execute()
        if not user_result.data:
            # Create user for this chat ID too
            test_user_data["telegram_chat_id"] = chat_id_numeric
            create_result = supabase.table("users").insert(test_user_data).execute()
        
        telegram_response = await handle_message(chat_id_numeric, message_text, user_context)
        print(f"   Telegram Response: {telegram_response}")
        
        print(f"\n🎉 TEST COMPLETED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error in comprehensive test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_transfer_with_pin())
