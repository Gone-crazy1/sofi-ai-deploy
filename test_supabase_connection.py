#!/usr/bin/env python3
import os
import sys
from supabase import create_client
from dotenv import load_dotenv

def test_supabase_connection():
    try:
        load_dotenv()
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
            
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test basic connection
        result = supabase.table('users').select('*').limit(1).execute()
        print(f"✅ Connection successful - users table accessible")
        
        # Check for new tables
        tables = ['transfer_requests', 'payment_attempts', 'refunds', 'bank_verification', 
                 'paystack_errors', 'audit_logs', 'beneficiaries', 'sofi_transfer_profit']
        
        for table in tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f'✅ {table}: EXISTS')
            except Exception as e:
                print(f'❌ {table}: {str(e)}')
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Supabase connection...")
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
