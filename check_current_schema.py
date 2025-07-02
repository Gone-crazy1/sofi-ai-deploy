#!/usr/bin/env python3
"""
Check Current Supabase Schema
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from supabase import create_client

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_schema():
    """Check current schema and show available columns"""
    
    print("🔍 Checking Supabase Schema")
    print("=" * 50)
    
    # Check users table
    try:
        print("\n📋 Checking users table...")
        result = supabase.table('users').select('*').limit(1).execute()
        print("✅ users table exists")
        
        # Try to insert a test record to see what columns are missing
        test_user = {
            'telegram_chat_id': 'test_schema_check',
            'first_name': 'Test',
            'full_name': 'Test User',
            'phone_number': '+1234567890',
            'wallet_balance': 0.0
        }
        
        try:
            result = supabase.table('users').insert(test_user).execute()
            print("✅ Basic user insert works")
            
            # Delete the test record
            supabase.table('users').delete().eq('telegram_chat_id', 'test_schema_check').execute()
            
        except Exception as e:
            print(f"❌ User insert failed: {e}")
            
    except Exception as e:
        print(f"❌ Error with users table: {e}")
    
    # Check virtual_accounts table
    try:
        print("\n📋 Checking virtual_accounts table...")
        result = supabase.table('virtual_accounts').select('*').limit(1).execute()
        print("✅ virtual_accounts table exists")
        
        # Try to insert a test record to see what columns are missing
        test_account = {
            'user_id': 'test_schema_check',
            'paystack_customer_id': 'test',
            'account_number': '1234567890',
            'bank_name': 'Test Bank',
            'status': 'active'
        }
        
        try:
            result = supabase.table('virtual_accounts').insert(test_account).execute()
            print("✅ Basic virtual_account insert works")
            
            # Delete the test record
            supabase.table('virtual_accounts').delete().eq('user_id', 'test_schema_check').execute()
            
        except Exception as e:
            print(f"❌ Virtual account insert failed: {e}")
            
    except Exception as e:
        print(f"❌ Error with virtual_accounts table: {e}")
    
    print("\n✨ Schema check completed!")

if __name__ == "__main__":
    check_schema()
