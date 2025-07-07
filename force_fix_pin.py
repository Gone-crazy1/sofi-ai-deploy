#!/usr/bin/env python3
"""
Force Fix User PIN
==================
Manually update the user's PIN hash to work with the current system
"""

import os
import asyncio
import hashlib
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

async def force_fix_pin():
    """Force fix the user's PIN"""
    
    print("🔧 Force fixing user PIN...")
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
        
        chat_id = "5495194750"
        correct_pin = "1998"
        
        # Use the exact same method as the verification function
        pin_hash = hashlib.sha256(correct_pin.encode()).hexdigest()
        
        print(f"💡 Force updating PIN hash for user {chat_id}")
        print(f"   PIN: {correct_pin}")
        print(f"   New SHA256 hash: {pin_hash}")
        
        # Use raw SQL to bypass any triggers
        sql_query = f"""
        UPDATE users 
        SET pin_hash = '{pin_hash}',
            has_pin = true,
            pin_attempts = 0,
            pin_locked_until = null
        WHERE telegram_chat_id = '{chat_id}'
        RETURNING telegram_chat_id, pin_hash;
        """
        
        result = supabase.rpc('exec_sql', {'sql': sql_query}).execute()
        print(f"SQL result: {result}")
        
        # Test verification immediately
        print("\n🔐 Testing PIN verification...")
        from functions.security_functions import verify_pin
        test_result = await verify_pin(chat_id, correct_pin)
        print(f"Verification test: {test_result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Fallback: try direct table update
        print("\n🔄 Trying direct table update...")
        try:
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # Direct update without triggers
            result = supabase.table("users").update({
                "pin_hash": pin_hash
            }).eq("telegram_chat_id", chat_id).execute()
            
            print(f"Direct update result: {result.data}")
            
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")

if __name__ == "__main__":
    asyncio.run(force_fix_pin())
