#!/usr/bin/env python3
"""
Test script to check Supabase connection and RLS policies
"""
import asyncio
import os
from dotenv import load_dotenv
from utils.memory import save_chat_message, get_chat_history

# Load environment variables
load_dotenv()

async def test_supabase_connection():
    """Test if we can save and retrieve chat messages"""
    test_chat_id = "test_123"
    
    print("Testing Supabase connection...")
    print(f"Using Supabase URL: {os.getenv('SUPABASE_URL')}")
    print(f"Using key type: {'SERVICE_ROLE' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'ANON'}")
    
    try:
        # Test saving a message
        print("\n1. Testing save_chat_message...")
        result = await save_chat_message(test_chat_id, "user", "Test message from connection test")
        print(f"Save result: {result}")
        
        if result:
            print("✅ Message saved successfully!")
        else:
            print("❌ Failed to save message")
            return False
        
        # Test retrieving messages
        print("\n2. Testing get_chat_history...")
        history = await get_chat_history(test_chat_id)
        print(f"Retrieved {len(history)} messages")
        
        if history:
            print("✅ Chat history retrieved successfully!")
            for i, msg in enumerate(history):
                print(f"  Message {i+1}: {msg['role']} - {msg['content'][:50]}...")
        else:
            print("⚠️ No chat history found (this might be expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_supabase_connection())
    if success:
        print("\n🎉 Supabase connection test completed successfully!")
    else:
        print("\n💥 Supabase connection test failed!")
