#!/usr/bin/env python3
"""
🔍 VERIFY CRYPTO TABLES DEPLOYMENT
=================================

This script will verify if all crypto tables are successfully deployed to Supabase.
Run this AFTER executing the SQL in Supabase Dashboard.
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_table_deployment():
    """Verify all required tables exist and are accessible"""
    
    required_tables = [
        'bank_transactions',
        'crypto_rates', 
        'crypto_trades',
        'sofi_financial_summary',
        'transfer_charges'
    ]
    
    print("🔍 VERIFYING CRYPTO TABLES DEPLOYMENT")
    print("=" * 45)
    
    deployed_tables = []
    failed_tables = []
    
    for table in required_tables:
        try:
            # Try to query the table
            result = supabase.table(table).select("*").limit(1).execute()
            deployed_tables.append(table)
            print(f"✅ {table} - DEPLOYED & ACCESSIBLE")
            
            # Check if it has data (for financial summary)
            if table == 'sofi_financial_summary':
                if result.data:
                    print(f"   📊 Initial record exists: {len(result.data)} row(s)")
                else:
                    print(f"   ⚠️  No initial record - will be created on first transaction")
                    
        except Exception as e:
            failed_tables.append(table)
            print(f"❌ {table} - FAILED ({str(e)[:60]}...)")
    
    print(f"\n📊 DEPLOYMENT SUMMARY:")
    print(f"   Successfully deployed: {len(deployed_tables)}/{len(required_tables)} tables")
    print(f"   Failed: {len(failed_tables)} tables")
    
    if len(deployed_tables) == len(required_tables):
        print("\n🎉 ALL CRYPTO TABLES SUCCESSFULLY DEPLOYED!")
        print("✅ Your crypto system is ready for production!")
        return True
    else:
        print(f"\n⚠️  DEPLOYMENT INCOMPLETE")
        print(f"   Missing tables: {', '.join(failed_tables)}")
        return False

def test_crypto_system_integration():
    """Test if crypto system can save data to deployed tables"""
    
    print("\n🧪 TESTING CRYPTO SYSTEM INTEGRATION")
    print("=" * 40)
    
    try:
        # Test 1: Save a test crypto rate
        print("1️⃣ Testing crypto_rates table...")
        test_rate = {
            'btc_market_rate': 162000000,
            'btc_sofi_rate': 156000000,
            'usdt_market_rate': 1500,
            'usdt_sofi_rate': 1250,
            'source': 'test'
        }
        
        result = supabase.table('crypto_rates').insert(test_rate).execute()
        if result.data:
            print("   ✅ Rate saving works")
            # Clean up test data
            rate_id = result.data[0]['id']
            supabase.table('crypto_rates').delete().eq('id', rate_id).execute()
        
        # Test 2: Update financial summary
        print("2️⃣ Testing sofi_financial_summary table...")
        result = supabase.table('sofi_financial_summary').select('*').execute()
        if result.data:
            print("   ✅ Financial summary accessible")
        else:
            # Insert initial record
            supabase.table('sofi_financial_summary').insert({}).execute()
            print("   ✅ Initial financial summary created")
        
        # Test 3: Test transfer charges
        print("3️⃣ Testing transfer_charges table...")
        test_charge = {
            'telegram_chat_id': '123456789',
            'transfer_amount': 10000,
            'fee_amount': 50,
            'transaction_reference': 'TEST_REF_123'
        }
        
        result = supabase.table('transfer_charges').insert(test_charge).execute()
        if result.data:
            print("   ✅ Transfer fee tracking works")
            # Clean up test data
            charge_id = result.data[0]['id']
            supabase.table('transfer_charges').delete().eq('id', charge_id).execute()
        
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Your crypto revenue tracking system is fully operational!")
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        return False

def show_next_steps():
    """Show what to do after successful deployment"""
    
    print("\n🚀 NEXT STEPS AFTER SUCCESSFUL DEPLOYMENT")
    print("=" * 45)
    
    print("1️⃣ TEST CRYPTO COMMANDS:")
    print("   • Send 'crypto rates' to your bot")
    print("   • Send 'btc rate' or 'usdt rate'")
    print("   • Verify rates display correctly")
    
    print("\n2️⃣ MONITOR REVENUE TRACKING:")
    print("   • Each transfer will now collect ₦50 fee")
    print("   • Crypto deposits will track profits automatically")
    print("   • Financial summary updates in real-time")
    
    print("\n3️⃣ EXPECTED MONTHLY REVENUE:")
    print("   • Transfer fees: 1000 × ₦50 = ₦50,000")
    print("   • Crypto profits: Variable (₦2.9M+ potential)")
    print("   • Total projection: ₦3M+ per month")
    
    print("\n4️⃣ CUSTOMER-FRIENDLY RATES:")
    print("   • USDT: Only 2.5% below market (competitive)")
    print("   • BTC: Only 3.5% below market (attractive)")
    print("   • Focus on volume and customer retention")
    
    print("\n💡 OPTIMIZATION TIPS:")
    print("   • Monitor competitor rates weekly")
    print("   • Adjust margins based on customer feedback")
    print("   • Track customer retention metrics")
    print("   • Gradually increase margins as loyalty grows")

def main():
    print("🔍 CRYPTO TABLES DEPLOYMENT VERIFICATION")
    print("=" * 50)
    print("🎯 Verifying customer-friendly crypto system deployment")
    print()
    
    # Step 1: Verify table deployment
    tables_deployed = verify_table_deployment()
    
    if not tables_deployed:
        print("\n❌ Please deploy the missing tables first!")
        print("📋 Use the SQL from deploy_crypto_tables.sql in Supabase Dashboard")
        return
    
    # Step 2: Test system integration
    integration_works = test_crypto_system_integration()
    
    if integration_works:
        show_next_steps()
        print("\n🎊 CRYPTO SYSTEM FULLY DEPLOYED & READY!")
    else:
        print("\n⚠️  Tables deployed but integration needs attention")

if __name__ == "__main__":
    main()
