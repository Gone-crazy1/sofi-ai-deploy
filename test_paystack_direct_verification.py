#!/usr/bin/env python3
"""Test Paystack account verification directly"""

import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

async def test_paystack_verification():
    """Test Paystack account verification with different accounts"""
    try:
        from utils.bank_api import BankAPI
        
        bank_api = BankAPI()
        
        # Test different accounts
        test_accounts = [
            {"account": "0123456789", "bank": "Access Bank", "code": "044"},  # Access Bank
            {"account": "6115491450", "bank": "OPay", "code": "999991"},  # OPay
            {"account": "1234567890", "bank": "GTBank", "code": "058"},  # GTBank
        ]
        
        for test in test_accounts:
            print(f"\n🔍 Testing {test['bank']} ({test['code']}) - Account: {test['account']}")
            
            result = await bank_api.verify_account_name(test['account'], test['code'])
            
            print(f"   Result: {result}")
        
        # Check if we have valid API key
        print(f"\n🔑 PAYSTACK_SECRET_KEY configured: {'Yes' if os.getenv('PAYSTACK_SECRET_KEY') else 'No'}")
        secret_key = os.getenv('PAYSTACK_SECRET_KEY')
        if secret_key:
            print(f"   Key starts with: {secret_key[:12]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_paystack_verification())
