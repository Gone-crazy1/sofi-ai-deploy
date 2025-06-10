#!/usr/bin/env python3
"""
Test script for virtual account creation
"""
import requests
import json

def test_virtual_account_creation():
    """Test the virtual account creation API"""
    url = "https://sofi-ai-trio.onrender.com/api/create_virtual_account"
    
    test_data = {
        "firstName": "Test",
        "lastName": "User",
        "bvn": "12345678901",
        "phone": "08012345678"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Virtual account creation test passed!")
        else:
            print("❌ Virtual account creation test failed!")
            
    except Exception as e:
        print(f"❌ Error testing virtual account creation: {e}")

def test_local_virtual_account():
    """Test the virtual account creation locally"""
    url = "http://localhost:5000/api/create_virtual_account"
    
    test_data = {
        "firstName": "Local",
        "lastName": "Test",
        "bvn": "12345678901", 
        "phone": "08012345678"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        print(f"Local Status Code: {response.status_code}")
        print(f"Local Response: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("Local server not running - skipping local test")
    except Exception as e:
        print(f"❌ Error testing local virtual account creation: {e}")

if __name__ == "__main__":
    print("Testing virtual account creation...")
    print("\n1. Testing deployed version:")
    test_virtual_account_creation()
    
    print("\n2. Testing local version:")
    test_local_virtual_account()
