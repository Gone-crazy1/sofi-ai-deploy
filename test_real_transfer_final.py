#!/usr/bin/env python3
"""Create proper test user and test real money transfer"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.append('.')
load_dotenv()

async def create_test_user_and_transfer():
    """Create test user with proper schema and test real transfer"""
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Create proper test user
        test_user_data = {
            "telegram_chat_id": "real_user_test",
            "full_name": "Test User for PIN 1998",
            "email": "test1998@sofi.ai",
            "phone": "+2348000000000",
            "wallet_balance": 10000.0,
            "transaction_pin": "1998"
        }
        
        print("🔨 Creating test user with proper schema...")
        
        # Check if user exists
        existing = supabase.table("users").select("*").eq("telegram_chat_id", "real_user_test").execute()
        
        if existing.data:
            user_data = existing.data[0]
            print("✅ Test user already exists:")
            print(f"   Name: {user_data.get('full_name')}")
            print(f"   Balance: ₦{user_data.get('wallet_balance', 0):,.2f}")
            print(f"   PIN: {user_data.get('transaction_pin', 'Not set')}")
            
            # Update PIN if needed
            if user_data.get('transaction_pin') != "1998":
                print("🔄 Updating PIN to 1998...")
                supabase.table("users").update({"transaction_pin": "1998"}).eq("telegram_chat_id", "real_user_test").execute()
        else:
            create_result = supabase.table("users").insert(test_user_data).execute()
            if create_result.data:
                user_data = create_result.data[0]
                print("✅ Test user created successfully!")
            else:
                print("❌ Failed to create test user")
                return
        
        # Test account verification first
        print(f"\n🔍 Testing account verification...")
        from functions.verification_functions import verify_account_name
        
        account_number = "9325047112"
        bank_name = "Wema Bank"
        
        verify_result = await verify_account_name(account_number, bank_name)
        print(f"Verification: {verify_result}")
        
        if not verify_result.get('verified'):
            print("❌ Account verification failed")
            return
        
        print(f"✅ Account verified: {verify_result.get('account_name')}")
        
        # Test real money transfer
        print(f"\n💰 Testing real money transfer...")
        from functions.transfer_functions import send_money
        
        transfer_result = await send_money(
            chat_id="real_user_test",
            account_number=account_number,
            bank_name=bank_name,
            amount=100.0,
            pin="1998",
            narration="Real test transfer via Sofi AI"
        )
        
        print(f"Transfer result: {transfer_result}")
        
        if transfer_result.get('success'):
            print("🎉 REAL TRANSFER SUCCESSFUL!")
            print(f"Message: {transfer_result.get('message')}")
            
            # Check updated balance
            updated_user = supabase.table("users").select("wallet_balance").eq("telegram_chat_id", "real_user_test").execute()
            if updated_user.data:
                new_balance = updated_user.data[0].get('wallet_balance', 0)
                print(f"New balance: ₦{new_balance:,.2f}")
        else:
            print("❌ Transfer failed")
            print(f"Error: {transfer_result.get('error')}")
        
        # Test through OpenAI Assistant
        print(f"\n🤖 Testing through OpenAI Assistant...")
        from assistant.sofi_assistant import get_assistant
        
        assistant = get_assistant()
        
        transfer_message = f"Send ₦50 to account {account_number} at {bank_name}"
        print(f"Assistant message: {transfer_message}")
        
        response, function_data = await assistant.process_message("real_user_test", transfer_message)
        print(f"Assistant response: {response}")
        
        if function_data:
            print(f"Functions called: {list(function_data.keys())}")
            for func_name, func_result in function_data.items():
                print(f"  {func_name}: {func_result}")
        
        print(f"\n✅ ALL TESTS COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_user_and_transfer())
