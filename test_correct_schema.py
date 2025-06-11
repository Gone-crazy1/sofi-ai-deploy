#!/usr/bin/env python3
"""
Test the correct column names for virtual_accounts table
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🧪 Testing correct column names for virtual_accounts...")

# Test the lowercase column names
correct_columns = ["id", "telegram_chat_id", "accountnumber", "accountname", "bankname", "created_at"]

for column in correct_columns:
    try:
        result = supabase.table("virtual_accounts").select(column).limit(1).execute()
        print(f"✅ Column '{column}' exists")
    except Exception as e:
        print(f"❌ Column '{column}' error: {e}")

print("\n🧪 Testing a complete insert with correct column names...")

test_data = {
    "telegram_chat_id": "123456789",
    "accountnumber": "1234567890", 
    "accountname": "Test User",
    "bankname": "Test Bank"
}

try:
    result = supabase.table("virtual_accounts").insert(test_data).execute()
    print(f"✅ Insert successful: {result.data}")
    
    # Clean up the test record
    if result.data and 'id' in result.data[0]:
        delete_result = supabase.table("virtual_accounts").delete().eq('id', result.data[0]['id']).execute()
        print("🧹 Test record cleaned up")
        
except Exception as e:
    print(f"❌ Insert failed: {e}")

print("\n📋 Testing users table insert...")
user_data = {
    "first_name": "Test",
    "last_name": "User", 
    "bvn": "12345678901",
    "telegram_chat_id": "123456789"
}

try:
    result = supabase.table("users").insert(user_data).execute()
    print(f"✅ Users insert successful: {result.data}")
    
    # Clean up
    if result.data and 'id' in result.data[0]:
        supabase.table("users").delete().eq('id', result.data[0]['id']).execute()
        print("🧹 Test user record cleaned up")
        
except Exception as e:
    print(f"❌ Users insert failed: {e}")
