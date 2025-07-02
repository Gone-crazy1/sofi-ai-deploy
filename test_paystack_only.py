#!/usr/bin/env python3
"""
PAYSTACK ACCOUNT CREATION TEST - FOCUSED
=======================================
This test verifies just the Paystack integration:
✅ Environment variables
✅ Paystack API connection  
✅ Customer creation
✅ Virtual account creation

Schema application is shown as a manual step.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from paystack.paystack_service import PaystackService
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

class PaystackOnlyTest:
    def __init__(self):
        self.paystack_secret = os.getenv('PAYSTACK_SECRET_KEY')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.test_user = {
            'email': f'paystack_test_{timestamp}@sofi.ai',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+2348123456789'
        }
        
        print("🧪 Paystack Account Creation Test (API Only)")
        print(f"📧 Test Email: {self.test_user['email']}")
        
    def check_environment(self):
        print("\n1️⃣ Environment Check...")
        if not self.paystack_secret:
            print("❌ PAYSTACK_SECRET_KEY not found")
            return False
        print(f"✅ PAYSTACK_SECRET_KEY: {self.paystack_secret[:8]}...")
        return True
    
    def test_paystack_connection(self):
        print("\n2️⃣ Paystack Connection...")
        try:
            self.paystack = PaystackService()
            banks = self.paystack.get_supported_banks()
            if banks and banks.get('success'):
                print("✅ Paystack API connected successfully")
                return True
            else:
                print(f"❌ Paystack connection failed: {banks}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_account_creation(self):
        print("\n3️⃣ Account Creation...")
        try:
            result = self.paystack.create_user_account(self.test_user)
            
            if result and result.get('success'):
                data = result.get('data', {})
                print("✅ Paystack account creation successful!")
                print(f"   Status: {result.get('message', 'Created')}")
                
                # Show what data was returned
                interesting_fields = ['customer_code', 'account_number', 'bank_name', 'account_name']
                for field in interesting_fields:
                    if field in data:
                        print(f"   {field.title()}: {data[field]}")
                    else:
                        print(f"   {field.title()}: Pending (will be provided via webhook)")
                
                self.account_data = data
                return True
            else:
                print(f"❌ Account creation failed: {result}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def run_test(self):
        print("=" * 55)
        print("🧪 PAYSTACK INTEGRATION TEST")
        print("=" * 55)
        
        steps = [
            ("Environment Check", self.check_environment),
            ("Paystack Connection", self.test_paystack_connection),
            ("Account Creation", self.test_account_creation),
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
        
        print("\n" + "=" * 55)
        print("🏁 TEST RESULTS")
        print("=" * 55)
        print(f"Passed: {passed}/{len(steps)} steps")
        
        if passed == len(steps):
            print("🎉 SUCCESS! Paystack integration is working!")
            print("\n📋 WHAT HAPPENED:")
            print("✅ Paystack API connection established")
            print("✅ Customer account creation request sent")
            print("✅ Virtual account assignment initiated")
            print("\n⏳ NEXT STEPS:")
            print("1. Apply the ultra_safe_schema.sql to your Supabase database:")
            print("   - Go to Supabase Dashboard > SQL Editor")
            print("   - Copy and paste the contents of ultra_safe_schema.sql")
            print("   - Click RUN to execute")
            print("\n2. Set up webhook endpoint:")
            print("   - Configure Paystack webhook URL in your dashboard")
            print("   - Point to: https://yourdomain.com/paystack-webhook")
            print("\n3. Test end-to-end flow:")
            print("   - Create user account")
            print("   - Receive webhook notifications")
            print("   - Update user balance")
            print("\n✅ Your Paystack integration core is ready!")
        else:
            print("❌ Some tests failed. Check the errors above.")
        
        return passed == len(steps)

async def main():
    tester = PaystackOnlyTest()
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
