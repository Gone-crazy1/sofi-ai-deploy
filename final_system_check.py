#!/usr/bin/env python3
"""
Final Production System Check for Sofi AI
Validates all components are ready for deployment
"""

import sys
import os
import traceback
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import(module_name, description):
    """Test importing a module and return success status"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def test_core_functions():
    """Test core Sofi AI functions"""
    print("🧪 Testing Core Functions:")
    
    try:
        # Test intent detection
        from main import detect_intent
        from unittest.mock import patch, MagicMock
        import json
        
        with patch('main.openai.ChatCompletion.create') as mock_openai:
            mock_response = {
                "intent": "balance_inquiry",
                "confidence": 0.9,
                "details": {}
            }
            mock_openai.return_value = MagicMock(
                choices=[{'message': {'content': json.dumps(mock_response)}}]
            )
            
            result = detect_intent("What's my balance?")
            if result.get("intent") == "balance_inquiry":
                print("✅ Intent detection working")
            else:
                print("❌ Intent detection failed")
                
    except Exception as e:
        print(f"❌ Core functions test failed: {str(e)}")

def check_crypto_integration():
    """Check crypto integration status"""
    print("\n₿ Checking Crypto Integration:")
    
    try:
        from crypto.rates import CRYPTO_MAPPING
        
        # Verify ETH is removed
        if "ETH" not in CRYPTO_MAPPING:
            print("✅ ETH successfully removed from crypto mapping")
        else:
            print("❌ ETH still present in crypto mapping")
            
        # Verify BTC and USDT are present
        if "BTC" in CRYPTO_MAPPING and "USDT" in CRYPTO_MAPPING:
            print("✅ BTC and USDT properly configured")
        else:
            print("❌ BTC or USDT missing from crypto mapping")
            
        print(f"✅ Supported cryptos: {list(CRYPTO_MAPPING.keys())}")
        
    except Exception as e:
        print(f"❌ Crypto integration check failed: {str(e)}")

def check_database_schema():
    """Check database schema files"""
    print("\n🗄️ Checking Database Schema:")
    
    schema_files = [
        "create_complete_crypto_tables.sql",
        "COMPLETE_CRYPTO_SETUP.sql"
    ]
    
    for file in schema_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                content = f.read()
                if "eth_address" not in content.lower():
                    print(f"✅ {file} - ETH references removed")
                else:
                    print(f"❌ {file} - Still contains ETH references")
        else:
            print(f"⚠️ {file} - File not found")

def run_final_system_check():
    """Run comprehensive system check"""
    print("🚀 SOFI AI FINAL PRODUCTION SYSTEM CHECK")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Module import tests
    print("📦 Testing Module Imports:")
    modules = [
        ("main", "Main application module"),
        ("crypto.rates", "Cryptocurrency rates module"),
        ("crypto.wallet", "Crypto wallet module"),
        ("utils.enhanced_ai_responses", "Enhanced AI responses"),
        ("nlp.intent_parser", "NLP intent parser"),
        ("webhooks.monnify_webhook", "Monnify webhook handler")
    ]
    
    import_success = 0
    for module, description in modules:
        if test_import(module, description):
            import_success += 1
    
    print(f"\nImport Success Rate: {import_success}/{len(modules)} ({(import_success/len(modules)*100):.1f}%)")
    
    # Test core functions
    test_core_functions()
    
    # Check crypto integration
    check_crypto_integration()
    
    # Check database schema
    check_database_schema()
    
    # Environment check
    print("\n🔧 Environment Check:")
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "TELEGRAM_BOT_TOKEN"]
    env_success = 0
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} configured")
            env_success += 1
        else:
            print(f"⚠️ {var} not set (required for production)")
    
    print(f"\nEnvironment Success Rate: {env_success}/{len(required_vars)} ({(env_success/len(required_vars)*100):.1f}%)")
    
    # Final assessment
    print("\n" + "=" * 50)
    print("🎯 FINAL ASSESSMENT:")
    
    total_success = import_success + env_success
    total_possible = len(modules) + len(required_vars)
    overall_rate = (total_success / total_possible) * 100
    
    if overall_rate >= 90:
        print("🟢 EXCELLENT - Ready for production deployment!")
    elif overall_rate >= 75:
        print("🟡 GOOD - Minor configurations needed")
    elif overall_rate >= 60:
        print("🟠 FAIR - Some issues need addressing")
    else:
        print("🔴 POOR - Major fixes required")
    
    print(f"Overall Readiness: {overall_rate:.1f}%")
    
    print("\n✨ Sofi AI System Check Complete!")
    return overall_rate

if __name__ == "__main__":
    try:
        run_final_system_check()
    except Exception as e:
        print(f"🔥 System check failed with error: {str(e)}")
        traceback.print_exc()
