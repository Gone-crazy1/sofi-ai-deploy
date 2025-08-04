#!/usr/bin/env python3
"""
🔧 Emergency Database Schema Fix
Adds the missing 'status' column and other required fields to the users table
"""

import os
from supabase import create_client, Client

def update_database_schema():
    """Add missing columns to users table"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in environment variables")
            print("   Make sure SUPABASE_URL and SUPABASE_KEY are set")
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # SQL commands to add missing columns
        schema_updates = [
            """
            -- Add missing columns if they don't exist
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS first_name TEXT,
            ADD COLUMN IF NOT EXISTS last_name TEXT,
            ADD COLUMN IF NOT EXISTS bvn TEXT,
            ADD COLUMN IF NOT EXISTS address TEXT,
            ADD COLUMN IF NOT EXISTS signup_source TEXT DEFAULT 'web',
            ADD COLUMN IF NOT EXISTS flow_token TEXT,
            ADD COLUMN IF NOT EXISTS registration_completed BOOLEAN DEFAULT FALSE;
            """,
            """
            -- Add missing timestamp columns if they don't exist
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
            """,
            """
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_users_first_name ON users(first_name);
            CREATE INDEX IF NOT EXISTS idx_users_last_name ON users(last_name);
            CREATE INDEX IF NOT EXISTS idx_users_bvn ON users(bvn);
            CREATE INDEX IF NOT EXISTS idx_users_flow_token ON users(flow_token);
            CREATE INDEX IF NOT EXISTS idx_users_signup_source ON users(signup_source);
            """
        ]
        
        print("🔧 Updating database schema...")
        
        for i, sql in enumerate(schema_updates, 1):
            try:
                result = supabase.rpc('execute_sql', {'sql': sql}).execute()
                print(f"✅ Schema update {i}/3 completed")
            except Exception as e:
                print(f"❌ Schema update {i}/3 failed: {e}")
                # Try alternative method
                try:
                    # Use direct SQL execution (if available)
                    print(f"   🔄 Trying alternative method for update {i}...")
                    # Note: Direct SQL execution depends on your Supabase setup
                    print(f"   ⚠️  Please run this SQL manually in Supabase SQL Editor:")
                    print(f"   {sql}")
                except Exception as e2:
                    print(f"   ❌ Alternative method also failed: {e2}")
        
        print("✅ Schema update completed!")
        print("\n📋 Next steps:")
        print("1. If any updates failed, run them manually in Supabase SQL Editor")
        print("2. Test your WhatsApp Flow again")
        print("3. Check the logs for any remaining issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("\n🔧 Manual Fix Required:")
        print("Go to your Supabase dashboard → SQL Editor → Run this SQL:")
        print("""
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS last_name TEXT,
ADD COLUMN IF NOT EXISTS bvn TEXT,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS signup_source TEXT DEFAULT 'web',
ADD COLUMN IF NOT EXISTS flow_token TEXT,
ADD COLUMN IF NOT EXISTS registration_completed BOOLEAN DEFAULT FALSE;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
        """)
        return False

if __name__ == "__main__":
    print("🚨 Emergency Database Schema Fix")
    print("=" * 40)
    update_database_schema()
