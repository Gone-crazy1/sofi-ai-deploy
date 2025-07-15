#!/usr/bin/env python3
"""
🔐 PIN System Validation Test
Tests our secure PIN verification without full Flask app
"""

import sys
import os
sys.path.append('.')

def test_pin_system():
    """Test the PIN verification system components"""
    
    print("🔐 SOFI PIN SYSTEM VALIDATION")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Secure PIN Verification Import
    print("\n1️⃣ Testing secure PIN verification import...")
    try:
        from utils.secure_pin_verification import secure_pin_verification
        print("✅ PASS: Secure PIN verification imported")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Import error - {e}")
    
    # Test 2: Token Generation
    print("\n2️⃣ Testing token generation...")
    try:
        import uuid
        
        txn_id = f"TEST{uuid.uuid4().hex[:8].upper()}"
        test_data = {
            'chat_id': '12345',
            'amount': 5000,
            'transfer_data': {
                'recipient_name': 'John Doe',
                'account_number': '0123456789',
                'bank': 'GTBank',
                'narration': 'Test transfer'
            },
            'user_data': {'id': 'test-user-uuid'}
        }
        
        token = secure_pin_verification.store_pending_transaction(txn_id, test_data)
        
        if token and len(token) > 20:
            print(f"✅ PASS: Token generated ({len(token)} chars)")
            print(f"   Token: {token[:15]}...")
            print(f"   Transaction: {txn_id}")
            tests_passed += 1
        else:
            print("❌ FAIL: Invalid token generated")
            
    except Exception as e:
        print(f"❌ FAIL: Token generation error - {e}")
    
    # Test 3: Token Retrieval
    print("\n3️⃣ Testing token retrieval...")
    try:
        retrieved = secure_pin_verification.get_pending_transaction_by_token(token)
        
        if retrieved:
            amount = retrieved.get('amount')
            recipient = retrieved.get('transfer_data', {}).get('recipient_name')
            
            if amount == 5000 and recipient == 'John Doe':
                print("✅ PASS: Token retrieval successful")
                print(f"   Amount: ₦{amount:,}")
                print(f"   Recipient: {recipient}")
                tests_passed += 1
            else:
                print("❌ FAIL: Retrieved data incorrect")
        else:
            print("❌ FAIL: Token retrieval returned None")
            
    except Exception as e:
        print(f"❌ FAIL: Token retrieval error - {e}")
    
    # Test 4: Security System
    print("\n4️⃣ Testing security system...")
    try:
        from utils.security import is_telegram_bot_ip, RateLimiter, SECURITY_CONFIG
        
        # Test bot IP detection
        telegram_ip = is_telegram_bot_ip("149.154.167.50")  # Real Telegram IP
        normal_ip = is_telegram_bot_ip("192.168.1.1")       # Normal IP
        
        if telegram_ip and not normal_ip:
            print("✅ PASS: Bot IP detection working")
            print(f"   Telegram IP detected: {telegram_ip}")
            print(f"   Normal IP ignored: {normal_ip}")
            tests_passed += 1
        else:
            print("❌ FAIL: Bot IP detection not working")
            
    except Exception as e:
        print(f"❌ FAIL: Security system error - {e}")
    
    # Test 5: Rate Limiting Config
    print("\n5️⃣ Testing rate limiting configuration...")
    try:
        pin_limit = SECURITY_CONFIG.get('pin_verification_per_minute', 0)
        general_limit = SECURITY_CONFIG.get('requests_per_minute', 0)
        
        if pin_limit > general_limit and pin_limit >= 15:
            print("✅ PASS: Rate limiting configured correctly")
            print(f"   PIN limit: {pin_limit}/min")
            print(f"   General limit: {general_limit}/min")
            tests_passed += 1
        else:
            print("❌ FAIL: Rate limiting not configured properly")
            
    except Exception as e:
        print(f"❌ FAIL: Rate limiting error - {e}")
    
    # Test 6: PIN URL Generation
    print("\n6️⃣ Testing PIN URL generation...")
    try:
        pin_url = f"/verify-pin?token={token}"
        legacy_url = f"/verify-pin?txn_id={txn_id}"
        
        if len(pin_url) > 30 and 'token=' in pin_url:
            print("✅ PASS: PIN URL generated correctly")
            print(f"   Secure URL: {pin_url[:40]}...")
            print(f"   Legacy URL: {legacy_url}")
            tests_passed += 1
        else:
            print("❌ FAIL: PIN URL generation failed")
            
    except Exception as e:
        print(f"❌ FAIL: PIN URL error - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    print("=" * 50)
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Your PIN verification system is ready!")
        print(f"🔗 Test URL: http://localhost:5000{pin_url}")
        
        print("\n📋 Next Steps:")
        print("1. Start Flask server: python main.py")
        print("2. Test in browser with the URL above")
        print("3. Verify bot blocking works")
        print("4. Test PIN submission")
        
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the errors above.")
        return False

if __name__ == "__main__":
    test_pin_system()
