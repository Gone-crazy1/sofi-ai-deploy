"""
Test Paystack account verification and transfer functionality
"""
import os
import asyncio
from dotenv import load_dotenv
from paystack.paystack_service import PaystackService

load_dotenv()

async def test_paystack_transfers():
    """Test account verification and transfer process"""
    
    print("🧪 Testing Paystack Transfer Functionality")
    print("=" * 50)
    
    try:
        # Initialize Paystack service
        paystack = PaystackService()
        
        # Test 1: Account verification with various banks
        test_accounts = [
            {"account": "0123456789", "bank": "058", "name": "GTBank"},
            {"account": "0987654321", "bank": "044", "name": "Access Bank"},
            {"account": "1234567890", "bank": "999992", "name": "OPay"},
        ]
        
        print("📋 Testing Account Verification:")
        for test in test_accounts:
            print(f"\n🔍 Testing {test['name']} account verification...")
            result = paystack.verify_account_number(test["account"], test["bank"])
            
            if result.get("success"):
                print(f"✅ Verification successful: {result.get('account_name', 'N/A')}")
            else:
                print(f"❌ Verification failed: {result.get('error', 'Unknown error')}")
        
        # Test 2: Bank list availability
        print(f"\n📋 Testing Bank List:")
        banks_result = paystack.transfer_api.get_banks()
        if banks_result.get("success"):
            banks = banks_result.get("data", [])
            print(f"✅ Retrieved {len(banks)} banks")
            
            # Show some popular banks
            popular_banks = ["058", "044", "011", "033", "999992"]  # GTB, Access, First, UBA, OPay
            print("Popular banks available:")
            for bank in banks[:10]:  # Show first 10
                bank_code = bank.get("code")
                bank_name = bank.get("name")
                if bank_code in popular_banks:
                    print(f"  ✅ {bank_code}: {bank_name}")
        else:
            print(f"❌ Failed to get banks: {banks_result.get('error')}")
        
        # Test 3: Transfer recipient creation (dry run)
        print(f"\n🎯 Testing Transfer Recipient Creation:")
        recipient_result = paystack.transfer_api.create_transfer_recipient(
            account_number="0123456789",
            bank_code="058",
            name="Test User"
        )
        
        if recipient_result.get("success"):
            print("✅ Transfer recipient creation works")
            recipient_code = recipient_result["data"]["recipient_code"]
            print(f"   Recipient code: {recipient_code}")
        else:
            print(f"❌ Transfer recipient creation failed: {recipient_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_paystack_transfers())
