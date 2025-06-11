#!/usr/bin/env python3
"""
Verify that the phone column was successfully added to the users table
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_phone_column():
    """Verify the phone column exists in the users table"""
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Missing Supabase credentials")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test inserting a user with phone column
        test_user = {
            "first_name": "Test",
            "last_name": "User", 
            "bvn": "12345678901",
            "phone": "+2348123456789",
            "telegram_chat_id": 999999999
        }
        
        print("🔍 Testing phone column by inserting test user...")
        result = supabase.table("users").insert(test_user).execute()
        
        if result.data:
            print("✅ Phone column exists and accepts data!")
            print(f"📝 Inserted test user: {result.data[0]}")
            
            # Clean up - delete the test user
            user_id = result.data[0]['id']
            supabase.table("users").delete().eq("id", user_id).execute()
            print("🧹 Cleaned up test user")
            return True
        else:
            print("❌ Failed to insert test user")
            return False
            
    except Exception as e:
        if "phone" in str(e).lower():
            print("❌ Phone column does not exist or has issues")
            print(f"Error: {e}")
            return False
        else:
            print(f"❌ Other error: {e}")
            return False

if __name__ == "__main__":
    print("=== Verifying Phone Column ===")
    success = verify_phone_column()
    if success:
        print("\n✅ Phone column verification successful!")
        print("✅ Ready to update main.py to include phone field")
    else:
        print("\n❌ Phone column verification failed!")
        print("❌ Please check the SQL command execution")
