#!/usr/bin/env python3
"""
Create Mosese Virtual Account with Valid Nigerian Phone
"""

import os
import uuid
import random
from dotenv import load_dotenv

load_dotenv()

def create_mosese_account_fixed():
    """Create virtual account with proper Nigerian phone format"""
    print("🏦 Creating Mosese Virtual Account (Fixed Phone Format)...")
    
    try:
        from utils.ninepsb_api import NINEPSBApi
        
        # Generate unique user ID
        unique_id = f"mosese_{random.randint(1000, 9999)}"
        
        api_key = os.getenv("NINEPSB_API_KEY")
        secret_key = os.getenv("NINEPSB_SECRET_KEY")
        base_url = os.getenv("NINEPSB_BASE_URL")
        
        print(f"👤 User ID: {unique_id}")
        
        psb = NINEPSBApi(api_key, secret_key, base_url)
        
        # Valid Nigerian phone numbers start with: 080, 081, 070, 090, 091
        valid_prefixes = ['080', '081', '070', '090', '091']
        prefix = random.choice(valid_prefixes)
        phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        valid_phone = f"{prefix}{phone_suffix}"
        
        # Generate unique email
        email_suffix = random.randint(100, 999)
        
        user_data = {
            "first_name": "Mosese",
            "last_name": "Smart Ayobami",
            "email": f"mosese.smart{email_suffix}@gmail.com",
            "phone": valid_phone
        }
        
        print(f"📝 User Data:")
        print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Phone: {user_data['phone']}")
        print(f"   User ID: {unique_id}")
        
        response = psb.create_virtual_account(unique_id, user_data)
        
        print("\n🎯 9PSB API Response:")
        print("=" * 50)
        
        if isinstance(response, dict):
            status = response.get('status', 'UNKNOWN')
            message = response.get('message', 'No message')
            
            print(f"Status: {status}")
            print(f"Message: {message}")
            
            if status == 'SUCCESS':
                print("✅ Virtual Account Created Successfully!")
                
                # Look for account details in different possible locations
                data = response.get('data', response.get('response', response))
                
                if isinstance(data, dict):
                    account_number = data.get('account_number') or data.get('accountNumber')
                    bank_name = data.get('bank_name') or data.get('bankName')
                    account_name = data.get('account_name') or data.get('accountName')
                    
                    if account_number:
                        print(f"🏦 Account Number: {account_number}")
                    if bank_name:
                        print(f"🏛️ Bank Name: {bank_name}")
                    if account_name:
                        print(f"👤 Account Name: {account_name}")
                else:
                    print("📄 Full Response:", response)
                    
            elif status == 'FAILED':
                print(f"❌ Account Creation Failed: {message}")
                
                # Common issues and solutions
                if 'phone' in message.lower():
                    print("💡 Phone number issue - trying different format...")
                elif 'email' in message.lower():
                    print("💡 Email issue - trying different email...")
                elif 'exist' in message.lower():
                    print("💡 User already exists - trying different ID...")
                    
            else:
                print(f"⚠️ Unexpected status: {status}")
        else:
            print(f"📄 Raw Response: {response}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error creating virtual account: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_multiple_attempts():
    """Try creating account with different variations"""
    print("🔄 Testing Multiple Account Creation Attempts...")
    
    attempts = [
        {"phone_prefix": "080", "email_domain": "gmail.com"},
        {"phone_prefix": "081", "email_domain": "yahoo.com"},
        {"phone_prefix": "070", "email_domain": "outlook.com"}
    ]
    
    for i, attempt in enumerate(attempts, 1):
        print(f"\n--- Attempt {i} ---")
        
        try:
            from utils.ninepsb_api import NINEPSBApi
            
            api_key = os.getenv("NINEPSB_API_KEY")
            secret_key = os.getenv("NINEPSB_SECRET_KEY")
            base_url = os.getenv("NINEPSB_BASE_URL")
            
            psb = NINEPSBApi(api_key, secret_key, base_url)
            
            # Generate data for this attempt
            user_id = f"mosese_attempt_{i}_{random.randint(100, 999)}"
            phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            phone = f"{attempt['phone_prefix']}{phone_suffix}"
            email = f"mosese.smart.{i}@{attempt['email_domain']}"
            
            user_data = {
                "first_name": "Mosese",
                "last_name": "Smart Ayobami",
                "email": email,
                "phone": phone
            }
            
            print(f"Testing: {phone} | {email}")
            
            response = psb.create_virtual_account(user_id, user_data)
            
            if isinstance(response, dict) and response.get('status') == 'SUCCESS':
                print(f"✅ SUCCESS on attempt {i}!")
                print(f"Account created with {phone} and {email}")
                return response
            else:
                status = response.get('status') if isinstance(response, dict) else 'UNKNOWN'
                message = response.get('message') if isinstance(response, dict) else str(response)
                print(f"❌ Failed: {status} - {message}")
                
        except Exception as e:
            print(f"❌ Error in attempt {i}: {e}")
    
    print("\n❌ All attempts failed")
    return None

if __name__ == "__main__":
    print("🚀 9PSB Virtual Account Creation - Mosese Smart Ayobami")
    print("📱 Using Valid Nigerian Phone Format")
    print("=" * 60)
    
    # Try single attempt first
    result = create_mosese_account_fixed()
    
    # If it fails, try multiple attempts
    if not result or (isinstance(result, dict) and result.get('status') != 'SUCCESS'):
        print("\n" + "=" * 60)
        print("🔄 Single attempt failed, trying multiple variations...")
        test_multiple_attempts()
    
    print("\n✅ Test completed!")
