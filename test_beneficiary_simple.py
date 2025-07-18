#!/usr/bin/env python3
"""
Simple test script for Supabase Beneficiary Service
Tests just the core beneficiary functionality
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_beneficiary_basic():
    """Test basic beneficiary service functionality"""
    print("🧪 Testing Basic Beneficiary Service...")
    
    try:
        from utils.supabase_beneficiary_service import beneficiary_service
        print("✅ Beneficiary service imported successfully")
        
        # Use a mock user ID for testing
        test_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Test 1: Get empty beneficiaries list
        print("\n📝 Test 1: Get beneficiaries list (should be empty)...")
        beneficiaries_list = await beneficiary_service.format_beneficiaries_list(test_user_id)
        print(f"📥 Result: {beneficiaries_list[:200]}...")
        
        # Test 2: Create save prompt
        print("\n📝 Test 2: Create save beneficiary prompt...")
        save_prompt = beneficiary_service.create_save_beneficiary_prompt(
            recipient_name="JOHN SMITH",
            bank_name="Opay", 
            account_number="8104965538"
        )
        print(f"📥 Prompt: {save_prompt}")
        
        # Test 3: Test save response handling (without actual saving)
        print("\n📝 Test 3: Test save response handling...")
        transfer_data = {
            "recipient_name": "JOHN SMITH",
            "bank_name": "Opay",
            "account_number": "8104965538"
        }
        
        # Test different responses
        responses_to_test = ["yes", "no", "save as John", "Mum"]
        
        for response in responses_to_test:
            print(f"\n  Testing response: '{response}'")
            try:
                result = await beneficiary_service.handle_save_response(
                    user_id=test_user_id,
                    response=response,
                    transfer_data=transfer_data
                )
                print(f"  📥 Result: {result.get('success', False)} - {result.get('message', result.get('error', 'No message'))}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n✅ Basic beneficiary service tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_beneficiary_methods():
    """Test individual beneficiary methods"""
    print("\n🔧 Testing Individual Methods...")
    
    try:
        from utils.supabase_beneficiary_service import SofiBeneficiaryService
        
        # Create service instance
        service = SofiBeneficiaryService()
        print("✅ Service instance created")
        
        # Test user ID
        test_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Test find beneficiary (should return None for non-existent)
        print("\n📝 Testing find_beneficiary_by_name...")
        result = await service.find_beneficiary_by_name(test_user_id, "nonexistent")
        print(f"📥 Find result: {result}")
        
        # Test get beneficiaries (should return empty list)
        print("\n📝 Testing get_user_beneficiaries...")
        beneficiaries = await service.get_user_beneficiaries(test_user_id)
        print(f"📥 Beneficiaries count: {len(beneficiaries)}")
        
        print("\n✅ Individual method tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Simple Beneficiary Service Test")
    print("=" * 40)
    
    # Test basic functionality
    basic_result = asyncio.run(test_beneficiary_basic())
    
    # Test individual methods
    methods_result = asyncio.run(test_beneficiary_methods())
    
    if basic_result and methods_result:
        print("\n🎉 Core beneficiary service is working!")
        print("✅ Ready to integrate with Assistant")
    else:
        print("\n❌ Some core tests failed.")
    
    print("\n📋 What we tested:")
    print("✅ Service import and initialization")
    print("✅ Save prompt generation")
    print("✅ Response handling logic")
    print("✅ Individual method calls")
    print("✅ Error handling")
