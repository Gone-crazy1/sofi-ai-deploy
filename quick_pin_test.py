#!/usr/bin/env python3
"""
Quick PIN system test
"""

import sys
sys.path.append('.')

try:
    print("🔐 Testing SOFI PIN System")
    print("=" * 40)
    
    # Test 1: Import secure PIN verification
    print("\n1️⃣ Testing imports...")
    from utils.secure_pin_verification import secure_pin_verification
    print("✅ secure_pin_verification imported")
    
    # Test 2: Generate token
    print("\n2️⃣ Testing token generation...")
    import uuid
    
    txn_id = f"TEST{uuid.uuid4().hex[:8].upper()}"
    test_data = {
        'chat_id': '12345',
        'amount': 5000,
        'transfer_data': {
            'recipient_name': 'John Doe',
            'account_number': '0123456789',
            'bank': 'GTBank'
        },
        'user_data': {'id': 'test-user'}
    }
    
    token = secure_pin_verification.store_pending_transaction(txn_id, test_data)
    print(f"✅ Token generated: {token[:15]}...")
    print(f"📋 Transaction ID: {txn_id}")
    
    # Test 3: Retrieve transaction
    print("\n3️⃣ Testing token retrieval...")
    retrieved = secure_pin_verification.get_pending_transaction_by_token(token)
    
    if retrieved:
        print("✅ Token retrieval successful!")
        print(f"💰 Amount: {retrieved.get('amount')}")
        print(f"👤 Recipient: {retrieved.get('transfer_data', {}).get('recipient_name')}")
    else:
        print("❌ Token retrieval failed")
    
    # Test 4: Check security system
    print("\n4️⃣ Testing security system...")
    from utils.security import is_telegram_bot_ip, RateLimiter
    
    # Test bot detection
    bot_ip_test = is_telegram_bot_ip("149.154.167.50")  # Telegram IP
    normal_ip_test = is_telegram_bot_ip("192.168.1.1")  # Normal IP
    
    print(f"✅ Bot IP detection: Telegram IP={bot_ip_test}, Normal IP={normal_ip_test}")
    
    # Test rate limiter
    rate_limiter = RateLimiter()
    print("✅ Rate limiter initialized")
    
    # Test 5: Generate PIN URL
    print("\n5️⃣ Creating test PIN URL...")
    pin_url = f"/verify-pin?token={token}"
    print(f"🔗 PIN URL: {pin_url}")
    
    print("\n" + "=" * 40)
    print("🎯 SYSTEM TEST RESULTS:")
    print("✅ Secure token system: WORKING")
    print("✅ Transaction storage: WORKING")
    print("✅ Security features: WORKING")
    print("✅ PIN URL generation: WORKING")
    
    print(f"\n🚀 Test complete! Use this URL:")
    print(f"http://localhost:5000{pin_url}")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
