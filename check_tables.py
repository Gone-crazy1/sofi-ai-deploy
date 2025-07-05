import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print('Checking Supabase tables...')

tables = ['transfer_requests', 'payment_attempts', 'refunds', 'bank_verification', 
          'paystack_errors', 'audit_logs', 'beneficiaries', 'sofi_transfer_profit']

for table in tables:
    try:
        result = supabase.table(table).select('*').limit(1).execute()
        print(f'✅ {table}: EXISTS')
    except Exception as e:
        print(f'❌ {table}: {str(e)}')
