"""
Check webhook and user matching logic
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def check_all_users():
    try:
        # Check all users to see if there are multiple Ndidi entries
        user_result = supabase.table("users").select("*").execute()
        
        print("All users in database:")
        for user in user_result.data:
            if "ndidi" in user.get('full_name', '').lower():
                print(f"  Name: {user.get('full_name')}")
                print(f"  Telegram ID: {user.get('telegram_chat_id')}")
                print(f"  ID: {user.get('id')}")
                print(f"  Balance: ₦{user.get('wallet_balance', 0)}")
                print(f"  Created: {user.get('created_at')}")
                print("-" * 40)
        
        # Check virtual accounts for Ndidi
        print("\nVirtual Accounts:")
        va_result = supabase.table("virtual_accounts").select("*").execute()
        for va in va_result.data:
            if "ndidi" in va.get('account_name', '').lower():
                print(f"  Account: {va.get('account_number')} - {va.get('account_name')}")
                print(f"  User ID: {va.get('user_id')}")
                print(f"  Customer Code: {va.get('customer_code')}")
                print(f"  Balance: ₦{va.get('balance', 0)}")
                print("-" * 40)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_all_users()
