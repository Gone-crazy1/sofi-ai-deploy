"""
Check and fix user PIN for testing
"""

import os
import sys
import hashlib
import asyncio
from supabase import create_client

async def fix_user_pin():
    """Check and fix user PIN"""
    
    try:
        # Create Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        chat_id = "5495194750"
        test_pin = "1234"
        
        print("🔐 Checking and fixing user PIN...")
        print("=" * 50)
        
        # Get user data
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", chat_id).execute()
        
        if not user_result.data:
            print("❌ User not found")
            return False
        
        user_data = user_result.data[0]
        current_pin_hash = user_data.get("pin_hash")
        
        print(f"👤 User: {user_data.get('first_name', 'Unknown')}")
        print(f"💰 Balance: ₦{user_data.get('wallet_balance', 0):,.2f}")
        print(f"🔑 Current PIN hash: {current_pin_hash[:20] + '...' if current_pin_hash else 'None'}")
        
        # Hash the PIN using the same method as the system
        pin_hash = hashlib.pbkdf2_hmac('sha256', 
                                     test_pin.encode('utf-8'), 
                                     str(chat_id).encode('utf-8'), 
                                     100000)  # 100,000 iterations
        new_pin_hash = pin_hash.hex()
        
        print(f"🔧 Setting new PIN hash: {new_pin_hash[:20]}...")
        
        # Update PIN in database
        update_result = supabase.table("users").update({
            "pin_hash": new_pin_hash,
            "has_pin": True,
            "pin_set_at": "now()"
        }).eq("telegram_chat_id", chat_id).execute()
        
        if update_result.data:
            print("✅ PIN updated successfully")
            print(f"🎯 Test PIN set to: {test_pin}")
            
            # Test the PIN using the security function
            from functions.security_functions import verify_pin
            verification_result = await verify_pin(chat_id, test_pin)
            
            if verification_result.get("valid"):
                print("✅ PIN verification test passed")
            else:
                print(f"❌ PIN verification test failed: {verification_result.get('error')}")
            
            return True
        else:
            print("❌ Failed to update PIN")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(fix_user_pin())
