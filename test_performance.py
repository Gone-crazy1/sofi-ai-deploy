#!/usr/bin/env python3
"""
Performance Test for Sofi AI Ultra-Fast Response System
Tests the new instant response + background processing architecture
"""

import asyncio
import time
import json
from assistant import SofiAssistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_ultra_fast_responses():
    """Test the new ultra-fast response system"""
    print("🚀 Testing Sofi AI Ultra-Fast Response System")
    print("=" * 60)
    
    # Initialize assistant
    assistant = SofiAssistant()
    
    # Test messages that should get instant responses
    test_messages = [
        "send ₦5000 to 1234567890 GTBank",
        "what's my balance?",
        "I want to set a new PIN",
        "transfer money to my friend",
        "check my account balance",
        "send ₦1000 to my saved beneficiary"
    ]
    
    test_chat_id = "test_performance_123"
    test_user_data = {"first_name": "Test User", "virtual_account": {"account_number": "1234567890"}}
    
    print("🔥 Target: < 0.1 seconds per response (100ms)")
    print("🎯 Goal: Handle 50-100 concurrent users\n")
    
    # Test individual response times
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: '{message}'")
        
        start_time = time.time()
        
        try:
            response, function_data = await assistant.process_message(
                test_chat_id, message, test_user_data
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Check if response was instant
            if response_time < 100:  # Less than 100ms
                status = "✅ ULTRA-FAST"
            elif response_time < 500:  # Less than 500ms
                status = "⚡ FAST"
            else:
                status = "⚠️ SLOW"
            
            print(f"   Response: {response[:50]}{'...' if len(response) > 50 else ''}")
            print(f"   Time: {response_time:.1f}ms {status}")
            print(f"   Background Tasks: {len(function_data) if function_data else 0}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
    
    # Test concurrent load
    print("🔥 Testing Concurrent Load (10 simultaneous users)")
    print("-" * 40)
    
    async def simulate_user(user_id: int):
        """Simulate a single user interaction"""
        chat_id = f"concurrent_test_{user_id}"
        message = f"what's my balance user {user_id}?"
        
        start_time = time.time()
        try:
            response, _ = await assistant.process_message(chat_id, message, test_user_data)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return user_id, response_time, True
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return user_id, response_time, False
    
    # Run 10 concurrent users
    start_concurrent = time.time()
    concurrent_tasks = [simulate_user(i) for i in range(1, 11)]
    results = await asyncio.gather(*concurrent_tasks)
    end_concurrent = time.time()
    
    total_concurrent_time = (end_concurrent - start_concurrent) * 1000
    
    # Analyze concurrent results
    successful = sum(1 for _, _, success in results if success)
    response_times = [time for _, time, success in results if success]
    
    if response_times:
        avg_response = sum(response_times) / len(response_times)
        max_response = max(response_times)
        min_response = min(response_times)
        
        print(f"✅ Concurrent Users: 10")
        print(f"✅ Successful Responses: {successful}/10")
        print(f"⚡ Total Time: {total_concurrent_time:.1f}ms")
        print(f"📊 Average Response: {avg_response:.1f}ms")
        print(f"📊 Fastest Response: {min_response:.1f}ms")
        print(f"📊 Slowest Response: {max_response:.1f}ms")
        
        # Performance verdict
        if avg_response < 100:
            print("\n🎉 PERFORMANCE VERDICT: ULTRA-FAST! Ready for production!")
        elif avg_response < 500:
            print("\n⚡ PERFORMANCE VERDICT: FAST! Good for production.")
        else:
            print("\n⚠️ PERFORMANCE VERDICT: Needs optimization for high load.")
    else:
        print("❌ All concurrent requests failed")
    
    print("\n" + "=" * 60)
    print("🚀 Performance Test Complete")

if __name__ == "__main__":
    asyncio.run(test_ultra_fast_responses())
