#!/usr/bin/env python3
"""
Quick Domain Test - Focus on the most likely candidates
"""

import requests
import socket

def quick_test(domain):
    print(f"\n🔍 Testing {domain}:")
    
    # DNS test
    try:
        ip = socket.gethostbyname(domain)
        print(f"  ✅ DNS: {ip}")
        
        # HTTP test
        try:
            response = requests.head(f"https://{domain}", timeout=5)
            print(f"  ✅ HTTPS: {response.status_code}")
            return True
        except:
            try:
                response = requests.head(f"http://{domain}", timeout=5)
                print(f"  ✅ HTTP: {response.status_code}")
                return True
            except Exception as e:
                print(f"  ❌ Connection failed: {str(e)[:50]}")
                return False
    except Exception as e:
        print(f"  ❌ DNS failed: {str(e)[:50]}")
        return False

# Test the most likely candidates
domains = [
    "nellobytesystem.com",
    "clubkonnect.com", 
    "www.clubkonnect.com",
    "api.clubkonnect.com"
]

print("🚀 QUICK DOMAIN TEST")
print("=" * 30)

working = []
for domain in domains:
    if quick_test(domain):
        working.append(domain)

print(f"\n📊 RESULTS:")
if working:
    print("✅ Working domains:")
    for domain in working:
        print(f"   • {domain}")
else:
    print("❌ No working domains found")
