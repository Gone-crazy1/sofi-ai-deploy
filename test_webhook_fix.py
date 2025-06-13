#!/usr/bin/env python3
"""
Test script to verify webhook endpoint is working after critical fix
"""
import requests
import json
import time

def test_webhook_endpoints():
    """Test all webhook endpoints to ensure they're working"""
    base_url = "https://sofi-ai-trio.onrender.com"
    
    # Test data for webhook (minimal valid Telegram update)
    test_data = {
        "message": {
            "chat": {"id": 123456789},
            "text": "test message"
        }
    }
    
    endpoints_to_test = [
        "/webhook",           # Main webhook (was causing 404)
        "/webhook_incoming",  # Original webhook
        "/webhook_backup"     # Backup webhook
    ]
    
    results = []
    
    print("🔍 TESTING WEBHOOK ENDPOINTS...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        print(f"\n📡 Testing {endpoint}...")
        url = f"{base_url}{endpoint}"
        
        try:
            response = requests.post(url, json=test_data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: SUCCESS (200)")
                results.append(f"✅ {endpoint}: Working")
            elif response.status_code == 404:
                print(f"❌ {endpoint}: NOT FOUND (404)")
                results.append(f"❌ {endpoint}: 404 Error")
            else:
                print(f"⚠️  {endpoint}: Status {response.status_code}")
                results.append(f"⚠️ {endpoint}: Status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️  {endpoint}: TIMEOUT")
            results.append(f"⏱️ {endpoint}: Timeout")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {str(e)}")
            results.append(f"❌ {endpoint}: Error - {str(e)}")
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print("=" * 50)
    
    for result in results:
        print(result)
    
    # Check if main webhook is working
    main_webhook_working = any("✅ /webhook: Working" in result for result in results)
    
    if main_webhook_working:
        print(f"\n🎉 SUCCESS: Main webhook (/webhook) is now working!")
        print("The bot should be responding to messages again.")
        return True
    else:
        print(f"\n🚨 ISSUE: Main webhook (/webhook) still not working!")
        print("The deployment may need more time or there's still an issue.")
        return False

def test_health_endpoint():
    """Test health endpoint to verify service is running"""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get("https://sofi-ai-trio.onrender.com/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('status', 'unknown')}")
            print(f"🕐 Timestamp: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 CRITICAL WEBHOOK FIX VERIFICATION")
    print("=" * 50)
    
    # Wait a moment for deployment
    print("⏳ Waiting for deployment to stabilize...")
    time.sleep(5)
    
    # Test health first
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Test webhook endpoints
        webhook_ok = test_webhook_endpoints()
        
        if webhook_ok:
            print(f"\n🎉 ALL TESTS PASSED!")
            print("The Sofi AI bot should be fully operational now.")
        else:
            print(f"\n⚠️  WEBHOOK ISSUES DETECTED")
            print("The service is healthy but webhook endpoints need attention.")
    else:
        print(f"\n❌ SERVICE HEALTH ISSUES")
        print("The service itself is not responding properly.")
    
    print(f"\n🔗 Service URL: https://sofi-ai-trio.onrender.com")
