#!/usr/bin/env python3
"""
Simple test to verify parameter name fix works
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_send_money_direct():
    """Test send_money function directly with both parameter formats"""
    print("🧪 Testing send_money Function Parameter Compatibility...")
    
    test_chat_id = "TEST_PARAM_USER"
    
    try:
        from functions.transfer_functions import send_money
        
        # Test 1: New format (what OpenAI is sending)
        print(f"\n📱 Test 1: OpenAI Assistant format")
        result = await send_money(
            chat_id=test_chat_id,
            account_number="0252948419",  # New format
            bank_name="Wema Bank",        # New format
            amount=100,
            narration="Test transfer"
        )
        
        print(f"📊 Result: {json.dumps(result, indent=2, default=str)}")
        
        if result.get("requires_pin"):
            print(f"✅ OpenAI format works! PIN entry triggered.")
        elif result.get("success"):
            print(f"✅ OpenAI format works! Transfer completed.")
        else:
            print(f"❌ OpenAI format failed: {result.get('error')}")
        
        # Test 2: Old format (what was expected before)
        print(f"\n📱 Test 2: Original function format")
        result2 = await send_money(
            chat_id=test_chat_id,
            recipient_account="0252948419",  # Old format
            recipient_bank="Wema Bank",      # Old format
            amount=100,
            narration="Test transfer"
        )
        
        print(f"📊 Result: {json.dumps(result2, indent=2, default=str)}")
        
        if result2.get("requires_pin"):
            print(f"✅ Original format works! PIN entry triggered.")
        elif result2.get("success"):
            print(f"✅ Original format works! Transfer completed.")
        else:
            print(f"❌ Original format failed: {result2.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Error in direct function test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_send_money_direct())
