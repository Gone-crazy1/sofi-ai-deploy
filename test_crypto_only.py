#!/usr/bin/env python3
"""
Test crypto modules directly without importing main.py
"""

print("🔍 Testing crypto modules directly...")

try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from crypto.wallet import create_bitnob_wallet, get_user_wallet_addresses
    print("✅ Crypto wallet module imported successfully")
    
    from crypto.rates import get_crypto_to_ngn_rate, get_multiple_crypto_rates
    print("✅ Crypto rates module imported successfully")
    
    from crypto.webhook import handle_crypto_webhook
    print("✅ Crypto webhook module imported successfully")
    
    print("\n🎯 All crypto modules imported successfully!")
    
    # Test a simple function call
    rates = get_multiple_crypto_rates()
    if rates:
        print(f"✅ Crypto rates fetched: {len(rates)} currencies")
    else:
        print("⚠️ No crypto rates returned (might be API issue)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
