#!/usr/bin/env python3
"""
Test the migration - check if sender columns were added
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def test_migration():
    """Test if the migration was successful"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        print("🔍 Testing migration - checking for sender columns...")
        
        # Test columns we added
        test_columns = ['sender_name', 'narration', 'bank_name', 'bank_code', 'account_number']
        
        for column in test_columns:
            try:
                # Try to select this column - if it exists, no error
                result = supabase.table('bank_transactions').select(column).limit(1).execute()
                print(f"✅ {column} - EXISTS")
            except Exception as e:
                print(f"❌ {column} - MISSING: {str(e)[:60]}...")
        
        print("\n🔍 Getting sample record structure...")
        try:
            sample = supabase.table('bank_transactions').select('*').limit(1).execute()
            if sample.data:
                print(f"📋 All columns in bank_transactions:")
                for key in sorted(sample.data[0].keys()):
                    print(f"   - {key}")
            else:
                print("🔍 No records found in bank_transactions")
                
        except Exception as e:
            print(f"❌ Error getting sample: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing migration results...")
    test_migration()
