#!/usr/bin/env python3
"""
🔥 SIMULATED OPAY VIRTUAL ACCOUNT TEST

Since the OPay sandbox URL is not accessible, this script:
1. Simulates a successful virtual account creation
2. Records the simulated account in Supabase
3. Shows you exactly what the data would look like
4. Lets you verify the Supabase recording works

This way you can see the account creation process and check Supabase.
"""

import asyncio
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
import random

# Load environment
load_dotenv()

# Test user data
TEST_USER = {
    "telegram_id": random.randint(1000000000, 9999999999),  # Use numeric ID for bigint field
    "full_name": "Sofi Test User",
    "phone": "08012345678",
    "email": "test@sofi-ai.com",
    "bvn": "12345678901"
}

def generate_test_account():
    """Generate a test virtual account response like OPay would return"""
    account_number = f"90{random.randint(10000000, 99999999)}"
    
    return {
        "status": "success",
        "message": "Virtual account created successfully",
        "data": {
            "accountNumber": account_number,
            "accountName": TEST_USER["full_name"],
            "bankName": "OPay",
            "bankCode": "999992",
            "reference": f"SOFI_REAL_{int(datetime.now().timestamp())}",
            "status": "ACTIVE",
            "currency": "NGN",
            "country": "NG"
        }
    }

async def test_simulated_account_creation():
    """Test simulated virtual account creation and Supabase recording"""
    
    print("🔥 SIMULATED OPAY VIRTUAL ACCOUNT CREATION")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 60)
    
    print("ℹ️  Since OPay sandbox is not accessible, we're simulating")
    print("   the account creation to test Supabase recording.")
    print()
    
    # Step 1: Connect to Supabase
    print("🗄️ STEP 1: Connecting to Supabase")
    print("-" * 40)
    
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials missing")
            return
            
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection
        result = supabase.table("users").select("count", count="exact").execute()
        print(f"✅ Supabase connected: {result.count} existing users")
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return
    
    # Step 2: Generate simulated account
    print("\n🏦 STEP 2: Generating Simulated Virtual Account")
    print("-" * 40)
    
    simulated_response = generate_test_account()
    account_data = simulated_response["data"]
    
    print("✅ Simulated OPay Response:")
    print(json.dumps(simulated_response, indent=2))
    
    # Step 3: Record in Supabase (this tests the actual recording process)
    print("\n💾 STEP 3: Recording in Supabase")
    print("-" * 40)
    
    try:        # Create user record first (using actual column names)
        user_record = {
            "telegram_chat_id": TEST_USER["telegram_id"],
            "first_name": TEST_USER["full_name"].split()[0],
            "last_name": " ".join(TEST_USER["full_name"].split()[1:]),
            "telegram_username": f"sofi_test_{random.randint(100, 999)}",
            "phone": TEST_USER["phone"],
            "email": TEST_USER["email"],
            "bvn": TEST_USER["bvn"],
            "country": "Nigeria",
            "account_number": account_data["accountNumber"],  # Use the generated account number
            "bank_name": account_data["bankName"],
            "account_name": account_data["accountName"],
            "account_reference": account_data["reference"],
            "created_at": datetime.now().isoformat()
        }
        
        print("Creating user record...")
        user_result = supabase.table("users").insert(user_record).execute()
        print(f"✅ User created with ID: {user_result.data[0]['id'] if user_result.data else 'N/A'}")
          # Create virtual account record (using actual column names)
        account_record = {
            "telegram_chat_id": TEST_USER["telegram_id"],
            "accountnumber": account_data["accountNumber"],
            "accountname": account_data["accountName"],
            "bankname": account_data["bankName"],
            "accountreference": account_data["reference"],
            "balance": 0.00,
            "created_at": datetime.now().isoformat()
        }
        
        print("Creating virtual account record...")
        account_result = supabase.table("virtual_accounts").insert(account_record).execute()
        print(f"✅ Virtual account created with ID: {account_result.data[0]['id'] if account_result.data else 'N/A'}")
          # Create initial balance record (if table exists)
        # balance_record = {
        #     "user_id": TEST_USER["telegram_id"],
        #     "current_balance": 0.00,
        #     "last_updated": datetime.now().isoformat(),
        #     "account_number": account_data["accountNumber"]
        # }
        
        # print("Creating balance record...")
        # balance_result = supabase.table("user_balances").insert(balance_record).execute()
        # print(f"✅ Balance record created")
        print("ℹ️  Skipping balance record (table may not exist)")
        
        # Step 4: Verify records
        print("\n🔍 STEP 4: Verifying Records in Supabase")
        print("-" * 40)
        
        # Check user record
        user_check = supabase.table("users").select("*").eq("telegram_chat_id", TEST_USER["telegram_id"]).execute()
        if user_check.data:
            print("✅ User record found in database")
            user_data = user_check.data[0]
            print(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
            print(f"   Phone: {user_data.get('phone')}")
            print(f"   Status: {user_data.get('status')}")
          # Check virtual account record  
        account_check = supabase.table("virtual_accounts").select("*").eq("telegram_chat_id", TEST_USER["telegram_id"]).execute()
        if account_check.data:
            print("✅ Virtual account record found in database")
            account_data_check = account_check.data[0]
            print(f"   Account Number: {account_data_check.get('accountnumber')}")
            print(f"   Account Name: {account_data_check.get('accountname')}")
            print(f"   Bank: {account_data_check.get('bankname')}")
            print(f"   Balance: ₦{account_data_check.get('balance', 0):,.2f}")
          # Check balance record (if it exists)
        # balance_check = supabase.table("user_balances").select("*").eq("user_id", TEST_USER["telegram_id"]).execute()
        # if balance_check.data:
        #     print("✅ Balance record found in database")
        #     balance_data = balance_check.data[0]
        #     print(f"   Current Balance: ₦{balance_data.get('current_balance', 0):,.2f}")
        print("ℹ️  Balance table check skipped")
        
        print("\n🎉 SUCCESS! All records created successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create records: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return
    
    # Step 5: Show what to check in Supabase
    print("\n📋 CHECK YOUR SUPABASE DASHBOARD")
    print("=" * 60)
    print("🔍 Look for these records:")
    print(f"📊 **users table:**")
    print(f"   • telegram_chat_id: {TEST_USER['telegram_id']}")
    print(f"   • first_name: {user_record['first_name']}")
    print(f"   • phone: {TEST_USER['phone']}")
    print()
    print(f"🏦 **virtual_accounts table:**")
    print(f"   • telegram_chat_id: {TEST_USER['telegram_id']}")
    print(f"   • accountnumber: {account_record['accountnumber']}")
    print(f"   • bankname: {account_record['bankname']}")
    print(f"   • balance: ₦{account_record['balance']:,.2f}")
    print()
    print(f"💰 **user_balances table:**")
    print(f"   • user_id: {TEST_USER['telegram_id']}")
    print(f"   • current_balance: 0.00")
    
    print("\n🚀 NEXT STEPS:")
    print("1. ✅ Check Supabase dashboard for the new records")
    print("2. 🔗 Fix OPay API endpoint (contact OPay support for correct URL)")
    print("3. 🧪 Test with real OPay API once endpoint is working")
    print("4. 🗑️  Clean up test records when ready")
    
    # Offer to clean up
    print(f"\n🧹 CLEANUP")
    print("-" * 20)
    cleanup = input("Delete test records? (y/n): ").lower().strip()
    
    if cleanup == 'y':
        try:
            supabase.table("user_balances").delete().eq("user_id", TEST_USER["telegram_id"]).execute()
            supabase.table("virtual_accounts").delete().eq("telegram_chat_id", TEST_USER["telegram_id"]).execute()
            supabase.table("users").delete().eq("telegram_chat_id", TEST_USER["telegram_id"]).execute()
            print("✅ Test records cleaned up")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    else:
        print("ℹ️  Test records kept for manual verification")

if __name__ == "__main__":
    asyncio.run(test_simulated_account_creation())
