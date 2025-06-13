#!/usr/bin/env python3
"""
Add balance column to virtual_accounts table for storing virtual account balances
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

def add_balance_column():
    """Add balance column to virtual_accounts table"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🔧 Adding balance column to virtual_accounts table...")
        
        # Check if balance column already exists
        try:
            result = client.table("virtual_accounts").select("balance").limit(1).execute()
            print("✅ Balance column already exists in virtual_accounts table")
            return True
        except Exception:
            print("📝 Balance column doesn't exist, adding it...")
        
        # Add balance column with default value 0.0
        # Note: This would normally be done via SQL migration in production
        # For now, we'll add it manually via Supabase dashboard or SQL
        
        print("""
📋 MANUAL STEP REQUIRED:

Please run this SQL in your Supabase SQL editor:

ALTER TABLE virtual_accounts 
ADD COLUMN IF NOT EXISTS balance DECIMAL(15,2) DEFAULT 0.00;

UPDATE virtual_accounts 
SET balance = 0.00 
WHERE balance IS NULL;

This will:
1. Add a balance column to store virtual account balances
2. Set default balance to 0.00 for existing accounts
3. Allow the get_user_balance() function to work correctly
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_balance_column()
    if success:
        print("\n✅ Balance column setup process initiated!")
        print("📝 Please run the SQL command shown above in Supabase")
    else:
        print("\n❌ Failed to initiate balance column setup")
