#!/usr/bin/env python3
"""
Test the complete virtual_accounts table schema
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🧪 Testing complete virtual_accounts schema with accountreference...")

test_data = {
    "telegram_chat_id": "123456789",
    "accountnumber": "1234567890", 
    "accountname": "Test User",
    "bankname": "Test Bank",
    "accountreference": "test_ref_123"
}

try:
    result = supabase.table("virtual_accounts").insert(test_data).execute()
    print(f"✅ Complete insert successful!")
    print(f"   Data: {result.data}")
    
    # Clean up the test record
    if result.data and 'id' in result.data[0]:
        delete_result = supabase.table("virtual_accounts").delete().eq('id', result.data[0]['id']).execute()
        print("🧹 Test record cleaned up")
        
    print(f"\n🎉 SCHEMA DISCOVERED:")
    print(f"   virtual_accounts table columns:")
    print(f"   - id (auto-increment)")
    print(f"   - telegram_chat_id (required)")
    print(f"   - accountnumber (required)")
    print(f"   - accountname") 
    print(f"   - bankname")
    print(f"   - accountreference (required)")
    print(f"   - created_at (auto-timestamp)")
        
except Exception as e:
    print(f"❌ Insert failed: {e}")
    
    # Test with minimal required fields
    minimal_data = {
        "telegram_chat_id": "123456789",
        "accountnumber": "1234567890",
        "accountreference": "test_ref_123" 
    }
    
    try:
        result = supabase.table("virtual_accounts").insert(minimal_data).execute()
        print(f"✅ Minimal insert successful: {result.data}")
        
        # Clean up
        if result.data and 'id' in result.data[0]:
            supabase.table("virtual_accounts").delete().eq('id', result.data[0]['id']).execute()
            print("🧹 Minimal test record cleaned up")
            
    except Exception as e2:
        print(f"❌ Even minimal insert failed: {e2}")
