"""
Test the security endpoints and IP intelligence system
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
ADMIN_API_KEY = "your-secret-admin-key"  # Update with your actual key

def test_health_endpoint():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/security/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_ping_endpoint():
    """Test ping endpoint"""
    print("\n🏓 Testing ping endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/security/ping")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_security_stats():
    """Test security stats endpoint"""
    print("\n📊 Testing security stats endpoint...")
    try:
        headers = {"X-API-Key": ADMIN_API_KEY}
        response = requests.get(f"{BASE_URL}/security/stats", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_block_ip():
    """Test IP blocking endpoint"""
    print("\n🚫 Testing IP blocking endpoint...")
    try:
        headers = {"X-API-Key": ADMIN_API_KEY, "Content-Type": "application/json"}
        data = {
            "ip": "192.168.1.100",
            "reason": "Test blocking"
        }
        response = requests.post(f"{BASE_URL}/security/block-ip", headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_check_ip():
    """Test IP status check endpoint"""
    print("\n🔍 Testing IP status check endpoint...")
    try:
        headers = {"X-API-Key": ADMIN_API_KEY, "Content-Type": "application/json"}
        data = {"ip": "192.168.1.100"}
        response = requests.post(f"{BASE_URL}/security/check-ip", headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_bot_detection():
    """Test bot detection endpoint"""
    print("\n🤖 Testing bot detection endpoint...")
    try:
        headers = {
            "User-Agent": "python-requests/2.31.0",  # Suspicious user agent
            "Content-Type": "application/json"
        }
        data = {
            "path": "/wp-admin/admin.php",  # Suspicious path
            "method": "GET"
        }
        response = requests.post(f"{BASE_URL}/security/detect-bot", headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_rate_limiting():
    """Test rate limiting by making rapid requests"""
    print("\n⚡ Testing rate limiting...")
    try:
        # Make rapid requests to trigger rate limiting
        for i in range(15):
            response = requests.get(f"{BASE_URL}/security/ping")
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 429:
                print("Rate limiting triggered!")
                break
            time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")

def test_unauthorized_access():
    """Test unauthorized access to admin endpoints"""
    print("\n🔐 Testing unauthorized access...")
    try:
        # Try to access stats without API key
        response = requests.get(f"{BASE_URL}/security/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all security tests"""
    print("🔒 SOFI AI SECURITY SYSTEM TESTS")
    print("=" * 50)
    
    # Basic endpoint tests
    test_health_endpoint()
    test_ping_endpoint()
    
    # Admin endpoint tests
    test_security_stats()
    test_block_ip()
    test_check_ip()
    
    # Security feature tests
    test_bot_detection()
    test_rate_limiting()
    test_unauthorized_access()
    
    print("\n✅ Security tests completed!")

if __name__ == "__main__":
    main()
