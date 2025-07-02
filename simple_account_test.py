#!/usr/bin/env python3
"""
Simple account creation test - just test Paystack virtual account creation
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def simple_account_test():
    """Simple test of Paystack account creation"""
    print("🧪 Simple Account Creation Test")
    print("=" * 40)
    
    try:
        from paystack.paystack_service import PaystackService
        
        # Initialize Paystack service
        paystack = PaystackService()
        print("✅ Paystack service initialized")
        
        # Test user data
        test_user = {
            'chat_id': '12345',
            'email': 'test@sofi.ai',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+2348123456789'
        }
        
        print(f"👤 Creating account for: {test_user['first_name']} {test_user['last_name']}")
        print(f"📧 Email: {test_user['email']}")
        print(f"📱 Phone: {test_user['phone']}")
        
        # Create virtual account
        result = paystack.create_user_account_simple(test_user)
        
        if result.get("success"):
            account_details = result.get("account_details", {})
            print("\n🎉 Account created successfully!")
            print("=" * 40)
            
            # Extract account details
            customer = account_details.get("customer", {})
            dedicated_account = account_details.get("dedicated_account", {})
            
            print(f"👤 Customer Code: {customer.get('customer_code')}")
            print(f"🏦 Bank: {dedicated_account.get('bank', {}).get('name')}")
            print(f"🔢 Account Number: {dedicated_account.get('account_number')}")
            print(f"👤 Account Name: {dedicated_account.get('account_name')}")
            
            print("\n💰 TRANSFER DETAILS:")
            print("=" * 40)
            print(f"Bank: {dedicated_account.get('bank', {}).get('name')}")
            print(f"Account Number: {dedicated_account.get('account_number')}")
            print(f"Account Name: {dedicated_account.get('account_name')}")
            
            print("\n🎯 READY FOR TESTING!")
            print("You can now send money to the account above.")
            print("The webhook will process the payment and credit the user.")
            
        else:
            print(f"❌ Account creation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_account_test()
