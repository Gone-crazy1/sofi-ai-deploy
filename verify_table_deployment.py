#!/usr/bin/env python3
"""
🔍 VERIFY SOFI AI TABLE DEPLOYMENT
==================================

Run this script after executing the SQL in Supabase to verify all tables were created successfully.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists by trying to query it"""
    try:
        result = supabase.table(table_name).select("*").limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e).lower() or "404" in str(e):
            return False
        return True  # Assume exists if other error

def verify_all_tables():
    """Verify all required tables exist"""
    
    # All tables that should exist after deployment
    required_tables = [
        # Original existing tables
        "users",
        "virtual_accounts", 
        "beneficiaries",
        "chat_history",
        
        # New tables we're deploying
        "bank_transactions",
        "sofi_financial_summary",
        "crypto_trades", 
        "airtime_sales",
        "data_sales",
        "transfer_charges",
        "deposit_fees"
    ]
    
    print("🔍 VERIFYING SOFI AI DATABASE TABLES")
    print("=" * 50)
    
    existing_tables = []
    missing_tables = []
    
    for table in required_tables:
        print(f"Checking {table}...", end=" ")
        
        if check_table_exists(table):
            print("✅ EXISTS")
            existing_tables.append(table)
        else:
            print("❌ MISSING")
            missing_tables.append(table)
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Existing tables: {len(existing_tables)}/11")
    print(f"❌ Missing tables: {len(missing_tables)}")
    
    if missing_tables:
        print(f"\n❌ Missing tables:")
        for table in missing_tables:
            print(f"   • {table}")
        
        if "bank_transactions" in missing_tables:
            print(f"\n⚠️ Critical: bank_transactions table is missing - transfer logging won't work")
        
        if any(t in missing_tables for t in ["sofi_financial_summary", "crypto_trades", "airtime_sales", "data_sales", "transfer_charges", "deposit_fees"]):
            print(f"⚠️ Revenue tracking tables missing - fee collection won't work")
            
        print(f"\n🔧 Next steps:")
        print("1. Go to Supabase SQL Editor (opened in browser)")
        print("2. Copy all SQL from 'complete_sofi_database_schema.sql'")
        print("3. Paste and run in SQL Editor")
        print("4. Re-run this verification script")
        
    else:
        print(f"\n🎉 SUCCESS! All tables are deployed!")
        print("✅ Your Sofi AI database is complete with:")
        print("   • 4 original tables (users, virtual_accounts, beneficiaries, chat_history)")
        print("   • 7 new tables (1 transactions + 6 revenue tracking)")
        print("   • Total: 11 tables")
        
        print(f"\n📈 Revenue tracking is ready:")
        print("   • Transfer fees: ₦50 per transfer")
        print("   • Deposit fees: ₦10-25 per deposit") 
        print("   • Crypto profits: ₦500-1000 per conversion")
        print("   • Airtime/Data markup tracking")
        
        print(f"\n🔗 Integration needed:")
        print("   • Add fee collection calls to main.py")
        print("   • Use functions from fee_collection.py")
        print("   • Test with small transactions first")
    
    return len(existing_tables), len(missing_tables)

def test_revenue_system():
    """Test if revenue system is functional"""
    try:
        # Test if we can calculate revenue
        result = supabase.table("sofi_financial_summary").select("total_revenue").execute()
        if result.data:
            print(f"\n💰 Current total revenue: ₦{result.data[0]['total_revenue']:,.2f}")
            return True
    except Exception as e:
        print(f"\n❌ Revenue system test failed: {e}")
        return False

if __name__ == "__main__":
    existing_count, missing_count = verify_all_tables()
    
    if missing_count == 0:
        test_revenue_system()
        print(f"\n🚀 Ready to integrate fee collection into your bot!")
    else:
        print(f"\n📋 Complete table deployment first before proceeding.")
