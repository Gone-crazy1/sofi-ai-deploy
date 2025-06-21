#!/usr/bin/env python3
"""
Test Monnify webhook processing for credit alerts
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

load_dotenv()

def test_webhook_credit_processing():
    """Test webhook credit processing with sample data"""
    try:
        from monnify.monnify_webhook import MonnifyWebhookHandler
        
        print("🔔 TESTING WEBHOOK CREDIT PROCESSING")
        print("=" * 45)
        
        handler = MonnifyWebhookHandler()
        
        # Sample webhook data for successful transaction
        sample_webhook_data = {
            "eventType": "SUCCESSFUL_TRANSACTION",
            "eventData": {
                "transactionReference": f"SOFI_TEST_{int(datetime.now().timestamp())}",
                "amountPaid": 1000.00,
                "customer": {
                    "email": "test@sofi.ai"
                },
                "accountDetails": {
                    "accountNumber": "1234567890",  # Test account number
                    "accountName": "TEST USER",
                    "bankCode": "035",
                    "bankName": "Wema Bank"
                },
                "transactionDate": datetime.now().isoformat(),
                "paymentMethod": "ACCOUNT_TRANSFER",
                "paymentStatus": "PAID"
            }
        }
        
        print(f"📨 Processing test webhook...")
        print(f"   Event Type: {sample_webhook_data['eventType']}")
        print(f"   Amount: ₦{sample_webhook_data['eventData']['amountPaid']:,.2f}")
        print(f"   Account: {sample_webhook_data['eventData']['accountDetails']['accountNumber']}")
        
        # Process the webhook
        result = handler.handle_webhook(sample_webhook_data)
        
        print(f"\n📊 Webhook Processing Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
        
        if result.get('success'):
            print("   ✅ Webhook processing successful!")
            print("   💡 This means credit alerts should work when you receive real payments.")
        else:
            print("   ⚠️ Webhook processing failed - this explains why you're not getting credit alerts.")
            print("   🔧 Check the error message above for troubleshooting.")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_lookup_by_account():
    """Test if we can find users by virtual account number"""
    try:
        from monnify.monnify_webhook import MonnifyWebhookHandler
        
        print("\n👤 TESTING USER LOOKUP BY ACCOUNT")
        print("=" * 40)
        
        handler = MonnifyWebhookHandler()
        
        # Test with the problematic chat ID's account
        test_accounts = ["1234567890", "0123456789", "9876543210"]
        
        for account in test_accounts:
            print(f"🔍 Looking up account: {account}")
            user_info = handler._find_user_by_account(account)
            
            if user_info:
                print(f"   ✅ Found user: {user_info.get('full_name', 'Unknown')}")
                print(f"   📱 Chat ID: {user_info.get('telegram_chat_id', 'N/A')}")
                return True
            else:
                print(f"   ❌ User not found for account {account}")
        
        print("\n💡 If no users were found, this explains why webhook credit alerts aren't working.")
        print("   Solution: Ensure virtual accounts in database have proper user associations.")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing user lookup: {e}")
        return False

def main():
    """Run webhook tests"""
    print("🔔 SOFI AI WEBHOOK & CREDIT ALERT TESTING")
    print("=" * 55)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Webhook processing
    if test_webhook_credit_processing():
        tests_passed += 1
    
    # Test 2: User lookup by account
    if test_user_lookup_by_account():
        tests_passed += 1
    
    print("\n" + "=" * 55)
    print(f"📊 WEBHOOK TESTS RESULT: {tests_passed}/{total_tests} passed")
    
    if tests_passed > 0:
        print("✅ Webhook system is partially working!")
        print("\n🚀 Next steps to fix credit alerts:")
        print("   1. Ensure your virtual account is properly linked to your user record")
        print("   2. Check Monnify webhook URL is correctly configured")
        print("   3. Verify webhook endpoint is accessible from Monnify servers")
        print("   4. Test with a real small transfer to validate end-to-end flow")
    else:
        print("❌ Webhook system needs more work to handle credit alerts properly.")
    
    print(f"\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
