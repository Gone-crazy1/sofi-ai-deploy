#!/usr/bin/env python3
"""
Check the users table schema and fix phone field issue
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Checking users table schema...")

# Check existing users data to see the structure
try:
    result = supabase.table("users").select("*").limit(1).execute()
    if result.data:
        print(f"✅ Users table structure:")
        print(f"   Columns: {list(result.data[0].keys())}")
        print(f"   Sample record: {result.data[0]}")
    else:
        print("⚠️ Users table is empty")
        
    # Test different phone column names
    phone_column_names = ["phone", "phone_number", "mobile", "contact_number"]
    
    for phone_col in phone_column_names:
        try:
            test_result = supabase.table("users").select(phone_col).limit(1).execute()
            print(f"✅ Phone column '{phone_col}' exists")
            break
        except Exception as e:
            if "does not exist" in str(e):
                print(f"❌ Phone column '{phone_col}' does not exist")
            else:
                print(f"❓ Error testing '{phone_col}': {e}")
    
    # Test a minimal users insert to see what's required
    print(f"\n🧪 Testing users table insert with phone field...")
    
    test_data = {
        "first_name": "Test",
        "last_name": "User",
        "bvn": "12345678901",
        "phone": "08123456789",  # Try with phone first
        "telegram_chat_id": "test123"
    }
    
    try:
        insert_result = supabase.table("users").insert(test_data).execute()
        print(f"✅ Insert with 'phone' successful: {insert_result.data}")
        
        # Clean up
        if insert_result.data and 'id' in insert_result.data[0]:
            supabase.table("users").delete().eq('id', insert_result.data[0]['id']).execute()
            print("🧹 Cleaned up test record")
            
    except Exception as e:
        print(f"❌ Insert with 'phone' failed: {e}")
        
        # If phone doesn't work, try without it
        test_data_no_phone = {
            "first_name": "Test",
            "last_name": "User", 
            "bvn": "12345678901",
            "telegram_chat_id": "test123"
        }
        
        try:
            insert_result2 = supabase.table("users").insert(test_data_no_phone).execute()
            print(f"✅ Insert without phone successful: {insert_result2.data}")
            
            # Clean up
            if insert_result2.data and 'id' in insert_result2.data[0]:
                supabase.table("users").delete().eq('id', insert_result2.data[0]['id']).execute()
                print("🧹 Cleaned up test record")
                
        except Exception as e2:
            print(f"❌ Insert without phone also failed: {e2}")

except Exception as e:
    print(f"❌ Error checking users table: {e}")

print(f"\n📋 Summary of findings:")
print(f"   - Check actual column names in users table")
print(f"   - Determine if 'phone' field exists or has different name")
print(f"   - Update main.py accordingly")
