#!/usr/bin/env python3
"""
OPay Webhook Test Script

Test script to verify OPay webhook endpoint is working correctly
when the Sofi AI app is deployed on Render.
"""

import requests
import json
from datetime import datetime

def test_webhook_endpoint_simple():
    """Simple test to check if webhook endpoint exists"""
    webhook_url = "https://sofi-wallet.onrender.com/opay_webhook"
    
    print(f"🔌 Testing OPay Webhook Endpoint: {webhook_url}")
    print("-" * 60)
    
    try:
        # Test with GET request (should return 405 Method Not Allowed)
        print("📡 Testing GET request (should be rejected)...")
        response = requests.get(webhook_url, timeout=15)
        
        if response.status_code == 405:
            print("  ✅ GET request correctly rejected (405 Method Not Allowed)")
        elif response.status_code == 404:
            print("  ❌ Endpoint not found (404) - App may not be deployed or route missing")
            return False
        else:
            print(f"  ⚠️  Unexpected GET response: {response.status_code}")
        
        # Test with POST request (should accept but may return validation error)
        print("📡 Testing POST request (webhook format)...")
        
        test_payload = {
            "event": "test",
            "data": {
                "message": "OPay webhook connectivity test",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OPay-Webhook-Test/1.0"
        }
        
        response = requests.post(
            webhook_url, 
            json=test_payload, 
            headers=headers,
            timeout=15
        )
        
        if response.status_code in [200, 400, 422]:  # Valid responses
            print(f"  ✅ POST request accepted (status: {response.status_code})")
            if response.status_code == 400:
                print("    ℹ️  400 error expected for test data - endpoint is working")
            return True
        elif response.status_code == 404:
            print("  ❌ Endpoint not found (404) - Route may be missing")
            return False
        else:
            print(f"  ⚠️  Unexpected POST response: {response.status_code}")
            print(f"     Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("  ❌ Timeout - App may be starting up or not responding")
        return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Connection failed - App may not be deployed")
        return False
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_main_app_health():
    """Test if the main app is running"""
    base_url = "https://sofi-wallet.onrender.com"
    
    print(f"\n🏥 Testing Main App Health: {base_url}")
    print("-" * 60)
    
    try:
        response = requests.get(base_url, timeout=15)
        
        if response.status_code == 200:
            print("  ✅ Main app is running and responding")
            return True
        else:
            print(f"  ⚠️  Main app returned status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("  ❌ Main app timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to main app")
        return False
    except Exception as e:
        print(f"  ❌ Health check failed: {e}")
        return False

def main():
    """Run webhook connectivity tests"""
    print("🚀 OPay Webhook Connectivity Test")
    print("=" * 60)
    
    # Test main app health first
    app_healthy = test_main_app_health()
    
    # Test webhook endpoint
    webhook_working = test_webhook_endpoint_simple()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"{'✅ PASS' if app_healthy else '❌ FAIL':<8} Main App Health")
    print(f"{'✅ PASS' if webhook_working else '❌ FAIL':<8} Webhook Endpoint")
    
    if app_healthy and webhook_working:
        print("\n🎉 Webhook endpoint is ready for OPay notifications!")
        print("\n📋 Next Steps:")
        print("1. Configure this webhook URL in your OPay merchant dashboard:")
        print("   https://sofi-wallet.onrender.com/opay_webhook")
        print("2. Test with actual OPay transactions")
        print("3. Monitor logs for webhook notifications")
    elif app_healthy and not webhook_working:
        print("\n⚠️  App is running but webhook endpoint has issues.")
        print("   Check that the /opay_webhook route is properly configured.")
    else:
        print("\n❌ App deployment issues detected.")
        print("   Ensure your Sofi AI app is deployed and running on Render.")

if __name__ == "__main__":
    main()
