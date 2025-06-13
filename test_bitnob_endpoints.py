#!/usr/bin/env python3
"""
Simple test to discover the correct Bitnob API endpoints
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BITNOB_SECRET_KEY = os.getenv("BITNOB_SECRET_KEY")

def test_bitnob_endpoints():
    """Test various possible Bitnob API endpoints"""
    
    if not BITNOB_SECRET_KEY:
        print("❌ BITNOB_SECRET_KEY not found in environment variables")
        return
    
    headers = {
        "Authorization": f"Bearer {BITNOB_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # List of possible endpoints to test
    base_url = "https://api.bitnob.co"
    endpoints_to_test = [
        "/api/v1/customers/wallets",  # Common pattern
        "/api/v1/wallet",             # Singular version
        "/api/v1/accounts",           # Alternative naming
        "/api/v1/crypto/wallets",     # With crypto prefix
        "/api/v2/wallets",            # V2 API
        "/wallets",                   # Without api/v1
        "/customer/wallets",          # Customer-specific
        "/lightning/wallets",         # Lightning-specific
        "/btc/wallets",               # BTC-specific
    ]
    
    print("🔍 Testing Bitnob API endpoints...")
    print(f"🔑 Using API key: {BITNOB_SECRET_KEY[:20]}...")
    print()
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"Testing: {url}")
        
        try:
            # Test GET first (safer)
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  GET {response.status_code}: {response.text[:200]}")
            
            # If GET works, try POST for wallet creation
            if response.status_code in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                test_data = {
                    "customerEmail": "test@example.com",
                    "label": "Test Wallet"
                }
                post_response = requests.post(url, headers=headers, json=test_data, timeout=10)
                print(f"  POST {post_response.status_code}: {post_response.text[:200]}")
                
                if post_response.status_code not in [404, 405]:
                    print(f"  ✅ Potential working endpoint: {url}")
                    
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()
    
    # Also test some common API info endpoints
    info_endpoints = [
        "/api/v1/health",
        "/api/v1/status", 
        "/health",
        "/status",
        "/api/v1",
        "/api/v2",
        "/"
    ]
    
    print("🔍 Testing API info endpoints...")
    for endpoint in info_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url}: {response.text[:100]}")
        except:
            pass

if __name__ == "__main__":
    test_bitnob_endpoints()
