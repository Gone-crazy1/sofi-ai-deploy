#!/usr/bin/env python3
"""
Reset User PIN for Testing
===========================
Reset a user's PIN to a known value for testing purposes
"""

import hashlib
import os
from supabase import create_client

async def reset_user_pin():
    """Reset user PIN for testing"""
    print("🔄 Resetting User PIN for Testing...")
    
    # User to reset
    test_chat_id = "1797450723"
    test_pin = "1998"
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Generate correct PIN hash using pbkdf2_hmac
        pin_hash = hashlib.pbkdf2_hmac('sha256', 
                                     test_pin.encode('utf-8'), 
                                     str(test_chat_id).encode('utf-8'), 
                                     100000)
        pin_hash_hex = pin_hash.hex()
        
        print(f"Setting PIN: {test_pin}")
        print(f"For user: {test_chat_id}")
        print(f"Hash: {pin_hash_hex[:20]}...")
        
        # Update user's PIN
        result = supabase.table("users").update({
            "pin_hash": pin_hash_hex,
            "has_pin": True,
            "pin_attempts": 0,
            "pin_locked_until": None
        }).eq("telegram_chat_id", test_chat_id).execute()
        
        if result.data:
            print("✅ PIN updated successfully")
            
            # Verify the update
            user_result = supabase.table("users").select("pin_hash, has_pin").eq("telegram_chat_id", test_chat_id).execute()
            if user_result.data:
                user_data = user_result.data[0]
                stored_hash = user_data.get("pin_hash")
                has_pin = user_data.get("has_pin")
                
                print(f"✅ Verification: PIN hash stored = {stored_hash[:20]}...")
                print(f"✅ Verification: has_pin = {has_pin}")
                
                # Test verification
                if stored_hash == pin_hash_hex:
                    print("✅ PIN verification test PASSED")
                else:
                    print("❌ PIN verification test FAILED")
            else:
                print("❌ Could not verify PIN update")
        else:
            print("❌ Failed to update PIN")
    
    except Exception as e:
        print(f"❌ Error resetting PIN: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(reset_user_pin())
