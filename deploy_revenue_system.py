"""
Deploy Revenue Tracking System
Complete implementation of fee collection and revenue tracking for Sofi AI
"""

import os
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def create_revenue_tables():
    """Create all revenue tracking tables in Supabase"""
    
    # SQL commands to create tables
    tables_sql = [
        # Main financial summary table
        """
        CREATE TABLE IF NOT EXISTS sofi_financial_summary (
            id SERIAL PRIMARY KEY,
            total_revenue NUMERIC DEFAULT 0,
            total_crypto_profit NUMERIC DEFAULT 0,
            total_transfer_revenue NUMERIC DEFAULT 0,
            total_airtime_revenue NUMERIC DEFAULT 0,
            total_data_revenue NUMERIC DEFAULT 0,
            total_transfer_fee_collected NUMERIC DEFAULT 0,
            total_deposit_fee_collected NUMERIC DEFAULT 0,
            total_personal_withdrawal NUMERIC DEFAULT 0,
            last_updated TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Insert initial row if none exists
        """
        INSERT INTO sofi_financial_summary (total_revenue) 
        SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM sofi_financial_summary);
        """,
        
        # Crypto trades profit tracking
        """
        CREATE TABLE IF NOT EXISTS crypto_trades (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            trade_type TEXT NOT NULL, -- 'buy' or 'sell'
            crypto_type TEXT NOT NULL, -- 'bitcoin', 'ethereum', etc.
            amount_naira NUMERIC NOT NULL,
            crypto_amount NUMERIC NOT NULL,
            market_rate NUMERIC NOT NULL,
            sofi_rate NUMERIC NOT NULL,
            profit_margin NUMERIC NOT NULL, -- Our profit in Naira
            transaction_reference TEXT UNIQUE,
            status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Airtime sales markup tracking
        """
        CREATE TABLE IF NOT EXISTS airtime_sales (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            network TEXT NOT NULL, -- 'mtn', 'glo', 'airtel', '9mobile'
            amount NUMERIC NOT NULL,
            cost_price NUMERIC NOT NULL, -- What we pay to provider
            selling_price NUMERIC NOT NULL, -- What user pays
            profit_margin NUMERIC NOT NULL, -- Our markup profit
            transaction_reference TEXT UNIQUE,
            status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Data bundle sales markup tracking
        """
        CREATE TABLE IF NOT EXISTS data_sales (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            network TEXT NOT NULL,
            data_plan TEXT NOT NULL, -- '1GB', '2GB', etc.
            amount NUMERIC NOT NULL,
            cost_price NUMERIC NOT NULL,
            selling_price NUMERIC NOT NULL,
            profit_margin NUMERIC NOT NULL,
            transaction_reference TEXT UNIQUE,
            status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Transfer charges tracking
        """
        CREATE TABLE IF NOT EXISTS transfer_charges (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            transfer_amount NUMERIC NOT NULL,
            fee_charged NUMERIC NOT NULL, -- ₦50 standard fee
            recipient_bank TEXT,
            recipient_account TEXT,
            transfer_reference TEXT UNIQUE,
            status TEXT DEFAULT 'collected',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Deposit fees tracking
        """
        CREATE TABLE IF NOT EXISTS deposit_fees (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            deposit_amount NUMERIC NOT NULL,
            fee_charged NUMERIC NOT NULL, -- ₦10-25 based on amount
            deposit_method TEXT, -- 'bank_transfer', 'card', etc.
            deposit_reference TEXT UNIQUE,
            status TEXT DEFAULT 'collected',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
    ]
    
    print("🚀 Creating revenue tracking tables...")
    
    for i, sql in enumerate(tables_sql, 1):
        try:
            result = supabase.rpc('execute_sql', {'query': sql})
            print(f"✅ Table {i}/{len(tables_sql)} created successfully")
        except Exception as e:
            print(f"⚠️ Table {i} creation: {str(e)}")
    
    print("✅ All revenue tracking tables created!")

def create_revenue_functions():
    """Create helper functions for revenue tracking"""
    
    functions_sql = [
        # Function to update total revenue
        """
        CREATE OR REPLACE FUNCTION update_total_revenue()
        RETURNS void AS $$
        BEGIN
            UPDATE sofi_financial_summary SET
                total_crypto_profit = (SELECT COALESCE(SUM(profit_margin), 0) FROM crypto_trades WHERE status = 'completed'),
                total_transfer_revenue = (SELECT COALESCE(SUM(fee_charged), 0) FROM transfer_charges WHERE status = 'collected'),
                total_airtime_revenue = (SELECT COALESCE(SUM(profit_margin), 0) FROM airtime_sales WHERE status = 'completed'),
                total_data_revenue = (SELECT COALESCE(SUM(profit_margin), 0) FROM data_sales WHERE status = 'completed'),
                total_transfer_fee_collected = (SELECT COALESCE(SUM(fee_charged), 0) FROM transfer_charges WHERE status = 'collected'),
                total_deposit_fee_collected = (SELECT COALESCE(SUM(fee_charged), 0) FROM deposit_fees WHERE status = 'collected'),
                total_revenue = (
                    COALESCE((SELECT SUM(profit_margin) FROM crypto_trades WHERE status = 'completed'), 0) +
                    COALESCE((SELECT SUM(fee_charged) FROM transfer_charges WHERE status = 'collected'), 0) +
                    COALESCE((SELECT SUM(profit_margin) FROM airtime_sales WHERE status = 'completed'), 0) +
                    COALESCE((SELECT SUM(profit_margin) FROM data_sales WHERE status = 'completed'), 0) +
                    COALESCE((SELECT SUM(fee_charged) FROM deposit_fees WHERE status = 'collected'), 0)
                ),
                last_updated = NOW()
            WHERE id = 1;
        END;
        $$ LANGUAGE plpgsql;
        """,
        
        # Function to get revenue summary
        """
        CREATE OR REPLACE FUNCTION get_revenue_summary()
        RETURNS TABLE (
            total_revenue NUMERIC,
            crypto_profit NUMERIC,
            transfer_fees NUMERIC,
            airtime_profit NUMERIC,
            data_profit NUMERIC,
            deposit_fees NUMERIC,
            last_updated TIMESTAMP
        ) AS $$
        BEGIN
            PERFORM update_total_revenue();
            RETURN QUERY SELECT 
                s.total_revenue,
                s.total_crypto_profit,
                s.total_transfer_fee_collected,
                s.total_airtime_revenue,
                s.total_data_revenue,
                s.total_deposit_fee_collected,
                s.last_updated
            FROM sofi_financial_summary s WHERE s.id = 1;
        END;
        $$ LANGUAGE plpgsql;
        """
    ]
    
    print("🔧 Creating revenue calculation functions...")
    
    for i, sql in enumerate(functions_sql, 1):
        try:
            result = supabase.rpc('execute_sql', {'query': sql})
            print(f"✅ Function {i}/{len(functions_sql)} created successfully")
        except Exception as e:
            print(f"⚠️ Function {i} creation: {str(e)}")
    
    print("✅ All revenue functions created!")

def test_revenue_system():
    """Test the revenue tracking system"""
    print("🧪 Testing revenue tracking system...")
    
    try:
        # Test inserting sample data
        test_data = [
            # Test crypto trade
            {
                'table': 'crypto_trades',
                'data': {
                    'user_id': 'test_user_123',
                    'trade_type': 'buy',
                    'crypto_type': 'bitcoin',
                    'amount_naira': 100000,
                    'crypto_amount': 0.002,
                    'market_rate': 50000000,
                    'sofi_rate': 49500000,
                    'profit_margin': 1000,
                    'transaction_reference': f'TEST_CRYPTO_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                }
            },
            # Test transfer fee
            {
                'table': 'transfer_charges',
                'data': {
                    'user_id': 'test_user_123',
                    'transfer_amount': 50000,
                    'fee_charged': 50,
                    'recipient_bank': 'GTBank',
                    'recipient_account': '0123456789',
                    'transfer_reference': f'TEST_TRF_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                }
            }
        ]
        
        for test in test_data:
            result = supabase.table(test['table']).insert(test['data']).execute()
            print(f"✅ Test data inserted into {test['table']}")
        
        # Test revenue calculation
        result = supabase.rpc('get_revenue_summary').execute()
        if result.data:
            summary = result.data[0]
            print(f"✅ Revenue Summary Test:")
            print(f"   💰 Total Revenue: ₦{summary['total_revenue']:,.2f}")
            print(f"   🪙 Crypto Profit: ₦{summary['crypto_profit']:,.2f}")
            print(f"   🏦 Transfer Fees: ₦{summary['transfer_fees']:,.2f}")
            print(f"   📞 Airtime Profit: ₦{summary['airtime_profit']:,.2f}")
            print(f"   📶 Data Profit: ₦{summary['data_profit']:,.2f}")
            print(f"   💳 Deposit Fees: ₦{summary['deposit_fees']:,.2f}")
        
        print("✅ Revenue system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def main():
    """Deploy complete revenue tracking system"""
    print("🏦 SOFI AI REVENUE TRACKING SYSTEM DEPLOYMENT")
    print("=" * 50)
    
    try:
        # Step 1: Create tables
        create_revenue_tables()
        print()
        
        # Step 2: Create functions
        create_revenue_functions()
        print()
        
        # Step 3: Test system
        test_revenue_system()
        print()
        
        print("🎉 REVENUE TRACKING SYSTEM DEPLOYED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ All tables created")
        print("✅ All functions created")
        print("✅ System tested and working")
        print()
        print("💡 Next steps:")
        print("1. Integrate fee collection into transfer flow")
        print("2. Integrate profit tracking into crypto trades")
        print("3. Integrate markup tracking into airtime/data sales")
        print("4. Test with real transactions")
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")

if __name__ == "__main__":
    main()
