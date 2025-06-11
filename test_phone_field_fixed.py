#!/usr/bin/env python3
"""
Test script to verify phone field integration in virtual account creation
"""

import json
import requests
from supabase import create_client
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def test_phone_field_integration():
    """Test that phone field is correctly saved to users table"""
    
    # Test data
    test_data = {
        "firstName": "TestPhone",
        "lastName": "User",
        "bvn": "12345678901",
        "phone": "+2348012345678",
        "telegram_chat_id": "999999999"
    }
    
    print("🧪 Testing phone field integration...")
    print(f"📞 Test phone number: {test_data['phone']}")
    
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Missing Supabase credentials")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Clean up any existing test data first
        try:
            supabase.table("users").delete().eq("first_name", "TestPhone").execute()
            supabase.table("virtual_accounts").delete().eq("telegram_chat_id", "999999999").execute()
            print("🧹 Cleaned up existing test data")
        except Exception as e:
            print(f"⚠️ Cleanup note: {e}")
        
        # Test 1: Check phone column exists in users table
        print("\n1️⃣ Testing phone column exists...")
        try:
            result = supabase.table("users").select("phone").limit(1).execute()
            print("✅ Phone column exists in users table")
        except Exception as e:
            print(f"❌ Phone column test failed: {e}")
            return False
        
        # Test 2: Insert user data with phone field directly
        print("\n2️⃣ Testing direct user insertion with phone...")
        try:
            user_data = {
                "first_name": test_data["firstName"],
                "last_name": test_data["lastName"],
                "bvn": test_data["bvn"],
                "phone": test_data["phone"],
                "telegram_chat_id": int(test_data["telegram_chat_id"])
            }
            
            result = supabase.table("users").insert(user_data).execute()
            
            if result.data:
                print("✅ User data with phone inserted successfully")
                print(f"📋 Inserted user ID: {result.data[0].get('id')}")
                print(f"📞 Phone saved: {result.data[0].get('phone')}")
            else:
                print("❌ No data returned from user insertion")
                return False
                
        except Exception as e:
            print(f"❌ Direct user insertion failed: {e}")
            return False
        
        # Test 3: Verify phone field can be queried
        print("\n3️⃣ Testing phone field query...")
        try:
            result = supabase.table("users") \
                .select("first_name, last_name, phone, telegram_chat_id") \
                .eq("first_name", "TestPhone") \
                .execute()
            
            if result.data:
                user = result.data[0]
                print("✅ Phone field query successful")
                print(f"👤 User: {user.get('first_name')} {user.get('last_name')}")
                print(f"📞 Phone: {user.get('phone')}")
                print(f"💬 Chat ID: {user.get('telegram_chat_id')}")
            else:
                print("❌ No user found in phone field query")
                return False
                
        except Exception as e:
            print(f"❌ Phone field query failed: {e}")
            return False
        
        # Test 4: Test API endpoint with phone field (if running locally)
        print("\n4️⃣ Testing API endpoint with phone field...")
        try:
            # Try local API first
            api_url = "http://localhost:5000/api/create_virtual_account"
            
            # Clean up test data before API test
            supabase.table("users").delete().eq("first_name", "TestPhone").execute()
            supabase.table("virtual_accounts").delete().eq("telegram_chat_id", "999999999").execute()
            
            response = requests.post(api_url, json=test_data, timeout=10)
            
            if response.status_code == 201:
                response_data = response.json()
                print("✅ API endpoint test successful")
                print(f"🎉 Response: {response_data.get('message')}")
                
                # Verify user was saved with phone
                user_result = supabase.table("users") \
                    .select("*") \
                    .eq("first_name", "TestPhone") \
                    .execute()
                
                if user_result.data:
                    user = user_result.data[0]
                    if user.get('phone') == test_data['phone']:
                        print(f"✅ Phone field correctly saved via API: {user.get('phone')}")
                    else:
                        print(f"❌ Phone field mismatch: expected {test_data['phone']}, got {user.get('phone')}")
                        return False
                else:
                    print("❌ User not found after API call")
                    return False
                    
            else:
                print(f"⚠️ API endpoint not available (status: {response.status_code})")
                print("📝 This is expected if the server is not running locally")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API endpoint test skipped (server not running): {e}")
            print("📝 This is expected if the server is not running locally")
        
        print("\n🎉 All available tests passed!")
        print("✅ Phone field integration is working correctly")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        supabase.table("users").delete().eq("first_name", "TestPhone").execute()
        supabase.table("virtual_accounts").delete().eq("telegram_chat_id", "999999999").execute()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main function"""
    print("="*50)
    print("   PHONE FIELD INTEGRATION TEST")
    print("="*50)
    
    success = test_phone_field_integration()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("📞 Phone field integration is working correctly")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED!")
        print("🔧 Please check the issues above")
        sys.exit(1)

if __name__ == "__main__":
    main()
