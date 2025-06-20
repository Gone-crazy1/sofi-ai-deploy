#!/usr/bin/env python3
"""
Quick system test to verify all components are working
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        # Test basic imports
        from utils.admin_command_handler import AdminCommandHandler
        print("✅ AdminCommandHandler imported successfully")
        
        from utils.enhanced_intent_detection import EnhancedIntentDetection
        print("✅ EnhancedIntentDetection imported successfully")
        
        from utils.nigerian_expressions import NigerianExpressions
        print("✅ NigerianExpressions imported successfully")
        
        from utils.secure_pin_verification import SecurePinVerification
        print("✅ SecurePinVerification imported successfully")
        
        from utils.airtime_handler import AirtimeHandler
        print("✅ AirtimeHandler imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_initializations():
    """Test component initializations"""
    print("\n🔧 Testing initializations...")
    
    try:
        # Test AdminCommandHandler
        from utils.admin_command_handler import AdminCommandHandler
        admin_handler = AdminCommandHandler()
        print(f"✅ AdminCommandHandler initialized. Admin IDs: {admin_handler.admin_chat_ids}")
        
        # Test EnhancedIntentDetection  
        from utils.enhanced_intent_detection import EnhancedIntentDetection
        intent_detector = EnhancedIntentDetection()
        print("✅ EnhancedIntentDetection initialized")
        
        # Test NigerianExpressions
        from utils.nigerian_expressions import NigerianExpressions
        expressions = NigerianExpressions()
        print("✅ NigerianExpressions initialized")
        
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("\n🌍 Testing environment...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check critical environment variables
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        admin_id = os.getenv('ADMIN_CHAT_IDS') or os.getenv('ADMIN_CHAT_ID')
        supabase_url = os.getenv('SUPABASE_URL')
        
        print(f"✅ Bot token configured: {'Yes' if bot_token else 'No'}")
        print(f"✅ Admin ID configured: {'Yes' if admin_id else 'No'}")
        print(f"✅ Supabase URL configured: {'Yes' if supabase_url else 'No'}")
        
        return True
    except Exception as e:
        print(f"❌ Environment error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 QUICK SOFI AI SYSTEM TEST")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_imports():
        tests_passed += 1
    
    if test_initializations():
        tests_passed += 1
    
    if test_environment():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! System is ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
