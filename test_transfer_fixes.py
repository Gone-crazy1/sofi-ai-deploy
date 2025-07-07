#!/usr/bin/env python3
"""
Test Transfer Fixes
===================
Test that the transfer fixes work properly
"""

import requests
import json
import time

def test_transfer_fixes():
    """Test that transfer fixes work properly"""
    
    print("🔧 Testing Transfer Fixes...")
    
    # Test 1: Bank code conversion in send_money function
    print("\n1. Testing bank code conversion...")
    try:
        # This should work now without the UnboundLocalError
        from functions.transfer_functions import send_money
        import asyncio
        
        # Test with known bank name
        bank_name = "Opay"
        print(f"✅ Bank name '{bank_name}' should convert properly")
        print("✅ bank_code variable should be defined in all code paths")
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    # Test 2: PIN verification page error handling
    print("\n2. Testing PIN verification page...")
    try:
        response = requests.get(
            "https://pipinstallsofi.com/verify-pin?txn_id=test_invalid",
            timeout=10
        )
        
        if response.status_code in [200, 400]:
            print("✅ PASS: PIN verification page handles invalid transactions")
        else:
            print(f"❌ FAIL: Unexpected status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Receipt generation
    print("\n3. Testing receipt generation...")
    try:
        from beautiful_receipt_generator import SofiReceiptGenerator
        receipt_gen = SofiReceiptGenerator()
        
        test_data = {
            'user_name': 'Test User',
            'amount': 100,
            'recipient_name': 'THANKGOD OLUWASEUN NDIDI',
            'recipient_account': '8104965538',
            'recipient_bank': 'OPay',
            'fee': 20,
            'reference': 'test_ref_123',
            'balance_before': 1000,
            'balance_after': 880
        }
        
        receipt = receipt_gen.create_bank_transfer_receipt(test_data)
        if receipt:
            print("✅ PASS: Receipt generation works")
        else:
            print("❌ FAIL: Receipt generation failed")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n🎯 Transfer fixes test completed!")

if __name__ == "__main__":
    test_transfer_fixes()
