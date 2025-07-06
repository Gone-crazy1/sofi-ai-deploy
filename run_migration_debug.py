#!/usr/bin/env python3
"""
Run migration with detailed output
"""

import os
import sys
import traceback
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def run_migration_with_output():
    """Run migration with detailed output"""
    try:
        print("🚀 Starting migration process...")
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        print(f"🔧 Supabase URL: {'✅ Set' if supabase_url else '❌ Missing'}")
        print(f"🔧 Supabase Key: {'✅ Set' if supabase_key else '❌ Missing'}")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        print("🔄 Adding sender information columns to bank_transactions table...")
        
        # SQL to add sender columns
        sql_commands = [
            """
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS sender_name TEXT;
            """,
            """
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS narration TEXT;
            """,
            """
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS bank_name TEXT;
            """,
            """
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS bank_code TEXT;
            """,
            """
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS account_number TEXT;
            """
        ]
        
        for i, sql in enumerate(sql_commands, 1):
            try:
                print(f"🔄 Executing SQL command {i}/5...")
                print(f"📝 SQL: {sql.strip()}")
                
                # Try using PostgreSQL function
                result = supabase.rpc("execute_sql", {"sql": sql}).execute()
                print(f"✅ SQL command {i}/5 completed successfully")
                print(f"📊 Result: {result}")
                
            except Exception as e:
                print(f"⚠️ SQL command {i}/5 error: {e}")
                print(f"📊 Full error: {traceback.format_exc()}")
                
                # Try alternative approach
                try:
                    print(f"🔄 Trying alternative approach for command {i}/5...")
                    # This might not work but let's try
                    result = supabase.postgrest.rpc("execute_sql", {"sql": sql}).execute()
                    print(f"✅ Alternative approach worked for command {i}/5")
                except Exception as e2:
                    print(f"❌ Alternative approach also failed: {e2}")
        
        print("✅ Migration process completed!")
        
        # Test if columns exist
        print("\n🔍 Testing if columns were added...")
        test_columns = ['sender_name', 'narration', 'bank_name', 'bank_code', 'account_number']
        
        for column in test_columns:
            try:
                result = supabase.table('bank_transactions').select(column).limit(1).execute()
                print(f"✅ {column} - EXISTS")
            except Exception as e:
                print(f"❌ {column} - MISSING: {str(e)[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        print(f"📊 Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    run_migration_with_output()
