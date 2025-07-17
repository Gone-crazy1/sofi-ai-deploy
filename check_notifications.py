#!/usr/bin/env python3
"""
Check if notifications are being sent for recent deposits
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def check_notification_status():
    """Check recent deposits and their notification status"""
    try:
        # Initialize Supabase
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        print('🔍 Checking notification status for recent deposits...\n')
        
        # Get recent deposits (last 24 hours)
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        
        result = supabase.table('bank_transactions').select('*').eq('transaction_type', 'credit').gte('created_at', yesterday).order('created_at', desc=True).limit(10).execute()
        
        if not result.data:
            print('❌ No recent deposits found in the last 24 hours')
            return
            
        print(f'✅ Found {len(result.data)} recent deposits:')
        
        for i, txn in enumerate(result.data, 1):
            user_uuid = txn.get('user_id')
            amount = txn.get('amount', 0)
            sender = txn.get('sender_name', 'Unknown')
            created = txn.get('created_at', '')[:19] if txn.get('created_at') else 'Unknown'
            
            print(f'\n{i}. ₦{amount:,.0f} from "{sender}" at {created}')
            print(f'   User UUID: {user_uuid}')
            
            if user_uuid:
                # Find the telegram chat ID for this user
                user_query = supabase.table('users').select('telegram_chat_id, full_name').eq('id', user_uuid).execute()
                
                if user_query.data:
                    telegram_chat_id = user_query.data[0].get('telegram_chat_id')
                    full_name = user_query.data[0].get('full_name', 'Unknown')
                    
                    print(f'   ✅ User found: {full_name} (Chat ID: {telegram_chat_id})')
                    
                    # This is where notification should have been sent
                    print(f'   📱 Notification should be sent to Telegram chat: {telegram_chat_id}')
                    
                else:
                    print(f'   ❌ User not found in users table for UUID: {user_uuid}')
            else:
                print(f'   ❌ No user_id in transaction record')
                
        print(f'\n🔍 Summary: All {len(result.data)} recent deposits have been recorded in database')
        print('💡 If notifications are missing, the issue is in the notification sending logic')
        
    except Exception as e:
        print(f'❌ Error checking notifications: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_notification_status()
