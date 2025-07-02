"""
Test Updated Sofi AI Onboarding System with Paystack
====================================================
Test the new Paystack-based onboarding flow to ensure everything works.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_onboarding():
    """Test the complete onboarding process"""
    
    print("🧪 TESTING SOFI AI ONBOARDING WITH PAYSTACK")
    print("=" * 50)
    
    try:
        # Import the updated onboarding service
        from utils.user_onboarding import SofiUserOnboarding
        
        # Initialize onboarding service
        onboarding_service = SofiUserOnboarding()
        print("✅ Onboarding service initialized successfully")
        
        # Test user data (using test data that won't conflict)
        test_user_data = {
            'telegram_id': 'test_user_123456',  # Test ID
            'full_name': 'John Test User',
            'phone': '08012345678',
            'email': 'john.test@example.com',
            'address': 'Lagos, Nigeria',
            'bvn': '12345678901'  # Optional BVN for verification
        }
        
        print(f"\n📋 Testing with user data:")
        print(f"   Name: {test_user_data['full_name']}")
        print(f"   Phone: {test_user_data['phone']}")
        print(f"   Email: {test_user_data['email']}")
        print(f"   Telegram ID: {test_user_data['telegram_id']}")
        
        # Test the onboarding process
        print(f"\n🏦 Creating Paystack virtual account...")
        
        result = await onboarding_service.create_new_user(test_user_data)
        
        if result['success']:
            print("✅ ONBOARDING SUCCESSFUL!")
            print(f"\n📋 Account Details:")
            print(f"   User ID: {result['user_id']}")
            print(f"   Full Name: {result['full_name']}")
            print(f"   Customer ID: {result.get('customer_id', 'N/A')}")
            
            account_details = result.get('account_details', {})
            if account_details:
                print(f"\n🏦 Virtual Account:")
                print(f"   Account Number: {account_details['account_number']}")
                print(f"   Account Name: {account_details['account_name']}")
                print(f"   Bank Name: {account_details['bank_name']}")
                print(f"   Bank Code: {account_details['bank_code']}")
            
            print(f"\n💬 Message: {result['message']}")
            
            # Test getting user profile
            print(f"\n👤 Testing user profile retrieval...")
            profile = await onboarding_service.get_user_profile(test_user_data['telegram_id'])
            
            if profile:
                print("✅ User profile retrieved successfully")
                print(f"   Balance: ₦{profile['balance']:,.2f}")
                print(f"   Daily Limit: ₦{profile['daily_limit']:,.2f}")
                print(f"   Verified: {'Yes' if profile['is_verified'] else 'No'}")
            else:
                print("❌ Could not retrieve user profile")
                
        else:
            print("❌ ONBOARDING FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
            # If user already exists, that's also a success
            if "already registered" in result.get('error', '').lower():
                print("ℹ️  This is expected if the test user already exists")
                
                # Try to get existing user profile
                print(f"\n👤 Getting existing user profile...")
                profile = await onboarding_service.get_user_profile(test_user_data['telegram_id'])
                
                if profile:
                    print("✅ Existing user profile found")
                    print(f"   Name: {profile['full_name']}")
                    print(f"   Account: {profile['account_number']}")
                    print(f"   Bank: {profile['bank_name']}")
                    print(f"   Balance: ₦{profile['balance']:,.2f}")
        
        # Test the synchronous wrapper (used by Flask endpoint)
        print(f"\n🌐 Testing Flask endpoint wrapper...")
        sync_result = onboarding_service.create_virtual_account({
            'telegram_id': 'test_user_sync_789',
            'full_name': 'Jane Sync Test',
            'phone': '08087654321',
            'email': 'jane.sync@example.com'
        })
        
        if sync_result['success']:
            print("✅ Synchronous onboarding wrapper works!")
        else:
            print(f"❌ Sync wrapper failed: {sync_result.get('error')}")
            if "already registered" in sync_result.get('error', '').lower():
                print("ℹ️  User already exists (expected for repeat tests)")
        
        print(f"\n🎉 ONBOARDING TEST COMPLETED!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are properly installed")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    asyncio.run(test_onboarding())
