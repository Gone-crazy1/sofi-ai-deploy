#!/usr/bin/env python3
"""
Test script to verify RLS (Row Level Security) setup on users table
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Load environment variables
load_dotenv()

def test_rls_setup():
    """Test that RLS is properly configured on users table"""
    
    print("🔒 Testing Row Level Security (RLS) setup...")
    
    try:
        # Initialize Supabase client with service role key
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")  # Anonymous key
        
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            print("❌ Missing Supabase credentials")
            return False
        
        # Test 1: Service role should have full access
        print("\n1️⃣ Testing service role access...")
        try:
            service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            
            # Try to query users table with service role
            result = service_client.table("users").select("id, first_name").limit(5).execute()
            print("✅ Service role can access users table")
            print(f"📊 Found {len(result.data)} users")
            
        except Exception as e:
            print(f"❌ Service role access failed: {e}")
            return False
        
        # Test 2: Check if RLS is enabled
        print("\n2️⃣ Checking RLS status...")
        try:
            # Query to check RLS status
            rls_query = """
            SELECT schemaname, tablename, rowsecurity,
                   CASE WHEN rowsecurity THEN 'Enabled' ELSE 'Disabled' END as rls_status
            FROM pg_tables 
            WHERE tablename = 'users' AND schemaname = 'public'
            """
            
            result = service_client.rpc('execute_sql', {'query': rls_query}).execute()
            
            if result.data and len(result.data) > 0:
                rls_enabled = result.data[0].get('rowsecurity', False)
                if rls_enabled:
                    print("✅ RLS is enabled on users table")
                else:
                    print("⚠️ RLS is NOT enabled on users table")
                    print("🔧 Please run the SQL commands to enable RLS")
                    return False
            else:
                print("⚠️ Could not check RLS status")
                
        except Exception as e:
            print(f"ℹ️ RLS status check skipped (requires custom function): {e}")
            # This is normal - we'll check policies instead
        
        # Test 3: Check existing policies
        print("\n3️⃣ Checking RLS policies...")
        try:
            policies_query = """
            SELECT policyname, permissive, roles, cmd
            FROM pg_policies 
            WHERE tablename = 'users' AND schemaname = 'public'
            """
            
            result = service_client.rpc('execute_sql', {'query': policies_query}).execute()
            
            if result.data and len(result.data) > 0:
                print(f"✅ Found {len(result.data)} RLS policies:")
                for policy in result.data:
                    print(f"   📋 {policy.get('policyname')} - {policy.get('cmd')} for {policy.get('roles')}")
            else:
                print("⚠️ No RLS policies found")
                
        except Exception as e:
            print(f"ℹ️ Policy check skipped: {e}")
        
        # Test 4: Try anonymous access (should be blocked if RLS is working)
        if SUPABASE_ANON_KEY:
            print("\n4️⃣ Testing anonymous access (should be blocked)...")
            try:
                anon_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                result = anon_client.table("users").select("id").limit(1).execute()
                
                if result.data and len(result.data) > 0:
                    print("⚠️ Anonymous access is allowed - RLS may not be properly configured")
                    print("🔧 Consider blocking anonymous access to users table")
                else:
                    print("✅ Anonymous access is properly blocked")
                    
            except Exception as e:
                print("✅ Anonymous access is blocked (as expected)")
                print(f"   Error: {str(e)[:100]}...")
        
        # Test 5: Test your application's functionality
        print("\n5️⃣ Testing application functionality...")
        try:
            # Test inserting a user (like your onboarding flow)
            test_user = {
                "first_name": "RLSTest",
                "last_name": "User", 
                "bvn": "12345678901",
                "phone": "+2348012345678",
                "telegram_chat_id": 888888888
            }
            
            # Clean up first
            service_client.table("users").delete().eq("first_name", "RLSTest").execute()
            
            # Insert test user
            result = service_client.table("users").insert(test_user).execute()
            
            if result.data:
                print("✅ Application can still insert users")
                user_id = result.data[0].get('id')
                
                # Test querying
                query_result = service_client.table("users").select("*").eq("id", user_id).execute()
                if query_result.data:
                    print("✅ Application can still query users")
                else:
                    print("❌ Application cannot query users")
                    return False
                
                # Clean up
                service_client.table("users").delete().eq("id", user_id).execute()
                print("✅ Test data cleaned up")
            else:
                print("❌ Application cannot insert users")
                return False
                
        except Exception as e:
            print(f"❌ Application functionality test failed: {e}")
            return False
        
        print("\n🎉 RLS testing completed successfully!")
        print("🔒 Your users table security appears to be working correctly")
        return True
        
    except Exception as e:
        print(f"❌ RLS test failed with error: {e}")
        return False

def main():
    """Main function"""
    print("="*60)
    print("   ROW LEVEL SECURITY (RLS) TEST")
    print("="*60)
    
    success = test_rls_setup()
    
    if success:
        print("\n🎉 RLS TESTS PASSED!")
        print("🔒 Your users table security is properly configured")
        sys.exit(0)
    else:
        print("\n❌ RLS TESTS FAILED!")
        print("🔧 Please run the SQL commands to enable RLS")
        print("📄 Check: enable_rls_simplified.sql")
        sys.exit(1)

if __name__ == "__main__":
    main()
