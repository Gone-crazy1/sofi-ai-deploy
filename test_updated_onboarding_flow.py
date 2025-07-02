#!/usr/bin/env python3
"""
Test Updated Onboarding Flow with Correct DVA Handling
Tests the complete flow including DVA retry logic
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our modules
from utils.user_onboarding import SofiUserOnboarding

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_updated_onboarding():
    """Test the updated onboarding flow with correct DVA handling"""
    
    print("🚀 Testing Updated Onboarding Flow with DVA Retry Logic")
    print("=" * 60)
    
    try:
        # Create onboarding service
        onboarding = SofiUserOnboarding()
        
        # Test user data
        test_user = {
            'telegram_id': f'test_user_{int(datetime.now().timestamp())}',
            'full_name': 'Updated Flow Tester',
            'phone': '+2348123456789',
            'email': 'updated.test@example.com',
            'address': 'Lagos, Nigeria',
            'bvn': '12345678901'
        }
        
        print(f"\n📝 Test User Data:")
        print(f"   Telegram ID: {test_user['telegram_id']}")
        print(f"   Name: {test_user['full_name']}")
        print(f"   Phone: {test_user['phone']}")
        print(f"   Email: {test_user['email']}")
        
        # Step 1: Test onboarding
        print(f"\n🔄 Starting onboarding process...")
        result = await onboarding.create_new_user(test_user)
        
        if result.get('success'):
            print(f"\n✅ Onboarding successful!")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Customer ID: {result.get('customer_id')}")
            print(f"   Customer Code: {result.get('customer_code')}")
            
            account_details = result.get('account_details', {})
            if account_details:
                print(f"\n🏦 Account Details:")
                print(f"   Account Number: {account_details.get('account_number')}")
                print(f"   Account Name: {account_details.get('account_name')}")
                print(f"   Bank: {account_details.get('bank_name')}")
                print(f"   Bank Code: {account_details.get('bank_code')}")
            else:
                print("⚠️ No account details returned")
            
            print(f"\n📨 Message: {result.get('message')}")
            
            # Test duplicate user check
            print(f"\n🔄 Testing duplicate user detection...")
            duplicate_result = await onboarding.create_new_user(test_user)
            
            if not duplicate_result.get('success'):
                print(f"✅ Duplicate user correctly detected: {duplicate_result.get('error')}")
            else:
                print(f"❌ Duplicate user not detected!")
            
        elif result.get('pending_dva'):
            print(f"\n⏳ DVA creation is pending")
            print(f"   Customer Code: {result.get('customer_code')}")
            print(f"   Retry Instructions: {result.get('retry_instructions')}")
            
        else:
            print(f"\n❌ Onboarding failed: {result.get('error')}")
            if result.get('error'):
                print(f"   Error details: {result['error']}")
            
        print(f"\n✨ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        logger.error(f"Test error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_updated_onboarding())
