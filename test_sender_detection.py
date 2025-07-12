#!/usr/bin/env python3
"""
🧪 TEST SENDER NAME DETECTION
============================

Test script to verify that sender name detection correctly identifies
real senders like "Ndidi ThankGod" and ignores virtual account names like "Mr hawt"
"""

import sys
import os
sys.path.append('.')

def test_sender_detection():
    """Test the updated sender name detection"""
    print("🧪 TESTING SENDER NAME DETECTION")
    print("=" * 40)
    
    # Import the webhook handler
    from paystack.paystack_webhook import PaystackWebhookHandler
    
    handler = PaystackWebhookHandler()
    
    # Test case 1: Real sender name in authorization
    test_data_1 = {
        "authorization": {
            "account_name": "Ndidi ThankGod",  # Real sender
            "sender_name": "Mr hawt"  # Virtual account - should be ignored
        },
        "payer_name": "Mr hawt",  # Virtual account - should be ignored
        "amount": 12000  # 120 naira
    }
    
    # Test case 2: Real sender in originator_name
    test_data_2 = {
        "originator_name": "THANKGOD NDIDI",
        "account_name": "Mr hawt",  # Virtual account - should be ignored
        "sender_name": "paystack"  # Should be ignored
    }
    
    # Test case 3: Real sender in metadata
    test_data_3 = {
        "metadata": {
            "real_sender": "Ndidi ThankGod",
            "account_holder_name": "NDIDI THANKGOD"
        },
        "payer_name": "Mr hawt"  # Virtual account - should be ignored
    }
    
    test_cases = [
        ("Real sender in authorization.account_name", test_data_1, {}),
        ("Real sender in originator_name", test_data_2, {}),
        ("Real sender in metadata", test_data_3, {})
    ]
    
    print("\n🔍 Running sender detection tests...")
    
    for test_name, data, customer in test_cases:
        print(f"\n📋 Test: {test_name}")
        print(f"   Input data: {data}")
        
        detected_name = handler._extract_sender_name(data, customer)
        print(f"   ✅ Detected sender: '{detected_name}'")
        
        # Check if it correctly identified the real sender
        expected_names = ["Ndidi ThankGod", "THANKGOD NDIDI", "NDIDI THANKGOD"]
        is_correct = any(expected.lower() in detected_name.lower() for expected in expected_names)
        
        if is_correct:
            print(f"   🎉 SUCCESS: Correctly identified real sender!")
        elif detected_name == "Bank Transfer":
            print(f"   ⚠️ ACCEPTABLE: Fell back to 'Bank Transfer' (better than virtual account)")
        else:
            print(f"   ❌ ISSUE: Should detect real sender, not '{detected_name}'")
    
    print(f"\n🔍 Testing virtual account filtering...")
    
    # Test that virtual accounts are properly ignored
    virtual_test = {
        "payer_name": "Mr hawt",  # Should be ignored
        "sender_name": "mr hawt",  # Should be ignored
        "account_name": "Sofi User"  # Should be ignored
    }
    
    detected = handler._extract_sender_name(virtual_test, {})
    print(f"   Virtual account test result: '{detected}'")
    
    if detected == "Bank Transfer":
        print(f"   ✅ SUCCESS: Virtual accounts correctly ignored!")
    else:
        print(f"   ❌ ISSUE: Should ignore virtual accounts")
    
    print(f"\n✅ SENDER DETECTION TEST COMPLETE")
    return True

if __name__ == "__main__":
    test_sender_detection()
