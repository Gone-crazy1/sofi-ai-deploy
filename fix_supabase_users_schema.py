#!/usr/bin/env python3
"""
Fix Supabase Schema - Add Missing Columns
Run this to add missing columns to make virtual account creation work
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def fix_supabase_schema():
    """Add missing columns to users table"""
    print("🔧 Fixing Supabase Schema - Adding Missing Columns")
    print("=" * 60)
    
    try:
        # Initialize Supabase with service role key for admin operations
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Get current table structure
        print("🔍 Checking current users table structure...")
        try:
            result = supabase.table("users").select("*").limit(1).execute()
            print("✅ Users table exists")
        except Exception as e:
            print(f"❌ Users table check failed: {e}")
            return False
        
        # Add missing columns using SQL
        missing_columns_sql = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_id TEXT UNIQUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_limit DECIMAL DEFAULT 50000;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_complete BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS address TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS date_of_birth DATE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS gender TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS state TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS city TEXT;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();"
        ]
        
        print("🔄 Adding missing columns...")
        
        for i, sql in enumerate(missing_columns_sql, 1):
            try:
                # Use rpc to execute raw SQL
                result = supabase.rpc('execute_sql', {'query': sql}).execute()
                print(f"✅ Added column {i}/13")
            except Exception as e:
                print(f"⚠️  Column {i} may already exist or error: {e}")
        
        # Create indexes for better performance
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);"
        ]
        
        print("🔄 Creating indexes...")
        for i, sql in enumerate(indexes_sql, 1):
            try:
                result = supabase.rpc('execute_sql', {'query': sql}).execute()
                print(f"✅ Created index {i}/3")
            except Exception as e:
                print(f"⚠️  Index {i} may already exist or error: {e}")
        
        print("\n🎉 Schema fix completed!")
        print("✅ Users table should now support virtual account creation")
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_supabase_schema()
    if success:
        print("\n🚀 Ready to test virtual account creation again!")
        print("Run: python debug_virtual_account_form.py")
    else:
        print("\n⚠️  Manual schema fix required")
        print("Go to Supabase dashboard and add missing columns manually")
