#!/usr/bin/env python3
"""
🚀 DEPLOY ALL MISSING SOFI AI TABLES
====================================

This script:
1. Checks for the missing bank_transactions table
2. Deploys all 6 missing tables via SQL execution
3. Verifies deployment success
4. Creates fee collection integration functions

Tables to deploy:
- bank_transactions (for transaction logging)
- sofi_financial_summary (main revenue table)
- crypto_trades (crypto transaction details)
- airtime_sales (airtime purchase tracking)
- data_sales (data bundle tracking)
- transfer_charges (transfer fee collection)
- deposit_fees (deposit fee tracking)
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials. Check your .env file.")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists by trying to query it"""
    try:
        result = supabase.table(table_name).select("*").limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e).lower() or "404" in str(e):
            return False
        print(f"⚠️ Error checking {table_name}: {e}")
        return False

def deploy_tables_via_sql():
    """Deploy all missing tables using SQL execution"""
    
    # Complete SQL for all missing tables
    complete_sql = """
-- 🏦 SOFI AI COMPLETE DATABASE SCHEMA DEPLOYMENT
-- This includes all missing tables for the Sofi AI system

-- 1. Bank Transactions Table (Missing from transfer fixes)
CREATE TABLE IF NOT EXISTS bank_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id TEXT NOT NULL,
    transaction_reference TEXT UNIQUE NOT NULL,
    amount NUMERIC NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('credit', 'debit', 'transfer')),
    account_number TEXT,
    bank_name TEXT,
    recipient_name TEXT,
    narration TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed')),
    webhook_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Main Financial Summary Table
CREATE TABLE IF NOT EXISTS sofi_financial_summary (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    total_revenue NUMERIC DEFAULT 0,
    total_crypto_received_usdt NUMERIC DEFAULT 0,
    total_crypto_received_btc NUMERIC DEFAULT 0,
    total_naira_debited_for_crypto NUMERIC DEFAULT 0,
    total_crypto_profit NUMERIC DEFAULT 0,
    total_transfer_revenue NUMERIC DEFAULT 0,
    total_airtime_revenue NUMERIC DEFAULT 0,
    total_data_revenue NUMERIC DEFAULT 0,
    total_crypto_debit NUMERIC DEFAULT 0,
    total_airtime_amount_sold NUMERIC DEFAULT 0,
    total_data_amount_sold NUMERIC DEFAULT 0,
    total_crypto_naira_paid NUMERIC DEFAULT 0,
    total_conversion_rate_avg NUMERIC DEFAULT 0,
    total_transfer_fee_collected NUMERIC DEFAULT 0,
    total_deposit_fee_collected NUMERIC DEFAULT 0,
    total_personal_withdrawal NUMERIC DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Crypto Trades Tracking
CREATE TABLE IF NOT EXISTS crypto_trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT', 'ETH')),
    crypto_amount NUMERIC NOT NULL,
    naira_equivalent NUMERIC NOT NULL,
    conversion_rate_used NUMERIC NOT NULL,
    profit_made_on_trade NUMERIC DEFAULT 0,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Airtime Sales Tracking
CREATE TABLE IF NOT EXISTS airtime_sales (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    network TEXT NOT NULL CHECK (network IN ('MTN', 'Airtel', 'Glo', '9mobile')),
    amount_sold NUMERIC NOT NULL,
    sale_price NUMERIC NOT NULL,
    cost_price NUMERIC NOT NULL,
    profit NUMERIC GENERATED ALWAYS AS (sale_price - cost_price) STORED,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Data Sales Tracking
CREATE TABLE IF NOT EXISTS data_sales (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    network TEXT NOT NULL CHECK (network IN ('MTN', 'Airtel', 'Glo', '9mobile')),
    bundle_size TEXT NOT NULL,
    amount_sold NUMERIC NOT NULL,
    sale_price NUMERIC NOT NULL,
    cost_price NUMERIC NOT NULL,
    profit NUMERIC GENERATED ALWAYS AS (sale_price - cost_price) STORED,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Transfer Charges Tracking
CREATE TABLE IF NOT EXISTS transfer_charges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transfer_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    transaction_reference TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Deposit Fees Tracking
CREATE TABLE IF NOT EXISTS deposit_fees (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    deposit_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    fee_type TEXT DEFAULT 'bank_deposit',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_bank_transactions_user_id ON bank_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_reference ON bank_transactions(transaction_reference);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_created_at ON bank_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_chat_id ON crypto_trades(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_timestamp ON crypto_trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_airtime_sales_chat_id ON airtime_sales(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_data_sales_chat_id ON data_sales(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transfer_charges_chat_id ON transfer_charges(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_deposit_fees_chat_id ON deposit_fees(telegram_chat_id);

-- 9. Initialize the main summary record (run once)
INSERT INTO sofi_financial_summary DEFAULT VALUES 
ON CONFLICT DO NOTHING;

-- 10. Revenue calculation function
CREATE OR REPLACE FUNCTION calculate_total_revenue()
RETURNS NUMERIC AS $$
DECLARE
    revenue NUMERIC := 0;
BEGIN
    SELECT 
        COALESCE(SUM(profit_made_on_trade), 0) +
        COALESCE((SELECT SUM(profit) FROM airtime_sales), 0) +
        COALESCE((SELECT SUM(profit) FROM data_sales), 0) +
        COALESCE((SELECT SUM(fee_charged) FROM transfer_charges), 0) +
        COALESCE((SELECT SUM(fee_charged) FROM deposit_fees), 0)
    INTO revenue
    FROM crypto_trades;
    
    RETURN revenue;
END;
$$ LANGUAGE plpgsql;

-- 11. Update summary trigger function
CREATE OR REPLACE FUNCTION update_financial_summary()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE sofi_financial_summary 
    SET 
        total_revenue = calculate_total_revenue(),
        total_crypto_profit = (SELECT COALESCE(SUM(profit_made_on_trade), 0) FROM crypto_trades),
        total_airtime_revenue = (SELECT COALESCE(SUM(profit), 0) FROM airtime_sales),
        total_data_revenue = (SELECT COALESCE(SUM(profit), 0) FROM data_sales),
        total_transfer_fee_collected = (SELECT COALESCE(SUM(fee_charged), 0) FROM transfer_charges),
        total_deposit_fee_collected = (SELECT COALESCE(SUM(fee_charged), 0) FROM deposit_fees),
        last_updated = NOW()
    WHERE id = (SELECT id FROM sofi_financial_summary LIMIT 1);
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 12. Enable Row Level Security for all tables
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE airtime_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;
ALTER TABLE deposit_fees ENABLE ROW LEVEL SECURITY;

-- 13. Create policies for service role access
CREATE POLICY "Service role can manage bank transactions" ON bank_transactions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage financial summary" ON sofi_financial_summary
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage crypto trades" ON crypto_trades
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage airtime sales" ON airtime_sales
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage data sales" ON data_sales
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage transfer charges" ON transfer_charges
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage deposit fees" ON deposit_fees
    FOR ALL USING (auth.role() = 'service_role');
"""
    
    try:
        print("🚀 Executing SQL deployment...")
        
        # Try to execute the SQL using the RPC call method
        result = supabase.rpc('query', {'query': complete_sql}).execute()
        
        if result:
            print("✅ SQL executed successfully!")
            return True
        else:
            print("⚠️ SQL execution completed with no errors")
            return True
            
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        print("\n📋 MANUAL DEPLOYMENT REQUIRED:")
        print("The SQL needs to be run manually in Supabase SQL Editor.")
        
        # Save the SQL to a file for manual execution
        with open("complete_sofi_database_schema.sql", "w") as f:
            f.write(complete_sql)
        
        print("💾 Complete SQL saved to: complete_sofi_database_schema.sql")
        dashboard_url = SUPABASE_URL.replace('/rest/v1', '') + '/project/default/sql'
        print(f"🔗 Supabase SQL Editor: {dashboard_url}")
        return False

def verify_deployment():
    """Verify all tables were created successfully"""
    tables_to_check = [
        "bank_transactions",
        "sofi_financial_summary", 
        "crypto_trades",
        "airtime_sales",
        "data_sales", 
        "transfer_charges",
        "deposit_fees"
    ]
    
    print("\n🔍 Verifying table deployment...")
    
    existing_tables = []
    missing_tables = []
    
    for table in tables_to_check:
        if check_table_exists(table):
            existing_tables.append(table)
            print(f"✅ {table} - EXISTS")
        else:
            missing_tables.append(table)
            print(f"❌ {table} - MISSING")
    
    return existing_tables, missing_tables

def main():
    print("🚀 SOFI AI COMPLETE DATABASE DEPLOYMENT")
    print("=" * 50)
    
    print(f"🔗 Supabase URL: {SUPABASE_URL}")
    
    # Check current state
    print("\n🔍 Checking current table status...")
    existing_before, missing_before = verify_deployment()
    
    if not missing_before:
        print("\n🎉 ALL TABLES ALREADY EXIST!")
        print("✅ Your Sofi AI database is complete.")
        return
    
    print(f"\n📊 Current Status:")
    print(f"✅ Existing: {len(existing_before)}")
    print(f"❌ Missing: {len(missing_before)}")
    
    print(f"\n🚀 Deploying {len(missing_before)} missing tables...")
    
    # Deploy tables
    deployment_success = deploy_tables_via_sql()
    
    if deployment_success:
        print("\n🔍 Re-verifying after deployment...")
        existing_after, missing_after = verify_deployment()
        
        if not missing_after:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("✅ All 7 tables are now deployed:")
            for table in existing_after:
                print(f"   • {table}")
            
            print("\n📈 Your Sofi AI revenue tracking system is ready!")
            print("🔧 Next: Integrate fee collection into your backend")
            
        else:
            print(f"\n⚠️ Partial deployment - {len(missing_after)} tables still missing")
            for table in missing_after:
                print(f"   • {table}")
    
    else:
        print("\n📋 MANUAL DEPLOYMENT INSTRUCTIONS:")
        print("1. Go to your Supabase dashboard SQL Editor")
        print("2. Copy the SQL from 'complete_sofi_database_schema.sql'")
        print("3. Run it in the SQL Editor")
        print("4. Re-run this script to verify")

if __name__ == "__main__":
    main()
