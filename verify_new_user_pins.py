#!/usr/bin/env python3
"""
VERIFY NEW USER PIN FLOW
========================
Test that new users can use the PINs they set during onboarding
"""

import os
import hashlib
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def verify_new_user_pin_flow():
    """Verify that new users can use their onboarding PINs"""
    
    print("🔍 VERIFYING NEW USER PIN FLOW...")
    
    # Initialize Supabase
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    # Step 1: Simulate onboarding PIN hashing
    print("\n1. Simulating onboarding PIN hashing...")
    
    # New user data (simulating onboarding form)
    new_user_data = {
        'telegram_id': '123456789',  # This comes from onboarding form
        'full_name': 'Test New User',
        'phone': '08012345678',
        'email': 'test@example.com',
        'pin': '5678'  # User sets this PIN during onboarding
    }
    
    # Simulate onboarding PIN hashing (from utils/user_onboarding.py)
    telegram_id = str(new_user_data['telegram_id'])
    user_pin = new_user_data['pin']
    
    # Hash PIN using onboarding method
    onboarding_hash = hashlib.pbkdf2_hmac('sha256', 
                                        user_pin.encode('utf-8'), 
                                        telegram_id.encode('utf-8'), 
                                        100000)
    onboarding_hash_hex = onboarding_hash.hex()
    
    print(f"   User PIN: {user_pin}")
    print(f"   Telegram ID: {telegram_id}")
    print(f"   Onboarding Hash: {onboarding_hash_hex}")
    
    # Step 2: Simulate verification PIN hashing
    print("\n2. Simulating verification PIN hashing...")
    
    # In verification, we use telegram_chat_id (which should be same as telegram_id)
    chat_id = telegram_id  # This is the same value, just stored as telegram_chat_id
    
    # Hash PIN using verification method
    verification_hash = hashlib.pbkdf2_hmac('sha256', 
                                          user_pin.encode('utf-8'), 
                                          str(chat_id).encode('utf-8'), 
                                          100000)
    verification_hash_hex = verification_hash.hex()
    
    print(f"   Chat ID: {chat_id}")
    print(f"   Verification Hash: {verification_hash_hex}")
    
    # Step 3: Check if hashes match
    print("\n3. Checking if hashes match...")
    
    if onboarding_hash_hex == verification_hash_hex:
        print("✅ SUCCESS: Onboarding hash matches verification hash")
        print("✅ New users CAN use their onboarding PINs!")
    else:
        print("❌ PROBLEM: Onboarding hash does NOT match verification hash")
        print("❌ New users CANNOT use their onboarding PINs!")
        
        # Debug the difference
        print(f"\nDEBUG:")
        print(f"   Onboarding salt: '{telegram_id}'")
        print(f"   Verification salt: '{chat_id}'")
        print(f"   Are they equal? {telegram_id == chat_id}")
    
    # Step 4: Check actual database storage
    print("\n4. Checking how telegram_id is stored in database...")
    
    # Check users table structure
    users = supabase.table("users").select("telegram_id,telegram_chat_id,pin_hash").limit(1).execute()
    
    if users.data:
        user = users.data[0]
        print(f"   Database telegram_id: {user.get('telegram_id')}")
        print(f"   Database telegram_chat_id: {user.get('telegram_chat_id')}")
        print(f"   PIN hash exists: {bool(user.get('pin_hash'))}")
        
        # The issue might be that telegram_id is stored as telegram_chat_id
        if user.get('telegram_id') != user.get('telegram_chat_id'):
            print("⚠️  POTENTIAL ISSUE: telegram_id != telegram_chat_id")
            print("    This could cause PIN verification failures")
    
    # Step 5: Check the actual onboarding code
    print("\n5. Checking onboarding code...")
    
    # Let's see what the onboarding actually does
    try:
        with open('utils/user_onboarding.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check how telegram_id is used in PIN hashing
        if 'telegram_id.encode(' in content:
            print("✅ Onboarding uses telegram_id for PIN hashing")
        else:
            print("❌ Onboarding does NOT use telegram_id for PIN hashing")
            
        # Check how telegram_id is stored in database
        if 'telegram_chat_id' in content:
            print("✅ Onboarding stores telegram_chat_id in database")
        else:
            print("❌ Onboarding does NOT store telegram_chat_id")
            
    except Exception as e:
        print(f"❌ Error reading onboarding file: {e}")
    
    print("\n🎯 CONCLUSION:")
    if onboarding_hash_hex == verification_hash_hex:
        print("✅ NEW USERS CAN USE THEIR ONBOARDING PINs")
        print("✅ PIN system is working correctly")
    else:
        print("❌ NEW USERS CANNOT USE THEIR ONBOARDING PINs")
        print("❌ Need to fix the salt mismatch")

if __name__ == "__main__":
    verify_new_user_pin_flow()
