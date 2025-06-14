#!/usr/bin/env python3
"""
Simple Clubkonnect API Test
"""

import requests

def test_endpoint(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code, len(response.text)
    except Exception as e:
        return 0, str(e)[:50]

endpoints = [
    "https://clubkonnect.com/airtime_api.php",
    "https://www.clubkonnect.com/airtime_api.php", 
    "https://clubkonnect.com/api/airtime.php",
    "https://www.clubkonnect.com/api/airtime.php"
]

print("🔍 CLUBKONNECT API ENDPOINT TEST")
print("=" * 35)

for url in endpoints:
    status, info = test_endpoint(url)
    print(f"{url}")
    print(f"  Status: {status} | Response size: {info}")
    print()

print("💡 Next steps:")
print("1. Contact Clubkonnect support for correct API endpoint")
print("2. Request API documentation")
print("3. Verify your API credentials")
