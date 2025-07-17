#!/usr/bin/env python3
"""
Quick PIN verification fix - bypass missing pin_attempts table
"""

import asyncio
from utils.secure_pin_verification import secure_pin_verification

async def test_pin_verification_fix():
    """Test PIN verification with the updated system"""
    
    transaction_id = "transfer_7812930440_1752737626"  # From your logs
    pin = "1998"  # Your actual PIN
    
    print("🔧 TESTING PIN VERIFICATION FIX")
    print("=" * 40)
    
    try:
        # Test the PIN verification
        result = await secure_pin_verification.verify_pin_and_process_transfer(transaction_id, pin)
        
        print(f"📊 Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Error: {result.get('error', 'None')}")
        
        if result.get('success'):
            print("🎉 PIN verification would work!")
        else:
            print("❌ Still has issues:", result.get('error'))
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_pin_verification_fix())
