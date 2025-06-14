#!/usr/bin/env python3
"""
Test Clubkonnect Airtime API Endpoints
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

USERID = os.getenv("NELLOBYTES_USERID")
APIKEY = os.getenv("NELLOBYTES_APIKEY")

def test_airtime_endpoint(base_url, endpoint):
    """Test airtime API endpoint"""
    url = f"{base_url}{endpoint}"
    
    # Test parameters (won't actually purchase - just test connectivity)
    params = {
        'userid': USERID or 'test',
        'pass': APIKEY or 'test', 
        'amount': '100',
        'network': 'MTN',
        'phone': '08012345678',
        'ref': 'TEST123'
    }
    
    print(f"\n🔍 Testing: {url}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, str(e)

# Test different base URLs and endpoints
base_urls = [
    "https://clubkonnect.com",
    "https://www.clubkonnect.com",
    "http://clubkonnect.com",
    "http://www.clubkonnect.com"
]

endpoints = [
    "/airtime_api.php",
    "/api/airtime.php", 
    "/airtime.php",
    "/api/airtime",
    "/purchase_airtime.php"
]

print("🔍 TESTING CLUBKONNECT AIRTIME API")
print("=" * 40)

if not USERID or not APIKEY:
    print("⚠️ Warning: API credentials not found")
    print("   Using test credentials - expect authentication errors")

working_endpoints = []

for base_url in base_urls:
    print(f"\n🌐 Base URL: {base_url}")
    print("-" * 30)
    
    for endpoint in endpoints:
        success, result = test_airtime_endpoint(base_url, endpoint)
        if success:
            working_endpoints.append(f"{base_url}{endpoint}")

print(f"\n{'='*40}")
print("📊 SUMMARY")
print("=" * 40)

if working_endpoints:
    print("✅ Working endpoints found:")
    for endpoint in working_endpoints:
        print(f"   • {endpoint}")
    
    print(f"\n🔧 Update your configuration:")
    print(f"NELLOBYTES_BASE_URL = \"{working_endpoints[0].split('/airtime')[0]}\"")
else:
    print("❌ No working endpoints found")
    print("\n💡 Possible reasons:")
    print("1. Different endpoint path required")
    print("2. Authentication issues")
    print("3. API might be down")
    print("4. Need to contact Clubkonnect for API documentation")
