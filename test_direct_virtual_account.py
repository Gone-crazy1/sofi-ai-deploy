#!/usr/bin/env python3
"""
Direct test of the create_virtual_account function to identify issues
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from main import create_virtual_account
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def test_direct_virtual_account_creation():
    """Test the create_virtual_account function directly"""
    
    print("🧪 Testing create_virtual_account function directly...")
    
    # Generate unique test data using timestamp
    import time
    timestamp = int(time.time())
    
    # Test data with unique identifiers
    test_data = {
        "firstName": f"TestUser{timestamp}",
        "lastName": "Direct",
        "bvn": f"1234567890{timestamp % 10}"  # Make BVN unique but valid format
    }
    
    print(f"📝 Test data: {test_data}")
    
    try:
        # Call the function directly
        result = create_virtual_account(
            first_name=test_data["firstName"],
            last_name=test_data["lastName"],
            bvn=test_data["bvn"]
        )
        
        print(f"📊 Result: {json.dumps(result, indent=2)}")
        
        if result and result.get("accountNumber"):
            print("✅ SUCCESS: Virtual account created successfully!")
            print(f"📱 Account Number: {result.get('accountNumber')}")
            print(f"🏦 Bank Name: {result.get('bankName')}")
            print(f"👤 Account Name: {result.get('accountName')}")
            print(f"🔗 Reference: {result.get('accountReference')}")
            return True
        else:
            print("❌ FAILED: No account data returned")
            return False
            
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    
    print("\n🔧 Checking Environment Variables...")
    
    required_vars = [
        "MONNIFY_BASE_URL",
        "MONNIFY_API_KEY", 
        "MONNIFY_SECRET_KEY",
        "MONNIFY_CONTRACT_CODE",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n💥 Missing environment variables: {missing_vars}")
        return False
    else:
        print("\n🎯 All environment variables are set!")
        return True

def test_monnify_connection():
    """Test direct connection to Monnify API"""
    
    print("\n🌐 Testing Monnify API Connection...")
    
    try:
        import requests
        
        monnify_base_url = os.getenv("MONNIFY_BASE_URL")
        monnify_api_key = os.getenv("MONNIFY_API_KEY")
        monnify_secret_key = os.getenv("MONNIFY_SECRET_KEY")
        
        # Test authentication
        auth_url = f"{monnify_base_url}/api/v1/auth/login"
        print(f"🔗 Auth URL: {auth_url}")
        
        auth_response = requests.post(
            auth_url, 
            auth=(monnify_api_key, monnify_secret_key),
            timeout=10
        )
        
        print(f"📈 Auth Status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            if auth_data.get("requestSuccessful"):
                print("✅ Monnify authentication successful!")
                return True
            else:
                print(f"❌ Monnify auth failed: {auth_data}")
                return False
        else:
            print(f"❌ Monnify auth HTTP error: {auth_response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Monnify connection error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Direct Virtual Account Tests...")
    
    # Run all tests
    env_ok = test_environment_variables()
    monnify_ok = test_monnify_connection()
    
    if env_ok and monnify_ok:
        create_ok = test_direct_virtual_account_creation()
        
        if create_ok:
            print("\n🎉 All tests PASSED! Virtual account creation is working!")
        else:
            print("\n💥 Virtual account creation FAILED!")
    else:
        print("\n⚠️  Skipping virtual account test due to environment/connection issues")
    
    print("\n📋 Test Summary:")
    print(f"   Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"   Monnify Connection: {'✅' if monnify_ok else '❌'}")
    
    if env_ok and monnify_ok:
        print(f"   Virtual Account Creation: {'✅' if create_ok else '❌'}")
