#!/usr/bin/env python3
"""
Check the actual data type of the users table id column
"""

import os
from supabase import create_client, Client

def check_users_table_schema():
    # Initialize Supabase client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return
    
    supabase: Client = create_client(url, key)
    
    try:
        # Query information_schema to get column details
        response = supabase.rpc('sql', {
            'query': """
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
        }).execute()
        
        if response.data:
            print("✅ Users table schema:")
            for column in response.data:
                print(f"  - {column['column_name']}: {column['data_type']} (nullable: {column['is_nullable']})")
                if column['column_default']:
                    print(f"    Default: {column['column_default']}")
        else:
            print("❌ Could not retrieve users table schema")
            
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_users_table_schema()
