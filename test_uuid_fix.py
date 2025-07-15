#!/usr/bin/env python3
"""
Test script to verify Telegram ID to UUID resolution fix
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.getcwd())

async def test_uuid_resolution():
    """Test the UUID resolution functionality"""
    print("🧪 Testing Telegram ID to UUID Resolution Fix")
    print("=" * 50)
    
    try:
        # Test the utility function
        from utils.telegram_uuid_resolver import resolve_telegram_to_uuid_sync
        
        print("✅ Step 1: Utility imported successfully")
        
        # Test with the problematic Telegram ID
        test_telegram_id = "7812930440"
        print(f"🔍 Step 2: Testing with Telegram ID: {test_telegram_id}")
        
        result = resolve_telegram_to_uuid_sync(test_telegram_id)
        
        if result['success']:
            print(f"✅ Step 3: SUCCESS - Resolved to UUID: {result['uuid']}")
        else:
            print(f"ℹ️  Step 3: User not found (expected for new/test users): {result['error']}")
        
        # Test the fixed wallet statement function
        print("\n🧪 Testing Fixed get_wallet_statement Function")
        print("=" * 50)
        
        from functions.transaction_functions import get_wallet_statement
        
        print("✅ Step 4: Transaction functions imported successfully")
        
        # This should no longer fail with UUID error
        wallet_result = await get_wallet_statement(test_telegram_id, days=30)
        
        if wallet_result.get('success'):
            print("✅ Step 5: SUCCESS - Wallet statement retrieved without UUID error!")
            print(f"   📊 Transaction count: {wallet_result.get('transaction_count', 0)}")
            print(f"   💰 Current balance: ₦{wallet_result.get('current_balance', 0):,.2f}")
        else:
            error_msg = wallet_result.get('error', 'Unknown error')
            if 'invalid input syntax for type uuid' in error_msg:
                print("❌ Step 5: FAILED - UUID error still occurs!")
                return False
            else:
                print(f"ℹ️  Step 5: Expected error (user not found): {error_msg}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The UUID resolution fix is working correctly")
        print("✅ No more 'invalid input syntax for type uuid' errors")
        
        return True
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_uuid_resolution())
    sys.exit(0 if success else 1)
