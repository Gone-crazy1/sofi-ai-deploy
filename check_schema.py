#!/usr/bin/env python3
"""
Check Supabase Schema
Check what columns exist in the users table
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("🔍 Checking Supabase Schema")
print("=" * 40)

try:
    # Check if users table exists and what columns it has
    result = supabase.rpc('get_table_schema', {'table_name': 'users'}).execute()
    print(f"✅ users table schema: {result.data}")
except Exception as e:
    print(f"❌ Error checking schema: {e}")

try:
    # Try to get a sample record to see actual columns
    result = supabase.table('users').select('*').limit(1).execute()
    if result.data:
        print(f"✅ Sample user record columns: {list(result.data[0].keys())}")
    else:
        print("ℹ️ No users in table to check columns")
except Exception as e:
    print(f"❌ Error getting sample record: {e}")

# Try inserting with minimal data to see what works
try:
    test_data = {
        'telegram_chat_id': 'test_schema_check',
        'email': 'test@test.com'
    }
    result = supabase.table('users').insert(test_data).execute()
    if result.data:
        print("✅ Basic insert works")
        # Clean up
        supabase.table('users').delete().eq('telegram_chat_id', 'test_schema_check').execute()
    else:
        print("❌ Basic insert failed")
except Exception as e:
    print(f"ℹ️ Insert error (shows required columns): {e}")

print("\n📝 Recommendation:")
print("1. Apply the ultra_safe_schema.sql to your Supabase database")
print("2. Or modify the test to only use existing columns")
print("3. Check your Supabase dashboard > SQL Editor to run the schema")
