#!/usr/bin/env python3
"""
Test All Critical Fixes
=======================
Test that all user-facing features are working
"""

import asyncio
import os
from dotenv import load_dotenv
from sofi_money_functions import SofiMoneyTransferService

load_dotenv()

async def test_all_fixes():
    """Test all critical fixes"""
    
    print("🔧 Testing All Critical Fixes...")
    
    try:
        service = SofiMoneyTransferService()
        test_chat_id = "5495194750"  # The user who was having issues
        
        # Test 1: Balance check
        print("\n1️⃣ Testing balance check...")
        balance_result = await service.check_user_balance(test_chat_id)
        print(f"Balance result: {balance_result}")
        
        # Test 2: Get beneficiaries
        print("\n2️⃣ Testing get beneficiaries...")
        beneficiaries_result = await service.get_user_beneficiaries(test_chat_id, test_chat_id)
        print(f"Beneficiaries result: {beneficiaries_result}")
        
        # Test 3: Save beneficiary (test data)
        print("\n3️⃣ Testing save beneficiary...")
        save_result = await service.save_beneficiary(
            telegram_chat_id=test_chat_id,
            user_id=test_chat_id,
            name="Test Beneficiary",
            account_number="1234567890",
            bank_name="Test Bank",
            nickname="Test Contact"
        )
        print(f"Save beneficiary result: {save_result}")
        
        # Test 4: PIN verification (after fix)
        print("\n4️⃣ Testing PIN verification...")
        from functions.security_functions import verify_pin
        pin_result = await verify_pin(test_chat_id, "1998")
        print(f"PIN verification result: {pin_result}")
        
        # Test 5: Check if user has PIN set
        print("\n5️⃣ Testing PIN status...")
        from supabase import create_client
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        user_result = supabase.table("users").select("pin_hash, has_pin").eq("telegram_chat_id", test_chat_id).execute()
        if user_result.data:
            user_data = user_result.data[0]
            print(f"PIN status: pin_hash exists = {bool(user_data.get('pin_hash'))}, has_pin = {user_data.get('has_pin')}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_fixes())
