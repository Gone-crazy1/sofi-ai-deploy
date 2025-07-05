#!/usr/bin/env python3
"""
Debug the assistant integration to see what's causing the error
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_assistant():
    """Debug the assistant integration"""
    print("🔍 DEBUGGING ASSISTANT INTEGRATION")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    print(f"   OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"   SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Missing'}")
    print(f"   SUPABASE_KEY: {'✅ Set' if os.getenv('SUPABASE_KEY') else '❌ Missing'}")
    
    # Test assistant import
    print("\n🤖 Testing Assistant Import:")
    try:
        from assistant import get_assistant
        print("✅ Assistant import successful")
        
        # Test assistant creation
        assistant = get_assistant()
        print(f"✅ Assistant created: {type(assistant)}")
        
        # Test simple message processing
        print("\n💬 Testing Simple Message:")
        test_message = "Hello"
        test_chat_id = "debug_test"
        
        response, function_data = await assistant.process_message(test_chat_id, test_message, {})
        
        print(f"✅ Response: {response}")
        print(f"✅ Function data: {function_data}")
        
    except Exception as e:
        print(f"❌ Assistant error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test main handler
    print("\n🔧 Testing Main Handler:")
    try:
        from main import handle_message
        
        response = await handle_message("debug_test", "Hello")
        print(f"✅ Main handler response: {response}")
        
    except Exception as e:
        print(f"❌ Main handler error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_assistant())
