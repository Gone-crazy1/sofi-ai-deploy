#!/usr/bin/env python3
"""
Check bank_transactions table schema
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

def check_bank_transactions_schema():
    """Check the actual schema of bank_transactions table"""
    
    # Initialize Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🔍 Checking bank_transactions Table Schema")
    print("=" * 50)
    
    # Test common column names
    test_columns = [
        'id', 'user_id', 'telegram_chat_id', 'transaction_type', 
        'amount', 'reference', 'status', 'description', 
        'balance_after', 'balance_before', 'new_balance',
        'paystack_data', 'created_at', 'updated_at'
    ]
    
    working_columns = []
    
    for column in test_columns:
        try:
            # Try to select this column - if it exists, no error
            result = supabase.table('bank_transactions').select(column).limit(1).execute()
            print(f"  ✅ {column}")
            working_columns.append(column)
        except Exception as e:
            print(f"  ⚠️ {column} - {str(e)[:60]}...")
    
    print(f"\n✅ Working columns for bank_transactions: {working_columns}")
    
    # Try to get a sample record to see the actual structure
    try:
        sample = supabase.table('bank_transactions').select('*').limit(1).execute()
        if sample.data:
            print(f"\n📋 Sample record structure:")
            for key in sample.data[0].keys():
                print(f"   - {key}")
        else:
            print(f"\n📋 Table exists but no records found")
    except Exception as e:
        print(f"\n⚠️ Could not get sample: {str(e)}")

if __name__ == "__main__":
    check_bank_transactions_schema()
