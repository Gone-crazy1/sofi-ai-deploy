#!/usr/bin/env python3
"""
Debug PIN Verification
=====================
Check what's wrong with PIN verification
"""

import asyncio
import os
import hashlib
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def debug_pin_verification():
    """Debug PIN verification issues"""
    
    print("🔐 Debugging PIN Verification...")
    
    chat_id = "5495194750"  # Your chat ID
    test_pin = "1234"  # Replace with your actual PIN
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get user data
        print(f"\n1. Checking user data for chat_id: {chat_id}")
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            print("❌ User not found in database")
            return
        
        user_data = user_result.data[0]
        print(f"✅ User found: {user_data.get('full_name', 'No name')}")
        
        # Check PIN hash storage
        stored_pin_hash = user_data.get("pin_hash")
        print(f"\n2. PIN Hash Storage:")
        print(f"   Stored hash: {stored_pin_hash[:20] if stored_pin_hash else 'None'}...")
        print(f"   Hash exists: {'Yes' if stored_pin_hash else 'No'}")
        
        if not stored_pin_hash:
            print("❌ No PIN hash found. User needs to set PIN first.")
            return
        
        # Test PIN verification
        print(f"\n3. Testing PIN verification with: {test_pin}")
        pin_hash = hashlib.sha256(test_pin.encode()).hexdigest()
        print(f"   Generated hash: {pin_hash[:20]}...")
        print(f"   Stored hash:    {stored_pin_hash[:20]}...")
        print(f"   Hashes match: {'Yes' if pin_hash == stored_pin_hash else 'No'}")
        
        # Test with different PIN formats
        print(f"\n4. Testing different PIN formats:")
        test_pins = ["1234", "0000", "9999"]
        for test in test_pins:
            test_hash = hashlib.sha256(test.encode()).hexdigest()
            matches = test_hash == stored_pin_hash
            print(f"   PIN {test}: {'✅ MATCH' if matches else '❌ no match'}")
            if matches:
                print(f"   🎯 Your correct PIN is: {test}")
        
        # Check if there are any PIN attempts logged
        print(f"\n5. PIN Attempt Info:")
        print(f"   Attempts: {user_data.get('pin_attempts', 0)}")
        print(f"   Locked until: {user_data.get('pin_locked_until', 'Not locked')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_pin_verification())
