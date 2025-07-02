#!/usr/bin/env python3
"""
CHECK TRANSFER STATUS
====================
Check the status of the transfer we just initiated
Transfer ID: 842431389
Reference: xqgfpncnhlax5jy01ey5
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from paystack.paystack_transfer_api import PaystackTransferAPI
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def check_transfer_status():
    print("🔍 CHECKING TRANSFER STATUS")
    print("=" * 40)
    print("Transfer Details:")
    print("💰 Amount: ₦100.00")
    print("👤 To: MELLA EZINNE ILIEMENE")
    print("📱 Account: 8142749615 (OPay)")
    print("📋 Reference: xqgfpncnhlax5jy01ey5")
    print("🆔 Transfer ID: 842431389")
    print("=" * 40)
    
    try:
        transfer_api = PaystackTransferAPI()
        transfer_id = "842431389"
        
        print(f"\n🔍 Checking status of transfer {transfer_id}...")
        
        # Check transfer status
        result = transfer_api.fetch_transfer(transfer_id)
        
        if result.get("success"):
            data = result.get("data", {})
            status = data.get("status", "unknown")
            amount = data.get("amount", 0) / 100  # Convert from kobo
            reference = data.get("reference", "N/A")
            transferred_at = data.get("transferred_at")
            
            print(f"\n📊 TRANSFER STATUS: {status.upper()}")
            print(f"💰 Amount: ₦{amount:,.2f}")
            print(f"📋 Reference: {reference}")
            print(f"🕐 Created: {data.get('createdAt', 'N/A')}")
            print(f"📅 Transferred: {transferred_at or 'Not yet'}")
            
            if status == "success":
                print("\n🎉 TRANSFER COMPLETED SUCCESSFULLY!")
                print("✅ Money has been sent to MELLA EZINNE ILIEMENE")
                print("✅ Sofi AI Paystack integration is fully operational!")
                return True
            elif status == "pending":
                print("\n⏳ Transfer is still pending...")
                print("💡 This is normal for bank transfers")
                print("💡 It may take a few minutes to complete")
                return True
            elif status == "failed":
                print("\n❌ Transfer failed!")
                print(f"Reason: {data.get('reason', 'Unknown')}")
                return False
            else:
                print(f"\n🔄 Transfer status: {status}")
                return True
        else:
            print(f"\n❌ Failed to get transfer status: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n💥 Error checking status: {e}")
        return False

def monitor_transfer():
    print("👀 MONITORING TRANSFER COMPLETION")
    print("Checking every 10 seconds for 2 minutes...")
    
    for i in range(12):  # 12 checks over 2 minutes
        print(f"\n--- Check {i+1}/12 ---")
        
        success = check_transfer_status()
        if not success:
            break
            
        # Check if we should continue monitoring
        if i < 11:
            print("\n⏰ Waiting 10 seconds before next check...")
            time.sleep(10)
        else:
            print("\n⏰ Monitoring complete")

if __name__ == "__main__":
    print("🔍 TRANSFER STATUS CHECKER")
    print("This will check the status of your ₦100 transfer to Mella\n")
    
    # First check
    print("1️⃣ INITIAL STATUS CHECK")
    check_transfer_status()
    
    # Ask if user wants to monitor
    print("\n" + "="*50)
    print("Would you like to monitor until completion? (y/n)")
    
    # For automation, let's just do a few quick checks
    print("🔄 Doing automated monitoring...")
    monitor_transfer()
