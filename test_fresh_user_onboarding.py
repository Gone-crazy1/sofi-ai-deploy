#!/usr/bin/env python3
"""
Test Fresh User Onboarding (No Duplicates)
Tests the complete flow with a unique user to verify everything works
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

async def test_fresh_user_onboarding():
    """Test onboarding with a completely fresh user"""
    
    print("🆕 Testing Fresh User Onboarding (No Duplicates)")
    print("=" * 60)
    
    try:
        # Create onboarding service
        onboarding = SofiUserOnboarding()
        
        # Create a unique user each time
        timestamp = int(datetime.now().timestamp())
        test_user = {
            'telegram_id': f'fresh_user_{timestamp}',
            'full_name': f'Fresh User {timestamp}',
            'phone': f'+234812345{timestamp % 10000:04d}',  # Unique phone
            'email': f'fresh.user.{timestamp}@example.com',  # Unique email
            'address': 'Lagos, Nigeria',
            'bvn': '12345678901'
        }
        
        print(f"\n📝 Fresh User Data:")
        print(f"   Telegram ID: {test_user['telegram_id']}")
        print(f"   Name: {test_user['full_name']}")
        print(f"   Phone: {test_user['phone']}")
        print(f"   Email: {test_user['email']}")
        
        # Step 1: Test onboarding
        print(f"\n🔄 Starting fresh user onboarding...")
        result = await onboarding.create_new_user(test_user)
        
        if result.get('success'):
            print(f"\n🎉 ONBOARDING SUCCESSFUL!")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Customer ID: {result.get('customer_id')}")
            print(f"   Customer Code: {result.get('customer_code')}")
            
            account_details = result.get('account_details', {})
            if account_details:
                print(f"\n🏦 COMPLETE Account Details:")
                print(f"   Account Number: {account_details.get('account_number')}")
                print(f"   Account Name: {account_details.get('account_name')}")
                print(f"   Bank: {account_details.get('bank_name')}")
                print(f"   Bank Code: {account_details.get('bank_code')}")
            else:
                print("⚠️ No account details returned")
            
            print(f"\n📨 Message: {result.get('message')}")
            
            # Step 2: Test immediate duplicate detection
            print(f"\n🔄 Testing immediate duplicate detection...")
            duplicate_result = await onboarding.create_new_user(test_user)
            
            if not duplicate_result.get('success'):
                print(f"✅ Duplicate user correctly detected: {duplicate_result.get('error')}")
                if duplicate_result.get('existing_user'):
                    print("✅ Duplicate detection flag set correctly")
            else:
                print(f"❌ Duplicate user NOT detected - this is a problem!")
            
            print(f"\n🎯 FINAL RESULT: Complete user onboarding successful!")
            
        elif result.get('pending_dva'):
            print(f"\n⏳ DVA creation is pending")
            print(f"   Customer Code: {result.get('customer_code')}")
            print(f"   Retry Instructions: {result.get('retry_instructions')}")
            
        else:
            print(f"\n❌ Onboarding failed: {result.get('error')}")
            if result.get('existing_user'):
                print("ℹ️ This was due to existing user conflict")
            
        print(f"\n✨ Fresh user test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        logger.error(f"Test error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_fresh_user_onboarding())
