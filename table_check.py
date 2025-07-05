import os
import json
from supabase import create_client
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # Initialize Supabase client
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    
    # Tables to check
    tables = [
        'transfer_requests',
        'payment_attempts', 
        'refunds',
        'bank_verification',
        'paystack_errors',
        'audit_logs',
        'beneficiaries',
        'sofi_transfer_profit'
    ]
    
    print("🔍 Checking Supabase tables...")
    existing = []
    missing = []
    
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            existing.append(table)
            print(f"✅ {table}")
        except Exception as e:
            missing.append(table)
            print(f"❌ {table}: {str(e)}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Existing: {len(existing)}")
    print(f"❌ Missing: {len(missing)}")
    
    if missing:
        print(f"\n🚨 Missing tables: {', '.join(missing)}")
        print("Run create_sofi_tables.sql in Supabase SQL Editor")
    else:
        print("\n🎉 ALL TABLES EXIST! Database is ready.")

if __name__ == "__main__":
    main()
