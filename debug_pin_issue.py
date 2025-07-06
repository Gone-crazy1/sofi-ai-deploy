#!/usr/bin/env python3
"""
Debug PIN Storage Issue
======================
Check what's actually stored in the database for the user
"""

import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

async def debug_pin_storage():
    """Debug PIN storage for the user"""
    
    print("🔍 Debugging PIN storage...")
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Check the user's data
        chat_id = "5495194750"
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", chat_id).execute()
        
        if not user_result.data:
            print(f"❌ User {chat_id} not found")
            return
        
        user_data = user_result.data[0]
        
        print(f"📊 User data for {chat_id}:")
        print(f"   telegram_chat_id: {user_data.get('telegram_chat_id')}")
        print(f"   pin: {user_data.get('pin')}")
        print(f"   pin_hash: {user_data.get('pin_hash')}")
        print(f"   All columns: {list(user_data.keys())}")
        
        # Test different PIN hashing methods
        test_pin = "1998"
        import hashlib
        
        # Method 1: Simple SHA256
        hash1 = hashlib.sha256(test_pin.encode()).hexdigest()
        
        # Method 2: SHA256 with chat_id as salt
        hash2 = hashlib.sha256((test_pin + str(chat_id)).encode()).hexdigest()
        
        # Method 3: SHA256 with chat_id first
        hash3 = hashlib.sha256((str(chat_id) + test_pin).encode()).hexdigest()
        
        # Method 4: PBKDF2 (original verification method)
        hash4 = hashlib.pbkdf2_hmac('sha256', 
                                     test_pin.encode('utf-8'), 
                                     str(chat_id).encode('utf-8'), 
                                     100000).hex()
        
        stored_hash = user_data.get('pin_hash')
        
        print(f"\n🔐 Testing different hashing methods:")
        print(f"   Input PIN: '{test_pin}'")
        print(f"   Stored hash: '{stored_hash}'")
        print(f"   Method 1 (SHA256): '{hash1}'")
        print(f"   Method 2 (SHA256+chatid): '{hash2}'") 
        print(f"   Method 3 (chatid+SHA256): '{hash3}'")
        print(f"   Method 4 (PBKDF2): '{hash4}'")
        
        # Check matches
        if stored_hash == hash1:
            print("✅ MATCH: Simple SHA256")
        elif stored_hash == hash2:
            print("✅ MATCH: SHA256 with chat_id suffix")
        elif stored_hash == hash3:
            print("✅ MATCH: SHA256 with chat_id prefix")
        elif stored_hash == hash4:
            print("✅ MATCH: PBKDF2 with chat_id salt")
        else:
            print("❌ No matches found - need to investigate further")
        
        # Recommendation
        if user_data.get('pin') and not user_data.get('pin_hash'):
            print("\n💡 ISSUE: PIN is stored as plain text but verification expects hash")
        elif user_data.get('pin_hash') and not user_data.get('pin'):
            print("\n💡 ISSUE: PIN is stored as hash but might be checking wrong column")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_pin_storage())
