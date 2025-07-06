#!/usr/bin/env python3
"""
Test script to verify deployment fixes
"""

import requests
import json
import time

def test_health_endpoint():
    """Test that health endpoint works without conflicts"""
    try:
        # Test main health endpoint
        response = requests.get("https://pipinstallsofi.com/health", timeout=10)
        print(f"✅ Main health endpoint: {response.status_code} - {response.json()}")
        
        # Test security health endpoint
        response = requests.get("https://pipinstallsofi.com/security/health", timeout=10)
        print(f"✅ Security health endpoint: {response.status_code} - {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_pin_entry_page():
    """Test that PIN entry page loads without template errors"""
    try:
        # Test with a dummy transaction ID
        response = requests.get("https://pipinstallsofi.com/verify-pin?txn_id=test_123", timeout=10)
        
        if response.status_code == 400:
            print("✅ PIN entry page correctly rejects invalid transaction ID")
            return True
        elif response.status_code == 200:
            print("✅ PIN entry page loads successfully")
            return True
        else:
            print(f"❌ PIN entry page returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ PIN entry page test failed: {e}")
        return False

def test_assistant_webhook():
    """Test basic webhook functionality"""
    try:
        # Test webhook endpoint exists
        response = requests.get("https://pipinstallsofi.com/webhook", timeout=10)
        # Should return 405 (Method Not Allowed) for GET request
        if response.status_code == 405:
            print("✅ Webhook endpoint is active and properly configured")
            return True
        else:
            print(f"❌ Webhook endpoint returned unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def main():
    print("🧪 Testing deployment fixes...")
    print("=" * 50)
    
    tests = [
        ("Health Endpoints", test_health_endpoint),
        ("PIN Entry Page", test_pin_entry_page),
        ("Assistant Webhook", test_assistant_webhook)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
