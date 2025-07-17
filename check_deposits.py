#!/usr/bin/env python3
"""
Check for recent deposits and webhook activity
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def check_recent_deposits():
    """Check for recent deposit activity"""
    try:
        # Initialize Supabase
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        print('🔍 Checking recent deposit activity...\n')
        
        # Check for recent credit transactions (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        result = supabase.table('bank_transactions').select('*').eq('transaction_type', 'credit').gte('created_at', week_ago).order('created_at', desc=True).limit(20).execute()
        
        if result.data:
            print(f'✅ Found {len(result.data)} recent credit transactions:')
            for i, txn in enumerate(result.data, 1):
                amount = txn.get('amount', 0)
                sender = txn.get('sender_name', 'Unknown')
                reference = txn.get('reference', 'No ref')
                created = txn.get('created_at', '')[:19] if txn.get('created_at') else 'Unknown'
                user_id = txn.get('user_id', 'Unknown')
                
                print(f'  {i}. ₦{amount:,.0f} from "{sender}" | Ref: {reference} | User: {user_id} | {created}')
        else:
            print('❌ No recent credit transactions found in the last 7 days')
            
        # Check virtual accounts
        print('\n🔍 Checking virtual accounts...')
        accounts = supabase.table('virtual_accounts').select('telegram_chat_id, account_number, balance, created_at').order('created_at', desc=True).limit(10).execute()
        
        if accounts.data:
            print(f'✅ Found {len(accounts.data)} virtual accounts:')
            for i, acc in enumerate(accounts.data, 1):
                chat_id = acc.get('telegram_chat_id')
                account_num = acc.get('account_number')
                balance = acc.get('balance', 0)
                created = acc.get('created_at', '')[:19] if acc.get('created_at') else 'Unknown'
                
                print(f'  {i}. Chat ID: {chat_id} | Account: {account_num} | Balance: ₦{balance:,.0f} | Created: {created}')
        else:
            print('❌ No virtual accounts found')
            
        # Check users table for recent balance updates
        print('\n🔍 Checking users with recent balance changes...')
        users = supabase.table('users').select('telegram_chat_id, full_name, wallet_balance, updated_at').order('updated_at', desc=True).limit(10).execute()
        
        if users.data:
            print(f'✅ Found {len(users.data)} users with recent activity:')
            for i, user in enumerate(users.data, 1):
                chat_id = user.get('telegram_chat_id')
                name = user.get('full_name', 'Unknown')
                balance = user.get('wallet_balance', 0)
                updated = user.get('updated_at', '')[:19] if user.get('updated_at') else 'Unknown'
                
                print(f'  {i}. {name} (Chat: {chat_id}) | Balance: ₦{balance:,.0f} | Updated: {updated}')
        
    except Exception as e:
        print(f'❌ Error checking database: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_recent_deposits()
