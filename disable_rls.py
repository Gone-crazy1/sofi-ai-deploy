#!/usr/bin/env python3
"""
Disable Row Level Security for Testing
Uses direct SQL execution via Supabase
"""

import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def disable_rls():
    """Disable RLS on all tables for testing"""
    
    print("🔧 Disabling Row Level Security for Testing")
    print("=" * 50)
    
    try:
        # Initialize Supabase client with service role key (has admin privileges)
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            print("❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Try direct SQL approach using rpc
        print("🔄 Attempting to disable RLS...")
        
        try:
            # Try using rpc to execute SQL
            result = supabase.rpc('exec_sql', {'sql': 'ALTER TABLE users DISABLE ROW LEVEL SECURITY;'}).execute()
            print("✅ RLS disabled on users table")
        except Exception as e:
            print(f"⚠️ Could not disable RLS via rpc: {e}")
            
            # Alternative: Try to create a test user to check if RLS is the issue
            print("🔄 Testing direct user insert...")
            
            test_user = {
                "telegram_chat_id": "rls_test_user",
                "full_name": "RLS Test",
                "phone": "+1234567890",
                "email": "rls@test.com",
                "paystack_customer_code": "test_code",
                "wallet_balance": 0.0
            }
            
            try:
                insert_result = supabase.table("users").insert(test_user).execute()
                if insert_result.data:
                    print("✅ User insert successful - RLS may not be the issue")
                    # Clean up
                    supabase.table("users").delete().eq("telegram_chat_id", "rls_test_user").execute()
                else:
                    print("❌ User insert failed even with service key")
            except Exception as insert_error:
                print(f"❌ User insert failed: {insert_error}")
        
        print("\n📋 RLS Status Check:")
        print("=" * 50)
        
        # Check if we can insert a test record
        try:
            minimal_user = {
                "telegram_chat_id": f"test_minimal_{int(asyncio.get_event_loop().time())}",
                "full_name": "Minimal Test User",
                "phone": "+2348000000000",
                "email": "minimal@test.com",
                "paystack_customer_code": "TEST_CODE",
                "wallet_balance": 0.0
            }
            
            result = supabase.table("users").insert(minimal_user).execute()
            
            if result.data:
                user_id = result.data[0]["telegram_chat_id"]
                print(f"✅ Successfully inserted user: {user_id}")
                
                # Clean up
                supabase.table("users").delete().eq("telegram_chat_id", user_id).execute()
                print("✅ Test user cleaned up")
                
                return True
            else:
                print("❌ Failed to insert test user")
                return False
                
        except Exception as e:
            print(f"❌ Test user insert failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ RLS disable failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(disable_rls())
    if success:
        print("\n🎉 Database is ready for user registration!")
    else:
        print("\n❌ Database still has issues - check Supabase dashboard settings")
