#!/usr/bin/env python3
"""
Check RLS Policies and Create Compatible User Registration
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_rls_and_fix():
    """Check RLS policies and create compatible registration"""
    
    print("🔍 Checking RLS Policies and User Registration")
    print("=" * 55)
    
    try:
        # Use regular key first
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try different approaches to insert user
        print("🔄 Testing different user registration approaches...")
        
        # Approach 1: Minimal user data
        print("\n📝 Approach 1: Minimal user data")
        try:
            minimal_user = {
                "telegram_chat_id": f"approach1_{int(datetime.now().timestamp())}",
                "full_name": "Test User One"
            }
            
            result = supabase.table("users").insert(minimal_user).execute()
            if result.data:
                print("✅ Minimal user insert successful!")
                user_id = result.data[0]["telegram_chat_id"]
                supabase.table("users").delete().eq("telegram_chat_id", user_id).execute()
                return True
            else:
                print("❌ Minimal user insert failed")
        except Exception as e:
            print(f"❌ Minimal user failed: {e}")
        
        # Approach 2: User with UUID
        print("\n📝 Approach 2: User with generated UUID")
        try:
            user_with_uuid = {
                "id": str(uuid.uuid4()),
                "telegram_chat_id": f"approach2_{int(datetime.now().timestamp())}",
                "full_name": "Test User Two"
            }
            
            result = supabase.table("users").insert(user_with_uuid).execute()
            if result.data:
                print("✅ UUID user insert successful!")
                user_id = result.data[0]["telegram_chat_id"]
                supabase.table("users").delete().eq("telegram_chat_id", user_id).execute()
                return True
            else:
                print("❌ UUID user insert failed")
        except Exception as e:
            print(f"❌ UUID user failed: {e}")
        
        # Approach 3: Try upsert instead of insert
        print("\n📝 Approach 3: Using upsert instead of insert")
        try:
            upsert_user = {
                "telegram_chat_id": f"approach3_{int(datetime.now().timestamp())}",
                "full_name": "Test User Three",
                "phone": "+1234567890",
                "email": "test3@example.com"
            }
            
            result = supabase.table("users").upsert(upsert_user).execute()
            if result.data:
                print("✅ Upsert user successful!")
                user_id = result.data[0]["telegram_chat_id"]
                supabase.table("users").delete().eq("telegram_chat_id", user_id).execute()
                return True
            else:
                print("❌ Upsert user failed")
        except Exception as e:
            print(f"❌ Upsert user failed: {e}")
        
        # Approach 4: Check if we need auth
        print("\n📝 Approach 4: Check if authentication is required")
        try:
            # Check if we can at least read from users table
            result = supabase.table("users").select("telegram_chat_id").limit(1).execute()
            print(f"✅ Can read users table: {len(result.data) if result.data else 0} records")
            
            # Maybe RLS requires specific user context
            print("ℹ️ RLS may require user authentication context")
            
        except Exception as e:
            print(f"❌ Cannot even read users table: {e}")
        
        print("\n📋 Solutions:")
        print("=" * 30)
        print("1. 🔧 Disable RLS in Supabase Dashboard:")
        print("   - Go to Supabase Dashboard > Authentication > RLS")
        print("   - Disable RLS for 'users' and 'virtual_accounts' tables")
        print("\n2. 🔑 Create RLS policy that allows inserts:")
        print("   - Create policy: 'Allow all inserts' for 'users' table")
        print("   - Expression: true")
        print("\n3. 🔐 Use service role key:")
        print("   - Get service_role key from Supabase Dashboard")
        print("   - Add SUPABASE_SERVICE_KEY to .env file")
        
        return False
        
    except Exception as e:
        print(f"❌ RLS check failed: {e}")
        return False

if __name__ == "__main__":
    success = check_rls_and_fix()
    if not success:
        print("\n⚠️ Manual intervention required in Supabase Dashboard")
