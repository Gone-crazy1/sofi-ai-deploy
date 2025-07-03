#!/usr/bin/env python3
"""Check users in database for testing"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.append('.')
load_dotenv()

def check_users():
    """Check users in the database"""
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get all users
        users_result = supabase.table("users").select("telegram_chat_id, full_name, wallet_balance").limit(5).execute()
        
        print(f"Found {len(users_result.data)} users:")
        for user in users_result.data:
            chat_id = user.get('telegram_chat_id')
            name = user.get('full_name', 'Unknown')
            balance = user.get('wallet_balance', 0)
            print(f"  - Chat ID: {chat_id}, Name: {name}, Balance: ₦{balance}")
        
        if users_result.data:
            # Use the first user for testing
            test_user = users_result.data[0]
            print(f"\n✅ Will use Chat ID '{test_user['telegram_chat_id']}' for testing")
            return test_user['telegram_chat_id']
        else:
            print("❌ No users found in database")
            return None
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return None

if __name__ == "__main__":
    check_users()
