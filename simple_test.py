import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

print("Testing Supabase connection...")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20]}...")

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
print("✅ Supabase client created")

# Test basic connection
result = supabase.table('users').select('*').limit(1).execute()
print(f"✅ Users table accessible - {len(result.data)} records")

# Check for new tables
tables = ['transfer_requests', 'payment_attempts', 'refunds', 'bank_verification', 
          'paystack_errors', 'audit_logs', 'beneficiaries', 'sofi_transfer_profit']

for table in tables:
    try:
        result = supabase.table(table).select('*').limit(1).execute()
        print(f'✅ {table}: EXISTS')
    except Exception as e:
        print(f'❌ {table}: {str(e)}')

print("\nDone!")
