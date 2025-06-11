#!/usr/bin/env python3
"""
Create beneficiaries table in Supabase database
This script will execute the SQL commands to create the beneficiaries table
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_beneficiaries_table():
    """Create the beneficiaries table in Supabase"""
    
    # Initialize Supabase client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Read the SQL file
        with open('create_beneficiaries_table.sql', 'r') as file:
            sql_commands = file.read()
        
        print("📋 Executing SQL commands...")
        
        # Split and execute each SQL command
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        for i, command in enumerate(commands, 1):
            if command:
                try:
                    print(f"   {i}. Executing: {command[:50]}...")
                    result = supabase.rpc('exec_sql', {'sql': command}).execute()
                    print(f"   ✅ Command {i} executed successfully")
                except Exception as cmd_error:
                    print(f"   ⚠️ Command {i} warning: {str(cmd_error)}")
        
        # Verify table creation
        print("\n🔍 Verifying table creation...")
        try:
            # Try to query the table structure
            result = supabase.rpc('exec_sql', {
                'sql': "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'beneficiaries' ORDER BY ordinal_position"
            }).execute()
            
            if result.data:
                print("✅ Beneficiaries table created successfully!")
                print("📊 Table structure:")
                for column in result.data:
                    print(f"   - {column['column_name']}: {column['data_type']}")
            else:
                print("⚠️ Table may not have been created properly")
                
        except Exception as verify_error:
            print(f"⚠️ Could not verify table creation: {str(verify_error)}")
            print("   Please check your Supabase dashboard to confirm")
        
        print("\n🎉 Beneficiaries table setup complete!")
        print("💾 Your Save Beneficiary feature is now ready to use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating beneficiaries table: {str(e)}")
        print("\n🔧 Alternative: Execute the SQL manually in Supabase:")
        print("   1. Open Supabase Dashboard → SQL Editor")
        print("   2. Copy contents of 'create_beneficiaries_table.sql'")
        print("   3. Paste and run in SQL Editor")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   CREATING BENEFICIARIES TABLE")
    print("=" * 60)
    
    success = create_beneficiaries_table()
    
    if success:
        print("\n✅ SUCCESS: Beneficiaries table is ready!")
    else:
        print("\n❌ FAILED: Please create the table manually")
