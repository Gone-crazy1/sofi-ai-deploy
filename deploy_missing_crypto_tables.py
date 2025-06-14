#!/usr/bin/env python3
"""
Check current Supabase tables and deploy missing crypto tables
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_existing_tables():
    """Check what tables currently exist"""
    expected_tables = [
        'users',
        'virtual_accounts', 
        'beneficiaries',
        'chat_history',
        'bank_transactions',
        'crypto_rates',
        'crypto_trades',
        'sofi_financial_summary',
        'transfer_charges'
    ]
    
    existing_tables = []
    missing_tables = []
    
    print("🔍 CHECKING CURRENT SUPABASE TABLES")
    print("=" * 45)
    
    for table in expected_tables:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            existing_tables.append(table)
            print(f"✅ {table} - EXISTS")
        except Exception as e:
            missing_tables.append(table)
            print(f"❌ {table} - MISSING ({str(e)[:50]}...)")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Existing: {len(existing_tables)}/{len(expected_tables)} tables")
    print(f"   Missing: {len(missing_tables)} tables")
    
    return existing_tables, missing_tables

def deploy_missing_table(table_name):
    """Deploy a specific missing table"""
    
    table_sql = {
        'bank_transactions': """
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
            ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Enable all for service role" ON bank_transactions FOR ALL USING (true);
        """,
        
        'crypto_rates': """
            CREATE TABLE IF NOT EXISTS crypto_rates (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                btc_market_rate NUMERIC NOT NULL,
                btc_sofi_rate NUMERIC NOT NULL,
                usdt_market_rate NUMERIC NOT NULL,
                usdt_sofi_rate NUMERIC NOT NULL,
                source TEXT DEFAULT 'coingecko',
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            ALTER TABLE crypto_rates ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Enable all for service role" ON crypto_rates FOR ALL USING (true);
        """,
        
        'crypto_trades': """
            CREATE TABLE IF NOT EXISTS crypto_trades (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                telegram_chat_id TEXT NOT NULL,
                crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT')),
                crypto_amount NUMERIC NOT NULL,
                naira_equivalent NUMERIC NOT NULL,
                conversion_rate_used NUMERIC NOT NULL,
                profit_made NUMERIC DEFAULT 0,
                transaction_hash TEXT,
                status TEXT DEFAULT 'completed',
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Enable all for service role" ON crypto_trades FOR ALL USING (true);
        """,
        
        'sofi_financial_summary': """
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
                total_transfer_fee_collected NUMERIC DEFAULT 0,
                last_updated TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Enable all for service role" ON sofi_financial_summary FOR ALL USING (true);
            INSERT INTO sofi_financial_summary (id) VALUES (uuid_generate_v4()) ON CONFLICT DO NOTHING;
        """,
        
        'transfer_charges': """
            CREATE TABLE IF NOT EXISTS transfer_charges (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                telegram_chat_id TEXT NOT NULL,
                transfer_amount NUMERIC NOT NULL,
                fee_amount NUMERIC NOT NULL,
                transaction_reference TEXT,
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;
            CREATE POLICY "Enable all for service role" ON transfer_charges FOR ALL USING (true);
        """
    }
    
    if table_name not in table_sql:
        print(f"❌ No SQL definition for table: {table_name}")
        return False
    
    try:
        # Execute the SQL via RPC call (workaround for DDL)
        sql_commands = table_sql[table_name].strip().split(';')
        
        for sql_command in sql_commands:
            sql_command = sql_command.strip()
            if sql_command:
                try:
                    # Try to execute via RPC if available, otherwise skip DDL commands
                    if 'CREATE TABLE' in sql_command or 'ALTER TABLE' in sql_command or 'CREATE POLICY' in sql_command:
                        print(f"⚠️  DDL Command needs manual execution: {sql_command[:50]}...")
                    elif 'INSERT INTO' in sql_command:
                        # Try to parse INSERT command
                        if 'sofi_financial_summary' in sql_command:
                            # Try to insert initial record
                            try:
                                supabase.table('sofi_financial_summary').insert({}).execute()
                                print(f"✅ Initial record inserted for {table_name}")
                            except:
                                pass  # Table might not exist yet
                except Exception as e:
                    print(f"⚠️  Command execution issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying {table_name}: {e}")
        return False

def generate_manual_sql():
    """Generate SQL file for manual execution"""
    
    manual_sql = '''-- EXECUTE THIS IN SUPABASE SQL EDITOR
-- Missing Tables Deployment for Sofi AI

-- 1. Bank Transactions Table
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

-- 2. Crypto Rates Table
CREATE TABLE IF NOT EXISTS crypto_rates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    btc_market_rate NUMERIC NOT NULL,
    btc_sofi_rate NUMERIC NOT NULL,
    usdt_market_rate NUMERIC NOT NULL,
    usdt_sofi_rate NUMERIC NOT NULL,
    source TEXT DEFAULT 'coingecko',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Crypto Trades Table
CREATE TABLE IF NOT EXISTS crypto_trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    crypto_type TEXT NOT NULL CHECK (crypto_type IN ('BTC', 'USDT')),
    crypto_amount NUMERIC NOT NULL,
    naira_equivalent NUMERIC NOT NULL,
    conversion_rate_used NUMERIC NOT NULL,
    profit_made NUMERIC DEFAULT 0,
    transaction_hash TEXT,
    status TEXT DEFAULT 'completed',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Financial Summary Table
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
    total_transfer_fee_collected NUMERIC DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Transfer Charges Table  
CREATE TABLE IF NOT EXISTS transfer_charges (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transfer_amount NUMERIC NOT NULL,
    fee_amount NUMERIC NOT NULL,
    transaction_reference TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_rates ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE sofi_financial_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_charges ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies (Allow all operations for service role)
CREATE POLICY "Enable all operations" ON bank_transactions FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON crypto_rates FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON crypto_trades FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON sofi_financial_summary FOR ALL USING (true);
CREATE POLICY "Enable all operations" ON transfer_charges FOR ALL USING (true);

-- Insert initial financial summary record
INSERT INTO sofi_financial_summary (id) VALUES (uuid_generate_v4()) ON CONFLICT DO NOTHING;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_crypto_rates_timestamp ON crypto_rates(timestamp);
CREATE INDEX IF NOT EXISTS idx_crypto_trades_user ON crypto_trades(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_user ON bank_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transfer_charges_user ON transfer_charges(telegram_chat_id);

-- Verify table creation
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('bank_transactions', 'crypto_rates', 'crypto_trades', 'sofi_financial_summary', 'transfer_charges');
'''
    
    with open('MANUAL_DEPLOY_CRYPTO_TABLES.sql', 'w') as f:
        f.write(manual_sql)
    
    print(f"📄 Manual SQL file created: MANUAL_DEPLOY_CRYPTO_TABLES.sql")
    print("\n📋 MANUAL DEPLOYMENT STEPS:")
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the SQL from MANUAL_DEPLOY_CRYPTO_TABLES.sql")
    print("4. Click 'Run' to execute")
    print("5. Verify all tables are created")

def main():
    print("🚀 SUPABASE CRYPTO TABLES DEPLOYMENT")
    print("=" * 50)
    
    try:
        # Check existing tables
        existing, missing = check_existing_tables()
        
        if not missing:
            print("\n🎉 All tables already exist! No deployment needed.")
            return
        
        print(f"\n🔧 DEPLOYING {len(missing)} MISSING TABLES")
        print("=" * 35)
        
        # Generate manual SQL for deployment
        generate_manual_sql()
        
        print(f"\n⚠️  IMPORTANT:")
        print("Since Supabase API doesn't support DDL operations directly,")
        print("you need to manually execute the SQL in Supabase Dashboard.")
        print("\n📍 Supabase Dashboard URL:")
        print(f"   {SUPABASE_URL.replace('/rest/v1', '')}/project/default/sql")
        
    except Exception as e:
        print(f"❌ Error during deployment check: {e}")
        print("Please check your Supabase connection and try again.")

if __name__ == "__main__":
    main()
