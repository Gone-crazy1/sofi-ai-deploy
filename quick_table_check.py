import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

try:
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
    
    print("🔍 Checking Sharp AI tables...")
    
    tables = ['user_profiles', 'transaction_memory', 'conversation_context', 'spending_analytics', 'ai_learning']
    missing = []
    
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ {table}")
        except Exception as e:
            if 'does not exist' in str(e):
                print(f"❌ {table} - MISSING")
                missing.append(table)
    
    if missing:
        print(f"\n🔧 Missing tables: {missing}")
        print("💡 Need to run SQL deployment in Supabase")
    else:
        print("\n🎉 All Sharp AI tables ready!")
        print("✅ DEPLOYMENT READY!")
        
except Exception as e:
    print(f"Error: {e}")
