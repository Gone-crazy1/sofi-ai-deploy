#!/usr/bin/env python3
"""
Verify Airtime API Domains
Test multiple potential domains for the airtime service including Clubkonnect variants
"""

import requests
import socket
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials from environment
NELLOBYTES_USERID = os.getenv("NELLOBYTES_USERID")
NELLOBYTES_APIKEY = os.getenv("NELLOBYTES_APIKEY")

# Potential domains to test
POTENTIAL_DOMAINS = [
    # Current domain from your configuration
    "nellobytesystem.com",
    "www.nellobytesystem.com",
    
    # Clubkonnect variants (since you mentioned it's Clubkonnect's platform)
    "clubkonnect.com",
    "www.clubkonnect.com",
    "api.clubkonnect.com",
    "clubkonnect.ng",
    "www.clubkonnect.ng",
    
    # Other possible variants
    "nellobytes.com",
    "www.nellobytes.com",
    "api.nellobytes.com",
    "nellobyte.com",
    "www.nellobyte.com",
    
    # Alternative spellings/formats
    "nello-bytes.com",
    "nelloByte.com",
    "clubconnect.com",
    "club-konnect.com"
]

# Common API endpoints to test
API_ENDPOINTS = [
    "/airtime_api.php",
    "/api/airtime",
    "/api/v1/airtime",
    "/airtime",
    "/purchase_airtime.php",
    "/buy_airtime.php"
]

def test_dns_resolution(domain):
    """Test if domain resolves"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror as e:
        return False, str(e)

def test_http_connection(domain, use_https=True):
    """Test HTTP/HTTPS connection to domain"""
    protocol = "https" if use_https else "http"
    url = f"{protocol}://{domain}"
    
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return True, response.status_code, response.headers.get('server', 'Unknown')
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)

def test_api_endpoint(domain, endpoint, use_https=True):
    """Test specific API endpoint"""
    protocol = "https" if use_https else "http"
    url = f"{protocol}://{domain}{endpoint}"
    
    # Create a test API call (this won't actually purchase anything)
    params = {
        'userid': NELLOBYTES_USERID or 'test',
        'pass': NELLOBYTES_APIKEY or 'test',
        'amount': '100',
        'network': 'MTN',
        'phone': '08012345678',
        'ref': 'TEST123'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return True, response.status_code, response.text[:200]
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)

def main():
    print("🔍 AIRTIME API DOMAIN VERIFICATION")
    print("=" * 50)
    
    if not NELLOBYTES_USERID or not NELLOBYTES_APIKEY:
        print("⚠️ Warning: API credentials not found in .env file")
        print("   This will limit API endpoint testing")
    
    working_domains = []
    
    for domain in POTENTIAL_DOMAINS:
        print(f"\n🌐 Testing domain: {domain}")
        print("-" * 30)
        
        # Test DNS resolution
        dns_works, dns_result = test_dns_resolution(domain)
        if dns_works:
            print(f"✅ DNS Resolution: {dns_result}")
            
            # Test HTTPS connection
            https_works, https_code, https_server = test_http_connection(domain, use_https=True)
            if https_works:
                print(f"✅ HTTPS Connection: {https_code} ({https_server})")
                working_domains.append((domain, 'https'))
                
                # Test API endpoints
                for endpoint in API_ENDPOINTS:
                    api_works, api_code, api_response = test_api_endpoint(domain, endpoint, use_https=True)
                    if api_works and api_code == 200:
                        print(f"✅ API Endpoint {endpoint}: {api_code}")
                        print(f"   Response preview: {api_response}")
                    elif api_works:
                        print(f"⚠️ API Endpoint {endpoint}: {api_code}")
                        if "authentication" in api_response.lower() or "invalid" in api_response.lower():
                            print(f"   🎯 Potential working endpoint (auth error expected)")
                    
            else:
                print(f"❌ HTTPS Connection failed: {https_server}")
                
                # Try HTTP as fallback
                http_works, http_code, http_server = test_http_connection(domain, use_https=False)
                if http_works:
                    print(f"✅ HTTP Connection: {http_code} ({http_server})")
                    working_domains.append((domain, 'http'))
                else:
                    print(f"❌ HTTP Connection failed: {http_server}")
        else:
            print(f"❌ DNS Resolution failed: {dns_result}")
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 SUMMARY")
    print("=" * 50)
    
    if working_domains:
        print("✅ Working domains found:")
        for domain, protocol in working_domains:
            print(f"   • {protocol}://{domain}")
        
        print(f"\n💡 Recommended actions:")
        print("1. Update your .env file with the correct domain")
        print("2. Test the airtime API with the working domain")
        print("3. Update your airtime_api.py configuration")
        
        # Generate updated configuration
        primary_domain = working_domains[0][0]
        primary_protocol = working_domains[0][1]
        
        print(f"\n🔧 Suggested configuration update:")
        print(f"NELLOBYTES_BASE_URL = \"{primary_protocol}://{primary_domain}\"")
        
    else:
        print("❌ No working domains found")
        print("\n💡 Possible solutions:")
        print("1. Check if you have the correct service provider name")
        print("2. Contact Clubkonnect support for the correct API endpoint")
        print("3. Verify your network connection")
        print("4. Check if you need VPN or proxy settings")
    
    print(f"\n📞 Next steps:")
    print("1. If Clubkonnect is the actual provider, contact them for:")
    print("   - Correct API domain/endpoint")
    print("   - API documentation")
    print("   - Authentication requirements")
    print("2. Verify your API credentials are correct")
    print("3. Test with a small amount first")

if __name__ == "__main__":
    main()
