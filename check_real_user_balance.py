"""
Check the real user balance for Telegram ID 5495194750
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

try:
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    telegram_id = "5495194750"
    print(f"🔍 Checking balance for Telegram ID: {telegram_id}")
    print("=" * 50)
    
    # Check users table
    user_result = supabase.table("users").select("*").eq("telegram_chat_id", telegram_id).execute()
    
    if user_result.data:
        user = user_result.data[0]
        print(f"✅ User found:")
        print(f"  Full Name: {user.get('full_name')}")
        print(f"  Wallet Balance: ₦{user.get('wallet_balance', 0):,.2f}")
        print(f"  Account Number: {user.get('account_number')}")
        print(f"  Bank Name: {user.get('bank_name')}")
        print(f"  Created: {user.get('created_at')}")
        print(f"  Updated: {user.get('updated_at')}")
        
        user_id = user.get('id')
        print(f"  User UUID: {user_id}")
        
        # Check virtual_accounts table 
        va_result = supabase.table("virtual_accounts").select("*").eq("user_id", user_id).execute()
        if va_result.data:
            va = va_result.data[0]
            print(f"\n💳 Virtual Account:")
            print(f"  Account Number: {va.get('account_number')}")
            print(f"  Bank Name: {va.get('bank_name')}")
            print(f"  Account Name: {va.get('account_name')}")
            print(f"  Balance: ₦{va.get('balance', 0):,.2f}")
            print(f"  Status: {va.get('status')}")
        else:
            print(f"\n❌ No virtual account found for user")
        
        # Check recent transactions
        tx_result = supabase.table("bank_transactions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(5).execute()
        print(f"\n📊 Recent Transactions ({len(tx_result.data)}):")
        for tx in tx_result.data:
            print(f"  {tx.get('transaction_type')} ₦{tx.get('amount')} - {tx.get('status')} - {tx.get('created_at')[:19]}")
            
    else:
        print("❌ User not found with that Telegram ID")
        
        # Check if user exists with different ID format
        alt_result = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        if alt_result.data:
            print("✅ Found user with 'telegram_id' field instead:")
            user = alt_result.data[0]
            print(f"  Full Name: {user.get('full_name')}")
            print(f"  Wallet Balance: ₦{user.get('wallet_balance', 0):,.2f}")

except Exception as e:
    print(f"❌ Error: {e}")
