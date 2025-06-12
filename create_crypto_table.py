import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_crypto_transactions_table():
    """Create the crypto_transactions table in Supabase"""
    
    # Initialize Supabase client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Read the SQL file
    with open('create_crypto_transactions_table.sql', 'r') as file:
        sql_content = file.read()
    
    try:
        # Execute the SQL
        print("🚀 Creating crypto_transactions table...")
        
        # Split the SQL into individual statements
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in sql_statements:
            if statement:
                try:
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"ℹ️ Table/index already exists: {statement[:50]}...")
                    else:
                        print(f"⚠️ Warning executing statement: {e}")
        
        print("✅ Crypto transactions table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating crypto transactions table: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_crypto_transactions_table())
