#!/usr/bin/env python3
"""
Debug PIN and Bank Code Issues
==============================
Test PIN verification and bank code resolution
"""

import asyncio
import hashlib
import os
from supabase import create_client
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_pin_verification():
    """Debug PIN verification for a specific user"""
    print("🔍 Debugging PIN Verification...")
    
    # Test user - using the first user from the database
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        users_result = supabase.table("users").select("telegram_chat_id, full_name, pin_hash").order("created_at", desc=True).limit(1).execute()
        
        if not users_result.data:
            print("❌ No users found in database")
            return
        
        user = users_result.data[0]
        test_chat_id = user.get("telegram_chat_id")
        user_name = user.get("full_name", "Unknown")
        print(f"Testing with user: {user_name} ({test_chat_id})")
        
    except Exception as e:
        print(f"❌ Error getting test user: {str(e)}")
        return
    
    test_pin = "1998"  # Common test PIN - you may need to adjust this
    
    try:
        # Connect to Supabase
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # 1. Check if user exists
        print(f"\n1. Checking user existence for chat_id: {test_chat_id}")
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(test_chat_id)).execute()
        
        if not user_result.data:
            print("❌ User not found in database")
            return
        
        user_data = user_result.data[0]
        print(f"✅ User found: {user_data.get('name', 'Unknown')}")
        
        # 2. Check PIN hash
        stored_pin_hash = user_data.get("pin_hash")
        print(f"\n2. Stored PIN hash: {stored_pin_hash}")
        
        if not stored_pin_hash:
            print("❌ No PIN hash found in database")
            return
        
        # 3. Test PIN verification
        print(f"\n3. Testing PIN verification for PIN: {test_pin}")
        
        # Test both old SHA256 method and new pbkdf2_hmac method
        sha256_hash = hashlib.sha256(test_pin.encode()).hexdigest()
        print(f"SHA256 hash: {sha256_hash}")
        
        pbkdf2_hash = hashlib.pbkdf2_hmac('sha256', 
                                        test_pin.encode('utf-8'), 
                                        str(test_chat_id).encode('utf-8'), 
                                        100000)
        pbkdf2_hash_hex = pbkdf2_hash.hex()
        print(f"PBKDF2 hash: {pbkdf2_hash_hex}")
        
        if sha256_hash == stored_pin_hash:
            print("✅ PIN verification PASSED (SHA256 method)")
        elif pbkdf2_hash_hex == stored_pin_hash:
            print("✅ PIN verification PASSED (PBKDF2 method)")
        else:
            print("❌ PIN verification FAILED (both methods)")
            print("❓ Possible issues:")
            print("   - Wrong PIN being tested")
            print("   - PIN hash algorithm mismatch")
            print("   - PIN not set correctly during onboarding")
        
        # 4. Test with different PIN formats
        print(f"\n4. Testing different PIN formats:")
        pin_variants = [
            test_pin,
            test_pin.strip(),
            test_pin.encode().decode(),
            str(test_pin)
        ]
        
        for variant in pin_variants:
            # Test both hashing methods
            sha256_variant = hashlib.sha256(variant.encode()).hexdigest()
            pbkdf2_variant = hashlib.pbkdf2_hmac('sha256', 
                                               variant.encode('utf-8'), 
                                               str(test_chat_id).encode('utf-8'), 
                                               100000).hex()
            
            if sha256_variant == stored_pin_hash:
                print(f"✅ SHA256 match found with variant: '{variant}'")
            elif pbkdf2_variant == stored_pin_hash:
                print(f"✅ PBKDF2 match found with variant: '{variant}'")
            else:
                print(f"❌ No match for variant: '{variant}'")
    
    except Exception as e:
        print(f"❌ Error during PIN debug: {str(e)}")

async def debug_bank_codes():
    """Debug bank code resolution"""
    print("\n🏦 Debugging Bank Code Resolution...")
    
    test_cases = [
        {"bank_name": "opay", "expected_code": "999992"},
        {"bank_name": "Opay", "expected_code": "999992"},
        {"bank_name": "OPAY", "expected_code": "999992"},
        {"bank_name": "gtbank", "expected_code": "058"},
        {"bank_name": "access bank", "expected_code": "044"},
        {"bank_name": "zenith bank", "expected_code": "057"},
        {"bank_name": "palmpay", "expected_code": "999991"},
        {"bank_name": "kuda", "expected_code": "50211"},
    ]
    
    # Load bank codes from transfer_functions.py
    bank_name_to_code = {
        # Major Commercial Banks
        "access bank": "044",
        "access bank plc": "044",
        "access bank (diamond)": "063",
        "citibank": "023",
        "citibank nigeria": "023",
        "ecobank": "050",
        "ecobank nigeria": "050",
        "fidelity bank": "070",
        "fidelity bank plc": "070",
        "first bank": "011",
        "first bank of nigeria": "011",
        "first bank nigeria": "011",
        "fcmb": "214",
        "first city monument bank": "214",
        "gtbank": "058",
        "gtb": "058",
        "guaranty trust bank": "058",
        "heritage bank": "030",
        "heritage banking company": "030",
        "keystone bank": "082",
        "polaris bank": "076",
        "polaris bank limited": "076",
        "stanbic ibtc": "221",
        "stanbic ibtc bank": "221",
        "sterling bank": "232",
        "sterling bank plc": "232",
        "uba": "033",
        "united bank for africa": "033",
        "union bank": "032",
        "union bank of nigeria": "032",
        "unity bank": "215",
        "unity bank plc": "215",
        "wema bank": "035",
        "wema bank plc": "035",
        "alat by wema": "035A",
        "alat": "035A",
        "zenith bank": "057",
        "zenith bank plc": "057",
        
        # Digital/Fintech Banks
        "opay": "999992",
        "opay digital services": "999992",
        "moniepoint": "50515",
        "moniepoint mfb": "50515",
        "palmpay": "999991",
        "palmpay limited": "999991",
        "kuda": "50211",
        "kuda bank": "50211",
    }
    
    print("Testing bank code resolution...")
    for test_case in test_cases:
        bank_name = test_case["bank_name"]
        expected_code = test_case["expected_code"]
        
        # Test exact match
        resolved_code = bank_name_to_code.get(bank_name.lower())
        
        if resolved_code == expected_code:
            print(f"✅ {bank_name} -> {resolved_code}")
        else:
            print(f"❌ {bank_name} -> {resolved_code} (expected: {expected_code})")

async def check_user_data():
    """Check user data in database"""
    print("\n👤 Checking User Data...")
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get recent users
        users_result = supabase.table("users").select("telegram_chat_id, full_name, pin_hash, pin, has_pin").order("created_at", desc=True).limit(5).execute()
        
        print(f"Found {len(users_result.data)} recent users:")
        for user in users_result.data:
            chat_id = user.get("telegram_chat_id")
            name = user.get("full_name", "Unknown")
            has_pin_hash = "✅" if user.get("pin_hash") else "❌"
            has_pin_plain = "✅" if user.get("pin") else "❌"
            has_pin_flag = "✅" if user.get("has_pin") else "❌"
            print(f"  - {name} ({chat_id}): PIN_HASH {has_pin_hash}, PIN_PLAIN {has_pin_plain}, HAS_PIN {has_pin_flag}")
    
    except Exception as e:
        print(f"❌ Error checking user data: {str(e)}")

async def main():
    """Run all debug tests"""
    print("🔧 Starting Comprehensive Debug...")
    
    await debug_pin_verification()
    await debug_bank_codes()
    await check_user_data()
    
    print("\n✅ Debug completed!")

if __name__ == "__main__":
    asyncio.run(main())
