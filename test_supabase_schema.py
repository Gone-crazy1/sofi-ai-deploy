#!/usr/bin/env python3
"""
Simple test to understand the virtual_accounts table schema
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

print("Testing Supabase connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created")
    
    # Try to query virtual_accounts table
    print("\nTesting virtual_accounts table...")
    result = supabase.table("virtual_accounts").select("*").limit(5).execute()
    print(f"Query successful: {len(result.data)} records found")
    
    if result.data:
        print(f"Columns in virtual_accounts: {list(result.data[0].keys())}")
        for i, record in enumerate(result.data):
            print(f"Record {i+1}: {record}")
    else:
        print("No records found in virtual_accounts table")
        
    # Try inserting with minimal data to see what's required
    print("\nTesting minimal insert...")
    test_data = {
        "account_number": "1234567890",
        "account_name": "Test User",
        "bank_name": "Test Bank"
    }
    
    try:
        insert_result = supabase.table("virtual_accounts").insert(test_data).execute()
        print(f"✅ Insert successful: {insert_result.data}")
    except Exception as insert_error:
        print(f"❌ Insert failed: {insert_error}")
        # Try with different column names
        test_data2 = {
            "accountNumber": "1234567890",
            "accountName": "Test User", 
            "bankName": "Test Bank"
        }
        try:
            insert_result2 = supabase.table("virtual_accounts").insert(test_data2).execute()
            print(f"✅ Insert with camelCase successful: {insert_result2.data}")
        except Exception as insert_error2:
            print(f"❌ Insert with camelCase also failed: {insert_error2}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
