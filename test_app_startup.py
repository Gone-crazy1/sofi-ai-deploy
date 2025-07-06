#!/usr/bin/env python3
"""
Test App Startup
================
Test if the app can start without crashing
"""

import os
import sys
import time
import requests
from datetime import datetime

def test_app_startup():
    """Test if the app can start and respond"""
    
    print("🚀 Testing App Startup...")
    
    # Test just the deployed app
    print("\n1. Testing deployed app health...")
    try:
        response = requests.get(
            "https://pipinstallsofi.com/health",
            timeout=30,
            allow_redirects=True
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ PASS: App is running and healthy")
            try:
                data = response.json()
                print(f"Health data: {data}")
            except:
                print("Response is not JSON")
        else:
            print(f"❌ FAIL: Health check returned {response.status_code}")
            print(f"Response text: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test with a simple user agent
    print("\n2. Testing with simple user agent...")
    try:
        response = requests.get(
            "https://pipinstallsofi.com/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
            allow_redirects=True
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PASS: Home page loads with browser user agent")
        else:
            print(f"❌ FAIL: Home page returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test webhook endpoint
    print("\n3. Testing webhook endpoint...")
    try:
        response = requests.post(
            "https://pipinstallsofi.com/webhook",
            json={"test": "ping"},
            headers={"User-Agent": "TelegramBot (like TwitterBot)"},
            timeout=15
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code in [200, 400, 401, 403]:
            print("✅ PASS: Webhook endpoint is accessible")
        else:
            print(f"❌ FAIL: Webhook returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n🎯 App startup test completed!")

if __name__ == "__main__":
    test_app_startup()
