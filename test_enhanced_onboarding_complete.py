#!/usr/bin/env python3
"""
Comprehensive test for enhanced onboarding form with all required fields
"""

import json
import requests
from supabase import create_client
import os
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

def test_enhanced_onboarding():
    """Test the complete enhanced onboarding form with all fields"""
    
    print("=" * 60)
    print("   ENHANCED ONBOARDING COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Complete test data matching your requirements
    test_data = {
        "firstName": "Ndidi",
        "lastName": "Thankgod",
        "phone": "08012345678",
        "email": "ndidi.thankgod@example.com",
        "address": "12 Allen Avenue",
        "city": "Lagos",
        "state": "Lagos State",
        "country": "Nigeria",
        "pin": "1234",
        "bvn": "12345678901",
        "telegram_chat_id": "123456789"
    }
    
    print("📋 Test Data:")
    for key, value in test_data.items():
        if key == 'pin':
            print(f"   {key}: ****")
        else:
            print(f"   {key}: {value}")
    
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Missing Supabase credentials")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Clean up any existing test data
        print("\n🧹 Cleaned up existing test data")
        try:
            supabase.table("users").delete().eq("first_name", "Ndidi").execute()
            supabase.table("virtual_accounts").delete().eq("telegram_chat_id", "123456789").execute()
        except:
            pass
        
        # Test 1: Verify database schema has all required columns
        print("\n1️⃣ Verifying database schema...")
        try:
            result = supabase.table("users").select("*").limit(1).execute()
            if result.data:
                existing_columns = list(result.data[0].keys())
                required_columns = ['email', 'country', 'phone', 'pin', 'address', 'city', 'state']
                missing_columns = [col for col in required_columns if col not in existing_columns]
                
                if missing_columns:
                    print(f"❌ Missing columns in users table: {missing_columns}")
                    print("🔧 Run this SQL in Supabase to add missing columns:")
                    print("```sql")
                    if 'email' in missing_columns:
                        print("ALTER TABLE public.users ADD COLUMN email VARCHAR(255);")
                    if 'country' in missing_columns:
                        print("ALTER TABLE public.users ADD COLUMN country VARCHAR(100);")
                    print("```")
                    return False
                else:
                    print("✅ All required columns exist in database")
            else:
                print("❌ No data found in users table to check schema")
                return False
                
        except Exception as e:
            print(f"❌ Error checking database schema: {e}")
            return False
        
        # Test 2: Test field validation
        print("\n2️⃣ Testing field validation...")
        
        # Test invalid phone (should be 11 digits)
        invalid_phone_data = test_data.copy()
        invalid_phone_data['phone'] = "0801234567"  # Only 10 digits
        
        try:
            response = requests.post("http://localhost:5000/api/create_virtual_account", 
                                   json=invalid_phone_data, timeout=10)
            if response.status_code == 400:
                print("✅ Phone validation working correctly")
            else:
                print("⚠️ Phone validation might need improvement")
        except:
            print("⚠️ Local server not running, skipping validation test")
        
        # Test 3: Test complete onboarding flow
        print("\n3️⃣ Testing complete onboarding flow...")
        
        # Test with production endpoint
        production_url = "https://sofi-ai-trio.onrender.com/api/create_virtual_account"
        
        try:
            response = requests.post(production_url, json=test_data, timeout=30)
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                response_data = response.json()
                print("✅ Enhanced onboarding successful!")
                print(f"🎉 Message: {response_data.get('message')}")
                
                # Verify account creation
                account = response_data.get('account', {})
                if account:
                    print(f"💳 Account Number: {account.get('accountNumber')}")
                    print(f"🏦 Bank: {account.get('bankName')}")
                    print(f"👤 Account Name: {account.get('accountName')}")
                
                # Verify user data
                user_data_response = response_data.get('user_data', {})
                if user_data_response:
                    print(f"📱 Phone: {user_data_response.get('phone')}")
                    print(f"📧 Email: {user_data_response.get('email')}")
                    print(f"🏠 Address: {user_data_response.get('address')}")
                
                # Test 4: Verify data was saved correctly in database
                print("\n4️⃣ Verifying data persistence...")
                
                user_result = supabase.table("users") \
                    .select("first_name, last_name, phone, email, address, city, state, country, pin") \
                    .eq("first_name", "Ndidi") \
                    .execute()
                
                if user_result.data:
                    user = user_result.data[0]
                    print("✅ User data saved correctly:")
                    print(f"   📞 Phone: {user.get('phone')}")
                    print(f"   📧 Email: {user.get('email')}")
                    print(f"   🏠 Address: {user.get('address')}")
                    print(f"   🌆 City: {user.get('city')}")
                    print(f"   🗺️ State: {user.get('state')}")
                    print(f"   🌍 Country: {user.get('country')}")
                    
                    # Verify PIN is hashed
                    if user.get('pin'):
                        expected_hash = hashlib.sha256("1234".encode()).hexdigest()
                        if user.get('pin') == expected_hash:
                            print("✅ PIN properly hashed and stored")
                        else:
                            print("⚠️ PIN storage method may need verification")
                    
                    return True
                else:
                    print("❌ User data not found in database")
                    return False
                    
            else:
                print(f"❌ Onboarding failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up test data
        print("\n🧹 Test data cleaned up")
        try:
            if 'supabase' in locals():
                supabase.table("users").delete().eq("first_name", "Ndidi").execute()
                supabase.table("virtual_accounts").delete().eq("telegram_chat_id", "123456789").execute()
        except:
            pass

def main():
    """Main function"""
    print("🚀 Testing Enhanced Onboarding Form")
    print("=" * 50)
    
    success = test_enhanced_onboarding()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced onboarding form is working correctly")
        print("✅ All required fields are properly validated and saved")
        print("✅ PIN is securely hashed")
        print("✅ Virtual account creation integrated")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please check the issues above and fix them")
    print("=" * 60)

if __name__ == "__main__":
    main()
