#!/usr/bin/env python3
"""
Add missing columns (country, email) to the users table
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def add_missing_columns():
    """Add country and email columns to users table"""
    
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Missing Supabase credentials")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🔍 Checking existing columns...")
        
        # Test existing columns to see what we have
        try:
            result = supabase.table("users").select("*").limit(1).execute()
            if result.data:
                existing_columns = list(result.data[0].keys())
                print(f"📋 Existing columns: {existing_columns}")
                
                missing_columns = []
                if 'country' not in existing_columns:
                    missing_columns.append('country')
                if 'email' not in existing_columns:
                    missing_columns.append('email')
                    
                if missing_columns:
                    print(f"❌ Missing columns: {missing_columns}")
                    print("\n🔧 You need to add these columns via Supabase SQL Editor:")
                    print("Copy and paste these commands:")
                    print("```sql")
                    if 'country' in missing_columns:
                        print("ALTER TABLE public.users ADD COLUMN country VARCHAR(100);")
                    if 'email' in missing_columns:
                        print("ALTER TABLE public.users ADD COLUMN email VARCHAR(255);")
                    print("```")
                    return False
                else:
                    print("✅ All required columns already exist!")
                    return True
            else:
                print("❌ No data found in users table")
                return False
                
        except Exception as e:
            print(f"❌ Error checking columns: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Adding Missing Columns to Users Table ===")
    success = add_missing_columns()
    if success:
        print("\n✅ Database schema is ready!")
    else:
        print("\n⚠️ Please add the missing columns manually in Supabase")
