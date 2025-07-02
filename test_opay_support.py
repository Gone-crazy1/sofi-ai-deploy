#!/usr/bin/env python3
"""
🧪 Test Opay Bank Code and Account Verification
"""

import os
import asyncio
from dotenv import load_dotenv
from utils.bank_api import BankAPI

load_dotenv()

async def test_opay_support():
    """Test if Opay is now supported and can verify accounts"""
    
    print("🧪 Testing Opay Support in Sofi AI...")
    
    bank_api = BankAPI()
    
    # Test 1: Check if Opay bank code exists
    print("\n1️⃣ Testing Opay bank code lookup...")
    bank_code = bank_api.get_bank_code("opay")
    
    if bank_code:
        print(f"✅ Opay bank code found: {bank_code}")
    else:
        print("❌ Opay bank code not found")
        return
    
    # Test 2: Try different variations
    print("\n2️⃣ Testing Opay name variations...")
    variations = ["opay", "opay bank", "o pay", "OPAY", "OPay"]
    
    for variation in variations:
        code = bank_api.get_bank_code(variation)
        print(f"   '{variation}' → {code}")
    
    # Test 3: Test account verification (if you have a test account)
    print("\n3️⃣ Testing account verification...")
    test_account = "6115491450"  # Your test account
    
    try:
        result = bank_api.verify_account(test_account, bank_code)
        if result and result.get('verified'):
            print(f"✅ Account verification successful!")
            print(f"   Account Name: {result.get('account_name')}")
            print(f"   Account Number: {result.get('account_number')}")
            print(f"   Bank Code: {result.get('bank_code')}")
        else:
            print(f"⚠️ Account verification failed or returned None")
            print(f"   Result: {result}")
    except Exception as e:
        print(f"❌ Account verification error: {e}")
    
    print("\n🎉 Opay support test completed!")

if __name__ == "__main__":
    asyncio.run(test_opay_support())
