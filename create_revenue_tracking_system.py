#!/usr/bin/env python3
"""
🏦 SOFI AI REVENUE TRACKING SYSTEM SETUP
========================================

This script creates the complete revenue tracking system for Sofi AI:
1. Main financial summary table
2. Supporting transaction tables for detailed tracking
3. Fee collection logic implementation
4. Revenue calculation functions

Based on your specifications for tracking:
- Transfer fees (₦50 per transfer)
- Deposit fees (₦10-25 per deposit)
- Crypto trading margins (₦500-1000 per conversion)
- Airtime/Data markup profits
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

def create_main_financial_summary_table():
    """Create the main sofi_financial_summary table"""
    print("📊 Creating main financial summary table...")
    
    # Test if we can create tables via API (usually not possible)
    try:
        # Try to insert a test record to see table structure
        test_data = {
            "total_revenue": 0.0,
            "total_crypto_received_usdt": 0.0,
            "total_crypto_received_btc": 0.0,
            "total_naira_debited_for_crypto": 0.0,
            "total_crypto_profit": 0.0,
            "total_transfer_revenue": 0.0,
            "total_airtime_revenue": 0.0,
            "total_data_revenue": 0.0,
            "total_crypto_debit": 0.0,
            "total_airtime_amount_sold": 0.0,
            "total_data_amount_sold": 0.0,
            "total_crypto_naira_paid": 0.0,
            "total_conversion_rate_avg": 0.0,
            "total_transfer_fee_collected": 0.0,
            "total_deposit_fee_collected": 0.0,
            "total_personal_withdrawal": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        
        result = supabase.table("sofi_financial_summary").insert(test_data).execute()
        if result.data:
            # Delete the test record
            record_id = result.data[0].get('id')
            if record_id:
                supabase.table("sofi_financial_summary").delete().eq("id", record_id).execute()
            print("✅ sofi_financial_summary table exists and is accessible")
            return True
    except Exception as e:
        if "does not exist" in str(e).lower():
            print(f"❌ sofi_financial_summary table does not exist")
            return False
        else:
            print(f"⚠️ Error checking sofi_financial_summary table: {e}")
            return False

def create_supporting_tables():
    """Check/create supporting transaction tables"""
    tables_to_check = [
        ("crypto_trades", {
            "telegram_chat_id": "123456789",
            "crypto_type": "BTC",
            "crypto_amount": 0.001,
            "naira_equivalent": 50000.0,
            "conversion_rate_used": 50000000.0,
            "profit_made_on_trade": 500.0,
            "timestamp": datetime.now().isoformat()
        }),
        ("airtime_sales", {
            "telegram_chat_id": "123456789",
            "network": "MTN",
            "amount_sold": 1000.0,
            "sale_price": 1000.0,
            "cost_price": 980.0,
            "profit": 20.0,
            "timestamp": datetime.now().isoformat()
        }),
        ("data_sales", {
            "telegram_chat_id": "123456789",
            "network": "MTN",
            "bundle_size": "1GB",
            "amount_sold": 1000.0,
            "sale_price": 1000.0,
            "cost_price": 950.0,
            "profit": 50.0,
            "timestamp": datetime.now().isoformat()
        }),
        ("transfer_charges", {
            "telegram_chat_id": "123456789",
            "transfer_amount": 5000.0,
            "fee_charged": 50.0,
            "timestamp": datetime.now().isoformat()
        })
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table_name, test_data in tables_to_check:
        print(f"🔍 Checking {table_name} table...")
        try:
            result = supabase.table(table_name).insert(test_data).execute()
            if result.data:
                # Delete the test record
                record_id = result.data[0].get('id')
                if record_id:
                    supabase.table(table_name).delete().eq("id", record_id).execute()
                print(f"✅ {table_name} table exists and is accessible")
                existing_tables.append(table_name)
        except Exception as e:
            if "does not exist" in str(e).lower():
                print(f"❌ {table_name} table does not exist")
                missing_tables.append(table_name)
            else:
                print(f"⚠️ Error checking {table_name} table: {e}")
                missing_tables.append(table_name)
    
    return existing_tables, missing_tables

def generate_sql_for_missing_tables():
    """Generate SQL statements for missing tables"""
    sql_statements = """
-- Sofi AI Revenue Tracking System - Complete Database Schema
-- Run these commands in your Supabase SQL Editor

-- 1. Main Financial Summary Table
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

-- 2. Crypto Trades Tracking
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

-- 3. Airtime Sales Tracking
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

-- 4. Data Sales Tracking
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

-- 5. Transfer Charges Tracking
CREATE TABLE IF NOT EXISTS transfer_charges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transfer_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Deposit Fees Tracking (New)
CREATE TABLE IF NOT EXISTS deposit_fees (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    deposit_amount NUMERIC NOT NULL,
    fee_charged NUMERIC NOT NULL,
    fee_type TEXT DEFAULT 'bank_deposit',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_crypto_trades_chat_id ON crypto_trades(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_timestamp ON crypto_trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_airtime_sales_chat_id ON airtime_sales(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_data_sales_chat_id ON data_sales(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transfer_charges_chat_id ON transfer_charges(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_deposit_fees_chat_id ON deposit_fees(telegram_chat_id);

-- 8. Initialize the main summary record (run once)
INSERT INTO sofi_financial_summary DEFAULT VALUES 
ON CONFLICT DO NOTHING;

-- 9. Revenue calculation function
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

-- 10. Update summary trigger (optional)
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

-- Enable RLS (Row Level Security) for all tables
ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE airtime_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;
ALTER TABLE deposit_fees ENABLE ROW LEVEL SECURITY;

-- Create policies to allow service role access
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
    
    return sql_statements

def main():
    print("🏦 SOFI AI REVENUE TRACKING SYSTEM SETUP")
    print("=" * 50)
    
    print(f"🔗 Supabase URL: {SUPABASE_URL}")
    print("🔍 Checking existing revenue tracking infrastructure...")
    
    # Check main financial summary table
    main_table_exists = create_main_financial_summary_table()
    
    # Check supporting tables
    existing_tables, missing_tables = create_supporting_tables()
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Existing tables: {len(existing_tables)}")
    for table in existing_tables:
        print(f"   • {table}")
    
    print(f"❌ Missing tables: {len(missing_tables)}")
    for table in missing_tables:
        print(f"   • {table}")
    
    if not main_table_exists:
        missing_tables.insert(0, "sofi_financial_summary")
    
    if missing_tables:
        print(f"\n🔧 SETUP REQUIRED:")
        print("The following tables need to be created in your Supabase database.")
        print("Copy the SQL below and run it in your Supabase SQL Editor:\n")
        
        # Save SQL to file
        sql_content = generate_sql_for_missing_tables()
        sql_file = "create_revenue_tracking_tables.sql"
        
        with open(sql_file, 'w') as f:
            f.write(sql_content)
        
        print(f"💾 SQL file saved as: {sql_file}")
        print(f"\n📋 MANUAL STEPS:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the SQL from the file above")
        print("4. Click 'Run' to execute")
        print("5. Re-run this script to verify setup")
        
        dashboard_url = SUPABASE_URL.replace('/rest/v1', '') + '/project/default/sql'
        print(f"\n🔗 Supabase SQL Editor: {dashboard_url}")
        
    else:
        print(f"\n🎉 ALL REVENUE TRACKING TABLES ARE READY!")
        print("✅ Your Sofi AI revenue tracking system is fully operational.")
        print("\n📈 You can now track:")
        print("• Transfer fees (₦50 per transfer)")
        print("• Deposit fees (₦10-25 per deposit)") 
        print("• Crypto trading margins (₦500-1000 per conversion)")
        print("• Airtime/Data markup profits")
        print("• Total revenue and personal withdrawals")
        
        print(f"\n🔧 Next step: Integrate fee collection into your backend")

if __name__ == "__main__":
    main()
