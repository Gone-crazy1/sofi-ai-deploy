#!/usr/bin/env python3
"""
DIRECT TRANSFER TEST USING EXISTING RECIPIENT
=============================================
We already have a recipient code: RCP_f7je3wpz63589qb
Account: 8142749615 (MELLA EZINNE ILIEMENE)
Let's use this to complete the transfer directly.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from paystack.paystack_transfer_api import PaystackTransferAPI
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def test_direct_transfer():
    print("💸 DIRECT TRANSFER TEST")
    print("=" * 40)
    print("Using existing recipient:")
    print("👤 Name: MELLA EZINNE ILIEMENE")
    print("📱 Account: 8142749615")
    print("🏦 Bank: OPay")
    print("🔑 Recipient Code: RCP_f7je3wpz63589qb")
    print("💰 Amount: ₦100.00")
    print("=" * 40)
    
    try:
        # Initialize Paystack Transfer API
        transfer_api = PaystackTransferAPI()
        
        # Use the existing recipient code to initiate transfer
        recipient_code = "RCP_f7je3wpz63589qb"
        amount_kobo = 100 * 100  # ₦100 in kobo
        reason = "Sofi AI Integration Test - Direct Transfer"
        
        print("\n🚀 Initiating transfer with existing recipient...")
        
        result = transfer_api.initiate_transfer(
            recipient_code=recipient_code,
            amount=amount_kobo,
            reason=reason
        )
        
        print(f"\n📋 Transfer Result:")
        print(f"Response: {result}")
        
        if result.get("success"):
            data = result.get("data", {})
            print("\n🎉 TRANSFER INITIATED SUCCESSFULLY!")
            print(f"💰 Amount: ₦100.00")
            print(f"📋 Reference: {data.get('reference', 'N/A')}")
            print(f"📊 Status: {data.get('status', 'N/A')}")
            print(f"🆔 Transfer ID: {data.get('id', 'N/A')}")
            
            if data.get("status") == "otp":
                print("\n📱 OTP REQUIRED:")
                print(f"Transfer Code: {data.get('transfer_code', 'N/A')}")
                print("Complete the transfer by:")
                print("1. Check your SMS for OTP")
                print("2. Use Paystack dashboard to complete")
                print("3. Or use the transfer code to finalize")
            elif data.get("status") == "success":
                print("\n✅ TRANSFER COMPLETED IMMEDIATELY!")
            else:
                print(f"\n⏳ Transfer Status: {data.get('status')}")
                print("Check your Paystack dashboard for updates")
            
            return True
        else:
            print(f"\n❌ TRANSFER FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        return False

if __name__ == "__main__":
    print("⚠️  REAL MONEY TRANSFER - USING EXISTING RECIPIENT")
    print("This will attempt to send ₦100 to MELLA EZINNE ILIEMENE")
    print("Account: 8142749615 (OPay)\n")
    
    success = test_direct_transfer()
    
    if success:
        print("\n✅ Transfer test completed successfully!")
    else:
        print("\n❌ Transfer test failed.")
