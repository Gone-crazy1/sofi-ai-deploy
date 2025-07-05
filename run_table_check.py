#!/usr/bin/env python3
"""
Simple database table checker for Sofi AI
"""
import os
import json
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
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

results = {
    'timestamp': datetime.now().isoformat(),
    'existing_tables': [],
    'missing_tables': [],
    'errors': []
}

print("🔍 Checking Supabase tables...")

for table in tables:
    try:
        result = supabase.table(table).select('*').limit(1).execute()
        results['existing_tables'].append(table)
        print(f"✅ {table}")
    except Exception as e:
        results['missing_tables'].append(table)
        results['errors'].append(f"{table}: {str(e)}")
        print(f"❌ {table}: {str(e)}")

print(f"\n📊 SUMMARY:")
print(f"✅ Existing: {len(results['existing_tables'])}")
print(f"❌ Missing: {len(results['missing_tables'])}")

if results['missing_tables']:
    print(f"\n🚨 Missing tables: {', '.join(results['missing_tables'])}")
    print("Run create_sofi_tables.sql in Supabase SQL Editor")
else:
    print("\n🎉 ALL TABLES EXIST! Database is ready.")

# Save results to file
with open('table_check_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n💾 Results saved to table_check_results.json")
