#!/usr/bin/env python3
"""
Quick check of what tables exist in Supabase
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_table_exists(table_name):
    """Check if a table exists by trying to query it"""
    try:
        result = supabase.table(table_name).select("*").limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e).lower() or "relation" in str(e).lower():
            return False
        else:
            print(f"   Error checking {table_name}: {e}")
            return False

def main():
    print("🔍 CHECKING EXISTING TABLES IN SUPABASE")
    print("=" * 45)
    
    # Original tables (should exist)
    original_tables = [
        "users",
        "virtual_accounts", 
        "beneficiaries",
        "chat_history",
        "bank_transactions"
    ]
    
    # Revenue tracking tables (checking if added)
    revenue_tables = [
        "sofi_financial_summary",
        "crypto_trades",
        "airtime_sales",
        "data_sales", 
        "transfer_charges"
    ]
    
    print("\n📋 ORIGINAL SYSTEM TABLES:")
    existing_original = 0
    for table in original_tables:
        exists = check_table_exists(table)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {table:<20} | {status}")
        if exists:
            existing_original += 1
    
    print(f"\n📊 Original tables: {existing_original}/{len(original_tables)} exist")
    
    print("\n💰 REVENUE TRACKING TABLES:")
    existing_revenue = 0
    for table in revenue_tables:
        exists = check_table_exists(table)
        status = "✅ EXISTS" if exists else "❌ NOT ADDED"
        print(f"  {table:<20} | {status}")
        if exists:
            existing_revenue += 1
    
    print(f"\n💰 Revenue tables: {existing_revenue}/{len(revenue_tables)} exist")
    
    total_tables = existing_original + existing_revenue
    print("\n" + "=" * 45)
    print(f"TOTAL TABLES IN SUPABASE: {total_tables}")
    
    if existing_revenue == 0:
        print("\n🚨 REVENUE TRACKING SYSTEM NOT DEPLOYED")
        print("   The revenue tracking tables need to be created manually")
        print("   in the Supabase dashboard or via SQL.")
    elif existing_revenue < len(revenue_tables):
        print(f"\n⚠️  PARTIAL REVENUE SYSTEM: {existing_revenue}/{len(revenue_tables)} tables")
    else:
        print("\n✅ COMPLETE REVENUE TRACKING SYSTEM DEPLOYED")

if __name__ == "__main__":
    main()
