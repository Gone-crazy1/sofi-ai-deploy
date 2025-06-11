#!/usr/bin/env python3
"""
Simple test to verify core functionality without Unicode emojis
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_core_functionality():
    """Test core functionality without emojis"""
    print("Testing core functionality...")
    
    try:
        # Test 1: Supabase connection
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("ERROR: Missing Supabase credentials")
            return False
            
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("PASS: Supabase connection successful")
        
        # Test 2: Phone column exists
        try:
            result = supabase.table("users").select("phone").limit(1).execute()
            print("PASS: Phone column exists in users table")
        except Exception as e:
            print(f"FAIL: Phone column test failed: {e}")
            return False
        
        # Test 3: Virtual accounts table exists
        try:
            result = supabase.table("virtual_accounts").select("id").limit(1).execute()
            print("PASS: Virtual accounts table accessible")
        except Exception as e:
            print(f"FAIL: Virtual accounts table test failed: {e}")
            return False
        
        # Test 4: Main.py imports successfully
        try:
            import main
            print("PASS: main.py imports successfully")
        except Exception as e:
            print(f"FAIL: main.py import failed: {e}")
            return False
        
        print("\nALL CORE TESTS PASSED!")
        print("System is ready for Git commit and deployment")
        return True
        
    except Exception as e:
        print(f"ERROR: Core test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    if success:
        print("\nSUCCESS: Core functionality verified")
        exit(0)
    else:
        print("\nFAILED: Core functionality issues found")
        exit(1)
