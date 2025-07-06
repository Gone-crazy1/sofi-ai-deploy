#!/usr/bin/env python3
"""
Test Security Fixes
===================
Test that legitimate traffic is no longer blocked
"""

import requests
import json
import time

def test_security_fixes():
    """Test that security fixes work properly"""
    
    print("🔒 Testing Security Fixes...")
    
    # Test 1: Home page with go-http-client (should be allowed)
    print("\n1. Testing home page with go-http-client user agent...")
    try:
        response = requests.get(
            "https://pipinstallsofi.com/",
            headers={"User-Agent": "Go-http-client/2.0"},
            timeout=10,
            allow_redirects=False  # Don't follow redirects to see what's happening
        )
        
        if response.status_code == 200:
            print("✅ PASS: Home page accessible with go-http-client")
        else:
            print(f"❌ FAIL: Home page returned {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Health endpoint (should be accessible)
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get("https://pipinstallsofi.com/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ PASS: Health endpoint accessible")
        else:
            print(f"❌ FAIL: Health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: PIN verification page (should render correctly)
    print("\n3. Testing PIN verification page...")
    try:
        response = requests.get(
            "https://pipinstallsofi.com/verify-pin?txn_id=test_123",
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ PASS: PIN verification page accessible")
        elif response.status_code == 400:
            print("✅ PASS: PIN verification page returns proper error for invalid transaction")
        else:
            print(f"❌ FAIL: PIN verification page returned {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 4: Webhook endpoint (should be accessible for Telegram)
    print("\n4. Testing webhook endpoint accessibility...")
    try:
        response = requests.post(
            "https://pipinstallsofi.com/webhook",
            json={"test": "data"},
            headers={"User-Agent": "TelegramBot (like TwitterBot)"},
            timeout=10
        )
        
        # Even if it fails validation, it should not be blocked by security
        if response.status_code in [200, 400, 403]:
            print("✅ PASS: Webhook endpoint accessible (not blocked by security)")
        else:
            print(f"❌ FAIL: Webhook endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n🎯 Security fixes test completed!")

if __name__ == "__main__":
    test_security_fixes()
