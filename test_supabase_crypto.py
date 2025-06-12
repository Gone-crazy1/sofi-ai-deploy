#!/usr/bin/env python3
"""
Test Supabase connection specifically for crypto modules
"""

print("🔍 Testing Supabase connection for crypto modules...")

try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    print("✅ Environment loaded")
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    print(f"📍 SUPABASE_URL: {SUPABASE_URL[:30]}..." if SUPABASE_URL else "❌ No SUPABASE_URL")
    print(f"🔑 SUPABASE_KEY: {'Found' if SUPABASE_KEY else 'Missing'}")
    
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        print("✅ Supabase imported")
        
        print("🔌 Creating Supabase client...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client created successfully")
        
        # Test a simple query to see if connection works
        print("🧪 Testing connection with a simple query...")
        try:
            # Try to get table info without actually querying data
            result = supabase.table('users').select('*').limit(1).execute()
            print("✅ Supabase connection test successful")
            print(f"📊 Query executed, got {len(result.data)} rows")
        except Exception as query_error:
            print(f"⚠️ Supabase query failed: {query_error}")
            print("But client creation was successful")
    else:
        print("❌ Missing Supabase credentials")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
