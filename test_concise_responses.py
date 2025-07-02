"""
Test script to verify Sofi AI responses are concise and credit-efficient
"""

import asyncio
import os
from dotenv import load_dotenv
from main import generate_ai_reply, handle_message
from assistant import get_assistant

load_dotenv()

async def test_concise_responses():
    """Test that all responses are concise"""
    
    test_cases = [
        "/help",
        "help",
        "what can you do",
        "check my balance", 
        "send money",
        "buy airtime",
        "create account",
        "who are you"
    ]
    
    print("🧪 Testing Sofi AI Response Lengths")
    print("=" * 50)
    
    for message in test_cases:
        print(f"\n📝 Testing: '{message}'")
        
        try:
            # Test main message handler
            response = await handle_message("test_user_123", message, {})
            
            # Count words and characters
            word_count = len(response.split())
            char_count = len(response)
            
            print(f"📊 Response: {char_count} chars, {word_count} words")
            print(f"💬 Content: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            # Check if response is concise (under 500 characters)
            if char_count > 500:
                print("⚠️  WARNING: Response too long!")
            elif char_count > 300:
                print("⚡ MODERATE: Could be shorter")
            else:
                print("✅ GOOD: Concise response")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_concise_responses())
