#!/usr/bin/env python3
"""
PAYSTACK MONEY TRANSFER TEST
===========================
Test sending ₦100 to Opay account: 8142749615 (Mella)
This will test the complete transfer flow:
1. Verify recipient account
2. Create transfer recipient 
3. Initiate transfer
4. Handle response
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
    from functions.transfer_functions import send_money, calculate_transfer_fee
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

class MoneyTransferTest:
    def __init__(self):
        """Initialize transfer test"""
        self.paystack_secret = os.getenv('PAYSTACK_SECRET_KEY')
        
        # Transfer details
        self.transfer_details = {
            'account_number': '8142749615',
            'bank_name': 'Opay',
            'bank_code': '999992',  # Opay bank code
            'recipient_name': 'Mella',
            'amount': 100.00,
            'narration': 'Test transfer from Sofi AI',
            'sender_chat_id': 'test_sender_123'
        }
        
        print("💸 Paystack Money Transfer Test")
        print(f"💰 Amount: ₦{self.transfer_details['amount']:,.2f}")
        print(f"🏦 Recipient: {self.transfer_details['account_number']} ({self.transfer_details['recipient_name']})")
        print(f"🏛️ Bank: {self.transfer_details['bank_name']}")
        
    def check_environment(self):
        """Check environment setup"""
        print("\n1️⃣ Environment Check...")
        if not self.paystack_secret:
            print("❌ PAYSTACK_SECRET_KEY not found")
            return False
        print(f"✅ PAYSTACK_SECRET_KEY: {self.paystack_secret[:8]}...")
        return True
    
    def test_paystack_connection(self):
        """Test Paystack connection"""
        print("\n2️⃣ Paystack Connection...")
        try:
            self.paystack = PaystackService()
            banks = self.paystack.get_supported_banks()
            if banks and banks.get('success'):
                print("✅ Paystack API connected")
                return True
            else:
                print(f"❌ Connection failed: {banks}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def verify_recipient_account(self):
        """Verify the recipient account details"""
        print("\n3️⃣ Verifying Recipient Account...")
        try:
            result = self.paystack.verify_account_number(
                account_number=self.transfer_details['account_number'],
                bank_code=self.transfer_details['bank_code']
            )
            
            if result.get('success'):
                account_name = result.get('account_name', 'Unknown')
                print(f"✅ Account verified!")
                print(f"   Account Number: {self.transfer_details['account_number']}")
                print(f"   Account Name: {account_name}")
                print(f"   Bank: {self.transfer_details['bank_name']}")
                
                # Update with verified name
                self.transfer_details['verified_name'] = account_name
                return True
            else:
                print(f"❌ Account verification failed: {result}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def calculate_fees(self):
        """Calculate transfer fees"""
        print("\n4️⃣ Calculating Transfer Fees...")
        try:
            fee_result = await calculate_transfer_fee(self.transfer_details['amount'])
            
            if fee_result:
                amount = fee_result['amount']
                fee = fee_result['fee']
                total = fee_result['total']
                
                print(f"✅ Fee calculation:")
                print(f"   Transfer Amount: ₦{amount:,.2f}")
                print(f"   Service Fee: ₦{fee:,.2f}")
                print(f"   Total Deduction: ₦{total:,.2f}")
                
                self.transfer_details['fee'] = fee
                self.transfer_details['total_amount'] = total
                return True
            else:
                print("❌ Fee calculation failed")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def initiate_transfer(self):
        """Initiate the money transfer"""
        print("\n5️⃣ Initiating Transfer...")
        try:
            # Prepare transfer data
            transfer_data = {
                'recipient_account': self.transfer_details['account_number'],
                'recipient_bank': self.transfer_details['bank_name'],
                'recipient_name': self.transfer_details.get('verified_name', self.transfer_details['recipient_name']),
                'amount': self.transfer_details['amount'],
                'narration': self.transfer_details['narration'],
                'bank_code': self.transfer_details['bank_code']
            }
            
            print(f"💸 Sending ₦{self.transfer_details['amount']:,.2f}...")
            print(f"📝 Narration: {transfer_data['narration']}")
            
            # Call the send_money function
            result = await send_money(
                chat_id=self.transfer_details['sender_chat_id'],
                **transfer_data
            )
            
            if result.get('success'):
                print("✅ Transfer initiated successfully!")
                
                # Show transfer details
                if result.get('requires_otp'):
                    print("🔐 Transfer requires OTP verification")
                    print(f"📱 Transfer Code: {result.get('transfer_code')}")
                    print("📧 Check your email/SMS for OTP")
                else:
                    print("✨ Transfer completed immediately!")
                
                print(f"🆔 Transaction ID: {result.get('transaction_id')}")
                print(f"📄 Reference: {result.get('reference', 'N/A')}")
                
                return True
            else:
                print(f"❌ Transfer failed: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def run_test(self):
        """Run the complete transfer test"""
        print("=" * 60)
        print("💸 SOFI AI - MONEY TRANSFER TEST")
        print("=" * 60)
        
        steps = [
            ("Environment Check", self.check_environment),
            ("Paystack Connection", self.test_paystack_connection),
            ("Verify Recipient", self.verify_recipient_account),
            ("Calculate Fees", self.calculate_fees),
            ("Initiate Transfer", self.initiate_transfer),
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
        
        print("\n" + "=" * 60)
        print("🏁 TRANSFER TEST RESULTS")
        print("=" * 60)
        print(f"Passed: {passed}/{len(steps)} steps")
        
        if passed == len(steps):
            print("🎉 SUCCESS! Money transfer test completed!")
            print("\n📋 TRANSFER SUMMARY:")
            print(f"   💰 Amount: ₦{self.transfer_details['amount']:,.2f}")
            print(f"   🏦 To: {self.transfer_details['account_number']} ({self.transfer_details.get('verified_name', self.transfer_details['recipient_name'])})")
            print(f"   🏛️ Bank: {self.transfer_details['bank_name']}")
            print(f"   💸 Fee: ₦{self.transfer_details.get('fee', 0):,.2f}")
            print(f"   💳 Total: ₦{self.transfer_details.get('total_amount', 0):,.2f}")
            print("\n✅ Your money transfer system is working!")
        else:
            print("❌ Transfer test failed. Check the errors above.")
            
        return passed == len(steps)

async def main():
    tester = MoneyTransferTest()
    return await tester.run_test()

if __name__ == "__main__":
    try:
        print("⚠️  WARNING: This will attempt a REAL money transfer!")
        print("💰 Amount: ₦100.00 to Opay account 8142749615")
        
        # Uncomment the next line to proceed with real transfer
        # result = asyncio.run(main())
        
        print("\n🛡️  SAFETY NOTICE:")
        print("This test is configured but commented out for safety.")
        print("To run the actual transfer:")
        print("1. Ensure you have sufficient balance")
        print("2. Verify the recipient details are correct")
        print("3. Uncomment the line: result = asyncio.run(main())")
        print("4. Run the script again")
        
        print(f"\n📋 TRANSFER DETAILS:")
        print(f"   💰 Amount: ₦100.00")
        print(f"   🏦 Account: 8142749615")
        print(f"   👤 Name: Mella")
        print(f"   🏛️ Bank: Opay")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n💥 Error: {e}")
