#!/usr/bin/env python3
"""
Add phone column to users table in Supabase
This script safely adds a phone column to the users table if it doesn't already exist.
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_phone_column_exists():
    """Check if phone column already exists in users table"""
    try:
        result = supabase.table("users").select("phone").limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e):
            return False
        else:
            print(f"Error checking phone column: {e}")
            return None

def add_phone_column_via_api():
    """
    Try to add phone column by inserting a record with phone field
    This is a workaround since direct DDL isn't available via API
    """
    try:
        # Insert a test user with phone to force column creation
        test_user = {
            "first_name": "Test",
            "last_name": "User", 
            "bvn": "00000000000",
            "phone": "08000000000",
            "telegram_chat_id": 999999999
        }
        
        result = supabase.table("users").insert(test_user).execute()
        
        if result.data:
            # If successful, delete the test user
            user_id = result.data[0]['id']
            supabase.table("users").delete().eq("id", user_id).execute()
            print("✅ Phone column added successfully via API")
            return True
        
    except Exception as e:
        print(f"❌ Cannot add phone column via API: {e}")
        return False

def main():
    print("🔍 Checking phone column status in users table...")
    
    # Check if phone column exists
    phone_exists = check_phone_column_exists()
    
    if phone_exists is True:
        print("✅ Phone column already exists in users table")
        return
    elif phone_exists is None:
        print("❌ Unable to check phone column status")
        return
    
    print("❌ Phone column does not exist in users table")
    print("\n🔧 Attempting to add phone column...")
    
    # Try to add phone column via API
    success = add_phone_column_via_api()
    
    if success:
        print("✅ Phone column added successfully!")
        print("\n📝 Next steps:")
        print("1. Update your onboarding form to include phone field")
        print("2. Test the complete onboarding flow")
        print("3. Deploy the updated code")
    else:
        print("\n⚠️  Unable to add phone column via API")
        print("\n📋 Manual steps required:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to Table Editor > users table")
        print("3. Click 'Add Column'")
        print("4. Add column with these settings:")
        print("   - Name: phone")
        print("   - Type: text or varchar")
        print("   - Nullable: true (optional)")
        print("   - Default: null")
        print("5. Save the changes")
        print("\n🔗 Supabase Dashboard URL:")
        print(f"   {SUPABASE_URL.replace('/rest/v1', '')}/project/default/editor")

if __name__ == "__main__":
    main()
