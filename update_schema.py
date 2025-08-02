"""
Update Supabase Database Schema for Paystack Integration
========================================================
Adds required columns for Paystack virtual accounts
"""

import os
import logging
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database_schema():
    """Update Supabase users table to support Paystack virtual accounts"""
    
    try:
        # Initialize Supabase client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("❌ Supabase credentials not found in environment variables")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        logger.info("🔧 Updating Supabase users table schema...")
        
        # Read the SQL script
        with open('update_users_table_paystack.sql', 'r') as file:
            sql_script = file.read()
        
        # Execute the schema update
        # Note: Supabase Python client doesn't directly support raw SQL execution
        # This would need to be run manually in the Supabase SQL editor
        
        logger.info("📋 SQL script content:")
        print("\n" + "="*60)
        print(sql_script)
        print("="*60)
        
        logger.info("🎯 MANUAL ACTION REQUIRED:")
        logger.info("1. Copy the SQL script above")
        logger.info("2. Go to your Supabase dashboard")
        logger.info("3. Open the SQL Editor")
        logger.info("4. Paste and run the script")
        logger.info("5. Come back and run the test again")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema update failed: {e}")
        return False

def verify_schema():
    """Verify the schema has been updated correctly"""
    
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try to create a test record with the new fields
        test_record = {
            'whatsapp_number': '+2341234567890',
            'full_name': 'Schema Test User',
            'email': 'test@schema.com',
            'account_name': 'Schema Test User',
            'account_number': '1234567890',
            'bank_name': 'Wema Bank',
            'bank_code': '035',
            'paystack_customer_code': 'CUS_test123',
            'platform': 'whatsapp',
            'status': 'active',
            'metadata': {'test': True}
        }
        
        # Try inserting (will fail if schema not updated)
        result = supabase.table("users").insert(test_record).execute()
        
        if result.data:
            # Clean up test record
            supabase.table("users").delete().eq("whatsapp_number", '+2341234567890').execute()
            logger.info("✅ Schema verification successful!")
            return True
        else:
            logger.error("❌ Schema verification failed - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Schema verification failed: {e}")
        logger.info("💡 This means the schema hasn't been updated yet")
        return False

if __name__ == "__main__":
    print("🚀 Supabase Schema Update for Paystack Integration")
    print("=" * 60)
    
    print("\n1️⃣ Checking current schema...")
    if verify_schema():
        print("✅ Schema is already up to date!")
    else:
        print("⚠️ Schema needs to be updated")
        print("\n2️⃣ Generating update script...")
        if update_database_schema():
            print("\n3️⃣ After running the SQL script manually, run this again to verify")
    
    print("\n🎉 Schema update process completed!")
