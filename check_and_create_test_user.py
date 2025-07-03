#!/usr/bin/env python3
"""Check users table schema and create proper test user"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.append('.')
load_dotenv()

def check_users_schema():
    """Check the actual users table schema"""
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get a sample user to see the schema
        users_result = supabase.table("users").select("*").limit(1).execute()
        
        if users_result.data:
            user = users_result.data[0]
            print("📋 Users table schema:")
            for key, value in user.items():
                print(f"   {key}: {type(value).__name__} = {value}")
        else:
            print("❌ No users found")
        
        # Try to create a minimal test user
        test_user_data = {
            "telegram_chat_id": "real_user_test",
            "full_name": "Test User for PIN 1998",
            "phone": "+2348000000000",
            "wallet_balance": 10000.0,  # ₦10,000 balance
            "transaction_pin": "1998"   # Your PIN
        }
        
        print(f"\n🔨 Creating test user with data: {test_user_data}")
        
        # Check if user already exists
        existing = supabase.table("users").select("*").eq("telegram_chat_id", "real_user_test").execute()
        
        if existing.data:
            print("✅ Test user already exists:")
            print(f"   Name: {existing.data[0].get('full_name')}")
            print(f"   Balance: ₦{existing.data[0].get('wallet_balance', 0):,.2f}")
            print(f"   PIN: {existing.data[0].get('transaction_pin', 'Not set')}")
            return existing.data[0]
        else:
            create_result = supabase.table("users").insert(test_user_data).execute()
            if create_result.data:
                print("✅ Test user created successfully!")
                return create_result.data[0]
            else:
                print("❌ Failed to create test user")
                return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    check_users_schema()
