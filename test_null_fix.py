#!/usr/bin/env python3
"""
Test script to verify the null response fix for Sofi AI
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_assistant_response():
    """Test the assistant response handling"""
    try:
        from assistant import get_assistant
        
        print("🧪 Testing Assistant Response Fix...")
        
        assistant = get_assistant()
        
        # Test a balance check first
        print("\n1️⃣ Testing balance check...")
        response, function_data = await assistant.process_message(
            chat_id="5495194750",
            message="What is my balance?",
            user_data={}
        )
        
        print(f"✅ Balance Response: {response}")
        print(f"📊 Function Data: {function_data}")
        
        # Test a transfer request
        print("\n2️⃣ Testing transfer request...")
        response, function_data = await assistant.process_message(
            chat_id="5495194750", 
            message="Send 100 to 8104965538 at Opay",
            user_data={}
        )
        
        print(f"✅ Transfer Response: {response}")
        print(f"📊 Function Data: {function_data}")
        
        # Check if response is null or empty
        if not response or response.strip() == "" or response.strip().lower() == "null":
            print("❌ ISSUE: Response is null or empty!")
            return False
        else:
            print("✅ SUCCESS: Response is valid and not null!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🔧 SOFI AI NULL RESPONSE FIX TEST")
    print("=" * 50)
    
    success = await test_assistant_response()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! The null response issue should be fixed.")
        print("🚀 Ready to deploy the fix to production.")
    else:
        print("\n❌ TESTS FAILED! Need to investigate further.")
        
    return success

if __name__ == "__main__":
    asyncio.run(main())
