"""
Test the updated OpenAI Assistant integration
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append('.')

async def test_assistant_integration():
    """Test the assistant integration"""
    print("🔄 Testing OpenAI Assistant Integration...")
    
    try:
        # Test 1: Import the assistant
        print("\n1. Testing assistant import...")
        from assistant import get_assistant
        print("✅ Assistant import successful")
        
        # Test 2: Initialize assistant
        print("\n2. Initializing assistant...")
        assistant = get_assistant()
        print(f"✅ Assistant initialized with ID: {assistant.assistant_id}")
        
        # Test 3: Test a simple message
        print("\n3. Testing message processing...")
        test_chat_id = "test_user_123"
        test_message = "Hello, what can you help me with?"
        
        response, function_data = await assistant.process_message(
            test_chat_id, 
            test_message, 
            {"test": "data"}
        )
        
        print(f"✅ Message processed successfully")
        print(f"📄 Response: {response[:100]}..." if len(response) > 100 else f"📄 Response: {response}")
        
        if function_data:
            print(f"🔧 Function data: {function_data}")
        
        print("\n🎉 All tests passed! OpenAI Assistant integration is working!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_assistant_integration())
