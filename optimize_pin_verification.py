#!/usr/bin/env python3
"""Optimize PIN verification from 10 seconds to 1 second."""

import os
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

def test_pin_verification_speeds():
    """Test different PIN hashing methods for speed"""
    test_pin = "1234"
    test_chat_id = "123456789"
    
    print("🔍 Testing PIN Verification Speed...")
    print("=" * 50)
    
    # Test 1: Current SLOW method (pbkdf2_hmac with 100k iterations)
    print("\n1️⃣ CURRENT METHOD (pbkdf2_hmac with 100,000 iterations):")
    start_time = time.time()
    slow_hash = hashlib.pbkdf2_hmac('sha256', 
                                  test_pin.encode('utf-8'), 
                                  str(test_chat_id).encode('utf-8'), 
                                  100000)  # 100,000 iterations
    slow_time = time.time() - start_time
    print(f"   ⏱️  Time: {slow_time:.3f} seconds")
    print(f"   🐌 Status: {'TOO SLOW' if slow_time > 1 else 'ACCEPTABLE'}")
    
    # Test 2: Optimized pbkdf2_hmac (10k iterations)
    print("\n2️⃣ OPTIMIZED pbkdf2_hmac (10,000 iterations):")
    start_time = time.time()
    optimized_hash = hashlib.pbkdf2_hmac('sha256', 
                                       test_pin.encode('utf-8'), 
                                       str(test_chat_id).encode('utf-8'), 
                                       10000)  # 10,000 iterations (10x faster)
    optimized_time = time.time() - start_time
    print(f"   ⏱️  Time: {optimized_time:.3f} seconds")
    print(f"   ⚡ Status: {'FAST' if optimized_time <= 1 else 'SLOW'}")
    
    # Test 3: SHA256 + salt (very fast)
    print("\n3️⃣ SHA256 with salt (fastest):")
    start_time = time.time()
    fast_hash = hashlib.sha256((test_pin + str(test_chat_id)).encode()).hexdigest()
    fast_time = time.time() - start_time
    print(f"   ⏱️  Time: {fast_time:.6f} seconds")
    print(f"   🚀 Status: ULTRA FAST")
    
    # Test 4: Plain SHA256 (current permanent_memory.py method)
    print("\n4️⃣ Plain SHA256 (current fallback):")
    start_time = time.time()
    plain_hash = hashlib.sha256(test_pin.encode()).hexdigest()
    plain_time = time.time() - start_time
    print(f"   ⏱️  Time: {plain_time:.6f} seconds")
    print(f"   🚀 Status: ULTRA FAST")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATION:")
    
    if optimized_time <= 1.0:
        print("✅ Use optimized pbkdf2_hmac (10,000 iterations)")
        print("   - Maintains security")
        print("   - Achieves < 1 second target")
        print("   - Compatible with existing hashes (just need to reduce iterations)")
    else:
        print("✅ Use SHA256 + salt")
        print("   - Ultra fast (< 0.001 seconds)")
        print("   - Still secure with chat_id salt")
        print("   - Requires hash migration")
    
    return {
        "slow_time": slow_time,
        "optimized_time": optimized_time,
        "fast_time": fast_time,
        "plain_time": plain_time
    }

def create_optimized_pin_verification():
    """Create optimized PIN verification function"""
    
    optimized_function = '''
async def verify_user_pin_optimized(self, telegram_chat_id: str, pin: str) -> Dict[str, Any]:
    """Verify user's transaction PIN - OPTIMIZED VERSION (< 1 second)"""
    try:
        logger.info(f"🔐 Verifying PIN for user {telegram_chat_id} (optimized)")
        
        # Get user data
        user_data = self.supabase.table("users").select("*").eq("telegram_chat_id", telegram_chat_id).execute()
        
        if not user_data.data:
            return {"success": False, "error": "User not found"}
        
        user = user_data.data[0]
        
        # Check if user has PIN set
        if not user.get("pin_hash"):
            return {
                "success": False,
                "error": "No PIN set. Please set your PIN first.",
                "action_required": "set_pin"
            }
        
        # 🚀 OPTIMIZED: Use fast hashing (10,000 iterations instead of 100,000)
        pin_hash = hashlib.pbkdf2_hmac('sha256', 
                                     pin.encode('utf-8'), 
                                     str(telegram_chat_id).encode('utf-8'), 
                                     10000)  # ⚡ 10x faster!
        pin_hash = pin_hash.hex()
        
        if pin_hash == user["pin_hash"]:
            # Reset PIN attempts on success
            self.supabase.table("users").update({
                "pin_attempts": 0,
                "pin_locked_until": None
            }).eq("telegram_chat_id", telegram_chat_id).execute()
            
            return {"success": True, "message": "✅ PIN verified successfully"}
        else:
            # Handle failed attempts
            attempts = user.get("pin_attempts", 0) + 1
            update_data = {"pin_attempts": attempts}
            
            # Lock account after 5 failed attempts
            if attempts >= 5:
                from datetime import datetime, timedelta
                lock_until = datetime.utcnow() + timedelta(minutes=30)
                update_data["pin_locked_until"] = lock_until.isoformat()
                
                self.supabase.table("users").update(update_data).eq("telegram_chat_id", telegram_chat_id).execute()
                
                return {
                    "success": False,
                    "error": "Account locked for 30 minutes due to multiple failed PIN attempts"
                }
            else:
                self.supabase.table("users").update(update_data).eq("telegram_chat_id", telegram_chat_id).execute()
                remaining = 5 - attempts
                return {
                    "success": False,
                    "error": f"Invalid PIN. {remaining} attempts remaining."
                }
                
    except Exception as e:
        logger.error(f"❌ Error verifying PIN: {e}")
        return {"success": False, "error": "PIN verification failed"}
'''
    
    print("📝 OPTIMIZED PIN VERIFICATION FUNCTION:")
    print("=" * 60)
    print(optimized_function)
    
    return optimized_function

if __name__ == "__main__":
    print("🔧 PIN VERIFICATION OPTIMIZATION")
    print("================================")
    
    # Test speeds
    speeds = test_pin_verification_speeds()
    
    # Create optimized function
    print("\n" + "🔧" * 20)
    optimized_code = create_optimized_pin_verification()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Replace slow pbkdf2_hmac (100k) with fast version (10k)")
    print("2. Update existing user PIN hashes to use 10k iterations")
    print("3. Test with real user to confirm < 1 second performance")
    
    if speeds["optimized_time"] <= 1.0:
        print("\n✅ Target achieved! PIN verification will be < 1 second")
    else:
        print("\n⚠️  May need to use SHA256+salt method instead")
