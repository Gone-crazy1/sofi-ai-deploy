#!/usr/bin/env python3
"""
Test the receipt generation and balance update
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_transfer_with_receipt():
    """Test transfer with proper receipt and balance update"""
    print("🧪 Testing Transfer with Receipt and Balance Update...")
    
    # Use actual test user ID
    test_chat_id = "5495194750"
    
    try:
        # Test the send_money function with PIN (simulating completed PIN entry)
        from functions.transfer_functions import send_money
        
        print(f"\n📱 Simulating transfer with PIN provided...")
        
        result = await send_money(
            chat_id=test_chat_id,
            account_number="8104965538",  # Test Opay account
            bank_name="Opay",
            amount=100,  # Valid minimum amount
            pin="1234",  # Simulate PIN provided
            narration="Test transfer with receipt"
        )
        
        print(f"\n📊 Transfer result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Balance Updated: {result.get('balance_updated')}")
        print(f"   New Balance: ₦{result.get('new_balance', 0):,.2f}")
        print(f"   DB Saved: {result.get('db_saved')}")
        print(f"   Reference: {result.get('reference')}")
        
        if result.get("success"):
            print(f"\n✅ SUCCESS! Receipt generated:")
            print(f"━━━━━━━━━━━━━━━━━━━━━")
            print(result.get("message", "No message"))
            print(f"━━━━━━━━━━━━━━━━━━━━━")
        else:
            print(f"\n❌ Transfer failed: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Error in transfer test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_balance_check():
    """Test balance checking logic"""
    print(f"\n🧪 Testing Balance Check Logic...")
    
    test_chat_id = "5495194750"
    
    try:
        from functions.transfer_functions import send_money
        
        # Test with amount higher than balance
        result = await send_money(
            chat_id=test_chat_id,
            account_number="8104965538",
            bank_name="Opay", 
            amount=5000,  # High amount to trigger insufficient balance
            pin="1234",
            narration="Test insufficient balance"
        )
        
        print(f"   High amount result: {result.get('success')} - {result.get('error', 'No error')}")
        
    except Exception as e:
        print(f"   Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_balance_check())
    asyncio.run(test_transfer_with_receipt())
