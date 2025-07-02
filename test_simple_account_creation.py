#!/usr/bin/env python3
"""
SIMPLE PAYSTACK ACCOUNT CREATION TEST
====================================
This script tests just the core account creation functionality:
1. Create Paystack customer
2. Create dedicated virtual account (DVA)
3. Store in Supabase
4. Verify all data is correct
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase import create_client, Client
    from paystack.paystack_service import PaystackService
    from utils.balance_helper import get_user_balance
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you have installed all required packages:")
    print("pip install supabase paystack python-dotenv")
    sys.exit(1)

class SimpleAccountCreationTest:
    def __init__(self):
        """Initialize the tester."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')  # Use SUPABASE_KEY instead of SERVICE_ROLE_KEY
        self.paystack_secret = os.getenv('PAYSTACK_SECRET_KEY')
        
        # Test user data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_user = {
            'telegram_chat_id': f'test_simple_{timestamp}',
            'phone_number': '+2348123456789',
            'full_name': 'Simple Test User',
            'email': f'simple_test_{timestamp}@sofi.ai'
        }
        
        print("🧪 Simple Paystack Account Creation Test")
        print(f"📧 Test Email: {self.test_user['email']}")
        
    def check_environment(self):
        """Check environment variables."""
        print("\n1️⃣ Checking Environment...")
        
        missing = []
        for var in ['SUPABASE_URL', 'SUPABASE_KEY', 'PAYSTACK_SECRET_KEY']:
            if not os.getenv(var):
                missing.append(var)
                print(f"❌ {var}: Missing")
            else:
                print(f"✅ {var}: Set")
        
        return len(missing) == 0
    
    def test_supabase(self):
        """Test Supabase connection."""
        print("\n2️⃣ Testing Supabase...")
        
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            result = self.supabase.table('users').select('count', count='exact').execute()
            print(f"✅ Supabase connected! Users table has {result.count} records")
            return True
        except Exception as e:
            print(f"❌ Supabase failed: {e}")
            return False
    
    def test_paystack(self):
        """Test Paystack connection."""
        print("\n3️⃣ Testing Paystack...")
        
        try:
            self.paystack = PaystackService()
            banks = self.paystack.get_supported_banks()
            if banks and banks.get('success'):
                print(f"✅ Paystack connected! Found banks data")
                return True
            else:
                print(f"❌ Paystack connection issue: {banks}")
                return False
        except Exception as e:
            print(f"❌ Paystack failed: {e}")
            return False
    
    async def create_customer_and_dva(self):
        """Create Paystack customer and dedicated virtual account."""
        print("\n4️⃣ Creating Customer and DVA...")
        
        try:
            user_data = {
                'email': self.test_user['email'],
                'first_name': self.test_user['full_name'].split()[0],
                'last_name': self.test_user['full_name'].split()[-1],
                'phone': self.test_user['phone_number'],
                'preferred_bank': 'wema-bank'
            }
            
            # Use the create_user_account method
            result = self.paystack.create_user_account(user_data)
            
            if result and result.get('success'):
                data = result['data']
                print(f"✅ Account created successfully!")
                
                # Extract customer and account information
                if 'customer_code' in data:
                    self.test_user['paystack_customer_code'] = data['customer_code']
                if 'account_number' in data:
                    self.test_user['paystack_account_number'] = data['account_number']
                if 'bank_name' in data:
                    self.test_user['paystack_bank_name'] = data['bank_name']
                
                print(f"   Customer Code: {self.test_user.get('paystack_customer_code', 'Pending')}")
                print(f"   Account Number: {self.test_user.get('paystack_account_number', 'Pending')}")
                print(f"   Bank: {self.test_user.get('paystack_bank_name', 'Pending')}")
                
                return True
            else:
                print(f"❌ Account creation failed: {result}")
                return False
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    def store_in_supabase(self):
        """Store user in Supabase."""
        print("\n5️⃣ Storing in Database...")
        
        try:
            # Use only basic columns that should exist
            result = self.supabase.table('users').insert({
                'telegram_chat_id': self.test_user['telegram_chat_id'],
                'phone_number': self.test_user['phone_number'],
                'full_name': self.test_user['full_name'],
                'email': self.test_user['email'],
                'paystack_customer_code': self.test_user.get('paystack_customer_code'),
                'paystack_dva_id': self.test_user.get('paystack_dva_id'),
                'paystack_account_number': self.test_user.get('paystack_account_number'),
                'paystack_bank_name': self.test_user.get('paystack_bank_name'),
                'wallet_balance': 0.00
                # Removed is_verified and is_active in case they don't exist
            }).execute()
            
            if result.data:
                user_id = result.data[0]['id']
                print(f"✅ User stored! ID: {user_id}")
                self.test_user['user_id'] = user_id
                return True
            else:
                print(f"❌ Storage failed: {result}")
                return False
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    async def test_balance(self):
        """Test balance retrieval."""
        print("\n6️⃣ Testing Balance...")
        
        try:
            balance = await get_user_balance(self.test_user['telegram_chat_id'])
            print(f"✅ Balance retrieved: ₦{balance:,.2f}")
            return True
        except Exception as e:
            print(f"❌ Balance test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up test data."""
        print("\n7️⃣ Cleaning up...")
        
        try:
            self.supabase.table('users').delete().eq(
                'telegram_chat_id', self.test_user['telegram_chat_id']
            ).execute()
            print("✅ Cleanup complete!")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def run_test(self):
        """Run the complete test."""
        print("=" * 50)
        print("🧪 PAYSTACK ACCOUNT CREATION TEST")
        print("=" * 50)
        
        steps = [
            ("Environment Check", self.check_environment),
            ("Supabase Test", self.test_supabase),
            ("Paystack Test", self.test_paystack),
            ("Create Account & DVA", self.create_customer_and_dva),
            ("Store in Database", self.store_in_supabase),
            ("Test Balance", self.test_balance),
        ]
        
        passed = 0
        for step_name, step_func in steps:
            try:
                if asyncio.iscoroutinefunction(step_func):
                    result = await step_func()
                else:
                    result = step_func()
                
                if result:
                    passed += 1
                else:
                    print(f"\n❌ Failed at: {step_name}")
                    break
            except Exception as e:
                print(f"\n💥 Exception in {step_name}: {e}")
                break
        
        # Always cleanup
        self.cleanup()
        
        # Results
        print("\n" + "=" * 50)
        print("🏁 TEST RESULTS")
        print("=" * 50)
        print(f"Passed: {passed}/{len(steps)} steps")
        
        if passed == len(steps):
            print("🎉 SUCCESS! Account creation works perfectly!")
            print("\n📋 ACCOUNT DETAILS:")
            print(f"   Customer Code: {self.test_user.get('paystack_customer_code')}")
            print(f"   Account Number: {self.test_user.get('paystack_account_number')}")
            print(f"   Bank: {self.test_user.get('paystack_bank_name')}")
            print(f"   Database ID: {self.test_user.get('user_id')}")
            print("\n✅ Your Paystack integration is working!")
        else:
            print("❌ Some tests failed. Check the errors above.")
        
        return passed == len(steps)

async def main():
    tester = SimpleAccountCreationTest()
    return await tester.run_test()

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)
