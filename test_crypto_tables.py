#!/usr/bin/env python3
"""
Test crypto tables setup in Supabase
Verify all crypto integration tables are created and accessible
"""

import os
from supabase import create_client
from dotenv import load_dotenv

def test_crypto_tables():
    """Test all crypto tables in Supabase"""
    load_dotenv()
    
    # Get Supabase credentials
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print('❌ Supabase credentials not found in .env file')
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test each crypto table
        tables_to_check = [
            'crypto_wallets',
            'crypto_transactions', 
            'wallet_balances',
            'crypto_rates_cache',
            'crypto_statistics'
        ]
        
        print('🔍 Checking crypto tables in Supabase...\n')
        
        success_count = 0
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f'✅ {table}: Connected successfully')
                success_count += 1
            except Exception as e:
                print(f'❌ {table}: Error - {str(e)}')
        
        print(f'\n📊 Summary: {success_count}/{len(tables_to_check)} tables accessible')
        
        # Test crypto rates cache specifically
        print('\n🎯 Testing crypto functionality...')
        
        try:
            rates = supabase.table('crypto_rates_cache').select('*').execute()
            if rates.data:
                print(f'📊 Found {len(rates.data)} cached rates:')
                for rate in rates.data:
                    symbol = rate.get('crypto_symbol', 'Unknown')
                    rate_ngn = rate.get('rate_ngn', 0)
                    print(f'   {symbol}: ₦{rate_ngn:,.2f}')
            else:
                print('📊 No cached rates found (this is normal for fresh setup)')
        except Exception as e:
            print(f'📊 Rates cache error: {e}')
        
        # Test wallet_balances table structure
        try:
            balance_test = supabase.table('wallet_balances').select('user_id, balance_naira, total_crypto_deposits').limit(1).execute()
            print('✅ wallet_balances: Schema looks good')
        except Exception as e:
            print(f'❌ wallet_balances schema issue: {e}')
        
        # Test crypto_wallets table structure
        try:
            wallet_test = supabase.table('crypto_wallets').select('user_id, btc_address, eth_address, usdt_address').limit(1).execute()
            print('✅ crypto_wallets: Schema looks good')
        except Exception as e:
            print(f'❌ crypto_wallets schema issue: {e}')
            
        return success_count == len(tables_to_check)
        
    except Exception as e:
        print(f'❌ General Supabase connection error: {e}')
        return False

if __name__ == '__main__':
    print('🚀 TESTING CRYPTO TABLES SETUP\n')
    success = test_crypto_tables()
    
    if success:
        print('\n🎉 ALL CRYPTO TABLES ARE READY!')
        print('\n📋 Next steps:')
        print('   1. ✅ Database tables created')
        print('   2. 🔑 Add BITNOB_SECRET_KEY to your .env file')
        print('   3. 🧪 Test crypto wallet creation')
        print('   4. 🎯 Test crypto deposit webhooks')
        print('   5. 💰 Test NGN conversion flow')
    else:
        print('\n⚠️  Some tables need attention. Check the errors above.')
