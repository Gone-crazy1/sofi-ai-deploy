#!/usr/bin/env python3
"""
Fix truncated account names in existing virtual accounts
"""
import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def fix_existing_account_names():
    """Fix truncated account names by extracting full names from account references"""
    
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials!")
            return False
            
        supabase = create_client(supabase_url, supabase_key)
        
        # Get all virtual accounts
        print("🔍 Checking virtual accounts for truncated names...")
        result = supabase.table("virtual_accounts").select("*").execute()
        
        if not result.data:
            print("📭 No virtual accounts found!")
            return True
            
        fixed_count = 0
        for account in result.data:
            account_id = account.get('id')
            current_name = account.get('accountname', '')
            account_ref = account.get('accountreference', '')
            
            print(f"\n🏦 Account ID {account_id}:")
            print(f"   Current Name: '{current_name}'")
            print(f"   Reference: '{account_ref}'")
            
            # Extract full name from reference pattern: FirstName_LastName_Number_Timestamp
            if account_ref:
                # Split by underscore and take first two parts as first and last name
                ref_parts = account_ref.split('_')
                if len(ref_parts) >= 2:
                    first_name = ref_parts[0]
                    last_name = ref_parts[1]
                    full_name = f"{first_name} {last_name}"
                    
                    # Check if current name is truncated (less than full name)
                    if len(current_name) < len(full_name) and current_name != full_name:
                        print(f"   ✅ Fixing: '{current_name}' → '{full_name}'")
                        
                        # Update the account name
                        update_result = supabase.table("virtual_accounts").update({
                            "accountname": full_name
                        }).eq("id", account_id).execute()
                        
                        if update_result.data:
                            print(f"   ✅ Successfully updated account name!")
                            fixed_count += 1
                        else:
                            print(f"   ❌ Failed to update account name")
                    else:
                        print(f"   ✅ Name is already correct: '{current_name}'")
                else:
                    print(f"   ⚠️  Cannot extract name from reference format")
            else:
                print(f"   ⚠️  No account reference found")
        
        print(f"\n🎉 Summary: Fixed {fixed_count} account names!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing account names: {e}")
        return False

def verify_fixes():
    """Verify that the fixes were applied correctly"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        print("\n🔍 Verifying account name fixes...")
        result = supabase.table("virtual_accounts").select("*").execute()
        
        for account in result.data:
            print(f"\n📋 Account {account.get('id')}:")
            print(f"   👤 Name: {account.get('accountname')}")
            print(f"   📱 Number: {account.get('accountnumber')}")
            print(f"   🏦 Bank: {account.get('bankname')}")
            print(f"   🔗 Reference: {account.get('accountreference')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying fixes: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Starting Account Name Fix Process...")
    
    success = fix_existing_account_names()
    
    if success:
        verify_fixes()
        print("\n✅ Account name fix process completed successfully!")
    else:
        print("\n❌ Account name fix process failed!")
