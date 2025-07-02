#!/usr/bin/env python3
"""
Test Virtual Accounts Table Format
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_virtual_accounts_format():
    """Test what format virtual_accounts table expects"""
    
    print("🔍 Testing Virtual Accounts Table Format")
    print("=" * 45)
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Test different approaches
    test_cases = [
        {
            "name": "String user_id",
            "data": {
                'user_id': 'test_string_user',
                'telegram_chat_id': 'test_string_user', 
                'account_number': '1234567890',
                'bank_name': 'Test Bank',
                'bank_code': '123'
            }
        },
        {
            "name": "UUID user_id",
            "data": {
                'user_id': str(uuid.uuid4()),
                'telegram_chat_id': 'test_uuid_user', 
                'account_number': '1234567891',
                'bank_name': 'Test Bank',
                'bank_code': '123'
            }
        },
        {
            "name": "With ID field",
            "data": {
                'id': str(uuid.uuid4()),
                'user_id': 'test_with_id_user',
                'telegram_chat_id': 'test_with_id_user', 
                'account_number': '1234567892',
                'bank_name': 'Test Bank',
                'bank_code': '123'
            }
        },
        {
            "name": "Minimal fields only",
            "data": {
                'telegram_chat_id': 'test_minimal_user', 
                'account_number': '1234567893',
                'bank_name': 'Test Bank',
                'bank_code': '123'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        try:
            result = supabase.table('virtual_accounts').insert(test_case['data']).execute()
            if result.data:
                print(f"✅ SUCCESS: {test_case['name']} works!")
                print(f"   Inserted ID: {result.data[0].get('id', 'No ID')}")
                
                # Clean up
                if 'id' in result.data[0]:
                    supabase.table('virtual_accounts').delete().eq('id', result.data[0]['id']).execute()
                else:
                    supabase.table('virtual_accounts').delete().eq('account_number', test_case['data']['account_number']).execute()
                    
            else:
                print(f"❌ FAILED: {test_case['name']} - No data returned")
        except Exception as e:
            print(f"❌ FAILED: {test_case['name']} - {e}")
    
    print(f"\n📋 Results Summary:")
    print("The working format will be used in the onboarding code.")

if __name__ == "__main__":
    test_virtual_accounts_format()
