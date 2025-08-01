#!/usr/bin/env python3
"""
Create Mosese Virtual Account - Final Test
Using correct 9PSB endpoint and payload format
"""

import os
import json
import requests
import uuid
import random
from dotenv import load_dotenv

load_dotenv()

def create_mosese_account():
    """Create virtual account for Mosese Smart Ayobami with correct 9PSB format"""
    print("🏦 Creating Mosese Virtual Account - Final Test")
    print("=" * 60)
    
    # Step 1: Get authentication token
    print("🔐 Step 1: Authentication...")
    
    username = os.getenv("NINEPSB_USERNAME")
    password = os.getenv("NINEPSB_PASSWORD")
    client_id = os.getenv("NINEPSB_CLIENT_ID")
    client_secret = os.getenv("NINEPSB_CLIENT_SECRET")
    auth_url = os.getenv("NINEPSB_AUTH_URL")
    
    auth_payload = {
        "username": username,
        "password": password,
        "clientId": client_id,
        "clientSecret": client_secret
    }
    
    try:
        auth_response = requests.post(auth_url, json=auth_payload, timeout=15)
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            access_token = auth_data.get("accessToken")
            if access_token:
                print(f"✅ Authentication successful: {access_token[:20]}...")
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Step 2: Create virtual account
    print("\n🏦 Step 2: Creating Virtual Account...")
    
    base_url = os.getenv("NINEPSB_BASE_URL")
    api_key = os.getenv("NINEPSB_API_KEY")
    secret_key = os.getenv("NINEPSB_SECRET_KEY")
    
    # Use the correct endpoint
    url = f"{base_url}/api/v1/open_wallet"
    
    # Generate unique data
    user_id = f"mosese_final_{random.randint(1000, 9999)}"
    phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    phone = f"080{phone_suffix}"
    email_suffix = random.randint(100, 999)
    email = f"mosese.final{email_suffix}@gmail.com"
    
    # Use correct 9PSB payload format
    payload = {
        "userId": user_id,
        "firstName": "Mosese",
        "lastName": "Smart Ayobami",
        "otherNames": "N/A",
        "gender": 1,  # 1 for male, 2 for female
        "dateOfBirth": "05/05/1990",  # dd/mm/yyyy format
        "phoneNo": phone,
        "phoneNumber": phone,
        "email": email,
        "bvn": "22190239861",  # Required BVN (test value)
        "channel": "APP",
        "password": "Sofi@1234",
        "transactionTrackingRef": str(uuid.uuid4())
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-key": api_key,
        "x-secret-key": secret_key,
        "Content-Type": "application/json"
    }
    
    print(f"📡 Request Details:")
    print(f"   URL: {url}")
    print(f"   User ID: {user_id}")
    print(f"   Phone: {phone}")
    print(f"   Email: {email}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"\n📊 Response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.text:
            try:
                response_data = response.json()
                print(f"   Response JSON: {json.dumps(response_data, indent=2)}")
                
                status = response_data.get("status")
                message = response_data.get("message", "No message")
                
                if status == "SUCCESS":
                    print("\n🎉 SUCCESS! Virtual Account Created!")
                    
                    # Extract account details
                    data = response_data.get("data", response_data)
                    
                    account_number = (data.get("accountNumber") or 
                                    data.get("account_number") or 
                                    data.get("virtualAccountNumber"))
                    
                    bank_name = (data.get("bankName") or 
                               data.get("bank_name") or 
                               data.get("bankCode"))
                    
                    account_name = (data.get("accountName") or 
                                  data.get("account_name") or 
                                  data.get("fullName"))
                    
                    print(f"📋 Account Details:")
                    if account_number:
                        print(f"   🏦 Account Number: {account_number}")
                    if bank_name:
                        print(f"   🏛️ Bank Name: {bank_name}")
                    if account_name:
                        print(f"   👤 Account Name: {account_name}")
                    
                    # Print all data for debugging
                    print(f"\n📄 Full Data: {json.dumps(data, indent=2)}")
                    
                    return True
                    
                elif status == "FAILED":
                    print(f"\n❌ Account Creation Failed: {message}")
                    
                    # Provide specific guidance based on error
                    if "phone" in message.lower():
                        print("💡 Suggestion: Phone number format issue")
                        print("   Try different Nigerian phone format (070, 080, 081, 090, 091)")
                    elif "email" in message.lower():
                        print("💡 Suggestion: Email format issue")
                        print("   Try different email address")
                    elif "bvn" in message.lower():
                        print("💡 Suggestion: BVN issue")
                        print("   Contact 9PSB support for valid test BVN")
                    elif "exist" in message.lower():
                        print("💡 Suggestion: User already exists")
                        print("   Using unique user ID, this shouldn't happen")
                    else:
                        print("💡 Suggestion: Check 9PSB API documentation for required fields")
                    
                    return False
                else:
                    print(f"\n⚠️ Unexpected Response Status: {status}")
                    print(f"Message: {message}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"   Raw Response: {response.text}")
                return False
        else:
            print("   Empty response")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Mosese Smart Ayobami - 9PSB Virtual Account Creation")
    print("🎯 Using Correct Endpoint and Payload Format")
    print("=" * 70)
    
    success = create_mosese_account()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ MISSION ACCOMPLISHED!")
        print("🎉 Mosese's virtual account has been created successfully")
        print("🔄 Next: Integrate with Sofi AI main application")
    else:
        print("❌ MISSION INCOMPLETE")
        print("🔧 Check the error messages above for troubleshooting")
        print("📞 May need to contact 9PSB support for API clarification")

if __name__ == "__main__":
    main()
