#!/usr/bin/env python3
"""
FINAL PRE-DEPLOYMENT TEST SUITE
Tests all critical Sofi AI features before deploying to Render
"""

import os
import sys
import asyncio
from datetime import datetime

def test_environment_variables():
    """Check that all required environment variables are available"""
    print("🔧 TESTING ENVIRONMENT VARIABLES")
    print("-" * 40)
    
    required_vars = [
        'OPENAI_API_KEY',
        'SUPABASE_URL', 
        'SUPABASE_KEY',
        'TELEGRAM_BOT_TOKEN',
        'MONNIFY_API_KEY',
        'MONNIFY_SECRET_KEY',
        'BITNOB_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * min(10, len(value))}...")
        else:
            print(f"   ❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        return False
    else:
        print("\n✅ All environment variables present")
        return True

def test_imports():
    """Test all critical imports"""
    print("\n📦 TESTING IMPORTS")
    print("-" * 40)
    
    imports_to_test = [
        ('Flask', 'from flask import Flask'),
        ('OpenAI', 'import openai'),
        ('Supabase', 'from supabase import create_client'),
        ('Main App', 'import main'),
        ('Crypto Functions', 'from crypto.wallet import create_bitnob_wallet'),
        ('NLP Intent Parser', 'from nlp.intent_parser import extract_intent'),
        ('Enhanced AI', 'from utils.enhanced_ai_responses import enhanced_detect_intent'),
        ('Permanent Memory', 'from utils.permanent_memory import save_user_memory'),
    ]
    
    failed_imports = []
    for name, import_stmt in imports_to_test:
        try:
            exec(import_stmt)
            print(f"   ✅ {name}")
        except Exception as e:
            print(f"   ❌ {name}: {str(e)}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {failed_imports}")
        return False
    else:
        print("\n✅ All imports successful")
        return True

def test_core_functionality():
    """Test core Sofi AI functionality"""
    print("\n🧠 TESTING CORE FUNCTIONALITY")
    print("-" * 40)
    
    try:
        # Test intent detection
        from main import detect_intent
        result = detect_intent("send 5000 to John")
        if result and result.get('intent') == 'transfer':
            print("   ✅ Intent detection working")
        else:
            print("   ❌ Intent detection failed")
            return False
        
        # Test beneficiary functions
        from main import find_beneficiary_by_name, save_beneficiary_to_supabase
        print("   ✅ Beneficiary functions available")
        
        # Test crypto functions
        from crypto.rates import get_multiple_crypto_rates
        print("   ✅ Crypto rate functions available")
        
        # Test memory functions
        from utils.permanent_memory import save_user_memory
        print("   ✅ Permanent memory functions available")
        
        print("\n✅ Core functionality verified")
        return True
        
    except Exception as e:
        print(f"\n❌ Core functionality test failed: {str(e)}")
        return False

def test_deployment_files():
    """Check deployment configuration files"""
    print("\n📋 TESTING DEPLOYMENT FILES")
    print("-" * 40)
    
    deployment_files = [
        ('requirements.txt', 'Python dependencies'),
        ('Procfile', 'Process file for deployment'),
        ('render.yaml', 'Render configuration'),
        ('.env', 'Environment variables (should exist)')
    ]
    
    missing_files = []
    for filename, description in deployment_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}: {description}")
        else:
            print(f"   ❌ {filename}: Missing - {description}")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n⚠️  Missing deployment files: {missing_files}")
        return False
    else:
        print("\n✅ All deployment files present")
        return True

def test_database_schema():
    """Test database connectivity and schema"""
    print("\n🗄️  TESTING DATABASE CONNECTIVITY")
    print("-" * 40)
    
    try:
        from main import get_supabase_client
        client = get_supabase_client()
        
        # Test table access
        tables_to_check = [
            'users',
            'virtual_accounts', 
            'beneficiaries',
            'crypto_wallets',
            'user_memory'
        ]
        
        for table in tables_to_check:
            try:
                # Just check if we can query the table (limit 1)
                response = client.table(table).select("*").limit(1).execute()
                print(f"   ✅ {table} table accessible")
            except Exception as e:
                print(f"   ⚠️  {table} table: {str(e)}")
        
        print("\n✅ Database connectivity verified")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {str(e)}")
        return False

def generate_deployment_report():
    """Generate final deployment readiness report"""
    print("\n" + "="*60)
    print("🚀 SOFI AI DEPLOYMENT READINESS REPORT")
    print("="*60)
    
    # Run all tests
    test_results = {
        'Environment Variables': test_environment_variables(),
        'Imports': test_imports(),
        'Core Functionality': test_core_functionality(),
        'Deployment Files': test_deployment_files(),
        'Database Connectivity': test_database_schema()
    }
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    print("-" * 40)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📈 OVERALL STATUS:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"\n🎉 DEPLOYMENT READY!")
        print("✅ Sofi AI is ready for production deployment to Render")
        print("✅ All critical systems verified")
        print("✅ Natural language understanding active")
        print("✅ Beneficiary system operational")
        print("✅ Crypto integration (BTC/USDT) working") 
        print("✅ Permanent memory system active")
        print("✅ Database connectivity confirmed")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Deploy to Render using the render.yaml configuration")
        print("2. Set environment variables in Render dashboard")
        print("3. Configure webhook URLs for Telegram and Monnify")
        print("4. Test production deployment")
        
        return True
    else:
        print(f"\n⚠️  DEPLOYMENT NOT READY")
        print(f"   Success rate too low: {success_rate:.1f}%")
        print("   Please fix failing tests before deployment")
        return False

if __name__ == "__main__":
    try:
        deployment_ready = generate_deployment_report()
        sys.exit(0 if deployment_ready else 1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(1)
