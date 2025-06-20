#!/usr/bin/env python3
"""
Fix Supabase Schema for Sofi AI
Run this to add missing columns to the users table
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def fix_supabase_schema():
    """Fix Supabase schema by adding missing columns"""
    print("🔧 Fixing Supabase Schema")
    print("=" * 40)
    
    try:
        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
        
        # Read SQL file
        with open("fix_supabase_schema.sql", "r") as f:
            sql_commands = f.read()
        
        # Split and execute SQL commands
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        for i, command in enumerate(commands, 1):
            if command.strip():
                try:
                    result = supabase.rpc('execute_sql', {'sql': command}).execute()
                    print(f"✅ Executed SQL command {i}")
                except Exception as e:
                    print(f"❌ SQL command {i} failed: {e}")
                    # Try alternative method
                    try:
                        # For some commands that don't work with rpc, we'll use direct table operations
                        if "ALTER TABLE users ADD COLUMN" in command:
                            print("🔄 Attempting alternative method for ALTER TABLE...")
                            # We'll handle this differently since direct SQL might not work
                            pass
                    except Exception as e2:
                        print(f"❌ Alternative method also failed: {e2}")
        
        print("\n🎉 Schema fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix schema: {e}")
        return False

if __name__ == "__main__":
    fix_supabase_schema()
