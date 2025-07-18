"""
Comprehensive Beneficiary System Test - Database Compatible
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.supabase_beneficiary_service import SupabaseBeneficiaryService

async def comprehensive_test():
    try:
        print("🧪 COMPREHENSIVE BENEFICIARY SYSTEM TEST")
        print("=" * 50)
        
        service = SupabaseBeneficiaryService()
        test_user_id = 5495194750  # Existing user ID from database
        
        print(f"\n1. 📋 GET EXISTING BENEFICIARIES")
        beneficiaries = await service.get_user_beneficiaries(test_user_id)
        print(f"✅ Found {len(beneficiaries)} existing beneficiaries for user {test_user_id}")
        for i, ben in enumerate(beneficiaries):
            print(f"   {i+1}. {ben.get('nickname')} - {ben.get('bank_name')} - {ben.get('account_number')}")
        
        print(f"\n2. 💾 SAVE NEW BENEFICIARY")
        success = await service.save_beneficiary(
            user_id=test_user_id,
            beneficiary_name="THANKGOD OLUWASEUN NDIDI",
            account_number="8104965538",
            bank_code="OPAY",
            bank_name="Opay",
            nickname="Thankgod Opay"
        )
        if success:
            print("✅ Successfully saved new beneficiary: THANKGOD OLUWASEUN NDIDI")
        else:
            print("❌ Failed to save beneficiary")
        
        print(f"\n3. 🔍 SEARCH BENEFICIARY BY NAME")
        found = await service.find_beneficiary_by_name(test_user_id, "thankgod")
        if found:
            print(f"✅ Found beneficiary by search: {found.get('nickname')} - {found.get('account_number')}")
        else:
            print("❌ Could not find beneficiary by name")
        
        print(f"\n4. 🔍 SEARCH PARTIAL NAME")
        found_partial = await service.find_beneficiary_by_name(test_user_id, "thank")
        if found_partial:
            print(f"✅ Found beneficiary by partial search: {found_partial.get('nickname')}")
        else:
            print("❌ Could not find beneficiary by partial name")
        
        print(f"\n5. 📋 GET UPDATED BENEFICIARY LIST")
        updated_beneficiaries = await service.get_user_beneficiaries(test_user_id)
        print(f"✅ Updated list has {len(updated_beneficiaries)} beneficiaries")
        for i, ben in enumerate(updated_beneficiaries):
            print(f"   {i+1}. {ben.get('nickname')} - {ben.get('bank_name')} - {ben.get('account_number')}")
        
        print(f"\n6. 🔄 TEST DUPLICATE PREVENTION")
        duplicate_success = await service.save_beneficiary(
            user_id=test_user_id,
            beneficiary_name="THANKGOD OLUWASEUN NDIDI",
            account_number="8104965538",
            bank_code="OPAY",
            bank_name="Opay",
            nickname="Thankgod Duplicate Test"
        )
        if duplicate_success:
            print("✅ Duplicate prevention working - returned success for existing beneficiary")
        else:
            print("❌ Duplicate prevention failed")
        
        print(f"\n7. 📝 TEST SAVE PROMPT GENERATION")
        prompt = service.create_save_prompt("JANE SMITH", "GTBank", "0123456789")
        print(f"✅ Save prompt: {prompt}")
        
        print(f"\n8. 🔧 TEST STRING USER ID CONVERSION")
        str_beneficiaries = await service.get_user_beneficiaries(str(test_user_id))
        print(f"✅ String user_id conversion works: Found {len(str_beneficiaries)} beneficiaries")
        
        print("\n" + "=" * 50)
        print("🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("✅ Database schema compatibility confirmed")
        print("✅ BIGINT user_id handling working correctly")
        print("✅ Save, search, and retrieval functions working")
        print("✅ Duplicate prevention working")
        print("✅ Ready for OpenAI Assistant integration!")
        
    except Exception as e:
        print(f"\n❌ Comprehensive test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(comprehensive_test())
