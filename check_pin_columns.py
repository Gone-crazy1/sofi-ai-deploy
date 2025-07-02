#!/usr/bin/env python3
"""
Check PIN Columns in Users Table

This script checks for PIN-related columns in the users table.
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

def check_pin_columns():
    """Check for PIN-related columns in users table"""
    
    # Initialize Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🔍 Checking PIN Columns in Users Table")
    print("=" * 45)
    
    # Test PIN-related column names
    pin_columns = [
        'pin_hash',
        'pin',
        'transaction_pin',
        'pin_attempts',
        'pin_locked_until',
        'pin_set_at',
        'has_pin'
    ]
    
    existing_columns = []
    
    for column in pin_columns:
        try:
            # Try to select the column to see if it exists
            response = supabase.table('users').select(column).limit(1).execute()
            print(f"  ✅ {column}")
            existing_columns.append(column)
        except Exception as e:
            error_msg = str(e)
            if 'does not exist' in error_msg:
                print(f"  ❌ {column} - Missing")
            else:
                print(f"  ⚠️ {column} - {error_msg[:60]}...")
    
    if existing_columns:
        print(f"\n✅ Existing PIN columns: {existing_columns}")
    else:
        print(f"\n❌ No PIN columns found!")
        print("\n🔧 You need to add PIN columns to your users table:")
        print("   ALTER TABLE users ADD COLUMN pin_hash TEXT;")
        print("   ALTER TABLE users ADD COLUMN pin_attempts INTEGER DEFAULT 0;")
        print("   ALTER TABLE users ADD COLUMN pin_locked_until TIMESTAMPTZ;")
        print("   ALTER TABLE users ADD COLUMN pin_set_at TIMESTAMPTZ;")

if __name__ == "__main__":
    check_pin_columns()
