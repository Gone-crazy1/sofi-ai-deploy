#!/usr/bin/env python3
"""
Debug script to investigate the duplicate key constraint issue
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def investigate_constraint_issue():
    """Investigate the users table constraint issue"""
    
    print("🔍 Investigating Supabase constraint issue...")
    
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ Missing Supabase credentials")
            return
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Check current users table structure
        print("\n1️⃣ Checking users table structure...")
        try:
            result = supabase.table("users").select("*").limit(5).execute()
            print(f"✅ Users table accessible - {len(result.data)} records found")
            
            if result.data:
                print("📋 Sample user record structure:")
                for key, value in result.data[0].items():
                    print(f"   {key}: {value}")
        except Exception as e:
            print(f"❌ Error accessing users table: {e}")
            return
        
        # 2. Check for records with account_number = "No"
        print("\n2️⃣ Checking for problematic records...")
        try:
            no_records = supabase.table("users").select("*").eq("account_number", "No").execute()
            print(f"🔍 Records with account_number='No': {len(no_records.data)}")
            
            if no_records.data:
                print("⚠️ Found problematic records:")
                for record in no_records.data:
                    print(f"   ID: {record.get('id')}, Name: {record.get('first_name')} {record.get('last_name')}")
        except Exception as e:
            print(f"❌ Error checking problematic records: {e}")
        
        # 3. Check for NULL account_numbers
        print("\n3️⃣ Checking for NULL account_numbers...")
        try:
            null_records = supabase.table("users").select("*").is_("account_number", "null").execute()
            print(f"🔍 Records with NULL account_number: {len(null_records.data)}")
        except Exception as e:
            print(f"❌ Error checking NULL records: {e}")
        
        # 4. Check all unique account_numbers
        print("\n4️⃣ Checking unique account_numbers...")
        try:
            all_users = supabase.table("users").select("id, first_name, last_name, account_number").execute()
            account_numbers = {}
            
            for user in all_users.data:
                acc_num = user.get('account_number', 'NULL')
                if acc_num not in account_numbers:
                    account_numbers[acc_num] = 0
                account_numbers[acc_num] += 1
            
            print("📊 Account number frequency:")
            for acc_num, count in account_numbers.items():
                if count > 1 or acc_num in ['No', 'NULL', None]:
                    print(f"   {acc_num}: {count} occurrences {'⚠️' if count > 1 else ''}")
                    
        except Exception as e:
            print(f"❌ Error checking account numbers: {e}")
        
        # 5. Analyze the issue
        print("\n🎯 ISSUE ANALYSIS:")
        print("The error suggests that:")
        print("1. Your users table has a UNIQUE constraint on 'account_number'")
        print("2. There's already a record with account_number = 'No'")
        print("3. New user registration is trying to insert another 'No' value")
        print("4. This likely happens when account_number is not properly set")
        
        print("\n🔧 RECOMMENDED SOLUTIONS:")
        print("1. Remove the unique constraint on account_number (if not needed)")
        print("2. Clean up existing 'No' values in the database")
        print("3. Fix the code to not insert 'No' as account_number")
        print("4. Make account_number nullable if it's not always available")
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")

if __name__ == "__main__":
    investigate_constraint_issue()
