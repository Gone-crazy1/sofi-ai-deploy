#!/usr/bin/env python3
"""
Comprehensive table verification script for Sofi AI
"""
import os
import sys
import traceback
from supabase import create_client
from dotenv import load_dotenv

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        print("=== SOFI AI SUPABASE TABLE VERIFICATION ===")
        print(f"URL: {supabase_url}")
        print(f"Key: {supabase_key[:20]}...")
        
        if not supabase_url or not supabase_key:
            print("❌ ERROR: Missing Supabase credentials")
            return False
            
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test basic connection with users table
        try:
            result = supabase.table('users').select('id').limit(1).execute()
            print(f"✅ Connection verified - users table accessible")
        except Exception as e:
            print(f"❌ Connection failed to users table: {str(e)}")
            return False
        
        # Define all tables that should exist
        required_tables = [
            'transfer_requests',
            'payment_attempts', 
            'refunds',
            'bank_verification',
            'paystack_errors',
            'audit_logs',
            'beneficiaries',
            'sofi_transfer_profit'
        ]
        
        print(f"\n=== CHECKING {len(required_tables)} REQUIRED TABLES ===")
        
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f'✅ {table}: EXISTS')
                existing_tables.append(table)
            except Exception as e:
                print(f'❌ {table}: MISSING - {str(e)}')
                missing_tables.append(table)
        
        print(f"\n=== SUMMARY ===")
        print(f"✅ Existing tables: {len(existing_tables)}")
        print(f"❌ Missing tables: {len(missing_tables)}")
        
        if missing_tables:
            print(f"\nMissing tables: {', '.join(missing_tables)}")
            print(f"\nTo create missing tables, run the SQL in create_sofi_tables.sql")
            return False
        else:
            print(f"\n🎉 ALL TABLES EXIST! Database is ready.")
            return True
            
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
