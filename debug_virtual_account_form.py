#!/usr/bin/env python3
"""
Debug Virtual Account Creation
Run this to test exactly what's failing in the form submission
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.user_onboarding import SofiUserOnboarding

def debug_virtual_account_creation():
    """Debug the virtual account creation with form data"""
    print("🔍 DEBUG: Virtual Account Creation")
    print("=" * 50)    # Simulate the exact data that would come from the Chrome form
    import time
    unique_id = int(time.time())
    
    test_form_data = {
        "first_name": "John",
        "last_name": "Doe", 
        "email": f"testuser{unique_id}@example.com",  # Unique email each time
        "phone": "+2348123456789",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "state": "Lagos",
        "city": "Lagos",
        "address": "Test Address 123"
    }
    
    # Apply the same field mapping as Flask endpoint
    if 'first_name' in test_form_data and 'last_name' in test_form_data:
        test_form_data['full_name'] = f"{test_form_data['first_name']} {test_form_data['last_name']}"
    
    # Generate temporary telegram_id for web users
    if not test_form_data.get('telegram_id'):
        import uuid
        test_form_data['telegram_id'] = f"web_user_{uuid.uuid4().hex[:8]}"
    
    print(f"📋 Testing with form data:")
    print(json.dumps(test_form_data, indent=2))
    print()
    
    try:
        # Initialize onboarding service (same as Flask endpoint)
        print("🔄 Initializing SofiUserOnboarding...")
        onboarding = SofiUserOnboarding()
        print("✅ SofiUserOnboarding initialized")
        
        # Call the same method as Flask endpoint
        print("🔄 Calling create_virtual_account...")
        result = onboarding.create_virtual_account(test_form_data)
        
        print("📤 Result received:")
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            print("✅ SUCCESS: Virtual account created!")
            if result.get('accounts'):
                print("\n🏦 Account Details:")
                for i, account in enumerate(result['accounts'], 1):
                    print(f"  Account {i}:")
                    print(f"    Bank: {account.get('bank_name', 'N/A')}")
                    print(f"    Account Number: {account.get('account_number', 'N/A')}")
                    print(f"    Account Name: {account.get('account_name', 'N/A')}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        print("📜 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_virtual_account_creation()
