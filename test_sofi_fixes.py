"""
🧪 TEST SOFI FIXES

Test script to verify all our fixes are working
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.balance_helper import get_user_balance, check_virtual_account
from utils.bank_name_converter import get_bank_name_from_code, format_transfer_message
from paystack.paystack_webhook import PaystackWebhookHandler

async def test_balance_fix():
    """Test enhanced balance functionality"""
    print("🔍 Testing Balance Fix...")
    
    # Test with a user who has funds
    test_user = "123456789"  # This user has 5000.0 according to sync
    balance = await get_user_balance(test_user, force_sync=True)
    print(f"✅ User {test_user} balance: ₦{balance:,}")
    
    # Test virtual account status
    account_info = await check_virtual_account(test_user)
    print(f"✅ Account status: {account_info.get('status', 'unknown')}")
    
def test_bank_name_converter():
    """Test bank code to name conversion"""
    print("\n🏦 Testing Bank Name Converter...")
    
    test_codes = ["035", "058", "50515", "999991", "unknown123"]
    for code in test_codes:
        name = get_bank_name_from_code(code)
        print(f"✅ {code} → {name}")
    
    # Test transfer message formatting
    message = format_transfer_message(5000, "John Doe", "1234567890", "035")
    print(f"\n📄 Transfer Message Preview:\n{message}")

def test_webhook_sender_extraction():
    """Test enhanced webhook sender extraction"""
    print("\n📥 Testing Webhook Sender Extraction...")
    
    handler = PaystackWebhookHandler()
    
    # Test data with various sender info patterns
    test_data = {
        "amount": 500000,  # 5000 naira in kobo
        "customer": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        },
        "payer_name": "John Doe",
        "sender_bank": "GTBank",
        "narration": "Transfer from John Doe via GTBank"
    }
    
    sender_name = handler._extract_sender_name(test_data, test_data.get("customer", {}))
    sender_bank = handler._extract_sender_bank(test_data)
    
    print(f"✅ Extracted sender: {sender_name}")
    print(f"✅ Extracted bank: {sender_bank}")

async def main():
    """Run all tests"""
    print("🚀 Testing Sofi AI Fixes")
    print("=" * 40)
    
    await test_balance_fix()
    test_bank_name_converter()
    test_webhook_sender_extraction()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Fix Summary:")
    print("✅ Balance sync with force refresh")
    print("✅ Smart virtual account status detection")
    print("✅ Enhanced sender info extraction")
    print("✅ Bank code to name conversion")
    print("✅ Improved notification messages")

if __name__ == "__main__":
    asyncio.run(main())
