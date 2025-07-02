#!/usr/bin/env python3
"""
Check Actual Database Schema
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_actual_schema():
    """Check what columns actually exist in the database"""
    
    print("🔍 Checking Actual Database Schema")
    print("=" * 40)
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Try different column names to see what works
    test_columns = [
        # User table columns to test
        ("users", [
            "telegram_chat_id", "chat_id", "telegram_id",
            "full_name", "first_name", "last_name", "name",
            "phone_number", "phone", "mobile",
            "email", "email_address",
            "wallet_balance", "balance", "account_balance",
            "paystack_customer_code", "customer_code", "paystack_customer_id",
            "paystack_account_number", "account_number", "virtual_account_number"
        ]),
        # Virtual accounts table columns to test
        ("virtual_accounts", [
            "user_id", "telegram_chat_id", "chat_id",
            "paystack_customer_id", "customer_id", "paystack_customer_code",
            "account_number", "paystack_account_number", "virtual_account_number",
            "account_name", "paystack_account_name", "name",
            "bank_name", "paystack_bank_name", "bank",
            "bank_code", "paystack_bank_code", "code"
        ])
    ]
    
    for table_name, columns in test_columns:
        print(f"\n📋 Testing {table_name} table:")
        working_columns = []
        
        for col in columns:
            try:
                # Try to select just this column
                result = supabase.table(table_name).select(col).limit(1).execute()
                working_columns.append(col)
                print(f"  ✅ {col}")
            except Exception as e:
                if "Could not find" in str(e):
                    print(f"  ❌ {col}")
                else:
                    print(f"  ⚠️ {col} - {str(e)[:50]}...")
        
        print(f"\n✅ Working columns for {table_name}: {working_columns}")

if __name__ == "__main__":
    check_actual_schema()
