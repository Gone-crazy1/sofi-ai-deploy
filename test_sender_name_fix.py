#!/usr/bin/env python3
"""
Test the improved sender name detection in webhook handler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paystack.paystack_webhook import PaystackWebhookHandler

def test_sender_name_extraction():
    """Test various sender name scenarios"""
    handler = PaystackWebhookHandler()
    
    print("🧪 Testing Enhanced Sender Name Detection\n")
    
    # Test cases with different webhook data patterns
    test_cases = [
        {
            "description": "Virtual account name 'Mr hawt' (should filter out)",
            "data": {
                "payer_name": "Mr hawt",
                "sender_name": "Mr hawt",
                "account_name": "Mr hawt"
            },
            "customer": {},
            "expected": "Bank Transfer"
        },
        {
            "description": "Virtual account name 'tobi' (should filter out)",
            "data": {
                "payer_name": "tobi",
                "narration": "Transfer from tobi to virtual account"
            },
            "customer": {},
            "expected": "Bank Transfer"
        },
        {
            "description": "Real sender name with virtual account noise",
            "data": {
                "payer_name": "Mr hawt",  # Virtual account name
                "narration": "Transfer from John Adebayo to account"
            },
            "customer": {},
            "expected": "John Adebayo"
        },
        {
            "description": "Clear real sender name",
            "data": {
                "payer_name": "ADEBAYO MICHAEL",
                "sender_name": "ADEBAYO MICHAEL"
            },
            "customer": {},
            "expected": "ADEBAYO MICHAEL"
        },
        {
            "description": "Sender in customer object",
            "data": {},
            "customer": {
                "name": "Sarah Johnson",
                "first_name": "Sarah",
                "last_name": "Johnson"
            },
            "expected": "Sarah Johnson"
        },
        {
            "description": "Sender in authorization field",
            "data": {
                "authorization": {
                    "account_name": "IBRAHIM HASSAN",
                    "sender_name": "IBRAHIM HASSAN"
                }
            },
            "customer": {},
            "expected": "IBRAHIM HASSAN"
        },
        {
            "description": "Sender in metadata",
            "data": {
                "metadata": {
                    "real_sender": "Ahmed Musa",
                    "sender_name": "Ahmed Musa"
                }
            },
            "customer": {},
            "expected": "Ahmed Musa"
        },
        {
            "description": "Complex narration with real sender",
            "data": {
                "narration": "Credit from OLUMIDE ADEYEMI to virtual account 9876543210",
                "payer_name": "tobi"  # Virtual account noise
            },
            "customer": {},
            "expected": "OLUMIDE ADEYEMI"
        },
        {
            "description": "Short/invalid names (should fall back)",
            "data": {
                "payer_name": "AB",  # Too short
                "sender_name": "test"  # Test pattern
            },
            "customer": {},
            "expected": "Bank Transfer"
        },
        {
            "description": "Paystack internal transaction",
            "data": {
                "payer_name": "Paystack DVA",
                "sender_name": "Virtual Account 123"
            },
            "customer": {},
            "expected": "Bank Transfer"
        }
    ]
    
    # Run test cases
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}: {case['description']}")
        
        result = handler._extract_sender_name(case['data'], case['customer'])
        expected = case['expected']
        
        if result == expected:
            print(f"   ✅ PASS: Got '{result}' (expected: '{expected}')")
            passed += 1
        else:
            print(f"   ❌ FAIL: Got '{result}' (expected: '{expected}')")
            failed += 1
        
        print()
    
    # Summary
    print(f"📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Enhanced sender name detection is working correctly.")
        print("\n🔥 Benefits:")
        print("• Filters out virtual account names like 'Mr hawt' and 'tobi'")
        print("• Extracts real sender names from transaction narrations")
        print("• Provides clear 'Bank Transfer' fallback when sender unknown")
        print("• Checks multiple data fields for sender information")
        print("• Validates sender names to avoid displaying test/temp accounts")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review the logic for improvement.")

if __name__ == "__main__":
    test_sender_name_extraction()
