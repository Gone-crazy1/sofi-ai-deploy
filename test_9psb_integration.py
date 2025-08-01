# 9PSB WAAS API Test Suite - Complete Integration Testing
# Run this script to test all integrated endpoints

import os
import json
import requests
from utils.ninepsb_api import NINEPSBApi
from utils.waas_auth import get_access_token
from dotenv import load_dotenv

load_dotenv()

def test_authentication():
    """Test 9PSB authentication"""
    print("🔐 Testing 9PSB Authentication...")
    token = get_access_token()
    if token:
        print(f"✅ Authentication successful! Token: {token[:20]}...")
        return True
    else:
        print("❌ Authentication failed!")
        return False

def test_create_virtual_account():
    """Test virtual account creation"""
    print("\n🏦 Testing Virtual Account Creation...")
    
    api = NINEPSBApi(
        api_key=os.getenv("NINEPSB_API_KEY"),
        secret_key=os.getenv("NINEPSB_SECRET_KEY"),
        base_url=os.getenv("NINEPSB_BASE_URL")
    )
    
    test_user_data = {
        "firstName": "Janet",
        "lastName": "Chinedu", 
        "otherNames": "Grace",
        "email": "janet.chinedu@example.com",
        "phoneNo": "08012345678",
        "gender": 2,  # Female
        "dateOfBirth": "15/08/1995",
        "bvn": "22190239861",
        "password": "Sofi@1234"
    }
    
    result = api.create_virtual_account("test_user_001", test_user_data)
    print(f"📊 Result: {json.dumps(result, indent=2)}")
    
    if result.get("error"):
        print("❌ Virtual account creation failed")
        return False, None
    else:
        print("✅ Virtual account creation successful!")
        return True, result

def test_upgrade_wallet(user_id, tier=2):
    """Test wallet upgrade to higher tier"""
    print(f"\n🆙 Testing Wallet Upgrade for {user_id} to Tier {tier}...")
    
    api = NINEPSBApi(
        api_key=os.getenv("NINEPSB_API_KEY"),
        secret_key=os.getenv("NINEPSB_SECRET_KEY"),
        base_url=os.getenv("NINEPSB_BASE_URL")
    )
    
    result = api.upgrade_wallet(user_id, tier)
    print(f"📊 Result: {json.dumps(result, indent=2)}")
    
    if result.get("error"):
        print("❌ Wallet upgrade failed")
        return False
    else:
        print("✅ Wallet upgrade successful!")
        return True

def test_webhook_endpoint():
    """Test webhook endpoint is working"""
    print("\n🔔 Testing Webhook Endpoint...")
    
    try:
        # Test GET request to webhook test endpoint
        response = requests.get("http://localhost:5000/webhook/9psb/test", timeout=10)
        print(f"📊 GET Test: {response.status_code} - {response.json()}")
        
        # Test POST request with sample webhook data
        test_webhook_data = {
            "eventType": "wallet.created",
            "data": {
                "userId": "test_webhook_user",
                "accountNumber": "9876543210",
                "accountName": "TEST WEBHOOK USER",
                "bankName": "9PSB",
                "walletId": "webhook_wallet_123"
            }
        }
        
        response = requests.post("http://localhost:5000/webhook/9psb/test", json=test_webhook_data, timeout=10)
        print(f"📊 POST Test: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint working!")
            return True
        else:
            print("❌ Webhook endpoint failed!")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        print("💡 Make sure Flask app is running: python main.py")
        return False

def run_basic_tests():
    """Run essential tests for 9PSB integration"""
    print("🚀 Starting 9PSB WAAS API Basic Test Suite")
    print("=" * 50)
    
    results = []
    
    # 1. Test Authentication
    print("\n1️⃣ AUTHENTICATION TEST")
    auth_success = test_authentication()
    results.append(("Authentication", auth_success))
    
    if not auth_success:
        print("❌ Cannot proceed without authentication!")
        print("\n💡 Check your .env file and credentials")
        return
    
    # 2. Test Virtual Account Creation
    print("\n2️⃣ VIRTUAL ACCOUNT CREATION TEST")
    account_success, account_data = test_create_virtual_account()
    results.append(("Virtual Account Creation", account_success))
    
    # 3. Test Wallet Upgrade
    print("\n3️⃣ WALLET UPGRADE TEST")
    test_user_id = "test_user_001"
    if account_data and not account_data.get("error"):
        test_user_id = account_data.get("userId") or test_user_id
    
    upgrade_success = test_upgrade_wallet(test_user_id, 2)
    results.append(("Wallet Upgrade", upgrade_success))
    
    # 4. Test Webhook Endpoint
    print("\n4️⃣ WEBHOOK ENDPOINT TEST")
    webhook_success = test_webhook_endpoint()
    results.append(("Webhook Endpoint", webhook_success))
    
    # Print Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print("=" * 50)
    print(f"📈 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All basic tests passed! 9PSB integration is working!")
        print("\n📋 NEXT STEPS:")
        print("- ✅ Authentication working")
        print("- ✅ Virtual account creation working") 
        print("- ✅ Wallet upgrade working")
        print("- ✅ Webhook endpoint ready")
        print("\n🚀 Ready for production use!")
    else:
        print(f"⚠️ {total-passed} tests failed. Check the logs above.")
        print("\n🔧 TROUBLESHOOTING:")
        if not results[0][1]:  # Auth failed
            print("- Check NINEPSB_BASE_URL in .env")
            print("- Verify credentials are correct")
        if not results[3][1]:  # Webhook failed
            print("- Make sure Flask app is running")
            print("- Check port 5000 is available")

if __name__ == "__main__":
    run_basic_tests()
