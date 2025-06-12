import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_crypto_transactions_table():
    """Create the crypto_transactions table in Supabase using direct SQL"""
    
    # Initialize Supabase client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        print("🚀 Creating crypto_transactions table...")
        
        # Try to create a simple table first to test the connection
        simple_create = """
        CREATE TABLE IF NOT EXISTS crypto_transactions (
            id BIGSERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            crypto_amount DECIMAL(18, 8) NOT NULL,
            crypto_currency VARCHAR(10) NOT NULL,
            ngn_amount DECIMAL(15, 2) DEFAULT 0,
            transaction_id VARCHAR(255),
            wallet_id VARCHAR(255),
            rate_used DECIMAL(15, 2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'completed',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
        
        # Use the SQL editor API endpoint directly
        print("✅ Attempting to create table via SQL...")
        
        # For now, let's just create the table structure using insert method
        # as a test to see if our crypto functions can interact with Supabase
        test_data = {
            'user_id': 'test_user',
            'transaction_type': 'deposit',
            'crypto_amount': 0.001,
            'crypto_currency': 'BTC',
            'ngn_amount': 50000.00,
            'transaction_id': 'test_tx_123',
            'status': 'test'
        }
        
        try:
            # This will fail if table doesn't exist, which is what we want to test
            result = supabase.table('crypto_transactions').select('id').limit(1).execute()
            print("✅ crypto_transactions table already exists!")
            return True
        except Exception as e:
            if "does not exist" in str(e).lower() or "relation" in str(e).lower():
                print("ℹ️ Table doesn't exist yet. You'll need to create it manually in Supabase SQL editor.")
                print("📋 SQL to run in Supabase SQL editor:")
                print(simple_create)
                print("\n🔧 After creating the table, also run these indexes:")
                print("CREATE INDEX IF NOT EXISTS idx_crypto_transactions_user_id ON crypto_transactions(user_id);")
                print("CREATE INDEX IF NOT EXISTS idx_crypto_transactions_type ON crypto_transactions(transaction_type);")
                return False
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error creating crypto transactions table: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_crypto_transactions_table())
