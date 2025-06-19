#!/usr/bin/env python3
"""
Simple Bitnob API test
"""

import os
import requests

# Check environment variable
bitnob_key = os.getenv("BITNOB_SECRET_KEY")
print(f"BITNOB_SECRET_KEY found: {bool(bitnob_key)}")
if bitnob_key:
    print(f"Key starts with: {bitnob_key[:10]}...")

# Test basic connectivity
try:
    print("Testing basic connectivity to Bitnob API...")
    response = requests.get("https://api.bitnob.co", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test with authentication header
if bitnob_key:
    print("\nTesting with authentication...")
    headers = {"Authorization": f"Bearer {bitnob_key}"}
    try:
        response = requests.get("https://api.bitnob.co/api/v1", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
