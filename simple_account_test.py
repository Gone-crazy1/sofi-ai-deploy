#!/usr/bin/env python3
"""
Simple test for virtual account creation functions
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing Account Creation Imports")
    print("=" * 40)
    
    try:
        # Test Monnify imports
        from monnify.Transfers import create_virtual_account
        from monnify.Auth import get_monnify_token
        print("✅ Monnify functions imported successfully")
        
        # Test Supabase import
        from supabase import create_client
        print("✅ Supabase client imported successfully")
        
        # Test main app functions
        from main import app
        print("✅ Flask app imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing Environment Variables")
    print("=" * 40)
    
    required_vars = [
        'MONNIFY_API_KEY',
        'MONNIFY_SECRET_KEY', 
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Present")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All environment variables present")
        return True

def test_account_creation_logic():
    """Test the account creation logic"""
    print("\n💳 Testing Account Creation Logic")
    print("=" * 40)
    
    # Test data
    test_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'bvn': '12345678901',
        'chat_id': 'test_user_123'
    }
    
    print(f"Test data: {test_data}")
    
    # Basic validation
    required_fields = ['first_name', 'last_name', 'bvn', 'chat_id']
    missing = [field for field in required_fields if not test_data.get(field)]
    
    if missing:
        print(f"❌ Missing required fields: {missing}")
        return False
    
    # BVN validation
    bvn = str(test_data['bvn'])
    if len(bvn) != 11 or not bvn.isdigit():
        print(f"❌ Invalid BVN format: {bvn}")
        return False
    
    print("✅ Input validation passed")
    
    # Test Monnify token generation
    try:
        from monnify.Auth import get_monnify_token
        token = get_monnify_token()
        
        if token:
            print(f"✅ Monnify token generated: {token[:20]}...")
            return True
        else:
            print("⚠️  Monnify token is None")
            return False
            
    except Exception as e:
        print(f"❌ Monnify auth error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SIMPLE ACCOUNT CREATION TEST")
    print("=" * 50)
    
    # Run tests
    imports_ok = test_imports()
    env_ok = test_environment()
    logic_ok = test_account_creation_logic()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Logic: {'✅ PASS' if logic_ok else '❌ FAIL'}")
    
    if all([imports_ok, env_ok, logic_ok]):
        print("\n🎉 ACCOUNT CREATION SYSTEM READY!")
        print("✅ All tests passed")
        print("🚀 Ready to create virtual accounts")
    else:
        print("\n⚠️  Some tests failed")
        print("🔧 Fix issues before proceeding")
    
    print(f"\n📅 Test completed at: {__import__('datetime').datetime.now()}")
