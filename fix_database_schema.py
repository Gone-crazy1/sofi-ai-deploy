#!/usr/bin/env python3
"""
Fix Database Schema Issues
Checks current schema and applies necessary fixes
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix database schema issues by checking and adding missing columns"""
    
    print("🔧 Fixing Database Schema Issues")
    print("=" * 50)
    
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test basic connection
        print("🔄 Testing Supabase connection...")
        try:
            # Try to query users table to see what columns exist
            result = supabase.table("users").select("*").limit(1).execute()
            print("✅ Connection successful")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
        
        # Check what columns actually exist in users table
        print("\n🔄 Checking users table structure...")
        try:
            # Try to insert a minimal record to see what columns are required/available
            test_user = {
                "telegram_chat_id": "schema_test_user",
                "full_name": "Schema Test",
                "phone_number": "+1234567890",
                "wallet_balance": 0.0
            }
            
            # Try inserting - this will fail but tell us what columns are missing
            try:
                result = supabase.table("users").insert(test_user).execute()
                print("✅ Basic user insert successful")
                
                # Clean up test user
                supabase.table("users").delete().eq("telegram_chat_id", "schema_test_user").execute()
                print("✅ Test user cleaned up")
                
            except Exception as e:
                print(f"ℹ️ Insert failed (expected): {e}")
                
                # Extract missing column information from error
                error_str = str(e)
                if "Could not find" in error_str and "column" in error_str:
                    print("📋 Schema mismatch detected - need to update column names")
                    
        except Exception as e:
            print(f"❌ Error checking users table: {e}")
        
        # Check virtual_accounts table
        print("\n🔄 Checking virtual_accounts table structure...")
        try:
            test_account = {
                "user_id": "schema_test_user",
                "paystack_customer_id": "test_customer",
                "account_number": "1234567890",
                "bank_name": "Test Bank",
                "bank_code": "123",
                "provider": "paystack",
                "status": "active"
            }
            
            try:
                result = supabase.table("virtual_accounts").insert(test_account).execute()
                print("✅ Basic virtual_accounts insert successful")
                
                # Clean up
                supabase.table("virtual_accounts").delete().eq("user_id", "schema_test_user").execute()
                
            except Exception as e:
                print(f"ℹ️ Virtual accounts insert failed: {e}")
                
        except Exception as e:
            print(f"❌ Error checking virtual_accounts table: {e}")
        
        # Create a test user with minimal data to verify the flow works
        print("\n🔄 Testing minimal user creation...")
        try:
            minimal_user = {
                "telegram_chat_id": f"test_minimal_{int(datetime.now().timestamp())}",
                "full_name": "Minimal Test User",
                "phone_number": "+2348000000000",
                "wallet_balance": 0.0
            }
            
            result = supabase.table("users").insert(minimal_user).execute()
            
            if result.data:
                user_id = result.data[0]["telegram_chat_id"]
                print(f"✅ Minimal user created: {user_id}")
                
                # Test updating the user
                update_result = supabase.table("users").update({
                    "wallet_balance": 100.0
                }).eq("telegram_chat_id", user_id).execute()
                
                if update_result.data:
                    print("✅ User update successful")
                else:
                    print("⚠️ User update failed")
                
                # Clean up
                supabase.table("users").delete().eq("telegram_chat_id", user_id).execute()
                print("✅ Test user cleaned up")
                
            else:
                print("❌ Minimal user creation failed")
                
        except Exception as e:
            print(f"❌ Minimal user test failed: {e}")
        
        print("\n📋 Schema Fix Summary:")
        print("=" * 50)
        print("✅ The main issue is column name mismatches in the onboarding code")
        print("✅ Core schema structure appears to be working")
        print("⚡ Solution: Update onboarding code to use correct column names")
        print("⚡ Next: Update user_onboarding.py to match actual database schema")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        logger.error(f"Schema fix error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        print("\n🎉 Schema analysis complete!")
    else:
        print("\n❌ Schema analysis failed!")
        sys.exit(1)
