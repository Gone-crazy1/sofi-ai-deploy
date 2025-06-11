#!/usr/bin/env python3
"""
Check the actual schema of the virtual_accounts table in Supabase
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_supabase_schema():
    """Check the schema of virtual_accounts table"""
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        print(f"🔗 Connecting to Supabase...")
        print(f"URL: {SUPABASE_URL}")
        print(f"Key (first 20 chars): {SUPABASE_KEY[:20]}...")
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("\n📋 Checking virtual_accounts table schema...")
        
        # Try to get any existing records to see the structure
        try:
            result = supabase.table("virtual_accounts").select("*").limit(1).execute()
            print(f"✅ Table exists! Sample data structure:")
            if result.data:
                print(f"   Columns found: {list(result.data[0].keys())}")
                print(f"   Sample record: {result.data[0]}")
            else:
                print("   ⚠️ Table is empty, trying to get column info...")
                
                # Try a test insert to see what columns are expected
                try:
                    test_data = {"test": "value"}
                    supabase.table("virtual_accounts").insert(test_data).execute()
                except Exception as insert_error:
                    print(f"   Schema info from error: {insert_error}")
                    
        except Exception as e:
            print(f"❌ Error accessing virtual_accounts table: {e}")
            
        print("\n📋 Checking users table schema...")
        try:
            result = supabase.table("users").select("*").limit(1).execute()
            print(f"✅ Users table exists! Sample data structure:")
            if result.data:
                print(f"   Columns found: {list(result.data[0].keys())}")
                print(f"   Sample record: {result.data[0]}")
            else:
                print("   ⚠️ Users table is empty")
        except Exception as e:
            print(f"❌ Error accessing users table: {e}")
            
        print("\n🔍 Listing all tables...")
        try:
            # Try to list all tables (this might not work with all permissions)
            tables_result = supabase.rpc('get_tables').execute()
            print(f"Available tables: {tables_result.data}")
        except Exception as e:
            print(f"Could not list tables: {e}")
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")

if __name__ == "__main__":
    check_supabase_schema()
