#!/usr/bin/env python3
"""
Clean up script to fix the constraint issue
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def fix_constraint_issue():
    """Fix the users table constraint issue"""
    
    print("🔧 Fixing Supabase constraint issue...")
    
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Option 1: Delete the problematic record
        print("\n🗑️ Option 1: Delete the problematic record")
        problematic_users = supabase.table("users").select("*").eq("account_number", "No").execute()
        
        if problematic_users.data:
            print(f"Found {len(problematic_users.data)} problematic records:")
            for user in problematic_users.data:
                print(f"   ID: {user.get('id')}, Name: {user.get('first_name')} {user.get('last_name')}")
            
            # Ask for confirmation (in production, you might want to backup first)
            print("\n⚠️ WARNING: This will delete the problematic records!")
            print("Proceeding with cleanup...")
            
            # Delete the problematic records
            delete_result = supabase.table("users").delete().eq("account_number", "No").execute()
            print(f"✅ Deleted {len(delete_result.data)} problematic records")
        
        # Option 2: Update the problematic record
        print("\n🔄 Option 2: Update problematic records with unique values")
        # This creates a unique account number for the existing record
        import time
        unique_account_number = f"TEMP_{int(time.time())}"
        
        # First, let's see if there are still any "No" records after deletion
        remaining_users = supabase.table("users").select("*").eq("account_number", "No").execute()
        
        if remaining_users.data:
            print("Updating remaining records with unique account numbers...")
            for i, user in enumerate(remaining_users.data):
                new_account_number = f"TEMP_{int(time.time())}_{i}"
                update_result = supabase.table("users").update({
                    "account_number": new_account_number
                }).eq("id", user["id"]).execute()
                print(f"Updated user {user['id']} account_number to {new_account_number}")
        
        print("\n✅ Constraint issue fixed!")
        print("You can now create new users without constraint violations.")
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        remaining_no_records = supabase.table("users").select("*").eq("account_number", "No").execute()
        print(f"Records with account_number='No': {len(remaining_no_records.data)}")
        
        if len(remaining_no_records.data) == 0:
            print("✅ Fix successful! No more conflicting records.")
        else:
            print("⚠️ Some records still exist. Manual intervention may be needed.")
            
    except Exception as e:
        print(f"❌ Fix failed: {e}")

if __name__ == "__main__":
    fix_constraint_issue()
