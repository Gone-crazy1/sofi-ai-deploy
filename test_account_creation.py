#!/usr/bin/env python3
"""
Test Account Creation and Payment Flow
=====================================
This script will:
1. Create a test user in Supabase
2. Create a virtual account via Paystack
3. Display the account details for you to send money to
4. Monitor for incoming payments
"""

import os
import asyncio
import time
from dotenv import load_dotenv
from supabase import create_client
from paystack.paystack_service import PaystackService

# Load environment variables
load_dotenv()

def test_account_creation():
    """Test creating a virtual account"""
    
    print("🧪 Testing Account Creation and Payment Flow")
    print("=" * 50)
    
    # Initialize services
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")  # Use regular key instead of service role
    )
    
    paystack = PaystackService()
    
    # Test user data
    test_chat_id = "test_user_12345"
    test_phone = "+2348123456789"
    test_name = "Test User"
    test_email = "testuser@example.com"
    
    try:
        print(f"👤 Creating test user: {test_name}")
        
        # Check if user already exists
        existing_user = supabase.table("users").select("*").eq("telegram_chat_id", test_chat_id).execute()
        
        if existing_user.data:
            print("✅ Test user already exists")
            user_data = existing_user.data[0]
        else:
            # Create new user
            user_data = {
                "telegram_chat_id": test_chat_id,
                "phone_number": test_phone,
                "full_name": test_name,
                "email": test_email,
                "balance": 0.0,
                "is_verified": True,
                "created_at": "now()"
            }
            
            result = supabase.table("users").insert(user_data).execute()
            user_data = result.data[0]
            print("✅ Test user created successfully")
        
        print(f"📱 User ID: {test_chat_id}")
        print(f"📧 Email: {test_email}")
        print(f"💰 Current Balance: ₦{user_data.get('balance', 0):,.2f}")
        
        # Create virtual account
        print("\n🏦 Creating virtual account...")
        
        account_result = paystack.create_user_account_simple({
            'chat_id': test_chat_id,
            'email': test_email,
            'first_name': test_name.split()[0] if test_name.split() else 'Test',
            'last_name': test_name.split()[-1] if len(test_name.split()) > 1 else 'User',
            'phone': test_phone
        })
        
        if account_result.get("success"):
            account_data = account_result["data"]
            
            print("✅ Virtual account created successfully!")
            print("\n" + "=" * 50)
            print("💳 ACCOUNT DETAILS FOR TESTING")
            print("=" * 50)
            print(f"🏛️  Bank: {account_data.get('bank_name', 'N/A')}")
            print(f"🔢 Account Number: {account_data.get('account_number', 'N/A')}")
            print(f"👤 Account Name: {account_data.get('account_name', 'N/A')}")
            print(f"📧 Customer Code: {account_data.get('customer_code', 'N/A')}")
            print("=" * 50)
            
            print("\n📝 INSTRUCTIONS:")
            print("1. Use the account details above to send money")
            print("2. Send any amount (minimum ₦100)")
            print("3. Check the logs to see the webhook in action")
            print("4. Your balance will be automatically updated")
            print("\n⏳ Waiting for payment... (Press Ctrl+C to stop)")
            
            # Monitor for balance changes
            initial_balance = user_data.get('balance', 0)
            print(f"\n📊 Monitoring balance (Current: ₦{initial_balance:,.2f})")
            
            while True:
                time.sleep(5)  # Check every 5 seconds
                
                # Check current balance
                current_user = supabase.table("users").select("balance").eq("telegram_chat_id", test_chat_id).execute()
                
                if current_user.data:
                    current_balance = current_user.data[0].get('balance', 0)
                    
                    if current_balance != initial_balance:
                        difference = current_balance - initial_balance
                        print(f"\n🎉 PAYMENT RECEIVED!")
                        print(f"💰 Amount: ₦{difference:,.2f}")
                        print(f"💳 New Balance: ₦{current_balance:,.2f}")
                        print("✅ Webhook processing successful!")
                        break
                    else:
                        print(f"⏳ Still waiting... (Balance: ₦{current_balance:,.2f})")
                
        else:
            print(f"❌ Failed to create virtual account: {account_result.get('error')}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_account_creation()
