#!/usr/bin/env python3
"""
Test the updated Bitnob wallet creation function
"""

import sys
sys.path.append('.')

from crypto.wallet import create_bitnob_wallet
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_wallet_creation():
    """Test wallet creation with updated endpoints"""
    
    print("🧪 Testing Bitnob wallet creation...")
    
    # Test wallet creation
    result = create_bitnob_wallet("test_user_123", "test@example.com")
    
    print(f"📊 Result: {result}")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Wallet creation successful!")
        
        # Check if it's a mock wallet
        wallet_data = result.get("data", result)
        if wallet_data.get("mock"):
            print("⚠️ Note: This is a mock wallet for development")
        
        # Show wallet details
        print(f"📝 Wallet ID: {wallet_data.get('id')}")
        print(f"📧 Email: {wallet_data.get('customerEmail')}")
        
        addresses = wallet_data.get('addresses', {})
        if addresses.get('BTC'):
            print(f"₿ BTC Address: {addresses['BTC']}")
        if addresses.get('USDT'):
            print(f"💰 USDT Address: {addresses['USDT']}")

if __name__ == "__main__":
    test_wallet_creation()
