#!/usr/bin/env python3
"""
Test script to create a virtual account using the Monnify API
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_virtual_account_creation():
    """Test creating a virtual account using our API endpoint"""
    
    # Test data
    test_user = {
        "firstName": "John",
        "lastName": "Doe", 
        "bvn": "12345678901",
        "phone": "08123456789"
    }
    
    print("Testing virtual account creation...")
    print(f"Test user data: {test_user}")
    
    try:
        # Test with local development server first
        local_url = "http://127.0.0.1:5000/api/create_virtual_account"
        
        print(f"\n1. Testing local endpoint: {local_url}")
        try:
            response = requests.post(local_url, json=test_user, timeout=10)
            print(f"Local response status: {response.status_code}")
            print(f"Local response: {response.text}")
        except requests.exceptions.ConnectionError:
            print("[ERROR] Local server not running")
        except Exception as e:
            print(f"[ERROR] Local test error: {e}")
        
        # Test with deployed Render endpoint
        render_url = "https://sofi-ai-trio.onrender.com/api/create_virtual_account"
        
        print(f"\n2. Testing deployed endpoint: {render_url}")
        try:
            response = requests.post(render_url, json=test_user, timeout=30)
            print(f"Deployed response status: {response.status_code}")
            print(f"Deployed response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print("[SUCCESS] Virtual account created successfully!")
                if "accountNumber" in data:
                    print(f"Account Number: {data['accountNumber']}")
                if "bankName" in data:
                    print(f"Bank: {data['bankName']}")
                if "accountName" in data:
                    print(f"Account Name: {data['accountName']}")
                return True
            else:
                print(f"[ERROR] Failed to create virtual account: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Deployed test error: {e}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing virtual account creation: {e}")
        return False

def test_monnify_direct():
    """Test Monnify API directly"""
    
    print("\n3. Testing Monnify API directly...")
    
    try:
        # Get Monnify token first (using Basic Auth)
        auth_url = f"{os.getenv('MONNIFY_BASE_URL')}/api/v1/auth/login"
        
        print(f"Getting auth token from: {auth_url}")
        print(f"Using API Key: {os.getenv('MONNIFY_API_KEY')}")
        
        # Monnify uses Basic Auth, not JSON
        auth_response = requests.post(
            auth_url, 
            auth=(os.getenv("MONNIFY_API_KEY"), os.getenv("MONNIFY_SECRET_KEY"))
        )
        print(f"Auth response status: {auth_response.status_code}")
        print(f"Auth response: {auth_response.text}")
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            if token_data.get("requestSuccessful"):
                access_token = token_data["responseBody"]["accessToken"]
                print("[SUCCESS] Successfully got Monnify auth token")                # Create virtual account
                create_url = f"{os.getenv('MONNIFY_BASE_URL')}/api/v2/bank-transfer/reserved-accounts"
                
                # Generate unique reference using timestamp
                import time
                timestamp = int(time.time())
                  payload = {
                    "accountReference": f"Test_User_{timestamp}",
                    "accountName": "Test User",
                    "currencyCode": "NGN",
                    "contractCode": os.getenv("MONNIFY_CONTRACT_CODE"),
                    "customerEmail": f"test.user.{timestamp}@example.com",
                    "customerName": "Test User",
                    "getAllAvailableBanks": True  # Changed to True
                }
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                  print(f"Creating virtual account with payload: {payload}")
                create_response = requests.post(create_url, json=payload, headers=headers)
                print(f"Create response status: {create_response.status_code}")
                print(f"Create response: {create_response.text}")
                
                if create_response.status_code == 200:  # Monnify returns 200 for success
                    response_data = create_response.json()
                    if response_data.get("requestSuccessful"):
                        print("[SUCCESS] Monnify direct API test successful!")
                        # Show created accounts
                        accounts = response_data.get("responseBody", {}).get("accounts", [])
                        for account in accounts:
                            print(f"Created account: {account['bankName']} - {account['accountNumber']}")
                        return True
                    else:
                        print("[ERROR] Monnify API returned unsuccessful response")
                        return False
                else:
                    print("[ERROR] Monnify direct API test failed")
                    return False
            else:
                print(f"[ERROR] Auth failed: {token_data}")
                return False
        else:
            print(f"[ERROR] Auth request failed: {auth_response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Direct Monnify test error: {e}")
        return False

if __name__ == "__main__":
    print(">>> Starting Virtual Account Creation Tests...")
    
    success1 = test_virtual_account_creation()
    success2 = test_monnify_direct()
    
    if success1 or success2:
        print("\n[SUCCESS] At least one test passed!")
    else:
        print("\n[ERROR] All tests failed!")
