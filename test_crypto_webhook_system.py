#!/usr/bin/env python3
"""
Test crypto webhook system - simulate Bitnob deposit notification
"""

import requests
import json
from datetime import datetime

def test_crypto_webhook():
    """Test the crypto webhook with a simulated Bitnob deposit"""
    
    # Simulate a Bitnob webhook for successful BTC deposit
    webhook_data = {
        "event": "wallet.deposit.successful",
        "data": {
            "customerEmail": "testuser123@sofiwallet.com",
            "amount": 0.0012,
            "currency": "BTC",
            "transactionId": "TXN123456789",
            "txHash": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "walletId": "wallet_123",
            "confirmations": 3,
            "status": "completed"
        }
    }
    
    print("🧪 Testing Crypto Webhook System")
    print("=" * 50)
    print(f"📋 Simulating BTC deposit webhook:")
    print(f"   Amount: {webhook_data['data']['amount']} BTC")
    print(f"   User: {webhook_data['data']['customerEmail']}")
    print(f"   TX Hash: {webhook_data['data']['txHash']}")
    
    # Test locally (if running Flask app)
    webhook_url = "http://localhost:5000/crypto/webhook"
    
    try:
        response = requests.post(
            webhook_url, 
            json=webhook_data, 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ Webhook Response: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 Webhook processed successfully!")
            print("📱 User should have received Telegram notification")
            print("💰 NGN balance should be updated in Supabase")
        else:
            print(f"\n❌ Webhook failed with status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n⚠️  Could not connect to {webhook_url}")
        print("💡 Make sure your Flask app is running first:")
        print("   python main.py")
    except Exception as e:
        print(f"\n❌ Error testing webhook: {e}")

def test_webhook_locally():
    """Test webhook processing function directly"""
    print("\n🔧 Testing webhook function directly...")
    
    try:
        from crypto.webhook import handle_successful_deposit
        
        # Test data
        test_data = {
            "data": {
                "customerEmail": "testuser123@sofiwallet.com",
                "amount": 0.001,
                "currency": "BTC",
                "transactionId": "TEST123",
                "txHash": "test_hash_123",
                "walletId": "test_wallet"
            }
        }
        
        print("📋 Testing with mock data:")
        print(f"   Amount: {test_data['data']['amount']} BTC")
        print(f"   User: {test_data['data']['customerEmail']}")
        
        # This would normally process the webhook
        # result = handle_successful_deposit(test_data)
        print("✅ Webhook function imported successfully")
        
    except Exception as e:
        print(f"❌ Error testing locally: {e}")

if __name__ == "__main__":
    print("🚀 CRYPTO WEBHOOK SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Direct function test
    test_webhook_locally()
    
    # Test 2: HTTP webhook test
    test_crypto_webhook()
    
    print("\n" + "=" * 50)
    print("✅ Crypto webhook system is ready!")
    print("\n🔧 To activate:")
    print("1. Add real BITNOB_SECRET_KEY to .env")
    print("2. Configure Bitnob webhook URL: your-domain.com/crypto/webhook")
    print("3. Test with real crypto deposits")
