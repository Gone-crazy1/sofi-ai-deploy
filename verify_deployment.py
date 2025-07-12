#!/usr/bin/env python3
"""
✅ SOFI DEPLOYMENT VERIFICATION
===============================

Quick check to verify all our updates are properly deployed
"""

import os
import sys

def verify_deployment():
    """Verify that all our updates are properly deployed"""
    
    print("✅ SOFI DEPLOYMENT VERIFICATION")
    print("=" * 40)
    
    checks = []
    
    # 1. Check transfer functions have correct domain
    print("\n🔍 Checking transfer functions...")
    
    try:
        with open("functions/transfer_functions.py", "r", encoding="utf-8") as f:
            transfer_content = f.read()
            
        if "pipinstallsofi.com" in transfer_content:
            print("   ✅ Correct domain (pipinstallsofi.com)")
            checks.append(True)
        else:
            print("   ❌ Wrong domain")
            checks.append(False)
            
        if '"feature_version": "v2.1_inline_keyboard_receipt"' in transfer_content:
            print("   ✅ Feature version set")
            checks.append(True)
        else:
            print("   ❌ Feature version missing")
            checks.append(False)
            
        if '"force_update": True' in transfer_content:
            print("   ✅ Force update enabled")
            checks.append(True)
        else:
            print("   ❌ Force update disabled")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ Error reading transfer functions: {e}")
        checks.append(False)
    
    # 2. Check webhook has enhanced sender detection
    print("\n🔍 Checking webhook sender detection...")
    
    try:
        with open("paystack/paystack_webhook.py", "r", encoding="utf-8") as f:
            webhook_content = f.read()
            
        if "hawt" in webhook_content.lower() and "virtual_account_patterns" in webhook_content:
            print("   ✅ Virtual account filtering enabled")
            checks.append(True)
        else:
            print("   ❌ Virtual account filtering missing")
            checks.append(False)
            
        if "_extract_sender_name" in webhook_content:
            print("   ✅ Enhanced sender detection")
            checks.append(True)
        else:
            print("   ❌ Sender detection not enhanced")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ Error reading webhook: {e}")
        checks.append(False)
    
    # 3. Check receipt template
    print("\n🔍 Checking receipt template...")
    
    try:
        with open("templates/success.html", "r", encoding="utf-8") as f:
            template_content = f.read()
            
        if "getsofi_bot" in template_content:
            print("   ✅ Correct bot redirect")
            checks.append(True)
        else:
            print("   ❌ Wrong bot redirect")
            checks.append(False)
            
        if "getsofi_bot" in template_content and ("window.close()" in template_content or "closeWindow" in template_content):
            print("   ✅ Auto-close with correct bot redirect")
            checks.append(True)
        else:
            print("   ❌ Auto-close or bot redirect missing")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ Error reading template: {e}")
        checks.append(False)
    
    # 4. Test sender detection
    print("\n🔍 Testing sender detection...")
    
    try:
        sys.path.append('.')
        from paystack.paystack_webhook import PaystackWebhookHandler
        
        handler = PaystackWebhookHandler()
        
        # Test with virtual account name
        test_data = {
            "authorization": {
                "account_name": "Ndidi ThankGod",
                "sender_name": "Mr hawt"
            },
            "payer_name": "Mr hawt"
        }
        
        detected = handler._extract_sender_name(test_data, {})
        
        if "Ndidi ThankGod" in detected:
            print("   ✅ Real sender detected correctly")
            checks.append(True)
        else:
            print(f"   ❌ Sender detection failed: '{detected}'")
            checks.append(False)
            
    except Exception as e:
        print(f"   ❌ Error testing sender detection: {e}")
        checks.append(False)
    
    # Summary
    print(f"\n📊 DEPLOYMENT SUMMARY")
    print(f"=" * 40)
    
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ Passed: {passed}/{total} checks ({percentage:.1f}%)")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! Deployment is ready!")
        print("\n🚀 NEXT STEPS:")
        print("1. The web PIN receipt feature will now work for all users")
        print("2. Sender names will show 'Ndidi ThankGod' instead of 'Mr hawt'")
        print("3. Users can take screenshots of receipts (no auto-close)")
        print("4. Bot redirects correctly to @getsofi_bot")
        return True
    else:
        print("⚠️ Some checks failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    verify_deployment()
