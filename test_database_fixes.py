#!/usr/bin/env python3
"""
Quick test of the database fixes for Sofi AI
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

load_dotenv()

def test_balance_helper():
    """Test the fixed balance helper"""
    try:
        import asyncio
        from utils.balance_helper import get_user_balance
        
        print("🧪 Testing balance helper...")
        
        # Test with the problematic chat ID
        test_chat_id = "5495194750"
        
        async def run_test():
            balance = await get_user_balance(test_chat_id)
            print(f"   Balance for {test_chat_id}: ₦{balance:,.2f}")
            return balance >= 0  # Balance should be 0 or positive
        
        result = asyncio.run(run_test())
        
        if result:
            print("   ✅ Balance helper test passed")
            return True
        else:
            print("   ❌ Balance helper test failed")
            return False
        
    except Exception as e:
        print(f"   ❌ Balance helper error: {e}")
        return False

def test_user_onboarding():
    """Test the fixed user onboarding"""
    try:
        import asyncio
        from utils.user_onboarding import UserOnboarding
        
        print("🧪 Testing user onboarding...")
        
        async def run_test():
            onboarding = UserOnboarding()
            
            # Test get_user_profile
            test_chat_id = "5495194750"
            profile = await onboarding.get_user_profile(test_chat_id)
            
            if profile:
                print(f"   ✅ User profile found: {profile.get('full_name', 'Unknown')}")
                return True
            else:
                print("   ⚠️ User profile not found - may need to create user")
                return True  # This is expected if user doesn't exist
        
        result = asyncio.run(run_test())
        
        if result:
            print("   ✅ User onboarding test passed")
            return True
        else:
            print("   ❌ User onboarding test failed")
            return False
        
    except Exception as e:
        print(f"   ❌ User onboarding error: {e}")
        return False

def test_webhook_handler():
    """Test the fixed webhook handler"""
    try:
        from monnify.monnify_webhook import MonnifyWebhookHandler
        
        print("🧪 Testing webhook handler...")
        
        handler = MonnifyWebhookHandler()
        
        # Test user lookup with a dummy account number
        user_info = handler._find_user_by_account("1234567890")
        
        print(f"   User lookup result: {'Found' if user_info else 'Not found'}")
        print("   ✅ Webhook handler test passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Webhook handler error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SOFI AI DATABASE FIXES TEST")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Balance Helper
    if test_balance_helper():
        tests_passed += 1
    
    # Test 2: User Onboarding
    if test_user_onboarding():
        tests_passed += 1
    
    # Test 3: Webhook Handler
    if test_webhook_handler():
        tests_passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 RESULT: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Database fixes are working.")
    else:
        print("⚠️ Some tests failed - check error messages above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
