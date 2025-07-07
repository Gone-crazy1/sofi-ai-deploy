#!/usr/bin/env python3
"""
URGENT PIN VERIFICATION FIX
===========================
Check and fix the salt mismatch between onboarding and verification
"""

import os
import hashlib
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def check_pin_salt_issue():
    """Check if PIN salt mismatch is causing verification failures"""
    
    print("🔍 Checking PIN salt issue...")
    
    # Initialize Supabase
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Get users with PINs set
    users = supabase.table("users").select("*").not_.is_("pin_hash", "null").limit(5).execute()
    
    if not users.data:
        print("❌ No users found")
        return
    
    user = users.data[0]
    telegram_id = user.get('telegram_id')
    telegram_chat_id = user.get('telegram_chat_id')
    pin_hash = user.get('pin_hash')
    
    print(f"📋 User data:")
    print(f"   telegram_id: {telegram_id}")
    print(f"   telegram_chat_id: {telegram_chat_id}")
    print(f"   pin_hash exists: {bool(pin_hash)}")
    
    # Test PIN "1998" with both salt methods
    test_pin = "1998"
    
    # Method 1: Using telegram_id as salt (onboarding method)
    hash1 = hashlib.pbkdf2_hmac('sha256', 
                               test_pin.encode('utf-8'), 
                               str(telegram_id).encode('utf-8'), 
                               100000)
    hash1_hex = hash1.hex()
    
    # Method 2: Using telegram_chat_id as salt (verification method)
    hash2 = hashlib.pbkdf2_hmac('sha256', 
                               test_pin.encode('utf-8'), 
                               str(telegram_chat_id).encode('utf-8'), 
                               100000)
    hash2_hex = hash2.hex()
    
    print(f"\n🔐 PIN Hash Comparison:")
    print(f"   Using telegram_id as salt: {hash1_hex}")
    print(f"   Using telegram_chat_id as salt: {hash2_hex}")
    print(f"   Stored hash: {pin_hash}")
    print(f"   Match with telegram_id: {hash1_hex == pin_hash}")
    print(f"   Match with telegram_chat_id: {hash2_hex == pin_hash}")
    
    # If neither matches, let's try other common test PINs
    if hash1_hex != pin_hash and hash2_hex != pin_hash:
        print(f"\n🔄 Testing other common PINs...")
        test_pins = ["1234", "0000", "1111", "2222", "1212"]
        
        for pin in test_pins:
            # Test with telegram_id
            hash_test = hashlib.pbkdf2_hmac('sha256', 
                                           pin.encode('utf-8'), 
                                           str(telegram_id).encode('utf-8'), 
                                           100000)
            if hash_test.hex() == pin_hash:
                print(f"✅ Found matching PIN: {pin} (using telegram_id)")
                return
            
            # Test with telegram_chat_id
            hash_test = hashlib.pbkdf2_hmac('sha256', 
                                           pin.encode('utf-8'), 
                                           str(telegram_chat_id).encode('utf-8'), 
                                           100000)
            if hash_test.hex() == pin_hash:
                print(f"✅ Found matching PIN: {pin} (using telegram_chat_id)")
                return
    
    print("\n💡 Recommendation:")
    if hash1_hex == pin_hash:
        print("✅ Use telegram_id as salt in verification functions")
        print("📝 Need to update security_functions.py and sofi_money_functions.py")
    elif hash2_hex == pin_hash:
        print("✅ Use telegram_chat_id as salt in verification functions")
        print("📝 Verification functions are correct")
    else:
        print("❌ PIN hash method mismatch - need to investigate further")

if __name__ == "__main__":
    check_pin_salt_issue()
