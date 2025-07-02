#!/usr/bin/env python3
"""
COMPLETE TRANSFER WITH OTP
==========================
Complete the pending transfer using OTP: 392451
Transfer Code: TRF_6wjgfrmwnwp70cir
Reference: fd54l9s5bdrv7w0wjt7v
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

def complete_otp_transfer():
    print("🔐 COMPLETING TRANSFER WITH OTP")
    print("=" * 40)
    print("📋 Transfer Details:")
    print("   Transfer Code: TRF_6wjgfrmwnwp70cir")
    print("   Reference: fd54l9s5bdrv7w0wjt7v")
    print("   Amount: ₦100.00")
    print("   Recipient: MELLA EZINNE ILIEMENE")
    print("   OTP Code: 392451")
    print("=" * 40)
    
    try:
        # Initialize Paystack Transfer API
        transfer_api = PaystackTransferAPI()
        
        # Complete the transfer with OTP
        transfer_code = "TRF_6wjgfrmwnwp70cir"
        otp_code = "392451"
        
        print("\n🚀 Submitting OTP to complete transfer...")
        
        # Check if the complete_otp_transfer method exists
        if hasattr(transfer_api, 'complete_otp_transfer'):
            result = transfer_api.complete_otp_transfer(transfer_code, otp_code)
        else:
            # If method doesn't exist, call the finalize transfer endpoint directly
            result = finalize_transfer_direct(transfer_api, transfer_code, otp_code)
        
        print(f"\n📋 Completion Result:")
        print(f"Response: {result}")
        
        if result.get("success"):
            data = result.get("data", {})
            print("\n🎉 TRANSFER COMPLETED SUCCESSFULLY!")
            print(f"💰 Amount: ₦100.00 sent to MELLA EZINNE ILIEMENE")
            print(f"📋 Reference: {data.get('reference', 'fd54l9s5bdrv7w0wjt7v')}")
            print(f"📊 Final Status: {data.get('status', 'completed')}")
            print(f"🆔 Transfer ID: {data.get('id', '842428836')}")
            print(f"💸 The money has been successfully transferred!")
            
            return True
        else:
            print(f"\n❌ TRANSFER COMPLETION FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print("Possible reasons:")
            print("- OTP might be incorrect or expired")
            print("- Transfer might have timed out")
            print("- Please try again or check Paystack dashboard")
            return False
            
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        return False

def finalize_transfer_direct(transfer_api, transfer_code, otp):
    """Direct API call to finalize transfer if method doesn't exist"""
    try:
        import requests
        
        url = f"{transfer_api.base_url}/transfer/finalize_transfer"
        
        payload = {
            "transfer_code": transfer_code,
            "otp": otp
        }
        
        response = requests.post(url, json=payload, headers=transfer_api.headers)
        result = response.json()
        
        if response.status_code == 200 and result.get("status"):
            return {
                "success": True,
                "data": result.get("data", {})
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Failed to complete transfer")
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("🔐 FINALIZING REAL MONEY TRANSFER")
    print("Using OTP: 392451")
    print("This will complete the ₦100 transfer to MELLA EZINNE ILIEMENE\n")
    
    success = complete_otp_transfer()
    
    if success:
        print("\n✅ REAL MONEY TRANSFER COMPLETED!")
        print("💰 ₦100 has been successfully sent!")
        print("🎉 Your Paystack integration is fully operational!")
    else:
        print("\n❌ Transfer completion failed.")
        print("💡 Try completing it manually in your Paystack dashboard")
