"""
Create beneficiaries table for Sofi AI
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def create_beneficiaries_table():
    """Create the beneficiaries table in Supabase"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Read SQL file
        with open("create_beneficiaries_table.sql", "r") as f:
            sql_commands = f.read()
        
        print("🔨 Creating beneficiaries table...")
        
        # Execute SQL (Note: Supabase Python client doesn't directly support DDL)
        # You may need to run this SQL manually in your Supabase dashboard
        print("📋 SQL to execute:")
        print(sql_commands)
        print("\n" + "="*50)
        print("🚨 IMPORTANT: Please run the above SQL in your Supabase SQL editor")
        print("   or use the database management interface")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_beneficiaries_table()
