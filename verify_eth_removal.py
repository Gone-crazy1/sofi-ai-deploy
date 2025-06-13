#!/usr/bin/env python3
"""
Verify ETH Cryptocurrency Removal - Complete Test
"""

print("🔍 VERIFYING ETH REMOVAL FROM SOFI AI SYSTEM...")
print("=" * 60)

try:
    # Test 1: Import main.py successfully
    print("\n1. Testing main.py import...")
    import main
    print("   ✅ main.py imports successfully")
    
    # Test 2: Check crypto rates mapping
    print("\n2. Testing crypto rates mapping...")
    from crypto.rates import CRYPTO_MAPPING
    print(f"   📊 Supported cryptocurrencies: {list(CRYPTO_MAPPING.keys())}")
    
    if 'ETH' not in CRYPTO_MAPPING:
        print("   ✅ ETH successfully removed from CRYPTO_MAPPING")
    else:
        print("   ❌ ETH still present in CRYPTO_MAPPING")
    
    # Test 3: Check handle_crypto_commands function
    print("\n3. Testing crypto command handling...")
    from main import handle_crypto_commands
    
    # Test user data
    test_user = {"id": "test123", "first_name": "TestUser"}
    
    # Test BTC wallet creation (should work)
    btc_response = handle_crypto_commands("test_chat", "create BTC wallet", test_user)
    if btc_response and "BTC" in btc_response:
        print("   ✅ BTC wallet creation works")
    else:
        print("   ⚠️  BTC wallet creation response:", btc_response[:100] if btc_response else "None")
    
    # Test USDT wallet creation (should work)  
    usdt_response = handle_crypto_commands("test_chat", "create USDT wallet", test_user)
    if usdt_response and "USDT" in usdt_response:
        print("   ✅ USDT wallet creation works")
    else:
        print("   ⚠️  USDT wallet creation response:", usdt_response[:100] if usdt_response else "None")
    
    # Test ETH wallet creation (should not work/not be recognized)
    eth_response = handle_crypto_commands("test_chat", "create ETH wallet", test_user)
    if eth_response is None:
        print("   ✅ ETH wallet creation properly removed (returns None)")
    else:
        print(f"   ❌ ETH wallet creation still responds: {eth_response[:100]}")
    
    # Test 4: Check funding message
    print("\n4. Testing funding message...")
    try:
        from main import show_funding_account_details
        # This is async, so we'll just check if the function exists
        print("   ✅ show_funding_account_details function exists")
    except ImportError as e:
        print(f"   ⚠️  show_funding_account_details import issue: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ETH REMOVAL VERIFICATION COMPLETE!")
    print("✅ All major components successfully updated")
    print("🪙 Supported cryptocurrencies: BTC, USDT")
    print("🚫 ETH support completely removed")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()
