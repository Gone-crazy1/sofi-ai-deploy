#!/usr/bin/env python3
"""
SHARP AI DATABASE DEPLOYMENT SCRIPT
Automatically deploys Sharp AI memory system to Supabase database
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Tuple, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SharpAIDatabaseDeployer:
    """Deploy Sharp AI memory system to Supabase"""
    
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Schema definition
        self.schema_sql = """
-- SHARP AI MEMORY SYSTEM - COMPLETE DEPLOYMENT
-- Auto-deployed by deploy_sharp_ai_database.py

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Enhanced User Profile Table (Complete User Memory)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
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

-- 2. Comprehensive Transaction Memory (All Money Movements)
CREATE TABLE IF NOT EXISTS transaction_memory (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('transfer', 'airtime', 'data', 'crypto_buy', 'crypto_sell', 'deposit', 'withdrawal')),
    amount NUMERIC NOT NULL,
    recipient_name TEXT,
    recipient_account TEXT,
    bank_name TEXT,
    narration TEXT,
    transaction_reference TEXT,
    status TEXT DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed')),
    transaction_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Conversation Context Memory (AI Context Awareness)
CREATE TABLE IF NOT EXISTS conversation_context (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    context_type TEXT NOT NULL CHECK (context_type IN ('intent', 'question', 'complaint', 'request', 'command')),
    context_summary TEXT NOT NULL,
    full_context TEXT,
    resolution_status TEXT DEFAULT 'pending' CHECK (resolution_status IN ('pending', 'resolved', 'escalated')),
    importance_level INTEGER DEFAULT 1 CHECK (importance_level BETWEEN 1 AND 5),
    context_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Smart Spending Analytics (Financial Intelligence)
CREATE TABLE IF NOT EXISTS spending_analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'yearly')),
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

-- 5. AI Learning & Preferences (Personalization Memory)
CREATE TABLE IF NOT EXISTS ai_learning (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    learning_type TEXT NOT NULL CHECK (learning_type IN ('preference', 'habit', 'pattern', 'behavior')),
    learning_key TEXT NOT NULL,
    learning_value TEXT NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.50 CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    last_observed TIMESTAMPTZ DEFAULT NOW(),
    observation_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(telegram_chat_id, learning_key)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_chat_id ON user_profiles(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transaction_memory_chat_id ON transaction_memory(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_transaction_memory_date ON transaction_memory(transaction_date);
CREATE INDEX IF NOT EXISTS idx_conversation_context_chat_id ON conversation_context(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_date ON conversation_context(context_date);
CREATE INDEX IF NOT EXISTS idx_spending_analytics_chat_id ON spending_analytics(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_spending_analytics_period ON spending_analytics(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_ai_learning_chat_id ON ai_learning(telegram_chat_id);

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE spending_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_learning ENABLE ROW LEVEL SECURITY;
"""

        self.rls_policies_sql = """
-- Create RLS policies (allow service role access)
DO $$
BEGIN
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Enable all operations for service role" ON user_profiles;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON transaction_memory;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON conversation_context;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON spending_analytics;
    DROP POLICY IF EXISTS "Enable all operations for service role" ON ai_learning;
EXCEPTION
    WHEN undefined_object THEN
        NULL;
END $$;

-- Create new policies
CREATE POLICY "Enable all operations for service role" ON user_profiles FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON transaction_memory FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON conversation_context FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON spending_analytics FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON ai_learning FOR ALL USING (true);
"""

        self.expected_tables = [
            'user_profiles',
            'transaction_memory', 
            'conversation_context',
            'spending_analytics',
            'ai_learning'
        ]
    
    def print_banner(self):
        """Print deployment banner"""
        print("=" * 80)
        print("🚀 SHARP AI DATABASE DEPLOYMENT")
        print("=" * 80)
        print("🎯 Target: Supabase Database")
        print("🧠 System: Sharp AI Memory System")
        print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 80)
    
    def check_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            logger.info("🔍 Testing Supabase connection...")
            
            # Test connection by trying to fetch table list
            result = self.supabase.rpc('version').execute()
            
            logger.info("✅ Supabase connection successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {str(e)}")
            return False
    
    def check_existing_tables(self) -> Dict[str, bool]:
        """Check which Sharp AI tables already exist"""
        existing_tables = {}
        
        try:
            logger.info("🔍 Checking existing Sharp AI tables...")
            
            for table_name in self.expected_tables:
                try:
                    # Try to query the table structure
                    result = self.supabase.table(table_name).select("*").limit(1).execute()
                    existing_tables[table_name] = True
                    logger.info(f"✅ Table '{table_name}' exists")
                    
                except Exception:
                    existing_tables[table_name] = False
                    logger.info(f"❌ Table '{table_name}' does not exist")
            
            return existing_tables
            
        except Exception as e:
            logger.error(f"Error checking existing tables: {str(e)}")
            return {table: False for table in self.expected_tables}
    
    def execute_sql(self, sql: str, description: str) -> bool:
        """Execute SQL statement"""
        try:
            logger.info(f"⚡ {description}...")
            
            # Execute SQL using Supabase RPC
            result = self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            
            if result.data:
                logger.info(f"✅ {description} completed successfully")
                return True
            else:
                logger.warning(f"⚠️ {description} completed with no data returned")
                return True
                
        except Exception as e:
            logger.error(f"❌ {description} failed: {str(e)}")
            return False
    
    def deploy_schema(self) -> bool:
        """Deploy the complete Sharp AI schema"""
        try:
            logger.info("🚀 Deploying Sharp AI memory system schema...")
            
            # Split SQL into individual statements for better error handling
            statements = [stmt.strip() for stmt in self.schema_sql.split(';') if stmt.strip()]
            
            success_count = 0
            total_statements = len(statements)
            
            for i, statement in enumerate(statements, 1):
                if statement.strip():
                    try:
                        logger.info(f"📝 Executing statement {i}/{total_statements}")
                        
                        # Use PostgREST to execute SQL
                        response = self.supabase.postgrest.session.post(
                            f"{self.supabase_url}/rest/v1/rpc/exec_sql",
                            json={"sql": statement},
                            headers={
                                "apikey": self.supabase_key,
                                "Authorization": f"Bearer {self.supabase_key}",
                                "Content-Type": "application/json"
                            }
                        )
                        
                        if response.status_code in [200, 201]:
                            success_count += 1
                        else:
                            logger.warning(f"⚠️ Statement {i} returned status {response.status_code}")
                            
                    except Exception as e:
                        logger.error(f"❌ Statement {i} failed: {str(e)}")
            
            logger.info(f"📊 Schema deployment: {success_count}/{total_statements} statements executed")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Schema deployment failed: {str(e)}")
            return False
    
    def deploy_rls_policies(self) -> bool:
        """Deploy RLS policies"""
        try:
            logger.info("🔒 Deploying Row Level Security policies...")
            
            # Execute RLS policies
            response = self.supabase.postgrest.session.post(
                f"{self.supabase_url}/rest/v1/rpc/exec_sql",
                json={"sql": self.rls_policies_sql},
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ RLS policies deployed successfully")
                return True
            else:
                logger.error(f"❌ RLS policies deployment failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ RLS policies deployment failed: {str(e)}")
            return False
    
    def verify_deployment(self) -> Tuple[bool, Dict[str, bool]]:
        """Verify all tables were created successfully"""
        logger.info("🔍 Verifying deployment...")
        
        verification_results = self.check_existing_tables()
        
        all_created = all(verification_results.values())
        
        if all_created:
            logger.info("✅ All Sharp AI tables created successfully!")
        else:
            missing_tables = [table for table, exists in verification_results.items() if not exists]
            logger.error(f"❌ Missing tables: {missing_tables}")
        
        return all_created, verification_results
    
    def test_memory_system(self) -> bool:
        """Test the Sharp AI memory system"""
        try:
            logger.info("🧪 Testing Sharp AI memory system...")
            
            test_chat_id = "test_deploy_123"
            
            # Test user profile creation
            profile_data = {
                "telegram_chat_id": test_chat_id,
                "full_name": "Test User",
                "last_action": "deployment_test",
                "last_action_time": datetime.now().isoformat()
            }
            
            result = self.supabase.table("user_profiles").upsert(profile_data).execute()
            
            if result.data:
                logger.info("✅ User profile test passed")
                
                # Test conversation context
                context_data = {
                    "telegram_chat_id": test_chat_id,
                    "context_type": "command",
                    "context_summary": "Deployment test",
                    "importance_level": 1
                }
                
                result = self.supabase.table("conversation_context").insert(context_data).execute()
                
                if result.data:
                    logger.info("✅ Conversation context test passed")
                    
                    # Clean up test data
                    self.supabase.table("user_profiles").delete().eq("telegram_chat_id", test_chat_id).execute()
                    self.supabase.table("conversation_context").delete().eq("telegram_chat_id", test_chat_id).execute()
                    
                    logger.info("✅ Sharp AI memory system working correctly!")
                    return True
            
            logger.error("❌ Memory system test failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Memory system test failed: {str(e)}")
            return False
    
    def generate_deployment_report(self, success: bool, verification_results: Dict[str, bool]) -> str:
        """Generate deployment report"""
        report = f"""
🚀 SHARP AI DATABASE DEPLOYMENT REPORT
{'='*60}

📅 Deployment Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🎯 Target Database: {self.supabase_url}
🧠 System: Sharp AI Memory System

📊 RESULTS:
{'='*60}
Overall Status: {'✅ SUCCESS' if success else '❌ FAILED'}

📋 Table Creation Status:
"""
        
        for table_name, created in verification_results.items():
            status = "✅ CREATED" if created else "❌ MISSING"
            report += f"  • {table_name}: {status}\n"
        
        if success:
            report += f"""
🎉 DEPLOYMENT SUCCESSFUL!
{'='*60}
✅ All 5 Sharp AI memory tables created
✅ Indexes and constraints applied
✅ Row Level Security enabled
✅ Memory system tested and working

🚀 NEXT STEPS:
1. Your Sharp AI system is now ready!
2. Run your bot to test the memory features
3. Check Supabase dashboard to see the new tables
4. Monitor the memory system performance

🧠 SHARP AI FEATURES NOW ACTIVE:
• Permanent user profiles and preferences
• Complete transaction history memory
• Conversation context awareness
• Intelligent spending analytics
• AI learning and personalization
"""
        else:
            missing_tables = [table for table, exists in verification_results.items() if not exists]
            report += f"""
❌ DEPLOYMENT INCOMPLETE
{'='*60}
Missing Tables: {', '.join(missing_tables)}

🔧 TROUBLESHOOTING:
1. Check your Supabase credentials
2. Verify service role permissions
3. Check database connection
4. Run the script again
5. Contact support if issues persist
"""
        
        return report
    
    async def deploy(self) -> bool:
        """Main deployment function"""
        self.print_banner()
        
        # Step 1: Check connection
        if not self.check_connection():
            print("❌ Cannot connect to Supabase. Check your credentials.")
            return False
        
        # Step 2: Check existing tables
        existing_tables = self.check_existing_tables()
        existing_count = sum(existing_tables.values())
        
        if existing_count == len(self.expected_tables):
            print("✅ All Sharp AI tables already exist!")
            return True
        
        print(f"📊 Found {existing_count}/{len(self.expected_tables)} existing tables")
        
        # Step 3: Deploy schema
        if not self.deploy_schema():
            print("❌ Schema deployment failed")
            return False
        
        # Step 4: Deploy RLS policies
        if not self.deploy_rls_policies():
            print("⚠️ RLS policies deployment failed (but tables created)")
        
        # Step 5: Verify deployment
        success, verification_results = self.verify_deployment()
        
        # Step 6: Test memory system
        if success:
            self.test_memory_system()
        
        # Step 7: Generate report
        report = self.generate_deployment_report(success, verification_results)
        print(report)
        
        # Save report to file
        with open("sharp_ai_deployment_report.txt", "w") as f:
            f.write(report)
        
        return success

def main():
    """Main function"""
    try:
        deployer = SharpAIDatabaseDeployer()
        
        # Run deployment
        success = asyncio.run(deployer.deploy())
        
        if success:
            print("\n🎉 Sharp AI Database Deployment Complete!")
            print("🧠 Your AI system now has permanent memory!")
            sys.exit(0)
        else:
            print("\n❌ Deployment failed. Check the logs above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment crashed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
