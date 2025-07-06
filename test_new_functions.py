"""
Test the new Sofi AI functions
"""

import asyncio
import os
from dotenv import load_dotenv
from sofi_money_functions import SofiMoneyTransferService

load_dotenv()

async def test_new_functions():
    """Test all the new functions"""
    print("🧪 Testing Sofi AI new functions...")
    
    service = SofiMoneyTransferService()
    test_chat_id = "test_5495194750"  # Your chat ID for testing
    
    try:
        # Test 1: Check balance
        print("\n1️⃣ Testing check_balance...")
        balance_result = await service.check_user_balance(test_chat_id)
        print(f"Balance result: {balance_result}")
        
        # Test 2: Get virtual account
        print("\n2️⃣ Testing get_virtual_account...")
        va_result = await service.get_virtual_account(test_chat_id, test_chat_id)
        print(f"Virtual account result: {va_result}")
        
        # Test 3: Calculate transfer fee
        print("\n3️⃣ Testing calculate_transfer_fee...")
        fee_result = await service.calculate_transfer_fee(test_chat_id, test_chat_id, 5000)
        print(f"Fee calculation result: {fee_result}")
        
        # Test 4: Get transfer history
        print("\n4️⃣ Testing get_transfer_history...")
        history_result = await service.get_transfer_history(test_chat_id, test_chat_id)
        print(f"Transfer history result: {history_result}")
        
        # Test 5: Get beneficiaries
        print("\n5️⃣ Testing get_user_beneficiaries...")
        beneficiaries_result = await service.get_user_beneficiaries(test_chat_id, test_chat_id)
        print(f"Beneficiaries result: {beneficiaries_result}")
        
        # Test 6: Save beneficiary (if table exists)
        print("\n6️⃣ Testing save_beneficiary...")
        try:
            save_result = await service.save_beneficiary(
                test_chat_id, test_chat_id, 
                "Test Beneficiary", "1234567890", "Test Bank", "test friend"
            )
            print(f"Save beneficiary result: {save_result}")
        except Exception as e:
            print(f"Save beneficiary failed (expected if table doesn't exist): {e}")
        
        print("\n✅ Function tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_functions())
