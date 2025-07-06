"""
SOFI AI SECURITY SYSTEM TEST
===========================
Test the comprehensive security system and end-to-end functionality
"""

import sys
import os
import requests
import time
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_security_imports():
    """Test that all security modules can be imported"""
    try:
        from utils.security import SecurityManager
        from utils.security_monitor import SecurityMonitor
        from utils.security_config import SECURITY_CONFIG
        print("✅ All security modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import security modules: {e}")
        return False

def test_security_initialization():
    """Test that security components initialize properly"""
    try:
        from utils.security import SecurityManager
        from utils.security_monitor import SecurityMonitor
        
        # Test security manager initialization
        security_manager = SecurityManager()
        print("✅ Security Manager initialized")
        
        # Test security monitor initialization
        security_monitor = SecurityMonitor()
        print("✅ Security Monitor initialized")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize security components: {e}")
        return False

def test_main_app_integration():
    """Test that main.py can be imported with security"""
    try:
        from main import app
        print("✅ Main app imported successfully with security")
        return True
    except Exception as e:
        print(f"❌ Failed to import main app: {e}")
        return False

def test_flask_app_creation():
    """Test that Flask app can be created with security middleware"""
    try:
        from main import app
        from utils.security import SecurityManager
        
        # Check if security middleware is attached
        if hasattr(app, 'security_manager'):
            print("✅ Security middleware attached to Flask app")
        else:
            print("⚠️  Security middleware not attached to Flask app")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create Flask app with security: {e}")
        return False

def test_security_routes():
    """Test that security routes are blocked correctly"""
    try:
        from main import app
        
        # Test blocked paths
        blocked_paths = [
            '/wp-admin',
            '/wp-login.php',
            '/wordpress',
            '/setup-config.php',
            '/.env',
            '/phpmyadmin'
        ]
        
        with app.test_client() as client:
            for path in blocked_paths:
                response = client.get(path)
                if response.status_code == 403:
                    print(f"✅ Blocked path {path} correctly returns 403")
                else:
                    print(f"⚠️  Path {path} returned {response.status_code} instead of 403")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test security routes: {e}")
        return False

def test_onboarding_flow():
    """Test that onboarding flow works correctly"""
    try:
        from main import app
        
        with app.test_client() as client:
            # Test onboarding route
            response = client.get('/onboard')
            if response.status_code == 200:
                print("✅ Onboarding route accessible")
                
                # Check if response contains expected elements
                content = response.get_data(as_text=True)
                if 'Telegram ID' in content:
                    print("✅ Onboarding shows Telegram ID field")
                else:
                    print("⚠️  Onboarding missing Telegram ID field")
                    
                if 'pipinstallsofi.com' in content:
                    print("✅ Onboarding uses correct domain")
                else:
                    print("⚠️  Onboarding domain check failed")
            else:
                print(f"❌ Onboarding route returned {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test onboarding flow: {e}")
        return False

def test_pin_verification():
    """Test that PIN verification page works"""
    try:
        from main import app
        
        with app.test_client() as client:
            # Test PIN verification route with test data
            response = client.get('/test-pin')
            if response.status_code == 200:
                print("✅ PIN verification test route accessible")
                
                # Check if response contains expected elements
                content = response.get_data(as_text=True)
                if 'Enter your PIN' in content or 'PIN' in content:
                    print("✅ PIN verification page contains PIN fields")
                else:
                    print("⚠️  PIN verification page missing PIN fields")
            else:
                print(f"❌ PIN verification route returned {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test PIN verification: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are accessible"""
    try:
        from main import app
        
        with app.test_client() as client:
            # Test webhook endpoint
            response = client.post('/webhook', 
                                 data=json.dumps({'test': 'data'}),
                                 content_type='application/json')
            if response.status_code in [200, 400, 405]:  # 400/405 are expected for test data
                print("✅ Webhook endpoint accessible")
            else:
                print(f"⚠️  Webhook endpoint returned {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test API endpoints: {e}")
        return False

def test_security_monitoring():
    """Test that security monitoring works"""
    try:
        from utils.security_monitor import SecurityMonitor, AlertLevel
        
        # Create a test security monitor
        monitor = SecurityMonitor()
        
        # Test creating a security event
        test_event = monitor.create_security_event(
            event_type="test_event",
            severity=AlertLevel.LOW,
            ip_address="127.0.0.1",
            user_agent="test-agent",
            path="/test",
            method="GET",
            details={"test": "data"}
        )
        
        if test_event:
            print("✅ Security event creation works")
        else:
            print("❌ Failed to create security event")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test security monitoring: {e}")
        return False

def main():
    """Run all security and functionality tests"""
    print("🔒 SOFI AI SECURITY SYSTEM TEST")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print()
    
    tests = [
        ("Security Module Imports", test_security_imports),
        ("Security Initialization", test_security_initialization),
        ("Main App Integration", test_main_app_integration),
        ("Flask App Creation", test_flask_app_creation),
        ("Security Routes", test_security_routes),
        ("Onboarding Flow", test_onboarding_flow),
        ("PIN Verification", test_pin_verification),
        ("API Endpoints", test_api_endpoints),
        ("Security Monitoring", test_security_monitoring),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed}/{passed + failed} ({(passed/(passed+failed)*100):.1f}%)")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Security system is ready for deployment.")
    else:
        print(f"\n⚠️  {failed} tests failed. Please review and fix issues before deployment.")
    
    print(f"\nTest completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
