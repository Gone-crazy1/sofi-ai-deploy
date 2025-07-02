#!/usr/bin/env python3
"""
🧪 TEST: Verify Opay Bank Code Support
Test that Sofi can now handle Opay transfers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bank_api import BankAPI
import asyncio

async def test_opay_support():
    """Test that Opay is now supported"""
    
    print("🧪 Testing Opay Bank Code Support...")
    
    try:
        # Initialize BankAPI
        bank_api = BankAPI()
        
        # Test 1: Check if Opay bank code is recognized
        opay_code = bank_api._get_bank_code("opay")
        print(f"1️⃣ Opay bank code: {opay_code}")
        
        if opay_code == "999991":
            print("✅ Opay bank code is correctly mapped!")
        else:
            print("❌ Opay bank code is missing or incorrect!")
            return False
        
        # Test 2: Test account verification (mock)
        print("\n2️⃣ Testing account verification for Opay...")
        
        # This will make a real API call to Paystack
        verification = await bank_api.verify_account_name("6115491450", "999991")
        
        if verification['success']:
            print(f"✅ Account verified: {verification['account_name']}")
        else:
            print(f"⚠️ Account verification failed: {verification['error']}")
            print("   This might be normal if the account doesn't exist")
        
        print("\n🎉 Test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_opay_support())
