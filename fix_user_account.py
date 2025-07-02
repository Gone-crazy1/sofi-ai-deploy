"""
Fix user account linkage and balance for Telegram ID 5495194750
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

try:
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    telegram_id = "5495194750"
    account_number = "9325047112"
    
    print(f"🔧 Fixing account for Telegram ID: {telegram_id}")
    print(f"🏦 Account Number: {account_number}")
    print("=" * 50)
    
    # 1. Get user ID
    user_result = supabase.table("users").select("id, wallet_balance, full_name").eq("telegram_chat_id", telegram_id).execute()
    
    if not user_result.data:
        print("❌ User not found!")
        exit()
    
    user = user_result.data[0]
    user_id = user["id"]
    wallet_balance = float(user["wallet_balance"] or 0)
    full_name = user["full_name"]
    
    print(f"✅ User found: {full_name}")
    print(f"💰 User wallet balance: ₦{wallet_balance:,.2f}")
    print(f"🆔 User ID: {user_id}")
    
    # 2. Update virtual account to link to user and sync balance
    va_update_result = supabase.table("virtual_accounts").update({
        "user_id": user_id,
        "balance": wallet_balance,
        "account_name": full_name
    }).eq("account_number", account_number).execute()
    
    if va_update_result.data:
        print(f"✅ Virtual account updated successfully!")
        print(f"   - Linked to user ID: {user_id}")
        print(f"   - Balance synced to: ₦{wallet_balance:,.2f}")
        print(f"   - Account name set to: {full_name}")
    else:
        print("❌ Failed to update virtual account")
    
    # 3. Also update the users table to have account details
    user_update_result = supabase.table("users").update({
        "account_number": account_number,
        "bank_name": "Wema Bank"
    }).eq("telegram_chat_id", telegram_id).execute()
    
    if user_update_result.data:
        print(f"✅ User account details updated!")
        print(f"   - Account number: {account_number}")
        print(f"   - Bank name: Wema Bank")
    
    # 4. Verify the fix
    print("\n🔍 Verification:")
    
    # Check virtual account
    va_check = supabase.table("virtual_accounts").select("*").eq("account_number", account_number).execute()
    if va_check.data:
        va = va_check.data[0]
        print(f"✅ Virtual Account:")
        print(f"   - Account: {va.get('account_number')}")
        print(f"   - Balance: ₦{va.get('balance', 0):,.2f}")
        print(f"   - User ID: {va.get('user_id')}")
        print(f"   - Account Name: {va.get('account_name')}")
    
    # Check user account
    user_check = supabase.table("users").select("*").eq("telegram_chat_id", telegram_id).execute()
    if user_check.data:
        user = user_check.data[0]
        print(f"✅ User Account:")
        print(f"   - Wallet Balance: ₦{user.get('wallet_balance', 0):,.2f}")
        print(f"   - Account Number: {user.get('account_number')}")
        print(f"   - Bank Name: {user.get('bank_name')}")
    
    print("\n🎉 Account fix completed! Your balance should now show correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
