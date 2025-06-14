#!/usr/bin/env python3
"""
Test Nellobytes API Connection
This script tests connectivity to the Nellobytes API endpoints
"""

import requests
import socket
import os
from dotenv import load_dotenv

load_dotenv()

def test_dns_resolution(domain):
    """Test DNS resolution for a domain"""
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ DNS resolution successful: {domain} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed for {domain}: {e}")
        return False

def test_http_connection(url):
    """Test HTTP connection to URL"""
    try:
        response = requests.head(url, timeout=10)
        print(f"✅ HTTP connection successful: {url} (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error to {url}: {e}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout connecting to {url}")
        return False
    except Exception as e:
        print(f"❌ Error connecting to {url}: {e}")
        return False

def test_airtime_api_endpoint():
    """Test the actual airtime API endpoint"""
    user_id = os.getenv("NELLOBYTES_USERID")
    api_key = os.getenv("NELLOBYTES_APIKEY")
    
    if not user_id or not api_key:
        print("❌ Nellobytes API credentials not found in .env file")
        print("   Please add NELLOBYTES_USERID and NELLOBYTES_APIKEY")
        return False
    
    # Test endpoint with invalid parameters to see if it responds
    url = "https://nellobytesystem.com/airtime_api.php"
    params = {
        "userid": "test",
        "pass": "test",
        "amount": 100,
        "network": "MTN",
        "phone": "08012345678",
        "ref": "TEST123"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"✅ Airtime API endpoint responds: {url} (Status: {response.status_code})")
        if response.text:
            print(f"   Response: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Airtime API endpoint error: {e}")
        return False

def main():
    print("🔍 Testing Nellobytes API Connection")
    print("=" * 50)
    
    # Test different endpoints
    endpoints = [
        "nellobytesystem.com",
        "www.nellobytesystem.com"
    ]
    
    print("\n1. Testing DNS Resolution:")
    dns_results = []
    for domain in endpoints:
        dns_results.append(test_dns_resolution(domain))
    
    print("\n2. Testing HTTP Connections:")
    http_results = []
    for domain in endpoints:
        for protocol in ["https", "http"]:
            url = f"{protocol}://{domain}"
            http_results.append(test_http_connection(url))
    
    print("\n3. Testing Airtime API Endpoint:")
    api_result = test_airtime_api_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY:")
    print(f"DNS Resolution: {sum(dns_results)}/{len(dns_results)} successful")
    print(f"HTTP Connections: {sum(http_results)}/{len(http_results)} successful")
    print(f"API Endpoint: {'✅ Working' if api_result else '❌ Failed'}")
    
    if not any(dns_results):
        print("\n🚨 CRITICAL: DNS resolution failed for all endpoints!")
        print("   This indicates a network connectivity issue.")
        print("   Possible solutions:")
        print("   • Check internet connection")
        print("   • Check DNS settings")
        print("   • Try using different DNS servers (8.8.8.8, 1.1.1.1)")
        print("   • Check if domain is blocked by firewall/proxy")
    elif not any(http_results):
        print("\n⚠️  DNS works but HTTP connections fail!")
        print("   Possible solutions:")
        print("   • Check firewall settings")
        print("   • Check proxy configuration")
        print("   • The service might be temporarily down")
    elif not api_result:
        print("\n⚠️  Network is OK but API endpoint has issues!")
        print("   The service might be temporarily unavailable.")
    else:
        print("\n🎉 All connectivity tests passed!")
        print("   The Nellobytes API should be working.")

if __name__ == "__main__":
    main()
