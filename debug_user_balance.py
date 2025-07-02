"""
Check user balance and transactions in database
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def check_user_data():
    try:
        # Find user by name
        user_result = supabase.table("users").select("*").ilike("full_name", "%Ndidi%").execute()
        
        if user_result.data:
            user = user_result.data[0]
            print(f"User found:")
            print(f"  Name: {user.get('full_name')}")
            print(f"  Telegram ID: {user.get('telegram_chat_id')}")
            print(f"  Wallet Balance: ₦{user.get('wallet_balance', 0)}")
            print(f"  ID: {user.get('id')}")
            
            # Check virtual account
            va_result = supabase.table("virtual_accounts").select("*").eq("user_id", user.get('id')).execute()
            if va_result.data:
                va = va_result.data[0]
                print(f"\nVirtual Account:")
                print(f"  Account Number: {va.get('account_number')}")
                print(f"  Bank: {va.get('bank_name')}")
                print(f"  Balance: ₦{va.get('balance', 0)}")
            
            # Check recent transactions
            tx_result = supabase.table("bank_transactions").select("*").eq("user_id", user.get('id')).order('created_at', desc=True).limit(3).execute()
            print(f"\nRecent Transactions:")
            for tx in tx_result.data:
                print(f"  {tx.get('transaction_type')} ₦{tx.get('amount')} - {tx.get('status')} - {tx.get('created_at')}")
        else:
            print("User not found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_data()
