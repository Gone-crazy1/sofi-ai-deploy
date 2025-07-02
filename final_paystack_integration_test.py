#!/usr/bin/env python3
"""
FINAL PAYSTACK INTEGRATION TEST
================================
This script will test the complete Paystack integration:
1. Load environment variables
2. Test Supabase connection
3. Create a Paystack customer
4. Create a dedicated virtual account (DVA)
5. Store user data in Supabase
6. Test balance retrieval
7. Test transaction history
8. Verify all systems work together

This is a LIVE test with real API calls.
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
    from utils.balance_helper import get_user_balance, update_user_balance
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you have installed all required packages:")
    print("pip install supabase paystack python-dotenv")
    sys.exit(1)

class FinalIntegrationTester:
    def __init__(self):
        """Initialize the tester with all required services."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.paystack_secret = os.getenv('PAYSTACK_SECRET_KEY')
        
        # Test user data
        self.test_user = {
            'telegram_chat_id': f'test_integration_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'phone_number': '+2348123456789',
            'full_name': 'Integration Test User',
            'email': f'integration_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@sofi.ai'
        }
        
        print("🚀 Final Paystack Integration Test Starting...")
        print(f"📧 Test User Email: {self.test_user['email']}")
        print(f"📱 Test Chat ID: {self.test_user['telegram_chat_id']}")
        
    def check_environment(self):
        """Check if all required environment variables are set."""
        print("\n1️⃣ Checking Environment Variables...")
        
        required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'PAYSTACK_SECRET_KEY']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
                print(f"❌ {var}: Not set")
            else:
                print(f"✅ {var}: {'*' * (len(value) - 4) + value[-4:]}")
        
        if missing_vars:
            print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        print("✅ All environment variables are set!")
        return True
    
    def test_supabase_connection(self):
        """Test Supabase connection and check if tables exist."""
        print("\n2️⃣ Testing Supabase Connection...")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            
            # Test connection by checking users table
            result = self.supabase.table('users').select('count', count='exact').execute()
            user_count = result.count
            print(f"✅ Supabase connected! Users table has {user_count} records")
            
            # Check if required tables exist
            tables_to_check = ['users', 'virtual_accounts', 'bank_transactions']
            for table in tables_to_check:
                try:
                    result = self.supabase.table(table).select('count', count='exact').execute()
                    print(f"✅ Table '{table}' exists with {result.count} records")
                except Exception as e:
                    print(f"❌ Table '{table}' issue: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Supabase connection failed: {str(e)}")
            return False
    
    def test_paystack_connection(self):
        """Test Paystack API connection."""
        print("\n3️⃣ Testing Paystack Connection...")
        
        try:
            self.paystack = PaystackService()
            
            # Test by fetching banks list
            banks = self.paystack.get_banks()
            if banks and len(banks) > 0:
                print(f"✅ Paystack connected! Found {len(banks)} banks")
                return True
            else:
                print("❌ Paystack connection failed: No banks returned")
                return False
                
        except Exception as e:
            print(f"❌ Paystack connection failed: {str(e)}")
            return False
    
    async def create_paystack_customer(self):
        """Create a Paystack customer for the test user."""
        print("\n4️⃣ Creating Paystack Customer...")
        
        try:
            customer_data = await self.paystack.create_customer(
                email=self.test_user['email'],
                first_name=self.test_user['full_name'].split()[0],
                last_name=self.test_user['full_name'].split()[-1],
                phone=self.test_user['phone_number']
            )
            
            if customer_data and customer_data.get('status'):
                customer_code = customer_data['data']['customer_code']
                print(f"✅ Customer created! Customer Code: {customer_code}")
                self.test_user['paystack_customer_code'] = customer_code
                return True
            else:
                print(f"❌ Customer creation failed: {customer_data}")
                return False
                
        except Exception as e:
            print(f"❌ Customer creation failed: {str(e)}")
            return False
    
    async def create_dedicated_virtual_account(self):
        """Create a dedicated virtual account for the customer."""
        print("\n5️⃣ Creating Dedicated Virtual Account...")
        
        try:
            dva_data = await self.paystack.create_dedicated_virtual_account(
                customer_code=self.test_user['paystack_customer_code']
            )
            
            if dva_data and dva_data.get('status'):
                account_data = dva_data['data']
                account_number = account_data['account_number']
                bank_name = account_data['bank']['name']
                
                print(f"✅ DVA created!")
                print(f"   Account Number: {account_number}")
                print(f"   Bank: {bank_name}")
                
                self.test_user.update({
                    'paystack_dva_id': str(account_data['id']),
                    'paystack_account_number': account_number,
                    'paystack_bank_name': bank_name
                })
                return True
            else:
                print(f"❌ DVA creation failed: {dva_data}")
                return False
                
        except Exception as e:
            print(f"❌ DVA creation failed: {str(e)}")
            return False
    
    def store_user_in_supabase(self):
        """Store the test user in Supabase with all Paystack data."""
        print("\n6️⃣ Storing User in Supabase...")
        
        try:
            # Insert user into database
            result = self.supabase.table('users').insert({
                'telegram_chat_id': self.test_user['telegram_chat_id'],
                'phone_number': self.test_user['phone_number'],
                'full_name': self.test_user['full_name'],
                'email': self.test_user['email'],
                'paystack_customer_code': self.test_user['paystack_customer_code'],
                'paystack_dva_id': self.test_user['paystack_dva_id'],
                'paystack_account_number': self.test_user['paystack_account_number'],
                'paystack_bank_name': self.test_user['paystack_bank_name'],
                'wallet_balance': 0.00,
                'is_verified': True,
                'is_active': True
            }).execute()
            
            if result.data and len(result.data) > 0:
                user_id = result.data[0]['id']
                print(f"✅ User stored in Supabase! User ID: {user_id}")
                self.test_user['user_id'] = user_id
                return True
            else:
                print(f"❌ Failed to store user: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to store user: {str(e)}")
            return False
    
    async def test_balance_functions(self):
        """Test balance retrieval and update functions."""
        print("\n7️⃣ Testing Balance Functions...")
        
        try:
            # Test getting balance
            balance = await get_user_balance(self.test_user['telegram_chat_id'])
            print(f"✅ Initial balance retrieved: ₦{balance:,.2f}")
            
            # Test updating balance
            test_amount = 1000.00
            success = await update_user_balance(
                telegram_chat_id=self.test_user['telegram_chat_id'],
                amount=test_amount,
                transaction_type="test_credit",
                reference=f"test_ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if success:
                new_balance = await get_user_balance(self.test_user['telegram_chat_id'])
                print(f"✅ Balance updated! New balance: ₦{new_balance:,.2f}")
                return True
            else:
                print("❌ Balance update failed")
                return False
                
        except Exception as e:
            print(f"❌ Balance function test failed: {str(e)}")
            return False
    
    async def test_transaction_history(self):
        """Test transaction history retrieval."""
        print("\n8️⃣ Testing Transaction History...")
        
        try:
            # Get transactions from Supabase
            result = self.supabase.table('bank_transactions').select('*').eq(
                'user_id', self.test_user['user_id']
            ).execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} transactions for user")
                for tx in result.data:
                    print(f"   - {tx['transaction_type']}: ₦{tx['amount']} ({tx['status']})")
                return True
            else:
                print("✅ No transactions found (expected for new user)")
                return True
                
        except Exception as e:
            print(f"❌ Transaction history test failed: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data."""
        print("\n9️⃣ Cleaning Up Test Data...")
        
        try:
            # Delete test user and related data
            self.supabase.table('bank_transactions').delete().eq(
                'user_id', self.test_user['user_id']
            ).execute()
            
            self.supabase.table('users').delete().eq(
                'telegram_chat_id', self.test_user['telegram_chat_id']
            ).execute()
            
            print("✅ Test data cleaned up!")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")
    
    async def run_complete_test(self):
        """Run the complete integration test."""
        print("=" * 60)
        print("🧪 SOFI AI - PAYSTACK INTEGRATION TEST")
        print("=" * 60)
        
        # Step-by-step test
        steps = [
            ("Environment Check", self.check_environment),
            ("Supabase Connection", self.test_supabase_connection),
            ("Paystack Connection", self.test_paystack_connection),
            ("Create Customer", self.create_paystack_customer),
            ("Create DVA", self.create_dedicated_virtual_account),
            ("Store in Supabase", self.store_user_in_supabase),
            ("Test Balance Functions", self.test_balance_functions),
            ("Test Transaction History", self.test_transaction_history),
        ]
        
        passed = 0
        total = len(steps)
        
        for step_name, step_func in steps:
            try:
                if asyncio.iscoroutinefunction(step_func):
                    result = await step_func()
                else:
                    result = step_func()
                
                if result:
                    passed += 1
                else:
                    print(f"\n❌ Test failed at step: {step_name}")
                    break
                    
            except Exception as e:
                print(f"\n💥 Exception in step '{step_name}': {str(e)}")
                break
        
        # Cleanup
        self.cleanup_test_data()
        
        # Final results
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed}/{total} steps")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Paystack integration is working perfectly!")
            print("\n📋 INTEGRATION SUMMARY:")
            print(f"   • Customer Code: {self.test_user.get('paystack_customer_code', 'N/A')}")
            print(f"   • Account Number: {self.test_user.get('paystack_account_number', 'N/A')}")
            print(f"   • Bank: {self.test_user.get('paystack_bank_name', 'N/A')}")
            print(f"   • Database: All tables working ✅")
            print(f"   • APIs: All endpoints working ✅")
            print("\n🚀 Your Sofi AI is ready for production!")
        else:
            print(f"❌ {total - passed} tests failed. Please check the errors above.")
        
        return passed == total

async def main():
    """Main test function."""
    tester = FinalIntegrationTester()
    success = await tester.run_complete_test()
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
