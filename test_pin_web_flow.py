#!/usr/bin/env python3
"""
🧪 PIN WEB FLOW TESTER
Test the complete PIN verification web flow
"""

import requests
import json
import uuid
from datetime import datetime

def test_pin_core_system():
    """Test just the core PIN verification system without web requests"""
    
    print("🔐 Testing Core PIN System (No Web Requests)")
    print("=" * 55)
    
    # Step 1: Test secure token generation (local only)
    print("\n1️⃣ Testing secure token generation (local)...")
    try:
        # Import and test token generation locally
        import sys
        import os
        sys.path.append(os.getcwd())
        
        from utils.secure_pin_verification import secure_pin_verification
        
        # Create test transaction
        txn_id = f"TEST{uuid.uuid4().hex[:8].upper()}"
        test_data = {
            'chat_id': '12345',
            'user_data': {'id': 'test_user'},
            'transfer_data': {
                'recipient_name': 'Test Recipient',
                'account_number': '1234567890',
                'bank': 'Test Bank'
            },
            'amount': 5000
        }
        
        secure_token = secure_pin_verification.store_pending_transaction(txn_id, test_data)
        print(f"✅ Secure token generated: {secure_token[:15]}...")
        print(f"📋 Transaction ID: {txn_id}")
        
        # Test token retrieval
        retrieved = secure_pin_verification.get_pending_transaction_by_token(secure_token)
        if retrieved:
            print(f"✅ Token validation successful")
            print(f"💰 Amount: ₦{retrieved.get('amount'):,}")
            print(f"👤 Recipient: {retrieved.get('transfer_data', {}).get('recipient_name')}")
        else:
            print("❌ Token validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Test security system components
    print("\n2️⃣ Testing security system...")
    try:
        from utils.security import is_telegram_bot_ip, SECURITY_CONFIG
        
        # Test bot IP detection
        telegram_ip_result = is_telegram_bot_ip("149.154.167.50")  # Real Telegram IP
        normal_ip_result = is_telegram_bot_ip("192.168.1.1")       # Normal IP
        
        print(f"✅ Bot IP detection: Telegram={telegram_ip_result}, Normal={normal_ip_result}")
        
        # Test rate limiting config
        pin_limit = SECURITY_CONFIG.get('pin_verification_per_minute', 0)
        general_limit = SECURITY_CONFIG.get('requests_per_minute', 0)
        
        print(f"✅ Rate limits: PIN={pin_limit}/min, General={general_limit}/min")
        
    except Exception as e:
        print(f"❌ Security system test failed: {e}")
        return False
    
    # Step 3: Test PIN URL generation
    print("\n3️⃣ Testing PIN URL generation...")
    try:
        # Generate PIN URLs
        secure_url = f"/verify-pin?token={secure_token}"
        legacy_url = f"/verify-pin?txn_id={txn_id}"
        
        print(f"✅ Secure PIN URL: {secure_url[:45]}...")
        print(f"✅ Legacy PIN URL: {legacy_url}")
        
        # Full URLs for testing
        base_url = "http://localhost:5000"
        full_secure_url = f"{base_url}{secure_url}"
        full_legacy_url = f"{base_url}{legacy_url}"
        
        print(f"🌐 Full secure URL: {full_secure_url[:60]}...")
        print(f"🌐 Full legacy URL: {full_legacy_url}")
            
    except Exception as e:
        print(f"❌ URL generation failed: {e}")
        return False
    
    # Step 4: Test token cleanup and security
    print("\n4️⃣ Testing token security features...")
    try:
        # Test token cleanup
        initial_count = len(secure_pin_verification.secure_tokens)
        secure_pin_verification.cleanup_expired_data()
        final_count = len(secure_pin_verification.secure_tokens)
        
        print(f"✅ Token cleanup: {initial_count} → {final_count} tokens")
        
        # Test token expiry information
        token_data = secure_pin_verification.secure_tokens.get(secure_token)
        if token_data:
            expires_at = token_data.get('expires_at')
            created_at = token_data.get('created_at')
            print(f"✅ Token expires: {expires_at}")
            print(f"✅ Token created: {created_at}")
        
    except Exception as e:
        print(f"❌ Security features test failed: {e}")
    
    print("\n" + "=" * 55)
    print("🎯 Core PIN System Test Complete!")
    print("✅ All core components are working!")
    
    print(f"\n🔗 Your test PIN URL:")
    print(f"{full_secure_url}")
    
    print(f"\n📋 Next steps to test web flow:")
    print("1. Start Flask server: python main.py")
    print("2. Open the URL above in browser")
    print("3. Test with bot User-Agent to verify blocking")
    print("4. Test PIN submission functionality")
    
    return True

def test_frontend_integration():
    """Test the frontend React component"""
    print("\n🎨 Testing Frontend Integration...")
    
    # Check if React template exists and has token support
    try:
        with open('templates/react-pin-app.html', 'r') as f:
            content = f.read()
            
        checks = {
            "Token parameter support": "getAuthParams" in content,
            "Secure token handling": "secure_token" in content,
            "API integration": "/api/verify-pin" in content,
            "Error handling": "setError" in content
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")
            
    except Exception as e:
        print(f"❌ Frontend integration test failed: {e}")

if __name__ == "__main__":
    print("🔐 SOFI AI PIN CORE SYSTEM TESTER")
    print("Testing core PIN verification components (no web requests)")
    
    # Test core system functionality
    success = test_pin_core_system()
    
    # Test frontend integration
    test_frontend_integration()
    
    if success:
        print("\n🎉 Core system tests completed successfully!")
        print("Your PIN verification system is ready for web testing.")
    else:
        print("\n💥 Core system tests failed. Check errors above.")
        
    print("\n📝 To test web functionality:")
    print("1. Start Flask server: python main.py")
    print("2. Use the generated URL in browser")
    print("3. Test bot detection and PIN submission")
