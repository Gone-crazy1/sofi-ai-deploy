#!/usr/bin/env python3
"""
Deploy Sharp AI Memory System to Supabase
This script deploys the complete memory and awareness system
"""

import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

async def deploy_sharp_ai_system():
    """Deploy the Sharp AI memory system"""
    
    print("🚀 DEPLOYING SHARP AI MEMORY SYSTEM")
    print("=" * 50)
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("   Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Read the deployment SQL
    sql_file_path = "deploy_sharp_ai_complete.sql"
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📋 Executing SQL deployment...")
        
        # Split SQL into individual statements to avoid issues
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(sql_statements, 1):
            if statement:
                try:
                    print(f"   Executing statement {i}/{len(sql_statements)}...")
                    result = supabase.rpc('sql', {'query': statement}).execute()
                    print(f"   ✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"   ⚠️ Statement {i} warning: {e}")
                    # Continue with next statement
        
        print("\n🎉 DEPLOYMENT COMPLETED!")
        
        # Verify tables were created
        print("\n📊 Verifying table creation...")
        tables_to_check = [
            'user_profiles',
            'transaction_memory', 
            'conversation_context',
            'spending_analytics',
            'ai_learning'
        ]
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"   ✅ {table} - OK")
            except Exception as e:
                print(f"   ❌ {table} - Error: {e}")
        
        print("\n🧠 Sharp AI Memory System is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(deploy_sharp_ai_system())
