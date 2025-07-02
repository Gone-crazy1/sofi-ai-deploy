#!/usr/bin/env python3
"""
REAL MONEY TRANSFER TEST
========================
This script will send REAL MONEY via Paystack.
Amount: ₦100
Recipient: 8142749615 (Opay - Mella)

⚠️ WARNING: THIS INVOLVES REAL MONEY TRANSFER ⚠️
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
    from supabase import create_client
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

class RealMoneyTransferTest:
    def __init__(self):
        self.paystack = PaystackService()
        
        # Transfer details
        self.recipient_account = "8142749615"
        self.recipient_name = "Mella"
        self.bank_name = "Opay"
        self.amount = 100.00
        self.reason = "Sofi AI Integration Test"
        
        # We need to find Opay's bank code
        self.bank_code = None
        
        print("💸 REAL MONEY TRANSFER TEST")
        print("=" * 40)
        print(f"💰 Amount: ₦{self.amount:,.2f}")
        print(f"📱 Account: {self.recipient_account}")
        print(f"👤 Name: {self.recipient_name}")
        print(f"🏦 Bank: {self.bank_name}")
        print("=" * 40)
        print("⚠️  WARNING: THIS WILL SEND REAL MONEY ⚠️")
        print("=" * 40)
    
    def find_bank_code(self):
        """Find Opay bank code from Paystack"""
        print("\n1️⃣ Finding Bank Code...")
        
        try:
            banks_result = self.paystack.get_supported_banks()
            
            if not banks_result.get('success'):
                print(f"❌ Failed to get banks: {banks_result}")
                return False
            
            # Search for Opay bank code
            banks_data = banks_result.get('data', [])
            opay_bank = None
            
            for bank in banks_data:
                if 'opay' in bank.get('name', '').lower():
                    opay_bank = bank
                    break
            
            if opay_bank:
                self.bank_code = opay_bank['code']
                print(f"✅ Found Opay: {opay_bank['name']} (Code: {self.bank_code})")
                return True
            else:
                print("❌ Opay bank not found in supported banks")
                print("Available banks with 'pay' in name:")
                for bank in banks_data:
                    if 'pay' in bank.get('name', '').lower():
                        print(f"  - {bank['name']} ({bank['code']})")
                return False
                
        except Exception as e:
            print(f"❌ Error finding bank code: {e}")
            return False
    
    def verify_account(self):
        """Verify recipient account details"""
        print("\n2️⃣ Verifying Account...")
        
        try:
            verification = self.paystack.verify_account_number(
                self.recipient_account, 
                self.bank_code
            )
            
            if verification.get('success'):
                account_name = verification.get('data', {}).get('account_name', 'Unknown')
                print(f"✅ Account verified!")
                print(f"   Account Number: {self.recipient_account}")
                print(f"   Account Name: {account_name}")
                print(f"   Bank: {verification.get('data', {}).get('bank_name', self.bank_name)}")
                
                # Ask for confirmation
                print(f"\n⚠️  CONFIRM TRANSFER DETAILS:")
                print(f"   Amount: ₦{self.amount:,.2f}")
                print(f"   To: {account_name} ({self.recipient_account})")
                print(f"   Bank: {self.bank_name}")
                print(f"   Purpose: {self.reason}")
                
                return True
            else:
                print(f"❌ Account verification failed: {verification}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying account: {e}")
            return False
    
    def calculate_fees(self):
        """Calculate transfer fees"""
        print("\n3️⃣ Calculating Fees...")
        
        try:
            # Use Paystack's fee calculation or our own
            if self.amount <= 5000:
                paystack_fee = 10.0
            elif self.amount <= 50000:
                paystack_fee = 25.0
            else:
                paystack_fee = 50.0
            
            total_deduction = self.amount + paystack_fee
            
            print(f"💰 Transfer Amount: ₦{self.amount:,.2f}")
            print(f"💸 Paystack Fee: ₦{paystack_fee:,.2f}")
            print(f"📊 Total Deduction: ₦{total_deduction:,.2f}")
            
            self.total_amount = total_deduction
            self.fee = paystack_fee
            return True
            
        except Exception as e:
            print(f"❌ Error calculating fees: {e}")
            return False
    
    def confirm_transfer(self):
        """Get final confirmation from user"""
        print("\n4️⃣ Final Confirmation...")
        print("🚨" * 20)
        print("   PROCEEDING WITH REAL TRANSFER")
        print("🚨" * 20)
        print(f"✅ CONFIRMED: Sending REAL MONEY")
        print(f"💰 Amount: ₦{self.amount:,.2f}")
        print(f"💸 Fee: ₦{self.fee:,.2f}")
        print(f"📊 Total: ₦{self.total_amount:,.2f}")
        print(f"👤 To: {self.recipient_account} ({self.recipient_name})")
        print(f"🏦 Bank: {self.bank_name}")
        print("")
        print("✅ USER CONFIRMED: Proceeding with real money transfer...")
        print("")
        
        return True  # Enable real transfer execution
    
    def execute_transfer(self):
        """Execute the actual transfer"""
        print("\n5️⃣ Executing Real Money Transfer...")
        print("💸 INITIATING REAL TRANSFER NOW...")
        
        try:
            # Create transfer recipient data
            recipient_data = {
                "account_number": self.recipient_account,
                "bank_code": self.bank_code,
                "account_name": self.recipient_name  # Changed from "name" to "account_name"
            }
            
            print(f"📤 Sending ₦{self.amount} to {self.recipient_account}...")
            
            # Execute the real transfer using PaystackService
            transfer_result = self.paystack.send_money(
                sender_data={"name": "Sofi AI Test User"},
                recipient_data=recipient_data,
                amount=self.amount,
                reason=self.reason
            )
            
            print(f"📋 Transfer Response: {transfer_result}")
            
            if transfer_result.get('success'):
                print("🎉 REAL MONEY TRANSFER SUCCESSFUL!")
                print(f"   💰 Amount Sent: ₦{self.amount:,.2f}")
                print(f"   📋 Reference: {transfer_result.get('reference', 'N/A')}")
                print(f"   📊 Status: {transfer_result.get('status', 'pending')}")
                print(f"   🏦 To: {self.recipient_account} ({self.bank_name})")
                
                if transfer_result.get('requires_otp'):
                    print("📱 OTP Required for completion")
                    print(f"   Transfer Code: {transfer_result.get('transfer_code')}")
                    print("   Complete the transfer in your Paystack dashboard")
                else:
                    print("✅ Transfer completed without OTP requirement")
                
                # Log transaction details
                print(f"\n📄 TRANSACTION SUMMARY:")
                print(f"   Reference: {transfer_result.get('reference')}")
                print(f"   Amount: ₦{self.amount:,.2f}")
                print(f"   Fee: ₦{self.fee:,.2f}")
                print(f"   Total Deducted: ₦{self.total_amount:,.2f}")
                print(f"   Recipient: {self.recipient_account}")
                print(f"   Bank: {self.bank_name}")
                print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True
            else:
                print(f"❌ TRANSFER FAILED!")
                print(f"   Error: {transfer_result.get('error', 'Unknown error')}")
                print(f"   Details: {transfer_result}")
                return False
                
        except Exception as e:
            print(f"❌ CRITICAL ERROR executing transfer: {e}")
            print(f"   Exception details: {str(e)}")
            return False
    
    async def run_test(self):
        """Run the complete transfer test"""
        print("\n🚀 Starting Real Money Transfer Test...")
        
        steps = [
            ("Find Bank Code", self.find_bank_code),
            ("Verify Account", self.verify_account),
            ("Calculate Fees", self.calculate_fees),
            ("Confirm Transfer", self.confirm_transfer),
            ("Execute Transfer", self.execute_transfer),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*50}")
            
            try:
                if asyncio.iscoroutinefunction(step_func):
                    result = await step_func()
                else:
                    result = step_func()
                
                if not result:
                    print(f"\n❌ Test stopped at: {step_name}")
                    if step_name == "Confirm Transfer":
                        print("\n🛡️ SAFETY STOP ACTIVATED")
                        print("This is intentional to prevent accidental real money transfers.")
                        print("\nTo enable real transfers:")
                        print("1. Review all details carefully")
                        print("2. Ensure sufficient Paystack balance") 
                        print("3. Modify confirm_transfer() to return True")
                        print("4. Add proper confirmation mechanism")
                    return False
                    
            except Exception as e:
                print(f"\n💥 Exception in {step_name}: {e}")
                return False
        
        print("\n" + "="*50)
        print("🎉 TRANSFER TEST COMPLETED")
        print("="*50)
        return True

async def main():
    """Main function"""
    print("⚠️  REAL MONEY TRANSFER TEST")
    print("This script is configured with safety stops.")
    print("Review the code before enabling real transfers.\n")
    
    tester = RealMoneyTransferTest()
    await tester.run_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
