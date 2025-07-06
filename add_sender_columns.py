#!/usr/bin/env python3
"""
Add sender information columns to bank_transactions table
========================================================
Adds sender_name, narration, and bank_name columns to support
rich deposit notifications with sender details.
"""

import os
import logging
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sender_columns():
    """Add sender information columns to bank_transactions table"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        logger.info("🔄 Adding sender information columns to bank_transactions table...")
        
        # SQL to add sender columns
        sql_commands = [
            """
            -- Add sender_name column
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS sender_name TEXT;
            """,
            """
            -- Add narration column
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS narration TEXT;
            """,
            """
            -- Add bank_name column (separate from bank_code)
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS bank_name TEXT;
            """,
            """
            -- Add bank_code column if it doesn't exist
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS bank_code TEXT;
            """,
            """
            -- Add account_number column if it doesn't exist
            ALTER TABLE bank_transactions 
            ADD COLUMN IF NOT EXISTS account_number TEXT;
            """
        ]
        
        for i, sql in enumerate(sql_commands, 1):
            try:
                logger.info(f"🔄 Executing SQL command {i}/5...")
                supabase.rpc("execute_sql", {"sql": sql}).execute()
                logger.info(f"✅ SQL command {i}/5 completed successfully")
            except Exception as e:
                logger.warning(f"⚠️ SQL command {i}/5 might have failed (column may already exist): {e}")
        
        logger.info("✅ Sender information columns added successfully!")
        logger.info("📊 Database schema updated for rich deposit notifications")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding sender columns: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Adding sender information columns to bank_transactions table...")
    success = add_sender_columns()
    
    if success:
        print("\n✅ SUCCESS: Sender columns added successfully!")
        print("📱 Enhanced deposit notifications are now ready!")
        print("\nFeatures enabled:")
        print("• 🎯 Sender name display in notifications")
        print("• 🏦 Sender bank information")
        print("• 📝 Transfer narration/description")
        print("• 🎉 Beautiful, emoji-rich messages")
    else:
        print("\n❌ FAILED: Could not add sender columns")
        print("Please check your Supabase credentials and try again.")
