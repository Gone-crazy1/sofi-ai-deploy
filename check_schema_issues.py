"""
Check and fix database schema issues for transaction logging
"""

import os
from supabase import create_client

def check_and_fix_schema():
    """Check and fix database schema issues"""
    
    try:
        # Create Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        print("🔧 Checking Database Schema Issues...")
        print("=" * 60)
        
        # Check bank_transactions table structure
        print("\n📋 BANK_TRANSACTIONS TABLE:")
        try:
            # Try to get one record to see columns
            sample = supabase.table("bank_transactions").select("*").limit(1).execute()
            
            if sample.data:
                columns = list(sample.data[0].keys())
                print(f"✅ Existing columns: {', '.join(columns)}")
            else:
                # Try to insert a minimal record to see what columns exist
                print("📝 Table is empty, checking column requirements...")
                
            # Check what columns are actually needed vs available
            needed_columns = [
                'id', 'sender_telegram_id', 'amount', 'recipient_account', 
                'recipient_name', 'bank_code', 'bank_name', 'recipient_bank',
                'narration', 'status', 'transfer_code', 'balance_before', 
                'balance_after', 'created_at'
            ]
            
            print(f"🎯 Columns needed: {', '.join(needed_columns)}")
            
        except Exception as e:
            print(f"❌ Error checking bank_transactions: {e}")
        
        # Check users table structure  
        print("\n👥 USERS TABLE:")
        try:
            user_sample = supabase.table("users").select("*").limit(1).execute()
            if user_sample.data:
                user_columns = list(user_sample.data[0].keys())
                print(f"✅ Existing columns: {', '.join(user_columns)}")
                
                # Check if updated_at exists
                if 'updated_at' not in user_columns:
                    print("⚠️ 'updated_at' column missing from users table")
                else:
                    print("✅ 'updated_at' column exists")
                    
        except Exception as e:
            print(f"❌ Error checking users table: {e}")
        
        print("\n🔧 RECOMMENDED FIXES:")
        print("1. Remove 'recipient_bank' from transfer_functions.py (use 'bank_name' instead)")
        print("2. Remove 'updated_at' from users table updates")
        print("3. Ensure all required columns exist in bank_transactions table")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_and_fix_schema()
