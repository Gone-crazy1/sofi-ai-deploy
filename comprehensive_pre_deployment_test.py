#!/usr/bin/env python3
"""
COMPREHENSIVE SOFI AI PRE-RENDER DEPLOYMENT TEST
Tests ALL real features including REAL crypto before production deployment
"""

import asyncio
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SofiPreDeploymentTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"  # Local test before Render
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.test_chat_id = "test_deployment_123456"
        self.passed_tests = []
        self.failed_tests = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        if passed:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name} - PASSED")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name} - FAILED: {details}")
        if details:
            print(f"   📝 Details: {details}")
    
    def test_environment_variables(self):
        """Test A: Environment Variables"""
        print("\n🔧 A. ENVIRONMENT VARIABLES TEST")
        print("=" * 50)
        
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_SERVICE_ROLE_KEY',
            'OPENAI_API_KEY',
            'TELEGRAM_BOT_TOKEN',
            'MONNIFY_API_KEY',
            'MONNIFY_SECRET_KEY',
            'BITNOB_API_KEY'  # Real crypto
        ]
        
        missing = []
        for var in required_vars:
            if os.getenv(var):
                print(f"   ✅ {var}")
            else:
                print(f"   ❌ {var} - MISSING")
                missing.append(var)
        
        passed = len(missing) == 0
        self.log_test("Environment Variables", passed, 
                     f"Missing: {missing}" if missing else "All variables present")
        return passed
    
    def test_database_connection(self):
        """Test B: Database Connection"""
        print("\n🗄️ B. DATABASE CONNECTION TEST")
        print("=" * 50)
        
        try:
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                self.log_test("Database Connection", False, "Missing Supabase credentials")
                return False
            
            supabase = create_client(supabase_url, supabase_key)
            
            # Test core tables
            core_tables = ['users', 'bank_transactions', 'beneficiaries', 'crypto_transactions', 'crypto_rates']
            table_status = {}
            
            for table in core_tables:
                try:
                    result = supabase.table(table).select('*').limit(1).execute()
                    table_status[table] = True
                    print(f"   ✅ {table} table exists")
                except Exception as e:
                    table_status[table] = False
                    print(f"   ❌ {table} table missing: {str(e)}")
            
            passed = all(table_status.values())
            self.log_test("Database Connection", passed, 
                         f"Tables status: {table_status}")
            return passed
            
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False
    
    def test_flask_server(self):
        """Test C: Flask Server & Webhooks"""
        print("\n🌐 C. FLASK SERVER TEST")
        print("=" * 50)
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=5)
            health_ok = response.status_code == 200
            print(f"   {'✅' if health_ok else '❌'} Health endpoint: {response.status_code}")
            
            # Test webhook endpoint
            test_message = {
                "message": {
                    "chat": {"id": self.test_chat_id},
                    "from": {"id": self.test_chat_id, "first_name": "Test"},
                    "text": "Hello Sofi"
                }
            }
            
            webhook_response = requests.post(f"{self.base_url}/webhook", 
                                           json=test_message, timeout=10)
            webhook_ok = webhook_response.status_code == 200
            print(f"   {'✅' if webhook_ok else '❌'} Webhook endpoint: {webhook_response.status_code}")
            
            passed = health_ok and webhook_ok
            self.log_test("Flask Server", passed, 
                         f"Health: {response.status_code}, Webhook: {webhook_response.status_code}")
            return passed
            
        except Exception as e:
            self.log_test("Flask Server", False, str(e))
            return False
    
    def test_monnify_integration(self):
        """Test D: Monnify Integration (REAL)"""
        print("\n💳 D. MONNIFY INTEGRATION TEST")
        print("=" * 50)
        
        try:
            # Test Monnify API credentials
            api_key = os.getenv('MONNIFY_API_KEY')
            secret_key = os.getenv('MONNIFY_SECRET_KEY')
            
            if not api_key or not secret_key:
                self.log_test("Monnify Credentials", False, "Missing API keys")
                return False
            
            print(f"   ✅ Monnify API Key present")
            print(f"   ✅ Monnify Secret Key present")
            
            # Test virtual account creation endpoint
            try:
                create_account_data = {
                    "chat_id": self.test_chat_id,
                    "full_name": "Test User",
                    "phone_number": "08012345678"
                }
                
                response = requests.post(f"{self.base_url}/api/create_virtual_account", 
                                       json=create_account_data, timeout=15)
                
                account_creation_ok = response.status_code in [200, 201]
                print(f"   {'✅' if account_creation_ok else '❌'} Virtual account creation: {response.status_code}")
                
                if account_creation_ok:
                    try:
                        response_data = response.json()
                        has_account_number = 'accountNumber' in str(response_data) or 'account' in str(response_data)
                        print(f"   {'✅' if has_account_number else '❌'} Account number in response")
                    except:
                        print("   ⚠️ Could not parse account creation response")
                
            except Exception as e:
                print(f"   ❌ Virtual account creation failed: {str(e)}")
                account_creation_ok = False
            
            # Test webhook endpoint
            try:
                test_webhook_data = {
                    "eventType": "SUCCESSFUL_TRANSACTION",
                    "eventData": {
                        "transactionReference": "test_ref_123",
                        "amount": 1000.00,
                        "customerAccountNumber": "1234567890"
                    }
                }
                
                webhook_response = requests.post(f"{self.base_url}/monnify_webhook", 
                                               json=test_webhook_data, timeout=10)
                webhook_ok = webhook_response.status_code == 200
                print(f"   {'✅' if webhook_ok else '❌'} Monnify webhook: {webhook_response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Monnify webhook test failed: {str(e)}")
                webhook_ok = False
            
            passed = account_creation_ok and webhook_ok
            self.log_test("Monnify Integration", passed, 
                         f"Account creation: {account_creation_ok}, Webhook: {webhook_ok}")
            return passed
            
        except Exception as e:
            self.log_test("Monnify Integration", False, str(e))
            return False
    
    def test_crypto_integration(self):
        """Test E: Crypto Integration (REAL)"""
        print("\n₿ E. CRYPTO INTEGRATION TEST (REAL)")
        print("=" * 50)
        
        try:
            # Test Bitnob API credentials
            bitnob_key = os.getenv('BITNOB_API_KEY')
            
            if not bitnob_key:
                self.log_test("Crypto Credentials", False, "Missing Bitnob API key")
                return False
            
            print(f"   ✅ Bitnob API Key present")
            
            # Test crypto rates endpoint
            try:
                response = requests.get(f"{self.base_url}/api/crypto_rates", timeout=10)
                rates_ok = response.status_code == 200
                print(f"   {'✅' if rates_ok else '❌'} Crypto rates endpoint: {response.status_code}")
                
                if rates_ok:
                    try:
                        rates_data = response.json()
                        has_btc = 'bitcoin' in str(rates_data).lower() or 'btc' in str(rates_data).lower()
                        print(f"   {'✅' if has_btc else '❌'} Bitcoin rates in response")
                    except:
                        print("   ⚠️ Could not parse rates response")
                
            except Exception as e:
                print(f"   ❌ Crypto rates test failed: {str(e)}")
                rates_ok = False
            
            # Test crypto webhook
            try:
                test_crypto_webhook = {
                    "type": "crypto.deposit",
                    "data": {
                        "amount": "0.001",
                        "currency": "BTC",
                        "address": "test_address"
                    }
                }
                
                crypto_webhook_response = requests.post(f"{self.base_url}/crypto_webhook", 
                                                      json=test_crypto_webhook, timeout=10)
                crypto_webhook_ok = crypto_webhook_response.status_code == 200
                print(f"   {'✅' if crypto_webhook_ok else '❌'} Crypto webhook: {crypto_webhook_response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Crypto webhook test failed: {str(e)}")
                crypto_webhook_ok = False
            
            passed = rates_ok and crypto_webhook_ok
            self.log_test("Crypto Integration", passed, 
                         f"Rates: {rates_ok}, Webhook: {crypto_webhook_ok}")
            return passed
            
        except Exception as e:
            self.log_test("Crypto Integration", False, str(e))
            return False
    
    def test_ai_conversation(self):
        """Test F: AI Conversation (No Date/Time Forcing)"""
        print("\n🧠 F. AI CONVERSATION TEST")
        print("=" * 50)
        
        try:
            # Test normal greeting
            test_messages = [
                {"text": "Hello", "expect": "normal_greeting"},
                {"text": "How are you?", "expect": "no_date_forcing"},
                {"text": "Send 5k to Mella", "expect": "transfer_response"},
                {"text": "What's my balance?", "expect": "balance_response"}
            ]
            
            conversation_results = []
            
            for test_msg in test_messages:
                try:
                    message_data = {
                        "message": {
                            "chat": {"id": self.test_chat_id},
                            "from": {"id": self.test_chat_id, "first_name": "Test"},
                            "text": test_msg["text"]
                        }
                    }
                    
                    response = requests.post(f"{self.base_url}/webhook", 
                                           json=message_data, timeout=15)
                    
                    success = response.status_code == 200
                    
                    # Check for problematic date/time forcing
                    if success and response.text:
                        response_text = response.text.lower()
                        has_forced_date = ("saturday" in response_text and "june" in response_text and 
                                         test_msg["text"].lower() not in ["what's the date", "what day"])
                        
                        if has_forced_date:
                            success = False
                            print(f"   ❌ '{test_msg['text']}' - Forced date/time response detected")
                        else:
                            print(f"   ✅ '{test_msg['text']}' - Normal response")
                    
                    conversation_results.append(success)
                    
                except Exception as e:
                    print(f"   ❌ '{test_msg['text']}' - Error: {str(e)}")
                    conversation_results.append(False)
            
            passed = all(conversation_results)
            self.log_test("AI Conversation", passed, 
                         f"Responses: {len([r for r in conversation_results if r])}/{len(conversation_results)} normal")
            return passed
            
        except Exception as e:
            self.log_test("AI Conversation", False, str(e))
            return False
    
    def test_airtime_features(self):
        """Test G: Airtime/Data Features"""
        print("\n📱 G. AIRTIME/DATA FEATURES TEST")
        print("=" * 50)
        
        try:
            # Test airtime endpoint
            airtime_data = {
                "phone_number": "08012345678",
                "amount": 100,
                "network": "mtn"
            }
            
            response = requests.post(f"{self.base_url}/api/buy_airtime", 
                                   json=airtime_data, timeout=10)
            
            # Expect either success or proper error handling
            airtime_ok = response.status_code in [200, 201, 400, 422]  # 400/422 for validation errors are ok
            print(f"   {'✅' if airtime_ok else '❌'} Airtime endpoint: {response.status_code}")
            
            self.log_test("Airtime Features", airtime_ok, 
                         f"Endpoint response: {response.status_code}")
            return airtime_ok
            
        except Exception as e:
            self.log_test("Airtime Features", False, str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 SOFI AI - COMPREHENSIVE PRE-DEPLOYMENT TEST")
        print("=" * 70)
        print("Testing ALL REAL features before Render deployment")
        print("=" * 70)
        
        # Run all tests
        test_results = [
            self.test_environment_variables(),
            self.test_database_connection(),
            self.test_flask_server(),
            self.test_monnify_integration(),
            self.test_crypto_integration(),  # REAL crypto
            self.test_ai_conversation(),
            self.test_airtime_features()
        ]
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 DEPLOYMENT TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        passed_count = len(self.passed_tests)
        
        print(f"\n✅ PASSED TESTS ({passed_count}):")
        for test in self.passed_tests:
            print(f"   ✅ {test}")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"   ❌ {test}")
        
        print(f"\n📈 SUCCESS RATE: {passed_count}/{total_tests} ({(passed_count/total_tests)*100:.1f}%)")
        
        if all(test_results):
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ SOFI AI IS READY FOR RENDER DEPLOYMENT!")
            print("\n🚀 DEPLOYMENT CHECKLIST:")
            print("   ✅ Core systems working")
            print("   ✅ Monnify integration active")
            print("   ✅ REAL crypto features working")
            print("   ✅ AI responses normal (no date forcing)")
            print("   ✅ Database connected")
            print("   ✅ All endpoints responding")
            print("\n🎯 READY TO DEPLOY TO RENDER!")
            return True
        else:
            print("\n⚠️ SOME TESTS FAILED")
            print("🔧 Fix issues before deployment")
            print("\n💡 Common fixes:")
            if not self.test_environment_variables():
                print("   - Add missing environment variables")
            if not self.test_database_connection():
                print("   - Check Supabase tables and permissions")
            print("   - Ensure Flask server is running locally")
            print("   - Verify API credentials")
            return False

async def main():
    """Main test function"""
    tester = SofiPreDeploymentTest()
    
    print("Starting comprehensive deployment test...")
    print("Make sure Flask server is running on http://localhost:5000")
    input("Press Enter when ready...")
    
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 READY FOR RENDER! 🚀")
    else:
        print("\n🔧 FIX ISSUES FIRST")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
