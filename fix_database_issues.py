#!/usr/bin/env python3
"""
🔧 SOFI AI - DATABASE FIX SCRIPT
===============================================================================
This script fixes the missing database tables causing PIN validation errors
===============================================================================
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("❌ Supabase not installed. Run: pip install supabase")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if Supabase connection works"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Missing SUPABASE_URL or SUPABASE_KEY environment variables")
            return None
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection
        result = supabase.table("users").select("id").limit(1).execute()
        logger.info("✅ Supabase connection successful")
        return supabase
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return None

def check_table_exists(supabase, table_name):
    """Check if a table exists"""
    try:
        # Try to query the table
        result = supabase.table(table_name).select("*").limit(1).execute()
        logger.info(f"✅ Table '{table_name}' exists")
        return True
    except Exception as e:
        if "does not exist" in str(e):
            logger.warning(f"⚠️ Table '{table_name}' does not exist")
            return False
        else:
            logger.error(f"❌ Error checking table '{table_name}': {e}")
            return False

def check_users_table_structure(supabase):
    """Check if users table has required PIN columns"""
    try:
        # Try to select PIN-related columns
        result = supabase.table("users").select("pin_hash, pin_attempts, pin_locked_until").limit(1).execute()
        logger.info("✅ Users table has required PIN columns")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Users table missing PIN columns: {e}")
        return False

def create_pin_attempts_table(supabase):
    """Create the pin_attempts table using SQL"""
    try:
        # Since Supabase Python client doesn't support DDL directly,
        # we'll create it through the SQL editor or via direct SQL execution
        logger.info("📝 To create pin_attempts table, please run this SQL in Supabase SQL Editor:")
        
        sql = """
-- Create pin_attempts table
CREATE TABLE IF NOT EXISTS public.pin_attempts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    attempt_count INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_attempt TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.pin_attempts ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Users can access their own pin attempts" ON public.pin_attempts
    FOR ALL USING (auth.uid() = user_id);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pin_attempts_user_id ON public.pin_attempts(user_id);
        """
        
        print("\n" + "="*70)
        print("📋 SQL TO RUN IN SUPABASE:")
        print("="*70)
        print(sql)
        print("="*70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating pin_attempts table: {e}")
        return False

def check_user_pin_data(supabase):
    """Check existing user PIN data"""
    try:
        result = supabase.table("users").select("id, telegram_chat_id, pin_hash").execute()
        
        total_users = len(result.data)
        users_with_pin = len([u for u in result.data if u.get('pin_hash')])
        
        logger.info(f"📊 User PIN Status:")
        logger.info(f"   Total users: {total_users}")
        logger.info(f"   Users with PIN: {users_with_pin}")
        logger.info(f"   Users without PIN: {total_users - users_with_pin}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking user PIN data: {e}")
        return False

def fix_missing_columns(supabase):
    """Instructions to fix missing columns"""
    logger.info("📝 To add missing columns to users table, run this SQL in Supabase:")
    
    sql = """
-- Add missing PIN columns to users table
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS pin_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS pin_locked_until TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS pin_set_at TIMESTAMPTZ;

-- Update existing users
UPDATE public.users 
SET pin_attempts = 0 
WHERE pin_attempts IS NULL;
    """
    
    print("\n" + "="*70)
    print("📋 SQL TO ADD MISSING COLUMNS:")
    print("="*70)
    print(sql)
    print("="*70)

def main():
    """Main function to check and fix database issues"""
    logger.info("🔧 SOFI AI - DATABASE FIX SCRIPT")
    logger.info("=" * 50)
    
    # 1. Check Supabase connection
    supabase = check_database_connection()
    if not supabase:
        logger.error("❌ Cannot proceed without Supabase connection")
        return False
    
    # 2. Check if pin_attempts table exists
    pin_attempts_exists = check_table_exists(supabase, "pin_attempts")
    
    # 3. Check users table structure
    users_structure_ok = check_users_table_structure(supabase)
    
    # 4. Check existing PIN data
    check_user_pin_data(supabase)
    
    # 5. Provide fix instructions
    logger.info("\n📋 FIX INSTRUCTIONS:")
    logger.info("=" * 50)
    
    if not pin_attempts_exists:
        logger.warning("⚠️ pin_attempts table missing - creating SQL to fix...")
        create_pin_attempts_table(supabase)
    
    if not users_structure_ok:
        logger.warning("⚠️ users table missing PIN columns - creating SQL to fix...")
        fix_missing_columns(supabase)
    
    if pin_attempts_exists and users_structure_ok:
        logger.info("✅ Database structure looks good!")
        logger.info("💡 If you're still getting PIN errors, the issue might be in the application logic.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
