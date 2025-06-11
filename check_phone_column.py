#!/usr/bin/env python3
"""
Check if we should add a phone column to users table or modify the approach
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Checking users table structure...")

# List all possible phone-related column names
phone_columns = [
    "phone", "phone_number", "mobile", "mobile_number", 
    "telephone", "contact", "contact_number"
]

for column in phone_columns:
    try:
        result = supabase.table("users").select(column).limit(1).execute()
        print(f"✅ Phone column '{column}' exists")
    except Exception as e:
        if "does not exist" in str(e):
            print(f"❌ Phone column '{column}' does not exist")
        else:
            print(f"❓ Error testing '{column}': {e}")

print("\n📋 Testing if we can add phone to an existing user record...")

# Get an existing user to see the full structure
try:
    result = supabase.table("users").select("*").limit(1).execute()
    if result.data:
        existing_user = result.data[0]
        print(f"Existing user structure: {list(existing_user.keys())}")
        print(f"Sample user: {existing_user}")
        
        # Try to update with phone column to see if it's allowed
        user_id = existing_user['id']
        try:
            update_result = supabase.table("users").update({"phone": "08123456789"}).eq("id", user_id).execute()
            print("✅ Successfully added phone column to existing user!")
            print(f"Update result: {update_result.data}")
            
            # Clean up - remove the phone field
            try:
                supabase.table("users").update({"phone": None}).eq("id", user_id).execute()
                print("🧹 Cleaned up test phone data")
            except:
                pass
                
        except Exception as update_error:
            print(f"❌ Cannot add phone column: {update_error}")
            
    else:
        print("No existing users found")
        
except Exception as e:
    print(f"Error getting users: {e}")

print("\n💡 RECOMMENDATIONS:")
print("1. If phone is critical for your app:")
print("   - Add phone column to users table via Supabase dashboard")
print("   - Or modify code to not require phone")
print("2. For immediate fix:")
print("   - Remove phone requirement from API endpoint")
print("   - Store phone in a separate user_profiles table")
print("   - Use existing fields creatively")
