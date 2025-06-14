#!/usr/bin/env python3
"""
Comprehensive verification script to ensure Sofi AI is deployment-ready
Checks database tables, API connections, and core functionality
"""

import os
import asyncio
import logging
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeploymentVerifier:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not all([self.supabase_url, self.supabase_key]):
            raise ValueError("Missing required environment variables")
        
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
    def verify_environment_variables(self):
        """Verify all required environment variables are set"""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_SERVICE_ROLE_KEY', 
            'OPENAI_API_KEY',
            'TELEGRAM_BOT_TOKEN',
            'MONNIFY_API_KEY',
            'MONNIFY_SECRET_KEY',
            'BITNOB_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            logger.info("✅ All required environment variables are set")
            return True
    
    def verify_database_tables(self):
        """Verify all required database tables exist"""
        required_tables = [
            'users',
            'bank_transactions', 
            'beneficiaries',
            'crypto_transactions',
            'crypto_rates',
            'memories',
            'chat_messages',
            'user_profiles',          # Sharp AI
            'transaction_memory',     # Sharp AI
            'conversation_context',   # Sharp AI
            'spending_analytics',     # Sharp AI
            'ai_learning'            # Sharp AI
        ]
        
        try:
            # Get all tables in the public schema
            result = self.supabase.rpc('get_table_names').execute()
            
            if not result.data:
                # Fallback method using information_schema
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
                result = self.supabase.rpc('execute_sql', {'query': query}).execute()
                existing_tables = [row['table_name'] for row in result.data] if result.data else []
            else:
                existing_tables = result.data
            
            logger.info(f"📋 Found tables: {existing_tables}")
            
            missing_tables = []
            for table in required_tables:
                if table not in existing_tables:
                    missing_tables.append(table)
            
            if missing_tables:
                logger.error(f"❌ Missing database tables: {', '.join(missing_tables)}")
                logger.info("💡 Run the Sharp AI SQL script in Supabase to create missing tables")
                return False, missing_tables
            else:
                logger.info("✅ All required database tables exist")
                return True, []
                
        except Exception as e:
            logger.error(f"❌ Error checking database tables: {str(e)}")
            return False, []
    
    def verify_sharp_ai_tables(self):
        """Specifically verify Sharp AI memory system tables"""
        sharp_ai_tables = [
            'user_profiles',
            'transaction_memory', 
            'conversation_context',
            'spending_analytics',
            'ai_learning'
        ]
        
        try:
            missing_sharp_tables = []
            
            for table in sharp_ai_tables:
                try:
                    # Try to query each table to verify it exists
                    result = self.supabase.table(table).select('*').limit(1).execute()
                    logger.info(f"✅ Sharp AI table '{table}' exists and accessible")
                except Exception as e:
                    if 'does not exist' in str(e):
                        missing_sharp_tables.append(table)
                        logger.error(f"❌ Sharp AI table '{table}' missing")
                    else:
                        logger.warning(f"⚠️ Issue accessing '{table}': {str(e)}")
            
            if missing_sharp_tables:
                logger.error(f"❌ Missing Sharp AI tables: {', '.join(missing_sharp_tables)}")
                return False, missing_sharp_tables
            else:
                logger.info("✅ All Sharp AI memory tables are ready!")
                return True, []
                
        except Exception as e:
            logger.error(f"❌ Error verifying Sharp AI tables: {str(e)}")
            return False, sharp_ai_tables
    
    def test_basic_functionality(self):
        """Test basic database operations"""
        try:
            # Test basic user table access
            result = self.supabase.table('users').select('*').limit(1).execute()
            logger.info("✅ Database connection and basic queries working")
            
            # Test Sharp AI functionality if tables exist
            try:
                # Test user profile creation
                test_profile = {
                    'telegram_chat_id': 'test_verification_123',
                    'full_name': 'Test User',
                    'last_action': 'verification_test',
                    'last_action_time': datetime.now().isoformat()
                }
                
                result = self.supabase.table('user_profiles').upsert(test_profile).execute()
                logger.info("✅ Sharp AI user profile operations working")
                
                # Clean up test data
                self.supabase.table('user_profiles').delete().eq('telegram_chat_id', 'test_verification_123').execute()
                
            except Exception as e:
                logger.warning(f"⚠️ Sharp AI tables not ready: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database functionality test failed: {str(e)}")
            return False
    
    async def test_sharp_ai_integration(self):
        """Test Sharp AI system integration"""
        try:
            # Import Sharp AI components
            from utils.sharp_memory import sharp_memory
            from utils.sharp_sofi_ai import handle_smart_message
            
            # Test memory system
            test_chat_id = "test_chat_verification"
            
            # Test smart message handling
            test_response = await handle_smart_message(test_chat_id, "Hello, test verification")
            
            if test_response and isinstance(test_response, str):
                logger.info("✅ Sharp AI message handling working")
                logger.info(f"📝 Test response: {test_response[:100]}...")
                return True
            else:
                logger.error("❌ Sharp AI message handling failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Sharp AI integration test failed: {str(e)}")
            return False
    
    def generate_deployment_sql(self):
        """Generate SQL for missing Sharp AI tables"""
        sql_script = """
-- SHARP AI MEMORY SYSTEM - DEPLOYMENT SQL
-- Execute this in Supabase SQL Editor if any tables are missing

-- 1. User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone_number TEXT,
    email TEXT,
    last_intent TEXT,
    last_action TEXT,
    last_action_time TIMESTAMPTZ,
    last_balance NUMERIC DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    total_spent NUMERIC DEFAULT 0,
    total_received NUMERIC DEFAULT 0,
    favorite_banks JSONB DEFAULT '[]'::jsonb,
    frequent_recipients JSONB DEFAULT '[]'::jsonb,
    spending_patterns JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Transaction Memory Table
CREATE TABLE IF NOT EXISTS transaction_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    recipient_name TEXT,
    recipient_account TEXT,
    bank_name TEXT,
    narration TEXT,
    transaction_reference TEXT,
    status TEXT DEFAULT 'completed',
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Conversation Context Table
CREATE TABLE IF NOT EXISTS conversation_context (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    context_type TEXT NOT NULL,
    context_summary TEXT NOT NULL,
    full_context TEXT,
    resolution_status TEXT DEFAULT 'pending',
    importance_level INTEGER DEFAULT 1,
    context_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Spending Analytics Table
CREATE TABLE IF NOT EXISTS spending_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    period_type TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    total_spent NUMERIC DEFAULT 0,
    total_transfers NUMERIC DEFAULT 0,
    total_airtime NUMERIC DEFAULT 0,
    total_data NUMERIC DEFAULT 0,
    total_crypto NUMERIC DEFAULT 0,
    transaction_count INTEGER DEFAULT 0,
    top_recipient TEXT,
    top_bank TEXT,
    spending_category JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. AI Learning Table
CREATE TABLE IF NOT EXISTS ai_learning (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    learning_type TEXT NOT NULL,
    learning_key TEXT NOT NULL,
    learning_value TEXT NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    last_observed TIMESTAMPTZ DEFAULT NOW(),
    observation_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_chat_id ON user_profiles(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transaction_memory_chat_id ON transaction_memory(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_chat_id ON conversation_context(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_spending_analytics_chat_id ON spending_analytics(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_ai_learning_chat_id ON ai_learning(telegram_chat_id);

-- Verify deployment
SELECT 'Sharp AI tables deployed successfully!' as status;
"""
        
        return sql_script
    
    async def run_comprehensive_verification(self):
        """Run complete deployment verification"""
        logger.info("🚀 Starting Sofi AI Deployment Verification...")
        logger.info("=" * 60)
        
        verification_results = {}
        
        # 1. Environment Variables
        logger.info("1️⃣ Checking Environment Variables...")
        verification_results['env_vars'] = self.verify_environment_variables()
        
        # 2. Database Tables
        logger.info("\n2️⃣ Checking Database Tables...")
        tables_ok, missing_tables = self.verify_database_tables()
        verification_results['database_tables'] = tables_ok
        verification_results['missing_tables'] = missing_tables
        
        # 3. Sharp AI Tables
        logger.info("\n3️⃣ Checking Sharp AI Memory Tables...")
        sharp_ai_ok, missing_sharp = self.verify_sharp_ai_tables()
        verification_results['sharp_ai_tables'] = sharp_ai_ok
        verification_results['missing_sharp_tables'] = missing_sharp
        
        # 4. Basic Functionality
        logger.info("\n4️⃣ Testing Basic Functionality...")
        verification_results['basic_functionality'] = self.test_basic_functionality()
        
        # 5. Sharp AI Integration
        if sharp_ai_ok:
            logger.info("\n5️⃣ Testing Sharp AI Integration...")
            verification_results['sharp_ai_integration'] = await self.test_sharp_ai_integration()
        else:
            logger.warning("\n5️⃣ Skipping Sharp AI integration test (tables missing)")
            verification_results['sharp_ai_integration'] = False
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 DEPLOYMENT VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        all_passed = True
        for check, result in verification_results.items():
            if isinstance(result, bool):
                status = "✅ PASS" if result else "❌ FAIL"
                if not result:
                    all_passed = False
                logger.info(f"{check.replace('_', ' ').title()}: {status}")
        
        if missing_tables:
            logger.info(f"\nMissing Tables: {', '.join(missing_tables)}")
        
        if missing_sharp:
            logger.info(f"Missing Sharp AI Tables: {', '.join(missing_sharp)}")
        
        logger.info("\n" + "=" * 60)
        
        if all_passed:
            logger.info("🎉 SOFI AI IS READY FOR RENDER DEPLOYMENT!")
            logger.info("✅ All systems verified and operational")
            logger.info("\n🚀 Next steps:")
            logger.info("1. git add .")
            logger.info("2. git commit -m 'Deploy Sharp AI system'")
            logger.info("3. git push origin main")
            logger.info("4. Deploy to Render")
        else:
            logger.info("⚠️ DEPLOYMENT NOT READY")
            logger.info("🔧 Issues found that need to be resolved:")
            
            if missing_sharp:
                logger.info("\n📝 Execute this SQL in Supabase SQL Editor:")
                logger.info("-" * 50)
                print(self.generate_deployment_sql())
        
        return all_passed, verification_results

async def main():
    """Main verification function"""
    try:
        verifier = DeploymentVerifier()
        deployment_ready, results = await verifier.run_comprehensive_verification()
        
        if deployment_ready:
            print("\n🎯 READY TO DEPLOY TO RENDER! 🚀")
            return True
        else:
            print("\n🔧 RESOLVE ISSUES BEFORE DEPLOYMENT")
            return False
            
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
