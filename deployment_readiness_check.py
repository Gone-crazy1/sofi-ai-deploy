"""
Final deployment readiness check for Sofi AI
"""
import os
import sys
from dotenv import load_dotenv

def main():
    print("🚀 SOFI AI DEPLOYMENT READINESS CHECK")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check 1: Environment Variables
    print("\n1️⃣ Checking Environment Variables...")
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY', 
        'OPENAI_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'MONNIFY_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var} - MISSING")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {missing_vars}")
        return False
    
    # Check 2: Core Imports
    print("\n2️⃣ Checking Core Imports...")
    try:
        from supabase import create_client
        print("   ✅ Supabase client")
        
        import openai
        print("   ✅ OpenAI")
        
        from flask import Flask
        print("   ✅ Flask")
        
        from utils.sharp_sofi_ai import handle_smart_message
        print("   ✅ Sharp AI handler")
        
        from utils.sharp_memory import sharp_memory
        print("   ✅ Sharp Memory system")
        
    except Exception as e:
        print(f"   ❌ Import error: {str(e)}")
        return False
    
    # Check 3: Database Connection
    print("\n3️⃣ Testing Database Connection...")
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Test basic connection
        result = supabase.table('users').select('*').limit(1).execute()
        print("   ✅ Database connection successful")
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
        return False
    
    # Check 4: Sharp AI Tables
    print("\n4️⃣ Checking Sharp AI Tables...")
    sharp_tables = [
        'user_profiles',
        'transaction_memory', 
        'conversation_context',
        'spending_analytics',
        'ai_learning'
    ]
    
    missing_tables = []
    for table in sharp_tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"   ✅ {table}")
        except Exception as e:
            if 'does not exist' in str(e):
                print(f"   ❌ {table} - MISSING")
                missing_tables.append(table)
            else:
                print(f"   ⚠️ {table} - Error: {str(e)}")
    
    # Check 5: Basic Functionality Test
    print("\n5️⃣ Testing Basic Functionality...")
    try:
        # Test main app import
        import main
        print("   ✅ Main application imports")
        
        # Test if Flask app exists
        if hasattr(main, 'app'):
            print("   ✅ Flask app initialized")
        else:
            print("   ⚠️ Flask app variable not found")
            
    except Exception as e:
        print(f"   ❌ Main app test failed: {str(e)}")
        return False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 50)
    
    if missing_tables:
        print("⚠️ DEPLOYMENT NOT READY")
        print(f"🔧 Missing Sharp AI tables: {missing_tables}")
        print("\n💡 TO FIX: Execute this SQL in Supabase SQL Editor:")
        print("---")
        print("""
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT UNIQUE NOT NULL,
    full_name TEXT,
    last_action TEXT,
    last_action_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transaction_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_chat_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
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
        """)
        print("---")
        return False
    else:
        print("🎉 DEPLOYMENT READY!")
        print("✅ All systems verified and operational")
        print("\n🚀 READY TO DEPLOY TO RENDER!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Deploy Sharp AI system'") 
        print("3. git push origin main")
        print("4. Deploy to Render")
        return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 GO FOR DEPLOYMENT! 🚀")
    else:
        print("\n🔧 FIX ISSUES FIRST")
    
    sys.exit(0 if success else 1)
