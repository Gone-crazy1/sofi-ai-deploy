#!/usr/bin/env python3
"""
SOFI AI DEPLOYMENT READINESS - QUICK CHECK
Focus on REAL features: Monnify, Crypto, AI (no date forcing)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_deployment_readiness():
    print("🚀 SOFI AI - DEPLOYMENT READINESS CHECK")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 7
    
    # 1. Environment Variables
    print("\n1️⃣ Environment Variables...")
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'OPENAI_API_KEY', 
                    'TELEGRAM_BOT_TOKEN', 'MONNIFY_API_KEY', 'MONNIFY_SECRET_KEY', 'BITNOB_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if not missing:
        print("   ✅ All environment variables present")
        checks_passed += 1
    else:
        print(f"   ❌ Missing: {missing}")
    
    # 2. Database Connection
    print("\n2️⃣ Database Connection...")
    try:
        from supabase import create_client
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
        result = supabase.table('users').select('*').limit(1).execute()
        print("   ✅ Supabase connection working")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Database error: {str(e)}")
    
    # 3. Sharp AI Disabled (Good!)
    print("\n3️⃣ Sharp AI Status...")
    try:
        with open('main.py', 'r') as f:
            main_content = f.read()
            if '# Sharp AI imports temporarily disabled' in main_content:
                print("   ✅ Sharp AI properly disabled (no date forcing)")
                checks_passed += 1
            else:
                print("   ⚠️ Check if Sharp AI is still active")
    except:
        print("   ⚠️ Could not check main.py")
    
    # 4. Monnify Integration
    print("\n4️⃣ Monnify Integration...")
    if os.getenv('MONNIFY_API_KEY') and os.getenv('MONNIFY_SECRET_KEY'):
        print("   ✅ Monnify credentials present")
        checks_passed += 1
    else:
        print("   ❌ Missing Monnify credentials")
    
    # 5. Crypto Integration (REAL)
    print("\n5️⃣ Crypto Integration...")
    if os.getenv('BITNOB_API_KEY'):
        print("   ✅ Bitnob API key present (REAL crypto)")
        checks_passed += 1
    else:
        print("   ❌ Missing Bitnob API key")
    
    # 6. Core Files Present
    print("\n6️⃣ Core Files...")
    required_files = ['main.py', 'requirements.txt', '.env']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if not missing_files:
        print("   ✅ All core files present")
        checks_passed += 1
    else:
        print(f"   ❌ Missing files: {missing_files}")
    
    # 7. Production Configuration
    print("\n7️⃣ Production Config...")
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            if 'debug=False' in content or 'DEBUG = False' in content:
                print("   ✅ Production mode configured")
                checks_passed += 1
            else:
                print("   ⚠️ Check debug mode settings")
    except:
        print("   ⚠️ Could not check production config")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 READINESS SCORE: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 PERFECT! READY FOR RENDER DEPLOYMENT!")
        print("\n🚀 DEPLOYMENT STEPS:")
        print("1. git add . && git commit -m 'Production ready'")
        print("2. git push origin main")
        print("3. Deploy to Render")
        print("4. Set webhook URL to Render domain")
        return True
    elif checks_passed >= 5:
        print("⚠️ MOSTLY READY - Minor issues to fix")
        return False
    else:
        print("❌ NOT READY - Major issues to resolve")
        return False

if __name__ == "__main__":
    success = check_deployment_readiness()
    if success:
        print("\n🎯 GO FOR DEPLOYMENT! 🚀")
    else:
        print("\n🔧 FIX ISSUES FIRST")
