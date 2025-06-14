#!/usr/bin/env python3
"""
Debug Bitcoin wallet address issue with Bitnob API
"""

import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append('.')

load_dotenv()

def test_bitnob_wallet_response():
    """Test actual Bitnob API to see wallet address format"""
    
    api_key = os.getenv("BITNOB_SECRET_KEY")
    if not api_key:
        print("❌ BITNOB_SECRET_KEY not found")
        return
    
    print("🔍 DEBUGGING BITNOB WALLET ADDRESS ISSUE")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test data
    timestamp = int(datetime.now().timestamp())
    test_data = {
        "customerEmail": f"debug{timestamp}@sofiwallet.com",
        "label": f"Debug Wallet {timestamp}",
        "currency": "NGN"
    }
    
    # Try the main Bitnob endpoints
    endpoints = [
        "https://api.bitnob.co/api/v1/wallets",
        "https://api.bitnob.co/api/v1/customers/wallets",
        "https://api.bitnob.co/api/v1/customers"
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing endpoint: {endpoint}")
        try:
            response = requests.post(endpoint, headers=headers, json=test_data, timeout=15)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}")
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    print("✅ SUCCESS! Analyzing wallet data...")
                    
                    # Look for wallet addresses in response
                    def find_addresses(obj, path=""):
                        addresses = {}
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                current_path = f"{path}.{key}" if path else key
                                if isinstance(value, str) and len(value) > 20:
                                    # Check if it looks like a crypto address
                                    if (value.startswith('bc1') or 
                                        value.startswith('1') or 
                                        value.startswith('3') or 
                                        value.startswith('0x')):
                                        addresses[current_path] = value
                                elif isinstance(value, (dict, list)):
                                    addresses.update(find_addresses(value, current_path))
                        elif isinstance(obj, list):
                            for i, item in enumerate(obj):
                                addresses.update(find_addresses(item, f"{path}[{i}]"))
                        return addresses
                    
                    found_addresses = find_addresses(data)
                    
                    if found_addresses:
                        print("🔍 FOUND ADDRESSES:")
                        for path, address in found_addresses.items():
                            print(f"   {path}: {address} (Length: {len(address)})")
                            
                            # Analyze Bitcoin addresses
                            if address.startswith('bc1'):
                                if len(address) < 42:
                                    print(f"   ⚠️  WARNING: Bitcoin address too short! Should be 42+ chars")
                                else:
                                    print(f"   ✅ Valid Bitcoin Segwit address length")
                    else:
                        print("   ❌ No crypto addresses found in response")
                        
                except json.JSONDecodeError:
                    print("   ⚠️ Response is not valid JSON")
                    
            elif response.status_code == 400:
                if "already" in response.text.lower():
                    print("   ✅ Endpoint works (customer already exists)")
                else:
                    print(f"   ❌ Bad Request: {response.text}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_mock_wallet_fix():
    """Test the fixed mock wallet generator"""
    
    print("\n🛠️  TESTING FIXED MOCK WALLET GENERATOR")
    print("=" * 45)
    
    try:
        from crypto.wallet import create_mock_wallet
        
        result = create_mock_wallet("debug_user", "debug@test.com")
        
        if result and result.get("data"):
            wallet_data = result["data"]
            addresses = wallet_data.get("addresses", {})
            
            print("✅ Mock wallet created successfully!")
            print(f"📧 Email: {wallet_data.get('customerEmail')}")
            
            for crypto, address in addresses.items():
                print(f"{crypto}: {address} (Length: {len(address)})")
                
                # Validate address format
                if crypto == "BTC":
                    if address.startswith("bc1q") and len(address) == 42:
                        print(f"   ✅ Valid Bitcoin Segwit address format")
                    else:
                        print(f"   ❌ Invalid Bitcoin address format")
                        
                elif crypto == "USDT":
                    if address.startswith("0x") and len(address) == 42:
                        print(f"   ✅ Valid Ethereum address format")
                    else:
                        print(f"   ❌ Invalid Ethereum address format")
        else:
            print("❌ Failed to create mock wallet")
            
    except Exception as e:
        print(f"❌ Error testing mock wallet: {e}")

def check_database_addresses():
    """Check if there are truncated addresses in the database"""
    
    print("\n🗄️  CHECKING DATABASE FOR INCOMPLETE ADDRESSES")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found")
            return
            
        supabase = create_client(supabase_url, supabase_key)
        
        # Check crypto_wallets table
        try:
            result = supabase.table("crypto_wallets").select("*").execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} wallet records")
                
                for wallet in result.data:
                    user_id = wallet.get("user_id")
                    btc_address = wallet.get("btc_address")
                    usdt_address = wallet.get("usdt_address")
                    
                    print(f"\n👤 User: {user_id}")
                    
                    if btc_address:
                        print(f"   BTC: {btc_address} (Length: {len(btc_address)})")
                        if len(btc_address) < 42 and btc_address.startswith('bc1'):
                            print(f"   ⚠️  WARNING: Incomplete Bitcoin address!")
                            
                    if usdt_address:
                        print(f"   USDT: {usdt_address} (Length: {len(usdt_address)})")
                        if len(usdt_address) < 42 and usdt_address.startswith('0x'):
                            print(f"   ⚠️  WARNING: Incomplete USDT address!")
            else:
                print("📝 No wallet records found in database")
                
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def main():
    """Run all debugging tests"""
    
    print("🐛 BITCOIN WALLET ADDRESS DEBUGGING")
    print("=" * 60)
    print("Investigating the incomplete address issue:")
    print("Expected: bc1q... (42 characters)")
    print("Your issue: bc1q2759a802930c4bd4a37cd4e445869f2b (35 characters)")
    print()
    
    # Test 1: Check actual Bitnob API
    test_bitnob_wallet_response()
    
    # Test 2: Test fixed mock wallet
    test_mock_wallet_fix()
    
    # Test 3: Check database for incomplete addresses
    check_database_addresses()
    
    print("\n🎯 SUMMARY & RECOMMENDATIONS:")
    print("=" * 35)
    print("1. Fixed mock wallet generator to create proper 42-char Bitcoin addresses")
    print("2. Check if issue is from Bitnob API or display truncation")
    print("3. If using mock wallets, they now generate correct addresses")
    print("4. For production, ensure Bitnob API returns complete addresses")

if __name__ == "__main__":
    main()
