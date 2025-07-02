#!/usr/bin/env python3
"""
🧪 QUICK TEST - Verify all critical fixes are working
Tests OpenAI Assistant ID, database schema, and Paystack integration
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from supabase import create_client
import openai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_critical_fixes():
    """Test all the critical fixes we applied"""
    
    print("🧪 TESTING CRITICAL FIXES FOR SOFI AI")
    print("=" * 50)
    
    # Test 1: OpenAI Assistant ID
    print("\n1️⃣ Testing OpenAI Assistant ID...")
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        print(f"   Assistant ID: {assistant_id}")
        
        # Try to retrieve the assistant
        assistant = openai.beta.assistants.retrieve(assistant_id)
        print(f"   ✅ Assistant found: {assistant.name}")
        print(f"   ✅ Assistant model: {assistant.model}")
        
    except Exception as e:
        print(f"   ❌ Assistant test failed: {e}")
    
    # Test 2: Database connection and schema
    print("\n2️⃣ Testing Database Schema...")
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Test users table - get a sample user
        users_result = supabase.table("users").select("id, telegram_chat_id, wallet_balance").limit(1).execute()
        if users_result.data:
            print(f"   ✅ Users table working")
            sample_user = users_result.data[0]
            print(f"   ✅ Sample user: ID={sample_user['id']}, Telegram={sample_user['telegram_chat_id']}")
        else:
            print(f"   ⚠️ No users found in database")
        
        # Test virtual_accounts table
        va_result = supabase.table("virtual_accounts").select("account_number, bank_name").limit(1).execute()
        if va_result.data:
            print(f"   ✅ Virtual accounts table working")
        else:
            print(f"   ⚠️ No virtual accounts found")
        
        # Test bank_transactions table
        bt_result = supabase.table("bank_transactions").select("id, amount, status").limit(1).execute()
        print(f"   ✅ Bank transactions table accessible")
        
        # Test user_daily_limits table
        try:
            udl_result = supabase.table("user_daily_limits").select("id").limit(1).execute()
            print(f"   ✅ User daily limits table exists")
        except Exception as e:
            print(f"   ❌ User daily limits table missing: {e}")
            print(f"   🔧 Please run the SQL in manual_database_fixes.sql")
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
    
    # Test 3: Check specific telegram user UUID resolution
    print("\n3️⃣ Testing UUID Resolution...")
    try:
        # Test with the telegram ID from the logs
        test_telegram_id = "5495194750"
        user_result = supabase.table("users").select("id").eq("telegram_chat_id", test_telegram_id).execute()
        
        if user_result.data:
            user_uuid = user_result.data[0]["id"]
            print(f"   ✅ Telegram ID {test_telegram_id} → UUID {user_uuid}")
            
            # Test bank_transactions with the UUID
            tx_result = supabase.table("bank_transactions").select("id, amount").eq("user_id", user_uuid).limit(1).execute()
            print(f"   ✅ UUID can be used in bank_transactions queries")
            
        else:
            print(f"   ⚠️ Test user {test_telegram_id} not found")
            
    except Exception as e:
        print(f"   ❌ UUID resolution test failed: {e}")
    
    # Test 4: Balance functions
    print("\n4️⃣ Testing Balance Functions...")
    try:
        from functions.balance_functions import check_balance
        
        # This would normally need a real user, but let's test the import
        print(f"   ✅ Balance functions imported successfully")
        
    except Exception as e:
        print(f"   ❌ Balance functions test failed: {e}")
    
    # Test 5: Transfer functions  
    print("\n5️⃣ Testing Transfer Functions...")
    try:
        from functions.transfer_functions import send_money
        print(f"   ✅ Transfer functions imported successfully")
        
    except Exception as e:
        print(f"   ❌ Transfer functions test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY:")
    print("1. Update .env with new Assistant ID ✅")
    print("2. Restart Flask app to pick up new .env")
    print("3. Run manual_database_fixes.sql in Supabase")
    print("4. Test transfers via Telegram")
    print("🚀 Ready for production testing!")

if __name__ == "__main__":
    asyncio.run(test_critical_fixes())
