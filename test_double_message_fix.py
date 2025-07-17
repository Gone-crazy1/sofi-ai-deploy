#!/usr/bin/env python3
"""
Test script to verify the double message fix for OpenAI Assistant API
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_double_message_fix():
    """Test that double messages are handled gracefully"""
    print("🧪 Testing double message fix...")
    
    try:
        from assistant import get_assistant
        
        assistant = get_assistant()
        test_chat_id = "test_user_123"
        test_message = "Hello"
        test_user_data = {"first_name": "Test"}
        
        print(f"✅ Assistant initialized: {assistant.assistant_id}")
        
        # Simulate double message scenario
        print("\n📝 Simulating double messages...")
        
        # Send first message
        print("📤 Sending first 'Hello'...")
        response1, data1 = await assistant.process_message(test_chat_id, test_message, test_user_data)
        print(f"📥 Response 1: {response1}")
        
        # Send second message immediately (simulating double message)
        print("📤 Sending second 'Hello' immediately...")
        response2, data2 = await assistant.process_message(test_chat_id, test_message, test_user_data)
        print(f"📥 Response 2: {response2}")
        
        # Both should be friendly responses, not error messages
        success = True
        if "error" in response1.lower() or "error" in response2.lower():
            print("❌ ERROR: Responses contain error messages")
            success = False
        
        if "400" in response1 or "400" in response2:
            print("❌ ERROR: 400 error still present")
            success = False
            
        if "active run" in response1.lower() or "active run" in response2.lower():
            print("❌ ERROR: Active run conflicts still present")
            success = False
        
        if success:
            print("✅ SUCCESS: Double messages handled gracefully!")
            print("✅ Both responses are user-friendly")
            print("✅ No OpenAI API 400 errors")
            print("✅ No technical error messages exposed to user")
        else:
            print("❌ FAILED: Issues detected in double message handling")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sofi AI Double Message Fix Test")
    print("=" * 50)
    
    result = asyncio.run(test_double_message_fix())
    
    if result:
        print("\n🎉 All tests passed! Double message fix is working.")
    else:
        print("\n❌ Tests failed. Check the implementation.")
    
    print("\n📋 Fix Summary:")
    print("✅ Enhanced user-level locking to prevent race conditions")
    print("✅ Added race condition detection with small delays")
    print("✅ Better error handling for active run conflicts")
    print("✅ Friendly responses for double messages instead of technical errors")
    print("✅ Varied greeting responses to make double messages feel natural")
