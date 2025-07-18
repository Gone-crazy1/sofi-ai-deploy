"""
Simple test for beneficiary service
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_service():
    try:
        # Import the service class directly
        from utils.supabase_beneficiary_service import SupabaseBeneficiaryService
        
        print("🧪 Testing Beneficiary Service...")
        
        # Create service instance
        service = SupabaseBeneficiaryService()
        print("✅ Service created successfully")
        
        # Test user_id conversion
        user_id = service._convert_user_id("5495194750")
        print(f"✅ User ID conversion works: {user_id}")
        
        # Test get beneficiaries for existing user
        beneficiaries = await service.get_user_beneficiaries(5495194750)
        print(f"✅ Found {len(beneficiaries)} beneficiaries")
        
        # Test save prompt
        prompt = service.create_save_prompt("JOHN DOE", "GTBank", "0123456789")
        print(f"✅ Save prompt: {prompt}")
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())
