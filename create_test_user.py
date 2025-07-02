#!/usr/bin/env python3
"""
Create Test User for Money System Testing
"""

import asyncio
from dotenv import load_dotenv
from utils.user_onboarding import onboarding_service

load_dotenv()

async def create_test_user():
    """Create a test user for money system testing"""
    
    test_user_data = {
        'telegram_id': 'test_money_user_123',
        'full_name': 'Test Money User',
        'phone': '+2348012345678',
        'email': 'testuser@sofi.ai',
        'address': 'Lagos, Nigeria',
        'pin': '1234',
        'confirm_pin': '1234'
    }
    
    print("📝 Creating test user for money system testing...")
    result = await onboarding_service.create_new_user(test_user_data)
    
    if result.get('success'):
        print("✅ Test user created successfully!")
        print(f"   User ID: {result.get('user_id')}")
        print(f"   Full Name: {result.get('full_name')}")
        print(f"   Account Number: {result.get('account_details', {}).get('account_number')}")
        print(f"   Bank: {result.get('account_details', {}).get('bank_name')}")
    else:
        print(f"❌ Failed to create test user: {result.get('error')}")
        
        # Check if user already exists
        if 'already registered' in result.get('error', ''):
            print("ℹ️  Test user already exists, that's fine for testing!")

if __name__ == "__main__":
    asyncio.run(create_test_user())
