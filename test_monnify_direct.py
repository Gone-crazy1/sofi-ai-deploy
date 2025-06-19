#!/usr/bin/env python3
"""
Direct test of Monnify transfer function
"""

import os
import uuid
from datetime import datetime

def test_monnify_send_money():
    """Test the send_money function directly"""
    print("🧪 DIRECT MONNIFY TRANSFER TEST")
    print("=" * 40)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment variables
    required_vars = ['MONNIFY_API_KEY', 'MONNIFY_SECRET_KEY', 'MONNIFY_BASE_URL']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    
    print("✅ Environment variables present")
    
    # Test imports
    try:
        from monnify.Transfers import send_money
        from monnify.Auth import get_monnify_token
        print("✅ Monnify functions imported")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test authentication
    try:
        print("\n🔑 Testing authentication...")
        token = get_monnify_token()
        if token:
            print(f"✅ Token received: {token[:15]}...")
        else:
            print("❌ No token received")
            return False
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False
    
    # Test transfer
    try:
        print("\n💰 Testing transfer...")
        
        # Test transfer parameters
        test_params = {
            'amount': 100.00,
            'bank_code': '044',  # Access Bank
            'account_number': '0123456789',
            'narration': 'Test transfer from Sofi AI',
            'reference': f'SOFI_TEST_{uuid.uuid4().hex[:8]}'
        }
        
        print(f"Parameters: {test_params}")
        
        # Execute transfer
        result = send_money(
            amount=test_params['amount'],
            bank_code=test_params['bank_code'],
            account_number=test_params['account_number'],
            narration=test_params['narration'],
            reference=test_params['reference']
        )
        
        print(f"\n📨 Transfer result: {result}")
        
        if result and result.get('requestSuccessful'):
            print("✅ TRANSFER SUCCESSFUL!")
            return True
        else:
            print("❌ Transfer failed")
            print(f"Error: {result.get('responseMessage', 'Unknown') if result else 'No response'}")
            return False
            
    except Exception as e:
        print(f"❌ Transfer error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bank_api_execution():
    """Test BankAPI execute_transfer function"""
    print("\n🏦 TESTING BANK API EXECUTE_TRANSFER")
    print("=" * 40)
    
    try:
        from utils.bank_api import BankAPI
        bank_api = BankAPI()
        print("✅ BankAPI imported")
        
        # Test data
        transfer_data = {
            'recipient_account': '0123456789',
            'recipient_bank': 'Access Bank',
            'amount': 100.00,
            'narration': 'Test via BankAPI'
        }
        
        print(f"Transfer data: {transfer_data}")
        
        # Execute
        import asyncio
        result = asyncio.run(bank_api.execute_transfer(transfer_data))
        
        print(f"Result: {result}")
        
        if result and result.get('success'):
            print("✅ BANK API TRANSFER SUCCESSFUL!")
            return True
        else:
            print("❌ Bank API transfer failed")
            return False
            
    except Exception as e:
        print(f"❌ BankAPI error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 MONNIFY TRANSFER VERIFICATION")
    print("=" * 50)
    
    # Test 1: Direct Monnify function
    monnify_success = test_monnify_send_money()
    
    # Test 2: BankAPI wrapper
    bank_api_success = test_bank_api_execution()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"Monnify Direct: {'✅ PASS' if monnify_success else '❌ FAIL'}")
    print(f"BankAPI Wrapper: {'✅ PASS' if bank_api_success else '❌ FAIL'}")
    
    if monnify_success or bank_api_success:
        print("\n🎉 TRANSFER CAPABILITY CONFIRMED!")
        print("✅ Sofi can send money via Monnify API")
    else:
        print("\n⚠️  Transfer tests failed")
        print("🔧 Check environment variables and Monnify setup")
