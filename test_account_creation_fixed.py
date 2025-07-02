#!/usr/bin/env python3
"""
Test Account Creation with Paystack
==================================
Create a test virtual account and show the details for testing payments
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Verify environment variables are loaded
print("🔧 Checking environment variables...")
paystack_key = os.getenv("PAYSTACK_SECRET_KEY")
if not paystack_key:
    print("❌ PAYSTACK_SECRET_KEY not found!")
    sys.exit(1)
else:
    print(f"✅ PAYSTACK_SECRET_KEY found: {paystack_key[:20]}...")

supabase_url = os.getenv("SUPABASE_URL")
if not supabase_url:
    print("❌ SUPABASE_URL not found!")
    sys.exit(1)
else:
    print(f"✅ SUPABASE_URL found: {supabase_url}")

# Now import our modules
try:
    from paystack.paystack_service import PaystackService
    from supabase import create_client
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_account_creation():
    """Test creating a virtual account"""
    
    print("\n🧪 Starting account creation test...")
    
    # Test user data
    test_chat_id = "test_12345"
    test_user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "+2348123456789"
    }
    
    try:
        # Initialize Paystack service
        paystack = PaystackService()
        print("✅ Paystack service initialized")
        
        # Initialize Supabase
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")  # Use regular key instead of service role
        )
        print("✅ Supabase client initialized")
        
        # Create user account
        print("\n📝 Creating virtual account...")
        user_data = {
            "telegram_chat_id": test_chat_id,
            "first_name": test_user_data["first_name"],
            "last_name": test_user_data["last_name"],
            "email": test_user_data["email"],
            "phone": test_user_data["phone"]
        }
        
        result = await paystack.create_user_account_simple(user_data)
        
        if result["success"]:
            account_info = result["data"]
            print(f"\n🎉 Account created successfully!")
            print(f"👤 Customer Code: {account_info.get('customer_code')}")
            print(f"🏦 Account Number: {account_info.get('account_number')}")
            print(f"🏢 Bank Name: {account_info.get('bank_name')}")
            print(f"📧 Email: {account_info.get('email')}")
            
            # Store in Supabase for testing
            user_data = {
                "telegram_chat_id": test_chat_id,
                "first_name": test_user_data["first_name"],
                "last_name": test_user_data["last_name"],
                "email": test_user_data["email"],
                "phone": test_user_data["phone"],
                "balance": 0.0,
                "paystack_customer_code": account_info.get('customer_code'),
                "created_at": "now()"
            }
            
            # Insert or update user
            existing_user = supabase.table("users").select("*").eq("telegram_chat_id", test_chat_id).execute()
            
            if existing_user.data:
                supabase.table("users").update(user_data).eq("telegram_chat_id", test_chat_id).execute()
                print("✅ Updated existing test user in database")
            else:
                supabase.table("users").insert(user_data).execute()
                print("✅ Created new test user in database")
            
            # Store virtual account info
            va_data = {
                "user_id": test_chat_id,
                "account_number": account_info.get('account_number'),
                "bank_name": account_info.get('bank_name'),
                "customer_code": account_info.get('customer_code'),
                "account_type": "dedicated_virtual",
                "is_active": True,
                "created_at": "now()"
            }
            
            # Insert or update virtual account
            existing_va = supabase.table("virtual_accounts").select("*").eq("user_id", test_chat_id).execute()
            
            if existing_va.data:
                supabase.table("virtual_accounts").update(va_data).eq("user_id", test_chat_id).execute()
                print("✅ Updated existing virtual account in database")
            else:
                supabase.table("virtual_accounts").insert(va_data).execute()
                print("✅ Created new virtual account in database")
            
            print("\n" + "="*50)
            print("🎯 TEST ACCOUNT READY FOR PAYMENT!")
            print("="*50)
            print(f"💳 Send money to this account:")
            print(f"   Account Number: {account_info.get('account_number')}")
            print(f"   Bank: {account_info.get('bank_name')}")
            print(f"   Account Name: {test_user_data['first_name']} {test_user_data['last_name']}")
            print("\n💡 What happens when you send money:")
            print("   1. Paystack receives the payment")
            print("   2. Paystack sends webhook to your app")
            print("   3. Your app credits the test user's balance")
            print("   4. Check the logs to see the webhook processing")
            print("\n🔍 Monitor webhook at: https://sofi-ai-trio.onrender.com/paystack-webhook")
            print("="*50)
            
        else:
            print(f"❌ Account creation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing Paystack Account Creation...")
    asyncio.run(test_account_creation())
