#!/usr/bin/env python3
"""
Fix User PIN Hash
================
Reset the user's PIN with the correct hashing method
"""

import os
import asyncio
import hashlib
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

async def fix_user_pin():
    """Fix the user's PIN hash"""
    
    print("🔧 Fixing user PIN hash...")
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        chat_id = "5495194750"
        correct_pin = "1998"  # The PIN the user knows
        
        # Use simple SHA256 hashing (matching other parts of the system)
        pin_hash = hashlib.sha256(correct_pin.encode()).hexdigest()
        
        print(f"💡 Updating PIN hash for user {chat_id}")
        print(f"   PIN: {correct_pin}")
        print(f"   New hash: {pin_hash}")
        
        # Update the user's PIN hash (minimal update)
        result = supabase.table("users").update({
            "pin_hash": pin_hash
        }).eq("telegram_chat_id", chat_id).execute()
        
        if result.data:
            print("✅ PIN hash updated successfully!")
            
            # Test verification
            from functions.security_functions import verify_pin
            test_result = await verify_pin(chat_id, correct_pin)
            print(f"🔐 Verification test: {test_result}")
            
        else:
            print("❌ Failed to update PIN hash")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_user_pin())
