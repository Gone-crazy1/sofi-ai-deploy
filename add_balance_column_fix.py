#!/usr/bin/env python3
"""
Add balance column to virtual_accounts table in Supabase
This script safely adds a balance column to the virtual_accounts table if it doesn't already exist.
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_balance_column_exists():
    """Check if balance column already exists in virtual_accounts table"""
    try:
        result = supabase.table("virtual_accounts").select("balance").limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e) or "column" in str(e).lower():
            return False
        else:
            print(f"Error checking balance column: {e}")
            return None

def add_balance_column_via_update():
    """
    Try to add balance column by updating existing records with balance field
    This is a workaround since direct DDL isn't available via API
    """
    try:
        # First, get all existing virtual accounts
        existing_accounts = supabase.table("virtual_accounts").select("id").execute()
        
        if not existing_accounts.data:
            print("No existing virtual accounts found")
            return False
        
        # Try to update the first record with a balance field
        first_account_id = existing_accounts.data[0]['id']
        
        result = supabase.table("virtual_accounts").update({
            "balance": 0.0
        }).eq("id", first_account_id).execute()
        
        if result.data:
            print("✅ Balance column added successfully via update")
            
            # Set all other accounts to have 0.0 balance
            for account in existing_accounts.data[1:]:
                supabase.table("virtual_accounts").update({
                    "balance": 0.0
                }).eq("id", account['id']).execute()
            
            print(f"✅ Updated {len(existing_accounts.data)} virtual accounts with balance = 0.0")
            return True
        
    except Exception as e:
        print(f"❌ Cannot add balance column via update: {e}")
        return False

def add_balance_column_via_insert():
    """
    Try to add balance column by inserting a test record with balance field
    """
    try:
        # Insert a test virtual account with balance to force column creation
        test_account = {
            "accountnumber": "0000000000",
            "accountname": "Test Account",
            "bankname": "Test Bank",
            "accountreference": "TEST_REF_BALANCE",
            "telegram_chat_id": "999999999",
            "balance": 0.0
        }
        
        result = supabase.table("virtual_accounts").insert(test_account).execute()
        
        if result.data:
            # If successful, delete the test account
            account_id = result.data[0]['id']
            supabase.table("virtual_accounts").delete().eq("id", account_id).execute()
            print("✅ Balance column added successfully via insert")
            return True
        
    except Exception as e:
        print(f"❌ Cannot add balance column via insert: {e}")
        return False

def verify_balance_column():
    """Verify that the balance column is working properly"""
    try:
        # Try to select balance column
        result = supabase.table("virtual_accounts").select("id, balance").limit(1).execute()
        if result.data:
            print("✅ Balance column verification successful")
            return True
        else:
            print("⚠️  No data found to verify balance column")
            return True  # Column exists but no data
    except Exception as e:
        print(f"❌ Balance column verification failed: {e}")
        return False

def main():
    print("🔍 ADDING BALANCE COLUMN TO VIRTUAL_ACCOUNTS TABLE")
    print("=" * 60)
    
    # Check if balance column already exists
    balance_exists = check_balance_column_exists()
    
    if balance_exists is True:
        print("✅ Balance column already exists in virtual_accounts table")
        
        # Verify it works
        if verify_balance_column():
            print("✅ Balance column is working correctly")
        else:
            print("❌ Balance column exists but has issues")
        return
    elif balance_exists is None:
        print("❌ Unable to check balance column status")
        return
    
    print("❌ Balance column does not exist in virtual_accounts table")
    print("\n🔧 Attempting to add balance column...")
    
    # Try multiple methods to add the balance column
    methods = [
        ("Insert Method", add_balance_column_via_insert),
        ("Update Method", add_balance_column_via_update),
    ]
    
    success = False
    for method_name, method_func in methods:
        print(f"\n📋 Trying {method_name}...")
        if method_func():
            success = True
            break
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Balance column added successfully!")
        
        # Verify the column works
        if verify_balance_column():
            print("✅ Balance column verification passed")
        
        print("\n📝 Next steps:")
        print("1. The balance system should now work correctly")
        print("2. Users can check their balance with 'balance' command")
        print("3. Balance will show 0.0 until funding occurs")
        print("4. Implement Monnify balance API calls for real-time balance")
        
    else:
        print("\n⚠️  Unable to add balance column via API methods")
        print("\n📋 Manual steps required:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to Table Editor > virtual_accounts table")
        print("3. Click 'Add Column'")
        print("4. Add column with these settings:")
        print("   - Name: balance")
        print("   - Type: numeric or decimal")
        print("   - Default: 0.0")
        print("   - Nullable: false")
        print("5. Save the changes")
        print("\n🔗 Supabase Dashboard URL:")
        print(f"   {SUPABASE_URL.replace('/rest/v1', '')}/project/default/editor")
        
        print("\n💡 Alternative: Run this SQL in Supabase SQL Editor:")
        print("   ALTER TABLE virtual_accounts ADD COLUMN balance DECIMAL(15,2) DEFAULT 0.0;")

if __name__ == "__main__":
    main()
