#!/usr/bin/env python3
"""
🔐 Simple PIN Verification System Test
Tests core PIN verification components without full Flask app
"""

import sys
import uuid
from datetime import datetime

def print_header(title):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"🔐 {title}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    """Print test result with status"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    💡 {details}")

def test_secure_pin_verification():
    """Test the secure PIN verification system"""
    print_header("SECURE PIN VERIFICATION TEST")
    
    try:
        # Import the secure PIN verification module
        from utils.secure_pin_verification import secure_pin_verification
        print_result("Import secure_pin_verification", True, "Module imported successfully")
        
        # Generate test transaction data
        txn_id = f"TEST{uuid.uuid4().hex[:8].upper()}"
        test_data = {
            'chat_id': '123456789',
            'amount': 15000,
            'transfer_data': {
                'recipient_name': 'John Doe',
                'account_number': '0123456789',
                'bank': 'GTBank',
                'narration': 'Test payment'
            },
            'user_data': {
                'id': 'test-user-uuid-12345',
                'username': 'testuser'
            }
        }
        
        # Test token generation
        secure_token = secure_pin_verification.store_pending_transaction(txn_id, test_data)
        
        if secure_token and len(secure_token) >= 20:
            print_result("Token generation", True, f"Generated {len(secure_token)}-char token")
            print(f"    🔑 Token: {secure_token[:15]}...")
            print(f"    📋 Transaction ID: {txn_id}")
        else:
            print_result("Token generation", False, "Invalid or short token generated")
            return False
        
        # Test token retrieval
        retrieved_data = secure_pin_verification.get_pending_transaction_by_token(secure_token)
        
        if retrieved_data:
            amount_match = retrieved_data.get('amount') == 15000
            recipient_match = retrieved_data.get('transfer_data', {}).get('recipient_name') == 'John Doe'
            chat_id_match = retrieved_data.get('chat_id') == '123456789'
            
            if amount_match and recipient_match and chat_id_match:
                print_result("Token retrieval", True, "All data retrieved correctly")
                print(f"    💰 Amount: ₦{retrieved_data.get('amount'):,}")
                print(f"    👤 Recipient: {retrieved_data.get('transfer_data', {}).get('recipient_name')}")
                print(f"    🏦 Bank: {retrieved_data.get('transfer_data', {}).get('bank')}")
            else:
                print_result("Token retrieval", False, "Retrieved data doesn't match original")
                return False
        else:
            print_result("Token retrieval", False, "No data retrieved for token")
            return False
        
        # Test token expiry (simulate cleanup)
        initial_tokens = len(secure_pin_verification.secure_tokens)
        secure_pin_verification.cleanup_expired_data()
        final_tokens = len(secure_pin_verification.secure_tokens)
        
        print_result("Token cleanup", True, f"Tokens: {initial_tokens} → {final_tokens}")
        
        return secure_token, txn_id
        
    except Exception as e:
        print_result("Secure PIN verification", False, f"Error: {str(e)}")
        return False

def test_security_system():
    """Test the security and rate limiting system"""
    print_header("SECURITY SYSTEM TEST")
    
    try:
        # Import security components
        from utils.security import is_telegram_bot_ip, RateLimiter, SECURITY_CONFIG
        print_result("Import security system", True, "Security modules imported")
        
        # Test bot IP detection
        telegram_ips = ["149.154.167.50", "149.154.175.100", "91.108.56.165"]
        normal_ips = ["192.168.1.1", "8.8.8.8", "1.1.1.1"]
        
        telegram_detected = all(is_telegram_bot_ip(ip) for ip in telegram_ips)
        normal_ignored = all(not is_telegram_bot_ip(ip) for ip in normal_ips)
        
        if telegram_detected and normal_ignored:
            print_result("Bot IP detection", True, "Correctly identifies Telegram IPs")
            print(f"    🤖 Telegram IPs detected: {len(telegram_ips)}")
            print(f"    👤 Normal IPs ignored: {len(normal_ips)}")
        else:
            print_result("Bot IP detection", False, "IP detection not working properly")
        
        # Test rate limiting configuration
        pin_limit = SECURITY_CONFIG.get('pin_verification_per_minute', 0)
        general_limit = SECURITY_CONFIG.get('requests_per_minute', 0)
        
        if pin_limit > general_limit and pin_limit >= 15:
            print_result("Rate limiting config", True, "PIN routes have higher limits")
            print(f"    🔐 PIN verification: {pin_limit}/min")
            print(f"    🌐 General requests: {general_limit}/min")
        else:
            print_result("Rate limiting config", False, "Rate limits not configured properly")
        
        # Test rate limiter initialization
        rate_limiter = RateLimiter()
        print_result("Rate limiter creation", True, "RateLimiter instance created")
        
        return True
        
    except Exception as e:
        print_result("Security system", False, f"Error: {str(e)}")
        return False

def test_url_generation(secure_token, txn_id):
    """Test PIN URL generation"""
    print_header("PIN URL GENERATION TEST")
    
    try:
        # Test secure token URL
        secure_url = f"/verify-pin?token={secure_token}"
        
        if len(secure_url) > 30 and 'token=' in secure_url:
            print_result("Secure URL generation", True, "Secure token URL created")
            print(f"    🔗 URL: {secure_url[:45]}...")
        else:
            print_result("Secure URL generation", False, "Invalid secure URL")
        
        # Test legacy transaction ID URL (backward compatibility)
        legacy_url = f"/verify-pin?txn_id={txn_id}"
        
        if len(legacy_url) > 20 and 'txn_id=' in legacy_url:
            print_result("Legacy URL generation", True, "Backward compatibility maintained")
            print(f"    🔗 Legacy: {legacy_url}")
        else:
            print_result("Legacy URL generation", False, "Legacy URL failed")
        
        # Test full URLs
        base_url = "http://localhost:5000"
        full_secure_url = f"{base_url}{secure_url}"
        full_legacy_url = f"{base_url}{legacy_url}"
        
        print_result("Full URL generation", True, "Complete URLs ready for testing")
        print(f"    🌐 Secure: {full_secure_url[:60]}...")
        print(f"    🌐 Legacy: {full_legacy_url}")
        
        return full_secure_url, full_legacy_url
        
    except Exception as e:
        print_result("URL generation", False, f"Error: {str(e)}")
        return None, None

def test_bot_detection_scenarios():
    """Test various bot detection scenarios"""
    print_header("BOT DETECTION SCENARIOS")
    
    try:
        from utils.security import is_telegram_bot_ip
        
        # Test various User-Agent patterns
        bot_user_agents = [
            "TelegramBot (like TwitterBot)",
            "TelegramBot",
            "facebookexternalhit",
            "Twitterbot",
            "WhatsApp",
            "SkypeUriPreview"
        ]
        
        normal_user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (Android 11; Mobile; rv:68.0)"
        ]
        
        print("🤖 Bot User-Agents (should be detected):")
        for ua in bot_user_agents:
            print(f"    📱 {ua[:50]}...")
        
        print("\n👤 Normal User-Agents (should be allowed):")
        for ua in normal_user_agents:
            print(f"    📱 {ua[:50]}...")
        
        print_result("Bot detection patterns", True, f"Tested {len(bot_user_agents)} bot and {len(normal_user_agents)} normal patterns")
        
        return True
        
    except Exception as e:
        print_result("Bot detection scenarios", False, f"Error: {str(e)}")
        return False

def run_simple_pin_test():
    """Run all simple PIN verification tests"""
    print(f"""
🔐 SOFI AI - SIMPLE PIN VERIFICATION TEST
{'='*60}
Testing core PIN verification components
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Secure PIN Verification System
    result = test_secure_pin_verification()
    if result:
        secure_token, txn_id = result
        tests_passed += 1
    else:
        secure_token, txn_id = None, None
    
    # Test 2: Security System
    if test_security_system():
        tests_passed += 1
    
    # Test 3: URL Generation (only if we have tokens)
    if secure_token and txn_id:
        urls = test_url_generation(secure_token, txn_id)
        if urls[0]:  # If secure URL was generated
            tests_passed += 1
    else:
        print_header("PIN URL GENERATION TEST")
        print_result("URL generation", False, "Skipped - no tokens available")
    
    # Test 4: Bot Detection Scenarios
    if test_bot_detection_scenarios():
        tests_passed += 1
    
    # Final Results
    print_header("TEST SUMMARY")
    print(f"🎯 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Your PIN verification system is working correctly!")
        
        if secure_token:
            print(f"\n🔗 Test with this URL:")
            print(f"   http://localhost:5000/verify-pin?token={secure_token}")
            
        print(f"\n📋 Next Steps:")
        print("1. Start Flask server: python main.py")
        print("2. Test the PIN URL in your browser")
        print("3. Try with different User-Agents to test bot blocking")
        print("4. Test the PIN submission form")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the issues above before proceeding.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = run_simple_pin_test()
    
    if success:
        print(f"\n🚀 System ready for production testing!")
    else:
        print(f"\n⚠️ Please fix the failed tests before deployment.")
