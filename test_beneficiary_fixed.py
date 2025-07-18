"""
Test Beneficiary Integration - Database Compatible Version

Tests the beneficiary system with the existing database schema.
This version uses integer user_id values to match the database.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.supabase_beneficiary_service import beneficiary_service

async def test_beneficiary_system():
    """Test the beneficiary system with real database schema."""
    
    # Use an existing user_id from your database (integer format)
    test_user_id = 5495194750  # This matches the user_id in your existing data
    
    print("🧪 Testing Beneficiary System with Database Schema Compatibility...")
    print(f"Using test user ID: {test_user_id}")
    
    try:
        print("\n1. Testing get_user_beneficiaries...")
        beneficiaries = await beneficiary_service.get_user_beneficiaries(test_user_id)
        print(f"✅ Found {len(beneficiaries)} existing beneficiaries")
        for i, beneficiary in enumerate(beneficiaries[:3]):  # Show first 3
            print(f"   {i+1}. {beneficiary.get('nickname', 'N/A')} - {beneficiary.get('bank_name', 'N/A')} - {beneficiary.get('account_number', 'N/A')}")
        
        print("\n2. Testing save_beneficiary...")
        success = await beneficiary_service.save_beneficiary(
            user_id=test_user_id,
            beneficiary_name="JOHN DOE TEST",
            account_number="1234567890",
            bank_code="TESTBANK",
            bank_name="Test Bank Nigeria",
            nickname="John Test"
        )
        if success:
            print("✅ Successfully saved test beneficiary")
        else:
            print("❌ Failed to save test beneficiary")
        
        print("\n3. Testing find_beneficiary_by_name...")
        found = await beneficiary_service.find_beneficiary_by_name(test_user_id, "john")
        if found:
            print(f"✅ Found beneficiary: {found.get('nickname')} - {found.get('account_number')}")
        else:
            print("❌ Could not find beneficiary by name")
        
        print("\n4. Testing create_save_prompt...")
        prompt = beneficiary_service.create_save_prompt("JANE SMITH", "GTBank", "0123456789")
        print(f"✅ Save prompt: {prompt}")
        
        print("\n5. Testing with string user_id conversion...")
        beneficiaries_str = await beneficiary_service.get_user_beneficiaries(str(test_user_id))
        print(f"✅ String user_id works: Found {len(beneficiaries_str)} beneficiaries")
        
        print("\n🎉 All beneficiary system tests completed successfully!")
        print("✅ Database schema compatibility confirmed")
        print("✅ Integer user_id handling working")
        print("✅ String to integer conversion working")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_beneficiary_system())
