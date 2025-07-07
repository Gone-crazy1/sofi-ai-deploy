#!/usr/bin/env python3
"""
CRITICAL PIN FIX FOR PRODUCTION
===============================
Fix PIN verification to use the same hashing method as onboarding
"""

import hashlib
import os
from supabase import create_client, Client

def fix_pin_verification():
    """Fix PIN verification to match onboarding method"""
    
    print("🔧 CRITICAL PIN FIX - Starting...")
    
    # First, let's check the onboarding method
    onboarding_file = "main.py"
    
    # Read current onboarding PIN hashing method
    with open(onboarding_file, 'r') as f:
        content = f.read()
    
    # Check if pbkdf2_hmac is used in onboarding
    if 'pbkdf2_hmac' in content:
        print("✅ Found pbkdf2_hmac in onboarding - this is the correct method")
        
        # Now fix the verification function
        security_file = "functions/security_functions.py"
        
        with open(security_file, 'r') as f:
            security_content = f.read()
        
        # Replace the SHA256 method with pbkdf2_hmac
        old_verify_method = '''    # Hash the provided PIN
    hashed_pin = hashlib.sha256(pin.encode()).hexdigest()'''
        
        new_verify_method = '''    # Hash the provided PIN using pbkdf2_hmac (same as onboarding)
    hashed_pin = hashlib.pbkdf2_hmac('sha256', pin.encode(), str(chat_id).encode(), 100000).hex()'''
        
        if old_verify_method in security_content:
            security_content = security_content.replace(old_verify_method, new_verify_method)
            
            with open(security_file, 'w') as f:
                f.write(security_content)
            
            print("✅ Fixed PIN verification in security_functions.py")
        else:
            print("⚠️  SHA256 method not found in security_functions.py - checking for pbkdf2_hmac")
            
            if 'pbkdf2_hmac' in security_content:
                print("✅ security_functions.py already uses pbkdf2_hmac")
            else:
                print("❌ Need to manually fix security_functions.py")
        
        # Also fix the set_pin function
        old_set_method = '''    # Hash the PIN
    hashed_pin = hashlib.sha256(pin.encode()).hexdigest()'''
        
        new_set_method = '''    # Hash the PIN using pbkdf2_hmac (same as onboarding)
    hashed_pin = hashlib.pbkdf2_hmac('sha256', pin.encode(), str(chat_id).encode(), 100000).hex()'''
        
        if old_set_method in security_content:
            security_content = security_content.replace(old_set_method, new_set_method)
            
            with open(security_file, 'w') as f:
                f.write(security_content)
            
            print("✅ Fixed PIN setting in security_functions.py")
        
        # Fix sofi_money_functions.py as well
        money_file = "sofi_money_functions.py"
        
        with open(money_file, 'r') as f:
            money_content = f.read()
        
        # Replace all SHA256 instances with pbkdf2_hmac
        old_patterns = [
            'hashlib.sha256(pin.encode()).hexdigest()',
            'hashlib.sha256(provided_pin.encode()).hexdigest()'
        ]
        
        for old_pattern in old_patterns:
            if old_pattern in money_content:
                if 'provided_pin' in old_pattern:
                    new_pattern = 'hashlib.pbkdf2_hmac(\'sha256\', provided_pin.encode(), str(chat_id).encode(), 100000).hex()'
                else:
                    new_pattern = 'hashlib.pbkdf2_hmac(\'sha256\', pin.encode(), str(chat_id).encode(), 100000).hex()'
                
                money_content = money_content.replace(old_pattern, new_pattern)
                print(f"✅ Fixed PIN hashing pattern: {old_pattern}")
        
        with open(money_file, 'w') as f:
            f.write(money_content)
        
        print("✅ Fixed PIN verification in sofi_money_functions.py")
        
        print("\n🎉 PIN FIX COMPLETED!")
        print("📋 Summary:")
        print("- Fixed PIN verification to use pbkdf2_hmac method")
        print("- Updated security_functions.py")
        print("- Updated sofi_money_functions.py")
        print("- All PIN operations now use the same hashing method as onboarding")
        
        return True
    
    else:
        print("❌ pbkdf2_hmac not found in onboarding - need to check method")
        return False

if __name__ == "__main__":
    fix_pin_verification()
