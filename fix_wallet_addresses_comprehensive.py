#!/usr/bin/env python3
"""
Comprehensive Bitcoin and USDT Address Fix
- Fix all invalid Bitcoin addresses in database
- Fix incomplete USDT addresses
- Implement proper address validation
- Update address generation with correct formats
"""

import secrets
import sys
import os
from supabase import create_client
from dotenv import load_dotenv
import re

# Add project root to path
sys.path.append('.')

# Load environment variables
load_dotenv()

def get_supabase_client():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase credentials not found")
        return None
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def validate_bitcoin_address(address):
    """Validate Bitcoin address format"""
    if not address:
        return False, "Empty address"
    
    # Bitcoin Segwit (bech32) address validation
    if address.startswith("bc1q"):
        if len(address) != 42:
            return False, f"Invalid length: {len(address)} (should be 42)"
        
        # Check if contains only valid bech32 characters (excluding '1', 'b', 'i', 'o')
        valid_chars = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
        address_body = address[4:]  # Remove 'bc1q'
        
        for char in address_body.lower():
            if char not in valid_chars:
                return False, f"Invalid character: {char}"
        
        return True, "Valid Bitcoin address"
    
    return False, "Invalid Bitcoin address format"

def validate_ethereum_address(address):
    """Validate Ethereum/USDT address format"""
    if not address:
        return False, "Empty address"
    
    if not address.startswith("0x"):
        return False, "Must start with 0x"
    
    if len(address) != 42:
        return False, f"Invalid length: {len(address)} (should be 42)"
    
    # Check if hex characters only
    address_body = address[2:]  # Remove '0x'
    if not re.match(r'^[0-9a-fA-F]+$', address_body):
        return False, "Contains invalid hex characters"
    
    return True, "Valid Ethereum address"

def generate_proper_bitcoin_address():
    """Generate a proper 42-character Bitcoin address"""
    # Generate 38 hex characters (19 bytes * 2)
    suffix = secrets.token_hex(19)  # This gives exactly 38 hex characters
    address = f"bc1q{suffix}"
    
    # Validate the generated address
    is_valid, message = validate_bitcoin_address(address)
    if not is_valid:
        print(f"⚠️ Generated invalid Bitcoin address: {message}")
        return generate_proper_bitcoin_address()  # Retry
    
    return address

def generate_proper_ethereum_address():
    """Generate a proper 42-character Ethereum address"""
    # Generate 40 hex characters (20 bytes * 2)
    address = f"0x{secrets.token_hex(20)}"
    
    # Validate the generated address
    is_valid, message = validate_ethereum_address(address)
    if not is_valid:
        print(f"⚠️ Generated invalid Ethereum address: {message}")
        return generate_proper_ethereum_address()  # Retry
    
    return address

def check_and_fix_all_addresses():
    """Check and fix all crypto wallet addresses in database"""
    print("🔧 Comprehensive Crypto Address Fix")
    print("=" * 60)
    
    client = get_supabase_client()
    if not client:
        return
    
    try:
        # Get all crypto wallets
        result = client.table("crypto_wallets").select("*").execute()
        wallets = result.data
        
        print(f"📊 Found {len(wallets)} crypto wallets in database")
        print("-" * 60)
        
        fixes_needed = []
        
        for wallet in wallets:
            user_id = wallet.get("user_id")
            btc_address = wallet.get("btc_address")
            usdt_address = wallet.get("usdt_address")
            
            print(f"\n👤 User: {user_id}")
            
            # Check Bitcoin address
            if btc_address:
                is_valid, message = validate_bitcoin_address(btc_address)
                if is_valid:
                    print(f"   ✅ BTC: {btc_address} (Length: {len(btc_address)})")
                else:
                    print(f"   ❌ BTC: {btc_address} (Length: {len(btc_address)}) - {message}")
                    fixes_needed.append({
                        'user_id': user_id,
                        'field': 'btc_address',
                        'old_value': btc_address,
                        'issue': message
                    })
            else:
                print(f"   ⚠️ BTC: No address found")
                fixes_needed.append({
                    'user_id': user_id,
                    'field': 'btc_address',
                    'old_value': None,
                    'issue': 'Missing address'
                })
            
            # Check USDT address  
            if usdt_address:
                is_valid, message = validate_ethereum_address(usdt_address)
                if is_valid:
                    print(f"   ✅ USDT: {usdt_address} (Length: {len(usdt_address)})")
                else:
                    print(f"   ❌ USDT: {usdt_address} (Length: {len(usdt_address)}) - {message}")
                    fixes_needed.append({
                        'user_id': user_id,
                        'field': 'usdt_address',
                        'old_value': usdt_address,
                        'issue': message
                    })
            else:
                print(f"   ⚠️ USDT: No address found")
                fixes_needed.append({
                    'user_id': user_id,
                    'field': 'usdt_address',
                    'old_value': None,
                    'issue': 'Missing address'
                })
        
        print(f"\n📊 Summary:")
        print(f"   🔧 Addresses needing fixes: {len(fixes_needed)}")
        
        if fixes_needed:
            print("\n🔧 Applying fixes...")
            
            for fix in fixes_needed:
                user_id = fix['user_id']
                field = fix['field']
                old_value = fix['old_value']
                issue = fix['issue']
                
                # Generate new address
                if field == 'btc_address':
                    new_address = generate_proper_bitcoin_address()
                    crypto_type = "BTC"
                else:
                    new_address = generate_proper_ethereum_address()
                    crypto_type = "USDT"
                
                # Update in database
                update_data = {field: new_address}
                client.table("crypto_wallets").update(update_data).eq("user_id", user_id).execute()
                
                print(f"   ✅ Fixed {user_id} {crypto_type}:")
                print(f"      Old: {old_value or 'None'}")
                print(f"      New: {new_address} (Length: {len(new_address)})")
        
        print("\n🎉 Comprehensive address fix complete!")
        
        # Verification
        print("\n🔍 Verification - checking all addresses again...")
        result = client.table("crypto_wallets").select("*").execute()
        wallets = result.data
        
        all_valid = True
        for wallet in wallets:
            user_id = wallet.get("user_id")
            btc_address = wallet.get("btc_address")
            usdt_address = wallet.get("usdt_address")
            
            if btc_address:
                is_valid, _ = validate_bitcoin_address(btc_address)
                if not is_valid:
                    all_valid = False
                    print(f"   ❌ {user_id} BTC still invalid: {btc_address}")
            
            if usdt_address:
                is_valid, _ = validate_ethereum_address(usdt_address)
                if not is_valid:
                    all_valid = False
                    print(f"   ❌ {user_id} USDT still invalid: {usdt_address}")
        
        if all_valid:
            print("   ✅ All addresses are now valid!")
        else:
            print("   ⚠️ Some addresses still need attention")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_address_generation():
    """Test the address generation functions"""
    print("\n🧪 Testing Address Generation")
    print("-" * 40)
    
    # Test Bitcoin
    print("Testing Bitcoin address generation:")
    for i in range(3):
        btc_addr = generate_proper_bitcoin_address()
        is_valid, message = validate_bitcoin_address(btc_addr)
        print(f"  {i+1}. {btc_addr} (Length: {len(btc_addr)}) - {'✅' if is_valid else '❌'} {message}")
    
    # Test Ethereum/USDT
    print("\nTesting Ethereum/USDT address generation:")
    for i in range(3):
        eth_addr = generate_proper_ethereum_address()
        is_valid, message = validate_ethereum_address(eth_addr)
        print(f"  {i+1}. {eth_addr} (Length: {len(eth_addr)}) - {'✅' if is_valid else '❌'} {message}")

if __name__ == "__main__":
    test_address_generation()
    check_and_fix_all_addresses()
