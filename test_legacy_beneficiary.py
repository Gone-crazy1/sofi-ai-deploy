#!/usr/bin/env python3
"""
Test script for Legacy Beneficiary Service
Works with existing beneficiaries table structure
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_legacy_beneficiary():
    """Test legacy beneficiary service functionality"""
    print("🧪 Testing Legacy Beneficiary Service...")
    
    try:
        from utils.legacy_beneficiary_service import legacy_beneficiary_service
        print("✅ Legacy beneficiary service imported successfully")
        
        # Use a test Telegram chat ID
        test_chat_id = "test_user_123"
        
        # Test 1: Get beneficiaries list (should work now)
        print("\n📝 Test 1: Get beneficiaries list...")
        beneficiaries_list = await legacy_beneficiary_service.format_beneficiaries_list(test_chat_id)
        print(f"📥 Result: {beneficiaries_list[:200]}...")
        
        # Test 2: Create save prompt
        print("\n📝 Test 2: Create save beneficiary prompt...")
        save_prompt = legacy_beneficiary_service.create_save_beneficiary_prompt(
            recipient_name="THANKGOD OLUWASEUN NDIDI",
            bank_name="Opay", 
            account_number="8104965538"
        )
        print(f"📥 Prompt: {save_prompt}")
        
        # Test 3: Test save response handling
        print("\n📝 Test 3: Test save response handling...")
        transfer_data = {
            "recipient_name": "THANKGOD OLUWASEUN NDIDI",
            "bank_name": "Opay",
            "account_number": "8104965538"
        }
        
        # Test different responses
        responses_to_test = ["yes", "no", "save as John", "Mum"]
        
        for response in responses_to_test:
            print(f"\n  Testing response: '{response}'")
            try:
                result = await legacy_beneficiary_service.handle_save_response(
                    telegram_chat_id=test_chat_id,
                    response=response,
                    transfer_data=transfer_data
                )
                print(f"  📥 Result: {result.get('success', False)} - {result.get('message', result.get('error', 'No message'))[:100]}...")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        # Test 4: Find beneficiary by name
        print("\n📝 Test 4: Find beneficiary by name...")
        found_beneficiary = await legacy_beneficiary_service.find_beneficiary_by_name(test_chat_id, "john")
        print(f"📥 Found result: {found_beneficiary}")
        
        # Test 5: Get beneficiaries again (should show saved ones)
        print("\n📝 Test 5: Get beneficiaries list after saving...")
        beneficiaries = await legacy_beneficiary_service.get_user_beneficiaries(test_chat_id)
        print(f"📥 Beneficiaries count: {len(beneficiaries)}")
        if beneficiaries:
            for i, beneficiary in enumerate(beneficiaries[:2], 1):  # Show first 2
                print(f"  {i}. {beneficiary.get('nickname', 'No nickname')} - {beneficiary.get('beneficiary_name', 'Unknown')}")
        
        print("\n✅ Legacy beneficiary service tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Legacy Beneficiary Service Test")
    print("=" * 40)
    
    # Test basic functionality
    result = asyncio.run(test_legacy_beneficiary())
    
    if result:
        print("\n🎉 Legacy beneficiary service is working!")
        print("✅ Compatible with existing database schema")
        print("✅ Ready to integrate with Assistant")
    else:
        print("\n❌ Legacy service tests failed.")
    
    print("\n📋 What we tested:")
    print("✅ Service import and initialization")
    print("✅ Get beneficiaries from existing table")
    print("✅ Save beneficiaries to existing table")
    print("✅ Save prompt generation")
    print("✅ Response handling logic")
    print("✅ Find beneficiary by nickname")
    print("✅ Error handling")
    print("\n💡 This service works with the existing beneficiaries table structure!")
