"""
PayStack Dedicated Account Test - Direct API call
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_dedicated_account_api():
    """Test PayStack dedicated account API directly"""
    
    secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    
    if not secret_key:
        print("❌ No PayStack secret key found")
        return
    
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Testing PayStack Dedicated Account API")
    print("=" * 50)
    print(f"Secret Key: {secret_key[:20]}...")
    print()
    
    # Step 1: Test customer creation first
    print("1️⃣ Testing customer creation...")
    customer_data = {
        "email": "test.dedicated@sofitest.com",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        # Create customer
        response = requests.post(
            "https://api.paystack.co/customer",
            headers=headers,
            json=customer_data,
            timeout=30
        )
        
        print(f"Customer creation - Status: {response.status_code}")
        
        if response.status_code == 200:
            customer_response = response.json()
            customer_code = customer_response['data']['customer_code']
            print(f"✅ Customer created: {customer_code}")
            
            # Step 2: Test dedicated account creation
            print("\\n2️⃣ Testing dedicated account creation...")
            account_data = {
                "customer": customer_code,
                "preferred_bank": "wema-bank"
            }
            
            response = requests.post(
                "https://api.paystack.co/dedicated_account",
                headers=headers,
                json=account_data,
                timeout=30
            )
            
            print(f"Dedicated account - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Dedicated account creation successful!")
                account_info = response.json()
                print(f"Account Number: {account_info.get('data', {}).get('account_number')}")
                print(f"Bank: {account_info.get('data', {}).get('bank', {}).get('name')}")
            else:
                print("❌ Dedicated account creation failed")
                
        else:
            print(f"❌ Customer creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dedicated_account_api()
