#!/usr/bin/env python3
"""
Check Web User in Database

This script verifies that the web user was successfully saved to Supabase.
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

def check_web_user():
    """Check if the web user was saved to database"""
    
    # Initialize Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    user_id = "web_user_1751458619"  # From the test
    
    print("🔍 Checking Web User in Database")
    print("=" * 40)
    print(f"User ID: {user_id}")
    print()
    
    try:
        # Check users table
        print("👤 Checking users table...")
        user_response = supabase.table('users').select('*').eq('telegram_chat_id', user_id).execute()
        
        if user_response.data:
            user = user_response.data[0]
            print("✅ User found!")
            print(f"   Full Name: {user.get('full_name')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Phone: {user.get('phone')}")
            print(f"   Customer Code: {user.get('paystack_customer_code')}")
            print(f"   Balance: ₦{user.get('wallet_balance', 0):,.2f}")
            print(f"   Created: {user.get('created_at')}")
        else:
            print("❌ User not found in database!")
            return
        
        print()
        
        # Check virtual_accounts table
        print("🏦 Checking virtual_accounts table...")
        account_response = supabase.table('virtual_accounts').select('*').eq('telegram_chat_id', user_id).execute()
        
        if account_response.data:
            account = account_response.data[0]
            print("✅ Virtual account found!")
            print(f"   Account Number: {account.get('account_number')}")
            print(f"   Bank: {account.get('bank_name')}")
            print(f"   Bank Code: {account.get('bank_code')}")
            print(f"   Created: {account.get('created_at')}")
        else:
            print("❌ Virtual account not found in database!")
        
        print()
        print("🎉 Web onboarding verification complete!")
        
    except Exception as e:
        print(f"💥 Error checking database: {e}")

if __name__ == "__main__":
    check_web_user()
