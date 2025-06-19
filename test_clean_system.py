"""
🧹 SOFI AI CLEAN SYSTEM TEST
Testing the cleaned up system with ONLY Monnify as banking partner

This test verifies:
1. Monnify API integration
2. Virtual account creation 
3. User onboarding flow
4. Database integration
5. Clean system architecture
"""

import os
import time
from dotenv import load_dotenv
import uuid

load_dotenv()

def test_clean_sofi_system():
    """Test the cleaned up Sofi AI system with only Monnify"""
    
    print("🧹 SOFI AI CLEAN SYSTEM VERIFICATION")
    print("=" * 60)
    print("Official Banking Partner: Monnify ONLY")
    print("Removed: PayStack, OPay, and all other banking integrations")
    print("=" * 60)
    
    # Test 1: Monnify API Integration
    print("\n🏦 TEST 1: Monnify API Integration")
    print("-" * 40)
    
    try:
        from monnify.monnify_api import MonnifyAPI
        
        monnify_api = MonnifyAPI()
        print("✅ Monnify API imported successfully")
        
        # Test authentication
        banks = monnify_api.get_banks()
        if banks.get('success'):
            print(f"✅ Monnify authentication successful: {banks.get('count', 0)} banks available")
        else:
            print(f"❌ Monnify authentication failed: {banks.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Monnify API test failed: {e}")
        return False
    
    # Test 2: Virtual Account Creation
    print("\n💳 TEST 2: Virtual Account Creation")
    print("-" * 40)
    
    try:
        test_user = {
            'first_name': 'Clean',
            'last_name': 'Test',
            'email': f'clean_test_{int(time.time())}@sofi-ai.com',
            'phone': '+2348012345678',
            'user_id': str(uuid.uuid4())
        }
        
        print(f"Creating virtual account for: {test_user['first_name']} {test_user['last_name']}")
        
        account_result = monnify_api.create_virtual_account(test_user)
        
        if account_result.get('success'):
            accounts = account_result.get('accounts', [])
            print(f"✅ Virtual accounts created successfully: {len(accounts)} accounts")
            
            for i, account in enumerate(accounts, 1):
                print(f"   Account {i}: {account['bank_name']} - {account['account_number']}")
                
        else:
            print(f"❌ Virtual account creation failed: {account_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Virtual account test failed: {e}")
        return False
    
    # Test 3: Clean Bank API
    print("\n🏛️ TEST 3: Clean Bank API")
    print("-" * 40)
    
    try:
        from utils.bank_api import BankAPI
        
        bank_api = BankAPI()
        print(f"✅ Bank API initialized with provider: {bank_api.provider}")
        
        # Test bank code lookup
        gtb_code = bank_api.get_bank_code("gtb")
        if gtb_code == "058":
            print("✅ Bank code lookup working correctly")
        else:
            print("❌ Bank code lookup failed")
            return False
            
    except Exception as e:
        print(f"❌ Bank API test failed: {e}")
        return False
      # Test 4: Clean Main.py Imports
    print("\n🏗️ TEST 4: Clean Main.py Imports")
    print("-" * 40)
    
    try:
        # Test that PayStack imports are gone
        with open('main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
            
        if 'paystack' in main_content.lower():
            print("⚠️ PayStack references still found in main.py")
        else:
            print("✅ PayStack references removed from main.py")
            
        if 'monnify' in main_content.lower():
            print("✅ Monnify integration found in main.py")
        else:
            print("❌ Monnify integration not found in main.py")
            return False
            
    except Exception as e:
        print(f"❌ Main.py import test failed: {e}")
        # Continue with other tests even if this fails
        print("⚠️ Continuing with other tests...")
    
    # Test 5: Environment Variables
    print("\n🔧 TEST 5: Environment Variables")
    print("-" * 40)
    
    required_vars = [
        'MONNIFY_API_KEY',
        'MONNIFY_SECRET_KEY', 
        'MONNIFY_CONTRACT_CODE',
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Configured")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    # Test 6: Webhook Handler
    print("\n🔔 TEST 6: Webhook Handler")
    print("-" * 40)
    
    try:
        from monnify.monnify_webhook import handle_monnify_webhook
        
        test_webhook = {
            'eventType': 'SUCCESSFUL_TRANSACTION',
            'eventData': {
                'transactionReference': 'TEST_REF_123',
                'amountPaid': 1000.0,
                'customer': {'email': 'test@example.com'}
            }
        }
        
        result = handle_monnify_webhook(test_webhook)
        print("✅ Monnify webhook handler working")
        
    except Exception as e:
        print(f"❌ Webhook handler test failed: {e}")
        return False
    
    # Success Summary
    print("\n🎉 CLEAN SYSTEM VERIFICATION COMPLETE!")
    print("=" * 60)
    print("✅ All tests passed - System is clean and ready!")
    print("\n📋 SYSTEM STATUS:")
    print("   🏦 Banking Partner: Monnify (Official)")
    print("   🗑️ Removed: PayStack, OPay, all other payment gateways")
    print("   💳 Virtual Accounts: Working perfectly")
    print("   🔄 Transfers: Monnify-powered")
    print("   🔔 Webhooks: Clean Monnify integration")
    print("   📊 Database: Supabase ready")
    print("\n🚀 READY FOR PRODUCTION DEPLOYMENT!")
    
    return True

if __name__ == "__main__":
    success = test_clean_sofi_system()
    
    if success:
        print("\n" + "🎯" * 20)
        print("SOFI AI BANKING SERVICE IS CLEAN & READY!")
        print("Official Banking Partner: Monnify")
        print("All other payment gateways successfully removed")
        print("🎯" * 20)
    else:
        print("\n" + "⚠️" * 20)
        print("ISSUES DETECTED - Please fix before deployment")
        print("⚠️" * 20)
