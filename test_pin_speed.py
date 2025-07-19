#!/usr/bin/env python3
"""Test the optimized PIN verification speed."""

import asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()

async def test_pin_verification_performance():
    """Test the new optimized PIN verification performance"""
    
    print("🚀 TESTING OPTIMIZED PIN VERIFICATION")
    print("=" * 50)
    
    try:
        # Import the money service
        from sofi_money_functions import SofiMoneyTransferService
        
        service = SofiMoneyTransferService()
        
        # Test data (use a test account that doesn't exist to avoid side effects)
        test_chat_id = "test_performance_user"
        test_pin = "1234"
        
        print(f"🔍 Testing PIN verification speed...")
        print(f"   Chat ID: {test_chat_id}")
        print(f"   PIN: {test_pin}")
        
        # Test 1: Regular verification speed
        print("\n1️⃣ Testing Current PIN Verification Speed:")
        start_time = time.time()
        
        try:
            result = await service.verify_user_pin(test_chat_id, test_pin)
            elapsed = time.time() - start_time
            
            print(f"   ⏱️  Verification Time: {elapsed:.3f} seconds")
            print(f"   📊 Result: {result}")
            
            if elapsed <= 1.0:
                print(f"   ✅ SUCCESS: Under 1 second target!")
            else:
                print(f"   ❌ SLOW: Over 1 second target")
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ⏱️  Time (with error): {elapsed:.3f} seconds")
            print(f"   ℹ️  Expected error (test user): {e}")
        
        # Test 2: Multiple verification attempts to test consistency
        print("\n2️⃣ Testing Multiple Verification Attempts:")
        times = []
        
        for i in range(5):
            start_time = time.time()
            try:
                await service.verify_user_pin(test_chat_id, test_pin)
            except:
                pass  # Expected error for test user
            elapsed = time.time() - start_time
            times.append(elapsed)
            print(f"   Attempt {i+1}: {elapsed:.3f}s")
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n📊 Performance Summary:")
        print(f"   Average Time: {avg_time:.3f} seconds")
        print(f"   Maximum Time: {max_time:.3f} seconds")
        print(f"   Target: < 1.0 seconds")
        
        if max_time <= 1.0:
            print(f"   ✅ ALL TESTS PASSED: Consistently under 1 second!")
        else:
            print(f"   ❌ PERFORMANCE ISSUE: Some attempts over 1 second")
        
        print("\n" + "=" * 50)
        print("🎯 OPTIMIZATION STATUS:")
        
        if avg_time <= 0.5:
            print("✅ EXCELLENT: PIN verification is now ultra-fast!")
        elif avg_time <= 1.0:
            print("✅ GOOD: PIN verification meets the 1-second target!")
        else:
            print("⚠️  NEEDS WORK: Still too slow, may need further optimization")
            
        return {
            "average_time": avg_time,
            "max_time": max_time,
            "all_times": times,
            "target_met": max_time <= 1.0
        }
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚡ PIN VERIFICATION PERFORMANCE TEST")
    print("===================================")
    
    result = asyncio.run(test_pin_verification_performance())
    
    if result and result.get("target_met"):
        print("\n🎉 MISSION ACCOMPLISHED!")
        print("PIN verification is now fast enough for production!")
    else:
        print("\n🔧 More optimization needed...")
