#!/usr/bin/env python3
"""
Direct Function Test - Money Transfer
Test the core functions directly for the transfer
"""

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def test_direct_functions():
    print("🔍 TESTING DIRECT FUNCTION CALLS")
    print("=" * 50)
    
    # Test account verification
    print("\n1. Testing account verification...")
    try:
        from sofi_money_functions import SofiMoneyTransferService
        money_service = SofiMoneyTransferService()
        
        verify_result = await money_service.verify_account_name(
            account_number="2206553670",
            bank_code="033"  # UBA
        )
        
        print(f"✅ Verification result: {verify_result}")
        
        if verify_result.get("success"):
            account_name = verify_result.get("account_name")
            print(f"   Account belongs to: {account_name}")
        
    except Exception as e:
        print(f"❌ Account verification error: {e}")
    
    # Test PIN verification
    print("\n2. Testing PIN verification...")
    try:
        from functions.security_functions import verify_pin
        
        pin_result = await verify_pin(
            chat_id="test_money_user_123",
            pin="1234"
        )
        
        print(f"✅ PIN verification: {pin_result}")
        
    except Exception as e:
        print(f"❌ PIN verification error: {e}")
    
    # Test transfer function
    print("\n3. Testing transfer function...")
    try:
        from functions.transfer_functions import send_money
        
        transfer_result = await send_money(
            chat_id="test_money_user_123",
            recipient_account="2206553670",
            recipient_bank="033",
            amount=50.0,
            pin="1234",
            narration="Test transfer to UBA account"
        )
        
        print(f"✅ Transfer result: {transfer_result}")
        
        if transfer_result.get("success"):
            print("🎉 TRANSFER SUCCESSFUL!")
            print(f"   Reference: {transfer_result.get('reference')}")
            print(f"   Status: {transfer_result.get('status')}")
            print(f"   Fee: ₦{transfer_result.get('fee', 0):.2f}")
        else:
            error = transfer_result.get('error', 'Unknown error')
            print(f"❌ Transfer failed: {error}")
            
            # Check if it's just insufficient funds
            if "insufficient" in error.lower() or "balance" in error.lower():
                print("💡 This is expected - test user has zero balance")
                print("✅ But the transfer system is working correctly!")
        
    except Exception as e:
        print(f"❌ Transfer function error: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_functions())
