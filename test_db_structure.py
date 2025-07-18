#!/usr/bin/env python3
"""
Simple database test to check what's actually in Supabase
"""

import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def test_supabase_connection():
    """Test basic Supabase connection and table structure"""
    print("🔍 Testing Supabase Connection...")
    
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        print("✅ Supabase client created")
        
        # Test 1: Check if beneficiaries table exists
        print("\n📝 Test 1: Check beneficiaries table...")
        try:
            result = supabase.table("beneficiaries").select("*").limit(5).execute()
            print(f"✅ Beneficiaries table exists, found {len(result.data)} records")
            if result.data:
                print(f"📥 Sample record structure: {list(result.data[0].keys())}")
                print(f"📥 Sample user_id type: {type(result.data[0].get('user_id'))}")
        except Exception as e:
            print(f"❌ Beneficiaries table error: {e}")
        
        # Test 2: Try to insert with TEXT user_id
        print("\n📝 Test 2: Try insert with TEXT user_id...")
        try:
            test_data = {
                "user_id": "test_text_123",
                "beneficiary_name": "TEST USER",
                "account_number": "1234567890",
                "bank_code": "TEST",
                "bank_name": "TEST BANK",
                "nickname": "test"
            }
            
            result = supabase.table("beneficiaries").insert(test_data).execute()
            if result.data:
                print("✅ Insert with TEXT user_id successful")
                # Clean up
                supabase.table("beneficiaries").delete().eq("user_id", "test_text_123").execute()
            else:
                print("❌ Insert failed but no error thrown")
        except Exception as e:
            print(f"❌ Insert failed: {e}")
        
        # Test 3: Check users table structure
        print("\n📝 Test 3: Check users table...")
        try:
            result = supabase.table("users").select("id,telegram_chat_id").limit(3).execute()
            print(f"✅ Users table exists, found {len(result.data)} records")
            if result.data:
                sample_user = result.data[0]
                print(f"📥 Sample user id type: {type(sample_user.get('id'))}")
                print(f"📥 Sample telegram_chat_id type: {type(sample_user.get('telegram_chat_id'))}")
                print(f"📥 Sample user: id={sample_user.get('id')}, telegram_chat_id={sample_user.get('telegram_chat_id')}")
        except Exception as e:
            print(f"❌ Users table error: {e}")
        
        print("\n✅ Database tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Supabase Database Structure Test")
    print("=" * 40)
    
    result = asyncio.run(test_supabase_connection())
    
    if result:
        print("\n✅ Database connection working!")
    else:
        print("\n❌ Database connection issues found.")
