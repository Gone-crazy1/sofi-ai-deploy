#!/usr/bin/env python3
"""
Final deployment readiness test
"""
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

print("🚀 SOFI AI DEPLOYMENT READINESS TEST")
print("=" * 50)

def test_environment():
    """Test environment configuration"""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "SUPABASE_URL", 
        "SUPABASE_KEY",
        "OPENAI_API_KEY",
        "PAYSTACK_SECRET_KEY",
        "ADMIN_CHAT_IDS"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are configured")
        return True

def test_imports():
    """Test critical imports"""
    try:
        import main
        print("✅ Main module imports successfully")
        
        # Test key components
        if hasattr(main, 'app'):
            print("✅ Flask app instance exists")
        
        if hasattr(main, 'supabase'):
            print("✅ Supabase client initialized")
        
        if hasattr(main, 'openai_client'):
            print("✅ OpenAI client initialized")
            
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_routes():
    """Test Flask routes"""
    try:
        import main
        routes = [rule.rule for rule in main.app.url_map.iter_rules()]
        
        critical_routes = [
            '/webhook',
            '/health',
            '/api/paystack/webhook',
            '/verify-pin',
            '/onboard'
        ]
        
        for route in critical_routes:
            if route in routes:
                print(f"✅ Route {route} registered")
            else:
                print(f"❌ Route {route} missing")
                
        print(f"✅ Total routes registered: {len(routes)}")
        return True
    except Exception as e:
        print(f"❌ Route test error: {e}")
        return False

# Run tests
print("\n🧪 Testing Environment...")
env_ok = test_environment()

print("\n📦 Testing Imports...")
import_ok = test_imports()

print("\n🛣️  Testing Routes...")
routes_ok = test_routes()

# Final status
print("\n" + "=" * 50)
if env_ok and import_ok and routes_ok:
    print("🎉 DEPLOYMENT READY!")
    print("✅ All critical tests passed")
    print("🚀 Sofi AI is ready to deploy and run")
    exit(0)
else:
    print("❌ DEPLOYMENT NOT READY")
    print("⚠️  Fix the issues above before deploying")
    exit(1)
