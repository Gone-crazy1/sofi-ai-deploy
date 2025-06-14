#!/usr/bin/env python3
"""
Check existing Bitcoin addresses in the database to identify incomplete ones
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

def check_bitcoin_addresses():
    """Check all Bitcoin addresses in the database"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all crypto wallets
        result = supabase.table("crypto_wallets").select("*").execute()
        
        print("🔍 Checking Bitcoin addresses in database:")
        print("-" * 50)
        
        if not result.data:
            print("No crypto wallets found in database")
            return
        
        incomplete_addresses = []
        proper_addresses = []
        
        for wallet in result.data:
            btc_address = wallet.get("btc_address")
            user_id = wallet.get("user_id")
            
            if btc_address:
                if btc_address.startswith("bc1q"):
                    address_length = len(btc_address)
                    if address_length == 42:
                        proper_addresses.append({
                            "user_id": user_id,
                            "address": btc_address,
                            "length": address_length
                        })
                        print(f"✅ User {user_id}: {btc_address} (Length: {address_length})")
                    else:
                        incomplete_addresses.append({
                            "user_id": user_id,
                            "address": btc_address,
                            "length": address_length
                        })
                        print(f"❌ User {user_id}: {btc_address} (Length: {address_length}) - INCOMPLETE")
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Proper addresses (42 chars): {len(proper_addresses)}")
        print(f"   ❌ Incomplete addresses: {len(incomplete_addresses)}")
        
        if incomplete_addresses:
            print(f"\n⚠️  Found {len(incomplete_addresses)} incomplete Bitcoin addresses that need to be fixed!")
            return incomplete_addresses
        else:
            print(f"\n🎉 All Bitcoin addresses are properly formatted!")
            return []
            
    except Exception as e:
        print(f"❌ Error checking addresses: {str(e)}")
        return []

def fix_incomplete_addresses(incomplete_addresses):
    """Fix incomplete Bitcoin addresses by generating new ones"""
    if not incomplete_addresses:
        print("No incomplete addresses to fix")
        return
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print(f"\n🔧 Fixing {len(incomplete_addresses)} incomplete addresses...")
        
        import secrets
        
        for address_info in incomplete_addresses:
            user_id = address_info["user_id"]
            old_address = address_info["address"]
            
            # Generate new proper Bitcoin address
            btc_suffix = secrets.token_hex(19)  # 38 hex characters
            new_btc_address = f"bc1q{btc_suffix}"
            
            # Update the address in database
            update_result = supabase.table("crypto_wallets").update({
                "btc_address": new_btc_address
            }).eq("user_id", user_id).execute()
            
            if update_result.data:
                print(f"✅ Fixed user {user_id}:")
                print(f"   Old: {old_address} ({len(old_address)} chars)")
                print(f"   New: {new_btc_address} ({len(new_btc_address)} chars)")
            else:
                print(f"❌ Failed to update address for user {user_id}")
        
        print(f"\n🎉 Address fixing complete!")
        
    except Exception as e:
        print(f"❌ Error fixing addresses: {str(e)}")

if __name__ == "__main__":
    print("🧪 Bitcoin Address Database Check")
    print("=" * 50)
    
    incomplete = check_bitcoin_addresses()
    
    if incomplete:
        print(f"\n" + "=" * 50)
        response = input("Would you like to fix these incomplete addresses? (y/n): ")
        if response.lower() == 'y':
            fix_incomplete_addresses(incomplete)
        else:
            print("Address fixing skipped.")
    
    print(f"\n✅ Check complete!")
