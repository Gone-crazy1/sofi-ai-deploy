#!/usr/bin/env python3
"""
Test different column names to discover the virtual_accounts table schema
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Common column names to test
test_columns = [
    "id",
    "user_id", 
    "telegram_chat_id",
    "account_number",
    "account_name", 
    "bank_name",
    "created_at",
    "updated_at",
    "accountNumber",
    "accountName",
    "bankName",
    "first_name",
    "last_name",
    "phone",
    "bvn"
]

print("🔍 Testing column names in virtual_accounts table...")

for column in test_columns:
    try:
        result = supabase.table("virtual_accounts").select(column).limit(1).execute()
        print(f"✅ Column '{column}' exists")
    except Exception as e:
        if "Could not find" in str(e):
            print(f"❌ Column '{column}' does not exist")
        else:
            print(f"❓ Error testing '{column}': {e}")

print("\n🔍 Testing minimal insert with basic columns...")

# Try the most basic insert possible
basic_inserts = [
    {"id": 999},  # If there's an auto-increment ID
    {"user_id": 1},  # If it requires a user_id
    {"telegram_chat_id": "123456789"},  # If it requires telegram_chat_id
    {}  # Empty insert to see default requirements
]

for i, test_data in enumerate(basic_inserts):
    try:
        print(f"\nTesting insert {i+1}: {test_data}")
        result = supabase.table("virtual_accounts").insert(test_data).execute()
        print(f"✅ Insert successful: {result.data}")
        
        # If successful, immediately delete it to keep table clean
        if result.data and 'id' in result.data[0]:
            supabase.table("virtual_accounts").delete().eq('id', result.data[0]['id']).execute()
            print("🧹 Cleaned up test record")
        break
    except Exception as e:
        print(f"❌ Insert failed: {e}")

print("\n📋 Let's check the users table schema for comparison...")
user_columns = [
    "id", "first_name", "last_name", "phone", "bvn", "telegram_chat_id", "created_at"
]

for column in user_columns:
    try:
        result = supabase.table("users").select(column).limit(1).execute()
        print(f"✅ Users column '{column}' exists")
    except Exception as e:
        if "Could not find" in str(e):
            print(f"❌ Users column '{column}' does not exist")
        else:
            print(f"❓ Error testing users '{column}': {e}")
