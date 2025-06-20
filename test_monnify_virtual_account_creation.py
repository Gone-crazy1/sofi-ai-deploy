#!/usr/bin/env python3
"""
Test Monnify Virtual Account Creation
Tests the full account creation flow with fake data
"""

import sys
import os
import requests
import time
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monnify.monnify_api import MonnifyAPI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def test_monnify_virtual_account_creation():
    """Test creating virtual accounts with Monnify API"""
    print("🧪 Testing Monnify Virtual Account Creation")
    print("=" * 50)
    
    try:
        # Initialize Monnify API
        monnify = MonnifyAPI()
        print("✅ Monnify API initialized")
        
        # Test data - fake user for testing
        test_customers = [
            {
                "user_id": f"test_user_{int(time.time())}",
                "email": f"testuser{int(time.time())}@sofibank.com", 
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+2348123456789"
            },
            {
                "user_id": f"test_user_{int(time.time())}_2",
                "email": f"testuser{int(time.time())}_jane@sofibank.com",
                "first_name": "Jane", 
                "last_name": "Smith",
                "phone": "+2348987654321"
            }
        ]
        
        successful_accounts = []
        
        for i, customer in enumerate(test_customers, 1):
            print(f"\n🏦 Creating virtual account {i} for {customer['first_name']} {customer['last_name']}")
            print(f"📧 Email: {customer['email']}")
            print(f"📱 Phone: {customer['phone']}")
            
            # Create virtual account
            result = monnify.create_virtual_account(customer)
            
            if result.get("success"):
                print("✅ Virtual account created successfully!")
                print(f"📝 Account Reference: {result['account_reference']}")
                print(f"🏛️ Customer Code: {result.get('customer_code', 'N/A')}")
                print(f"📊 Status: {result.get('status', 'N/A')}")
                
                # Display account details
                if result.get("accounts"):
                    print("\n🏦 Account Details:")
                    for j, account in enumerate(result["accounts"], 1):
                        print(f"  Account {j}:")
                        print(f"    Bank: {account['bank_name']}")
                        print(f"    Account Number: {account['account_number']}")
                        print(f"    Account Name: {account['account_name']}")
                        print(f"    Bank Code: {account['bank_code']}")
                    
                    successful_accounts.append({
                        "customer": customer,
                        "accounts": result["accounts"],
                        "reference": result["account_reference"]
                    })
                else:
                    print("❌ No account details returned")
            else:
                print(f"❌ Failed to create virtual account: {result.get('error')}")
                
            print("-" * 40)
            time.sleep(2)  # Rate limiting
        
        # Test saving to Supabase
        if successful_accounts:
            print(f"\n💾 Testing Supabase Integration...")
            test_supabase_integration(successful_accounts)
        
        print(f"\n🎉 Test Summary:")
        print(f"✅ Successful accounts: {len(successful_accounts)}")
        print(f"❌ Failed accounts: {len(test_customers) - len(successful_accounts)}")
        
        return successful_accounts
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return []

def test_supabase_integration(accounts_data):
    """Test saving account data to Supabase"""
    try:
        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found")
            return
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
        
        for account_data in accounts_data:
            customer = account_data["customer"]
            accounts = account_data["accounts"]
            
            # Save user data
            user_data = {
                "chat_id": customer["user_id"],
                "first_name": customer["first_name"],
                "last_name": customer["last_name"], 
                "email": customer["email"],
                "phone": customer.get("phone"),
                "is_verified": True,
                "onboarding_complete": True,
                "created_at": datetime.now().isoformat()
            }
            
            try:
                result = supabase.table("users").upsert(user_data).execute()
                print(f"✅ User {customer['first_name']} saved to Supabase")
            except Exception as e:
                print(f"❌ Failed to save user {customer['first_name']}: {e}")
                continue
            
            # Save virtual account data
            for account in accounts:
                account_data = {
                    "user_id": customer["user_id"],
                    "bank_name": account["bank_name"],
                    "account_number": account["account_number"],
                    "account_name": account["account_name"],
                    "bank_code": account["bank_code"],
                    "provider": account["provider"],
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                
                try:
                    result = supabase.table("virtual_accounts").upsert(account_data).execute()
                    print(f"✅ Virtual account {account['account_number']} saved to Supabase")
                except Exception as e:
                    print(f"❌ Failed to save virtual account {account['account_number']}: {e}")
        
    except Exception as e:
        print(f"❌ Supabase integration test failed: {e}")

def test_web_form_api():
    """Test the web form API endpoint"""
    print("\n🌐 Testing Web Form API Endpoint")
    print("=" * 50)
    
    try:
        # Test the create virtual account API endpoint
        base_url = "http://localhost:5000"  # Change to your deployed URL if testing production
        
        test_form_data = {
            "first_name": "Test",
            "last_name": "FormUser",
            "email": f"formtest{int(time.time())}@sofibank.com",
            "phone": "+2348100000001",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "state": "Lagos",
            "city": "Lagos",
            "address": "Test Address 123"
        }
        
        print(f"📤 Sending POST request to {base_url}/api/create_virtual_account")
        print(f"📋 Form data: {test_form_data}")
        
        response = requests.post(
            f"{base_url}/api/create_virtual_account",
            json=test_form_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Form submission successful!")
            print(f"📝 Response: {result}")
        else:
            print(f"❌ Form submission failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure your Flask app is running!")
    except Exception as e:
        print(f"❌ Web form test failed: {e}")

def run_full_test_suite():
    """Run complete test suite"""
    print("🚀 SOFI AI MONNIFY TEST SUITE")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Monnify API Virtual Account Creation
    successful_accounts = test_monnify_virtual_account_creation()
    
    # Test 2: Web Form API
    test_web_form_api()
    
    print("\n" + "=" * 60)
    print("🏁 TEST SUITE COMPLETED")
    print(f"🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful_accounts:
        print("\n🎯 READY FOR CHROME TESTING!")
        print("You can now test the onboarding form in Chrome.")
        print("The Monnify integration is working correctly.")
    else:
        print("\n⚠️  FIX REQUIRED!")
        print("Virtual account creation failed. Check your Monnify credentials.")

if __name__ == "__main__":
    run_full_test_suite()
