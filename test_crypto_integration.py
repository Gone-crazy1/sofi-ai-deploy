
#!/usr/bin/env python3
"""Test crypto rate integration"""

import asyncio
import sys
import os

async def test_crypto_integration():
    """Test all crypto rate functionality"""
    
    print("🧪 TESTING CRYPTO RATE INTEGRATION")
    print("=" * 50)
    
    try:
        # Test 1: Import check
        print("1️⃣ Testing imports...")
        from crypto_rate_manager import get_crypto_rates_message, handle_crypto_deposit
        print("   ✅ Crypto rate imports successful")
        
        # Test 2: Rate fetching
        print("\n2️⃣ Testing rate fetching...")
        rate_message = await get_crypto_rates_message()
        if "Bitcoin" in rate_message and "USDT" in rate_message:
            print("   ✅ Rate fetching working")
            print(f"   Sample: {rate_message[:100]}...")
        else:
            print("   ❌ Rate fetching failed")
            return False
        
        # Test 3: Deposit simulation
        print("\n3️⃣ Testing deposit processing...")
        deposit_result = await handle_crypto_deposit("test_user", "USDT", 10, "test_hash")
        if "Deposit Confirmed" in deposit_result:
            print("   ✅ Deposit processing working")
        else:
            print("   ❌ Deposit processing failed")
            return False
        
        # Test 4: Database integration
        print("\n4️⃣ Testing database integration...")
        from crypto_rate_manager import rate_manager
        rates = await rate_manager.get_current_rates()
        if rates and 'your_rates' in rates:
            print("   ✅ Database integration working")
            usdt_info = rates['your_rates'].get('USDT', {})
            if usdt_info:
                print(f"   USDT: Market=₦{usdt_info.get('market_rate', 0):,.2f}, Your=₦{usdt_info.get('your_rate', 0):,.2f}")
        else:
            print("   ❌ Database integration failed")
            return False
        
        print("\n🎉 ALL CRYPTO INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_crypto_integration())
    if success:
        print("\n🚀 CRYPTO RATE SYSTEM READY FOR PRODUCTION!")
    else:
        print("\n❌ Fix issues before deploying to production")
    