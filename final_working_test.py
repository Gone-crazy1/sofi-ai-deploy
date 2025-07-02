#!/usr/bin/env python3
"""
FINAL TEST - Direct 2-Step Process That We KNOW Works
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def final_working_test():
    """Use the 2-step process directly - we know this works from earlier"""
    try:
        print("🚀 FINAL TEST - Using Known Working 2-Step Process")
        
        secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        base_url = "https://api.paystack.co"
        
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        # Test user for onboarding
        test_user = {
            'email': 'final.working.test@example.com',
            'first_name': 'Final',
            'last_name': 'Working',
            'phone': '+2348012345685'
        }
        
        print(f"Creating complete account for: {test_user['first_name']} {test_user['last_name']}")
        
        # Step 1: Create customer
        print("\n🔄 Step 1: Creating customer...")
        customer_url = f"{base_url}/customer"
        customer_payload = {
            "email": test_user['email'],
            "first_name": test_user['first_name'],
            "last_name": test_user['last_name'],
            "phone": test_user['phone']
        }
        
        customer_response = requests.post(customer_url, json=customer_payload, headers=headers)
        customer_result = customer_response.json()
        
        if customer_result.get("status"):
            customer_data = customer_result["data"]
            customer_code = customer_data["customer_code"]
            customer_id = customer_data["id"]
            
            print(f"✅ Customer created: {customer_code}")
            
            # Step 2: Create DVA for customer
            print("\n🔄 Step 2: Creating dedicated virtual account...")
            dva_url = f"{base_url}/dedicated_account"
            dva_payload = {
                "customer": customer_code,
                "preferred_bank": "wema-bank"
            }
            
            dva_response = requests.post(dva_url, json=dva_payload, headers=headers)
            dva_result = dva_response.json()
            
            if dva_result.get("status"):
                dva_data = dva_result["data"]
                
                # Compile final account info
                account_info = {
                    'customer_id': customer_id,
                    'customer_code': customer_code,
                    'account_number': dva_data.get('account_number'),
                    'account_name': dva_data.get('account_name'),
                    'bank_name': dva_data.get('bank', {}).get('name', 'Wema Bank'),
                    'bank_code': '035',  # Wema Bank
                    'full_name': f"{test_user['first_name']} {test_user['last_name']}"
                }
                
                print("\n🎉 COMPLETE ACCOUNT CREATION SUCCESS!")
                print("=" * 60)
                print(f"👤 Full Name: {account_info['full_name']}")
                print(f"📧 Email: {test_user['email']}")
                print(f"📱 Phone: {test_user['phone']}")
                print(f"🆔 Customer ID: {account_info['customer_id']}")
                print(f"🔢 Account Number: {account_info['account_number']}")
                print(f"👤 Account Name: {account_info['account_name']}")
                print(f"🏦 Bank: {account_info['bank_name']}")
                print("=" * 60)
                
                print("\n💡 This is EXACTLY what Sofi will send to users after onboarding!")
                print(f"📧 Welcome email/message will include:")
                print(f"   - Account: {account_info['account_number']}")
                print(f"   - Bank: {account_info['bank_name']}")
                print(f"   - Name: {account_info['account_name']}")
                
                return {
                    'success': True,
                    'account_info': account_info,
                    'user_data': test_user
                }
            else:
                print(f"❌ DVA creation failed: {dva_result}")
                return None
        else:
            print(f"❌ Customer creation failed: {customer_result}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    result = final_working_test()
    
    if result and result.get('success'):
        print("\n✅ SUCCESS! The onboarding process works perfectly!")
        print("🎯 Sofi can now create accounts and send details to users!")
        
        account_info = result['account_info']
        
        # Show the exact message format Sofi will send
        welcome_message = f"""
🎉 Welcome to Sofi AI, {account_info['full_name']}!

Your virtual account is ready! 🏦

📋 Your Account Details:
👤 Account Name: {account_info['account_name']}
🏦 Bank Name: {account_info['bank_name']}
🔢 Account Number: {account_info['account_number']}
💳 Balance: ₦0.00

📱 How to Fund Your Account:
• Transfer money to your account number above
• Use any Nigerian bank or mobile app
• Funds are credited instantly!

Welcome to the future of digital banking! 🚀
        """
        
        print("\n📱 EXACT MESSAGE SOFI WILL SEND:")
        print("=" * 50)
        print(welcome_message)
        print("=" * 50)
    else:
        print("\n❌ Test failed!")
