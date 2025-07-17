#!/usr/bin/env python3
"""
🎯 TEST BANK CODE FIX

Test that bank code '035' is now properly recognized as Wema Bank
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.bank_api import PaystackAPI

def test_bank_code_handling():
    """Test that bank codes are properly handled"""
    print("🔍 Testing Bank Code Handling Fix")
    print("=" * 50)
    
    paystack = PaystackAPI()
    
    # Test bank code '035' (Wema Bank)
    test_cases = [
        ("035", "Wema Bank code"),
        ("044", "Access Bank code"),
        ("999992", "Opay code"),
        ("wema bank", "Wema Bank name"),
        ("access bank", "Access Bank name"),
    ]
    
    for input_val, description in test_cases:
        result = paystack._get_bank_code(input_val)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {description}: '{input_val}' → '{result}'")
    
    print("\n🎯 Key Test:")
    wema_code = paystack._get_bank_code("035")
    if wema_code == "035":
        print("✅ SUCCESS: Bank code '035' correctly handled!")
        print("✅ Transfer should now work for Wema Bank transfers")
    else:
        print("❌ FAILED: Bank code '035' not handled correctly")
    
    return wema_code == "035"

if __name__ == "__main__":
    success = test_bank_code_handling()
    print(f"\n🎯 Overall Result: {'✅ FIXED' if success else '❌ STILL BROKEN'}")
