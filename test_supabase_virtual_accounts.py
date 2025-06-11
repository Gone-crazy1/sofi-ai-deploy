#!/usr/bin/env python3
"""
Test script to check if virtual accounts are being saved to Supabase
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from supabase import create_client
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def check_supabase_virtual_accounts():
    """Check what virtual accounts exist in Supabase"""
    print("🔍 Checking Supabase for Virtual Accounts...")
    
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        print(f"📡 Supabase URL: {supabase_url}")
        print(f"🔑 Supabase Key: {supabase_key[:20]}..." if supabase_key else "❌ No key found")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials!")
            return False
            
        supabase = create_client(supabase_url, supabase_key)
        
        # Query virtual_accounts table
        print("\n📋 Querying virtual_accounts table...")
        result = supabase.table("virtual_accounts").select("*").execute()
        
        if result.data:
            print(f"✅ Found {len(result.data)} virtual accounts in Supabase:")
            for i, account in enumerate(result.data, 1):
                print(f"\n🏦 Account {i}:")
                print(f"   📱 Account Number: {account.get('accountNumber', 'N/A')}")
                print(f"   👤 Account Name: {account.get('accountName', 'N/A')}")
                print(f"   🏛️ Bank: {account.get('bankName', 'N/A')}")
                print(f"   📅 Created: {account.get('created_at', 'N/A')}")
                print(f"   💬 Telegram Chat ID: {account.get('telegram_chat_id', 'N/A')}")
                print(f"   📞 Phone: {account.get('phone', 'N/A')}")
        else:
            print("📭 No virtual accounts found in Supabase!")
            
        # Query users table
        print("\n📋 Querying users table...")
        users_result = supabase.table("users").select("*").execute()
        
        if users_result.data:
            print(f"✅ Found {len(users_result.data)} users in Supabase:")
            for i, user in enumerate(users_result.data, 1):
                print(f"\n👤 User {i}:")
                print(f"   📛 Name: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
                print(f"   📞 Phone: {user.get('phone', 'N/A')}")
                print(f"   📅 Created: {user.get('created_at', 'N/A')}")
        else:
            print("📭 No users found in Supabase!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking Supabase: {e}")
        return False

def test_virtual_account_with_logging():
    """Test virtual account creation with detailed logging"""
    print("\n🧪 Testing Virtual Account Creation with Logging...")
    
    test_data = {
        "firstName": "SupabaseTest",
        "lastName": "User", 
        "bvn": "12345678901",
        "phone": "08123456789",
        "telegram_chat_id": "999888777"  # Include chat ID for testing
    }
    
    try:
        # Test local endpoint first
        local_url = "http://127.0.0.1:5000/api/create_virtual_account"
        
        print(f"📡 Testing: {local_url}")
        print(f"📋 Data: {test_data}")
        
        response = requests.post(local_url, json=test_data, timeout=15)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Virtual account creation successful!")
            
            # Wait a moment for data to be saved
            import time
            time.sleep(2)
            
            # Check if data was saved to Supabase
            print("\n🔍 Checking if data was saved to Supabase...")
            check_supabase_virtual_accounts()
            
        else:
            print(f"❌ Virtual account creation failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Local server not running - please start the server first")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print(">>> Supabase Virtual Account Investigation <<<")
    
    # First check existing data
    check_supabase_virtual_accounts()
    
    # Then test new account creation
    test_virtual_account_with_logging()
