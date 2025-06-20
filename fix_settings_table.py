#!/usr/bin/env python3
"""
Create the missing settings table in Supabase
This will fix the 400 error in virtual account creation
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def create_settings_table():
    """Create the settings table and insert default fee settings"""
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase credentials not found in environment")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # First check if settings table exists
        try:
            result = supabase.table("settings").select("*").limit(1).execute()
            print("✅ Settings table already exists!")
            return True
        except Exception as e:
            if "does not exist" in str(e):
                print("🔧 Settings table does not exist. Creating it...")
            else:
                print(f"❌ Error checking settings table: {e}")
                return False
        
        # Create the table using SQL (you'll need to run this manually in Supabase SQL editor)
        create_table_sql = '''
        -- Create settings table for fee calculator
        CREATE TABLE IF NOT EXISTS public.settings (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) UNIQUE NOT NULL,
            value JSONB NOT NULL,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Insert default fee settings
        INSERT INTO public.settings (key, value, description) VALUES
        (
            'fee_structure',
            '{
                "transfer": {
                    "fixed_fee": 10.00,
                    "percentage_fee": 0.5,
                    "max_fee": 100.00,
                    "min_fee": 10.00
                },
                "airtime": {
                    "commission_percentage": 2.0,
                    "min_commission": 5.00,
                    "max_commission": 50.00
                },
                "data": {
                    "commission_percentage": 3.0,
                    "min_commission": 5.00,
                    "max_commission": 100.00
                },
                "crypto": {
                    "buy_spread": 1.5,
                    "sell_spread": 1.5,
                    "min_spread": 0.5,
                    "max_spread": 3.0
                }
            }'::jsonb,
            'Default fee structure for all transaction types'
        ),
        (
            'daily_limits',
            '{
                "individual_transfer_limit": 500000.00,
                "daily_transfer_limit": 2000000.00,
                "airtime_daily_limit": 50000.00,
                "data_daily_limit": 50000.00,
                "crypto_daily_limit": 1000000.00
            }'::jsonb,
            'Daily transaction limits for users'
        ) ON CONFLICT (key) DO NOTHING;
        '''
        
        print("📋 SQL to create settings table:")
        print("=" * 60)
        print(create_table_sql)
        print("=" * 60)
        print("\n🔗 Go to your Supabase dashboard > SQL Editor and run the above SQL")
        print("🌐 Dashboard: https://supabase.com/dashboard/project/{your-project-id}/sql")
        print("\n✅ This will fix the 'relation public.settings does not exist' error")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Creating Supabase settings table...")
    create_settings_table()
