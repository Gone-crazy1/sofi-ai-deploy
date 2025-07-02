"""
Get correct Paystack bank codes and test account verification
"""
import os
import asyncio
from dotenv import load_dotenv
from paystack.paystack_service import PaystackService

load_dotenv()

async def get_bank_codes():
    """Get correct bank codes from Paystack"""
    
    print("🏦 Getting Bank Codes from Paystack")
    print("=" * 40)
    
    try:
        paystack = PaystackService()
        
        # Get all banks
        banks_result = paystack.transfer_api.get_banks()
        if banks_result.get("success"):
            banks = banks_result.get("data", [])
            
            # Find popular banks
            popular_bank_names = ["gtbank", "guaranty trust bank", "access bank", "first bank", "uba", "zenith", "opay", "wema", "moniepoint", "palmpay", "kuda"]
            
            print("🔍 Popular Bank Codes:")
            for bank in banks:
                bank_name = bank.get("name", "").lower()
                bank_code = bank.get("code")
                
                for popular in popular_bank_names:
                    if popular in bank_name:
                        print(f"✅ {bank_code}: {bank.get('name')}")
                        break
                        
            # Test account verification with your actual account
            print(f"\n🧪 Testing with your actual account:")
            your_account = "9325047112"  # Your Wema Bank account
            wema_code = None
            
            # Find Wema Bank code
            for bank in banks:
                if "wema" in bank.get("name", "").lower():
                    wema_code = bank.get("code")
                    print(f"📋 Found Wema Bank: {wema_code} - {bank.get('name')}")
                    break
            
            if wema_code:
                print(f"\n🔍 Testing verification of your account...")
                result = paystack.verify_account_number(your_account, wema_code)
                
                if result.get("success"):
                    print(f"✅ Your account verified: {result.get('account_name')}")
                else:
                    print(f"❌ Your account verification failed: {result.get('error')}")
            
        else:
            print(f"❌ Failed to get banks: {banks_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_bank_codes())
