"""
Simple database verification for Sofi AI deployment
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_env_vars():
    """Check essential environment variables"""
    required = [
        'SUPABASE_URL', 
        'SUPABASE_SERVICE_ROLE_KEY', 
        'OPENAI_API_KEY',
        'TELEGRAM_BOT_TOKEN'
    ]
    
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    else:
        print("✅ Environment variables OK")
        return True

def check_database_connection():
    """Test database connection"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials missing")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Test basic query
        result = supabase.table('users').select('*').limit(1).execute()
        print("✅ Database connection OK")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_sharp_ai_tables():
    """Check if Sharp AI tables exist"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        sharp_tables = [
            'user_profiles',
            'transaction_memory', 
            'conversation_context',
            'spending_analytics',
            'ai_learning'
        ]
        
        existing_tables = []
        missing_tables = []
        
        for table in sharp_tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                existing_tables.append(table)
                print(f"✅ {table} exists")
            except Exception as e:
                if 'does not exist' in str(e):
                    missing_tables.append(table)
                    print(f"❌ {table} missing")
        
        if missing_tables:
            print(f"\n🔧 Missing Sharp AI tables: {missing_tables}")
            print("💡 Need to execute Sharp AI SQL script in Supabase")
            return False, missing_tables
        else:
            print("✅ All Sharp AI tables exist")
            return True, []
            
    except Exception as e:
        print(f"❌ Error checking Sharp AI tables: {str(e)}")
        return False, []

def main():
    print("🚀 Sofi AI Deployment Verification")
    print("=" * 40)
    
    # Check environment
    env_ok = check_env_vars()
    if not env_ok:
        return False
    
    # Check database connection
    db_ok = check_database_connection()
    if not db_ok:
        return False
    
    # Check Sharp AI tables
    tables_ok, missing = check_sharp_ai_tables()
    
    print("\n" + "=" * 40)
    
    if env_ok and db_ok and tables_ok:
        print("🎉 DEPLOYMENT READY!")
        print("✅ All systems verified")
        print("\n🚀 Ready to deploy to Render!")
        return True
    else:
        print("⚠️ DEPLOYMENT NOT READY")
        if missing:
            print(f"🔧 Create these tables in Supabase: {missing}")
            print("\n📝 Execute this SQL in Supabase SQL Editor:")
            print(generate_deployment_sql())
        return False

def generate_deployment_sql():
    return """
-- SHARP AI TABLES DEPLOYMENT SQL
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone_number TEXT,
    last_action TEXT,
    last_action_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transaction_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    recipient_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversation_context (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    context_type TEXT NOT NULL,
    context_summary TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS spending_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    period_type TEXT NOT NULL,
    total_spent NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_learning (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    learning_type TEXT NOT NULL,
    learning_key TEXT NOT NULL,
    learning_value TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
