#!/usr/bin/env python3
"""
Quick import test for crypto integration
"""

print("🔍 Testing imports...")

try:
    from main import show_funding_account_details, get_user_balance, check_insufficient_balance
    print("✅ Main funding functions imported successfully")
except ImportError as e:
    print(f"❌ Failed to import main functions: {e}")

try:
    from crypto.wallet import create_crypto_wallet, get_user_wallets
    print("✅ Crypto wallet functions imported successfully")
except ImportError as e:
    print(f"❌ Failed to import crypto wallet functions: {e}")

try:
    from crypto.rates import get_crypto_rates
    print("✅ Crypto rates function imported successfully")
except ImportError as e:
    print(f"❌ Failed to import crypto rates function: {e}")

try:
    import asyncio
    print("✅ Asyncio imported successfully")
except ImportError as e:
    print(f"❌ Failed to import asyncio: {e}")

print("\n🎯 Import test completed!")
