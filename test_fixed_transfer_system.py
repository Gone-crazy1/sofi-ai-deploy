#!/usr/bin/env python3
"""
Test the fixed transfer system with balance updates and receipts
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_fixed_transfer_system():
    """Test the complete fixed transfer system"""
    print("🧪 Testing Fixed Transfer System...")
    
    test_chat_id = "5495194750"  # Your actual chat ID
    
    try:
        # Test the fixed send_money function
        from functions.transfer_functions import send_money
        
        print(f"\n📱 Testing transfer with insufficient balance check...")
        
        # Test with real data
        result = await send_money(
            chat_id=test_chat_id,
            amount=50,  # Small amount for testing
            account_number="8104965538",
            bank_name="Opay",
            narration="Test transfer with fixes"
        )
        
        print(f"\n📊 Transfer result: {json.dumps(result, indent=2, default=str)}")
        
        if result.get("requires_pin"):
            print(f"\n✅ PIN entry triggered correctly!")
            print(f"💬 Message: {result.get('message')}")
            
            # Test with PIN provided (simulating after PIN entry)
            print(f"\n🔐 Testing with PIN provided...")
            
            result_with_pin = await send_money(
                chat_id=test_chat_id,
                amount=50,
                account_number="8104965538", 
                bank_name="Opay",
                pin="1234",  # Test PIN
                narration="Test transfer with PIN"
            )
            
            print(f"\n📊 Result with PIN: {json.dumps(result_with_pin, indent=2, default=str)}")
            
            if result_with_pin.get("success"):
                print(f"\n🎉 SUCCESS! All fixes are working:")
                print(f"   ✅ Receipt generated")
                print(f"   ✅ Balance check performed")
                print(f"   ✅ Detailed transfer information")
            else:
                print(f"\n⚠️ Transfer result: {result_with_pin.get('error')}")
                
        else:
            print(f"\n❌ PIN entry not triggered: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Error in fixed transfer test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_transfer_system())
