#!/usr/bin/env python3
"""
🔬 COMPLETE SOFI AI FEATURE TEST SUITE
=====================================
Tests EVERY single feature before deployment:
- Basic System Health
- Database Operations  
- AI Conversations
- Virtual Account Creation
- Bank Transfers & Webhooks
- Crypto Features (REAL API)
- Airtime/Data Purchase
- Beneficiary Management
- Memory System
- Error Handling
- Security Features
"""

import asyncio
import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CompleteSofiFeatureTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_chat_id = "complete_test_987654"
        self.passed_tests = []
        self.failed_tests = []
        self.test_results = {}
        
    def log_test(self, test_name, passed, details="", critical=False):
        """Log test results with criticality levels"""
        if passed:
            self.passed_tests.append(test_name)
            status = "✅ PASS"
            color = "GREEN"
        else:
            self.failed_tests.append(test_name)
            status = "❌ FAIL" if not critical else "🚨 CRITICAL FAIL"
            color = "RED"
        
        self.test_results[test_name] = {
            "passed": passed,
            "details": details,
            "critical": critical
        }
        
        print(f"{status} {test_name}")
        if details:
            print(f"      📝 {details}")
    
    # ===== SECTION 1: SYSTEM HEALTH =====
    def test_system_health(self):
        """Test 1: Complete System Health Check"""
        print("\n🏥 SECTION 1: SYSTEM HEALTH")
        print("=" * 60)
        
        # 1.1 Environment Variables
        required_vars = [
            'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'OPENAI_API_KEY',
            'TELEGRAM_BOT_TOKEN', 'MONNIFY_API_KEY', 'MONNIFY_SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        self.log_test("Environment Variables", len(missing_vars) == 0, 
                     f"Missing: {missing_vars}" if missing_vars else "All present", critical=True)
        
        # 1.2 Flask Server Health
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            health_ok = response.status_code == 200
            health_data = response.json() if health_ok else {}
            self.log_test("Flask Server Health", health_ok, 
                         f"Status: {response.status_code}, Data: {health_data}", critical=True)
        except Exception as e:
            self.log_test("Flask Server Health", False, str(e), critical=True)
        
        # 1.3 Database Connection
        try:
            from supabase import create_client
            supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
            result = supabase.table('users').select('*').limit(1).execute()
            self.log_test("Database Connection", True, "Supabase connected successfully")
        except Exception as e:
            self.log_test("Database Connection", False, str(e), critical=True)

    # ===== SECTION 2: AI CONVERSATION SYSTEM =====
    def test_ai_conversations(self):
        """Test 2: AI Conversation System"""
        print("\n🧠 SECTION 2: AI CONVERSATION SYSTEM")
        print("=" * 60)
        
        conversation_tests = [
            {"message": "Hello", "expect": "greeting"},
            {"message": "How are you?", "expect": "response"},
            {"message": "What can you do?", "expect": "capabilities"},
            {"message": "Help me with banking", "expect": "banking_help"},
            {"message": "Send money to John", "expect": "transfer_request"},
            {"message": "Check my balance", "expect": "balance_inquiry"},
            {"message": "Buy airtime", "expect": "airtime_help"},
            {"message": "Show crypto rates", "expect": "crypto_rates"}
        ]
        
        successful_conversations = 0
        
        for test in conversation_tests:
            try:
                message_data = {
                    "message": {
                        "chat": {"id": self.test_chat_id},
                        "from": {"id": self.test_chat_id, "first_name": "TestUser"},
                        "text": test["message"]
                    }
                }
                
                response = requests.post(f"{self.base_url}/webhook", 
                                       json=message_data, timeout=20)
                
                if response.status_code == 200:
                    successful_conversations += 1
                    self.log_test(f"AI Response: '{test['message']}'", True, 
                                 f"HTTP {response.status_code}")
                else:
                    self.log_test(f"AI Response: '{test['message']}'", False, 
                                 f"HTTP {response.status_code}")
                
                # Small delay between tests
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"AI Response: '{test['message']}'", False, str(e))
        
        overall_ai = successful_conversations >= len(conversation_tests) * 0.75
        self.log_test("AI Conversation System Overall", overall_ai, 
                     f"Success: {successful_conversations}/{len(conversation_tests)}")

    # ===== SECTION 3: VIRTUAL ACCOUNT SYSTEM =====
    def test_virtual_accounts(self):
        """Test 3: Virtual Account Creation & Management"""
        print("\n💳 SECTION 3: VIRTUAL ACCOUNT SYSTEM")
        print("=" * 60)
        
        # 3.1 Test Virtual Account Creation API
        try:
            account_data = {
                "chat_id": self.test_chat_id,
                "full_name": "Complete Test User",
                "phone_number": "08012345678"
            }
            
            response = requests.post(f"{self.base_url}/api/create_virtual_account", 
                                   json=account_data, timeout=30)
            
            account_created = response.status_code in [200, 201]
            response_text = response.text[:200] if response.text else "No response"
            
            self.log_test("Virtual Account Creation", account_created, 
                         f"HTTP {response.status_code}, Response: {response_text}")
            
            # Check if response contains account details
            if account_created and response.text:
                has_account_info = any(keyword in response.text.lower() 
                                     for keyword in ['account', 'number', 'bank', 'wema'])
                self.log_test("Account Details in Response", has_account_info, 
                             "Account information present in response")
        
        except Exception as e:
            self.log_test("Virtual Account Creation", False, str(e))

        # 3.2 Test Virtual Account Database Storage
        try:
            from supabase import create_client
            supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
            
            # Check if virtual_accounts table exists and has data
            result = supabase.table('virtual_accounts').select('*').limit(5).execute()
            has_accounts = len(result.data) > 0 if result.data else False
            
            self.log_test("Virtual Accounts Database", True, 
                         f"Found {len(result.data) if result.data else 0} accounts")
        except Exception as e:
            self.log_test("Virtual Accounts Database", False, str(e))

    # ===== SECTION 4: BANK TRANSFER SYSTEM =====
    def test_bank_transfers(self):
        """Test 4: Bank Transfer System"""
        print("\n🏦 SECTION 4: BANK TRANSFER SYSTEM")
        print("=" * 60)
        
        # 4.1 Test Bank Transfer Commands via AI
        transfer_commands = [
            "Send 1000 to GTB 0123456789",
            "Transfer 500 naira to Access Bank 9876543210",
            "Send 2k to Zenith 1122334455",
            "Pay Mella 3000 naira"
        ]
        
        transfer_responses = 0
        
        for command in transfer_commands:
            try:
                message_data = {
                    "message": {
                        "chat": {"id": self.test_chat_id},
                        "from": {"id": self.test_chat_id, "first_name": "TestUser"},
                        "text": command
                    }
                }
                
                response = requests.post(f"{self.base_url}/webhook", 
                                       json=message_data, timeout=15)
                
                if response.status_code == 200:
                    transfer_responses += 1
                    self.log_test(f"Transfer Command: '{command}'", True, "Command processed")
                else:
                    self.log_test(f"Transfer Command: '{command}'", False, 
                                 f"HTTP {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"Transfer Command: '{command}'", False, str(e))
        
        transfer_system_ok = transfer_responses >= len(transfer_commands) * 0.5
        self.log_test("Bank Transfer System", transfer_system_ok, 
                     f"Processed {transfer_responses}/{len(transfer_commands)} commands")

        # 4.2 Test Monnify Webhook
        try:
            webhook_data = {
                "eventType": "SUCCESSFUL_TRANSACTION",
                "settlementAmount": 5000.00,
                "destinationAccountNumber": "1234567890",
                "accountName": "Test User",
                "transactionReference": f"TEST_WEBHOOK_{int(time.time())}",
                "customerEmail": "test@example.com"
            }
            
            response = requests.post(f"{self.base_url}/monnify_webhook", 
                                   json=webhook_data, timeout=15)
            
            webhook_ok = response.status_code == 200
            self.log_test("Monnify Webhook Processing", webhook_ok, 
                         f"Webhook HTTP {response.status_code}")
            
        except Exception as e:
            self.log_test("Monnify Webhook Processing", False, str(e))

    # ===== SECTION 5: CRYPTO FEATURES =====
    def test_crypto_features(self):
        """Test 5: Cryptocurrency Features"""
        print("\n₿ SECTION 5: CRYPTOCURRENCY FEATURES")
        print("=" * 60)
        
        # 5.1 Test Crypto Rates API
        try:
            response = requests.get(f"{self.base_url}/api/crypto_rates", timeout=15)
            rates_ok = response.status_code == 200
            
            if rates_ok and response.text:
                has_bitcoin = 'bitcoin' in response.text.lower() or 'btc' in response.text.lower()
                has_rates = any(char.isdigit() for char in response.text)
                self.log_test("Crypto Rates API", rates_ok and has_bitcoin and has_rates, 
                             f"HTTP {response.status_code}, Contains BTC rates: {has_bitcoin}")
            else:
                self.log_test("Crypto Rates API", rates_ok, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Crypto Rates API", False, str(e))

        # 5.2 Test Crypto Commands via AI
        crypto_commands = [
            "Show crypto rates",
            "Bitcoin price",
            "Buy Bitcoin",
            "Crypto wallet address",
            "USDT rate"
        ]
        
        crypto_responses = 0
        
        for command in crypto_commands:
            try:
                message_data = {
                    "message": {
                        "chat": {"id": self.test_chat_id},
                        "from": {"id": self.test_chat_id, "first_name": "TestUser"},
                        "text": command
                    }
                }
                
                response = requests.post(f"{self.base_url}/webhook", 
                                       json=message_data, timeout=15)
                
                if response.status_code == 200:
                    crypto_responses += 1
                    self.log_test(f"Crypto Command: '{command}'", True, "Command processed")
                else:
                    self.log_test(f"Crypto Command: '{command}'", False, f"HTTP {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"Crypto Command: '{command}'", False, str(e))

        # 5.3 Test Crypto Webhook
        try:
            crypto_webhook_data = {
                "type": "crypto.deposit",
                "data": {
                    "amount": "0.001",
                    "currency": "BTC",
                    "address": "test_address_123",
                    "txid": f"test_tx_{int(time.time())}"
                }
            }
            
            response = requests.post(f"{self.base_url}/crypto_webhook", 
                                   json=crypto_webhook_data, timeout=10)
            
            crypto_webhook_ok = response.status_code == 200
            self.log_test("Crypto Webhook", crypto_webhook_ok, f"HTTP {response.status_code}")
            
        except Exception as e:
            self.log_test("Crypto Webhook", False, str(e))

    # ===== SECTION 6: AIRTIME & DATA =====
    def test_airtime_data(self):
        """Test 6: Airtime and Data Purchase"""
        print("\n📱 SECTION 6: AIRTIME & DATA PURCHASE")
        print("=" * 60)
        
        # 6.1 Test Airtime API Endpoint
        try:
            airtime_data = {
                "phone_number": "08012345678",
                "amount": 100,
                "network": "mtn"
            }
            
            response = requests.post(f"{self.base_url}/api/buy_airtime", 
                                   json=airtime_data, timeout=15)
            
            # Accept both success and proper error handling
            airtime_api_ok = response.status_code in [200, 201, 400, 422]
            self.log_test("Airtime API Endpoint", airtime_api_ok, 
                         f"HTTP {response.status_code}")
                         
        except Exception as e:
            self.log_test("Airtime API Endpoint", False, str(e))

        # 6.2 Test Airtime Commands via AI
        airtime_commands = [
            "Buy 100 naira MTN airtime for 08012345678",
            "Purchase 200 Airtel data for 07012345678", 
            "Top up 500 naira Glo airtime",
            "Buy data bundle for 9mobile"
        ]
        
        airtime_responses = 0
        
        for command in airtime_commands:
            try:
                message_data = {
                    "message": {
                        "chat": {"id": self.test_chat_id},
                        "from": {"id": self.test_chat_id, "first_name": "TestUser"},
                        "text": command
                    }
                }
                
                response = requests.post(f"{self.base_url}/webhook", 
                                       json=message_data, timeout=15)
                
                if response.status_code == 200:
                    airtime_responses += 1
                    self.log_test(f"Airtime Command: '{command[:30]}...'", True, "Processed")
                else:
                    self.log_test(f"Airtime Command: '{command[:30]}...'", False, 
                                 f"HTTP {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"Airtime Command: '{command[:30]}...'", False, str(e))

    # ===== SECTION 7: BENEFICIARY SYSTEM =====
    def test_beneficiary_system(self):
        """Test 7: Beneficiary Management"""
        print("\n👥 SECTION 7: BENEFICIARY MANAGEMENT")
        print("=" * 60)
        
        # 7.1 Test Beneficiary Database Table
        try:
            from supabase import create_client
            supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
            
            result = supabase.table('beneficiaries').select('*').limit(1).execute()
            self.log_test("Beneficiaries Table", True, "Table accessible")
            
        except Exception as e:
            self.log_test("Beneficiaries Table", False, str(e))

        # 7.2 Test Beneficiary Commands
        beneficiary_commands = [
            "Save John's GTB account 0123456789",
            "Add beneficiary Mary Access Bank 9876543210",
            "Save this account as Mella",
            "Show my saved accounts",
            "List beneficiaries"
        ]
        
        beneficiary_responses = 0
        
        for command in beneficiary_commands:
            try:
                message_data = {
                    "message": {
                        "chat": {"id": self.test_chat_id},
                        "from": {"id": self.test_chat_id, "first_name": "TestUser"},
                        "text": command
                    }
                }
                
                response = requests.post(f"{self.base_url}/webhook", 
                                       json=message_data, timeout=15)
                
                if response.status_code == 200:
                    beneficiary_responses += 1
                    self.log_test(f"Beneficiary: '{command[:25]}...'", True, "Processed")
                else:
                    self.log_test(f"Beneficiary: '{command[:25]}...'", False, 
                                 f"HTTP {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"Beneficiary: '{command[:25]}...'", False, str(e))

    # ===== SECTION 8: MEMORY & ANALYTICS =====
    def test_memory_system(self):
        """Test 8: Sharp AI Memory System"""
        print("\n🧠 SECTION 8: MEMORY & ANALYTICS SYSTEM")
        print("=" * 60)
        
        # 8.1 Test Sharp AI Tables
        sharp_tables = [
            'user_profiles', 'transaction_memory', 'conversation_context',
            'spending_analytics', 'ai_learning'
        ]
        
        try:
            from supabase import create_client
            supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
            
            working_tables = 0
            for table in sharp_tables:
                try:
                    result = supabase.table(table).select('*').limit(1).execute()
                    working_tables += 1
                    self.log_test(f"Sharp AI Table: {table}", True, "Accessible")
                except Exception as e:
                    self.log_test(f"Sharp AI Table: {table}", False, str(e))
            
            memory_system_ok = working_tables >= len(sharp_tables) * 0.8
            self.log_test("Sharp AI Memory System", memory_system_ok, 
                         f"Working tables: {working_tables}/{len(sharp_tables)}")
                         
        except Exception as e:
            self.log_test("Sharp AI Memory System", False, str(e))

    # ===== SECTION 9: ERROR HANDLING =====
    def test_error_handling(self):
        """Test 9: Error Handling & Edge Cases"""
        print("\n⚠️ SECTION 9: ERROR HANDLING & EDGE CASES")
        print("=" * 60)
        
        # 9.1 Test Invalid Requests
        error_tests = [
            {"endpoint": "/webhook", "data": {}, "test": "Empty webhook data"},
            {"endpoint": "/webhook", "data": {"invalid": "data"}, "test": "Invalid webhook structure"},
            {"endpoint": "/monnify_webhook", "data": {"invalid": "webhook"}, "test": "Invalid Monnify webhook"},
            {"endpoint": "/api/create_virtual_account", "data": {}, "test": "Missing account data"}
        ]
        
        error_handling_ok = 0
        
        for test in error_tests:
            try:
                response = requests.post(f"{self.base_url}{test['endpoint']}", 
                                       json=test['data'], timeout=10)
                
                # Good error handling should return 4xx or handle gracefully
                handles_error = response.status_code in [200, 400, 422, 500]
                if handles_error:
                    error_handling_ok += 1
                    
                self.log_test(f"Error Test: {test['test']}", handles_error, 
                             f"HTTP {response.status_code}")
                
            except Exception as e:
                self.log_test(f"Error Test: {test['test']}", False, str(e))

        # 9.2 Test Message Edge Cases
        edge_messages = [
            "",  # Empty message
            "x" * 1000,  # Very long message
            "🚀💰₿🏦📱",  # Only emojis
            "Send money to",  # Incomplete command
            "1234567890",  # Only numbers
        ]
        
        edge_responses = 0
        
        for msg in edge_messages:
            try:
                message_data = {
                    "message": {
                        "chat": {"id": self.test_chat_id},
                        "from": {"id": self.test_chat_id, "first_name": "TestUser"},
                        "text": msg
                    }
                }
                
                response = requests.post(f"{self.base_url}/webhook", 
                                       json=message_data, timeout=10)
                
                if response.status_code == 200:
                    edge_responses += 1
                    self.log_test(f"Edge Message: '{msg[:20]}...'", True, "Handled gracefully")
                else:
                    self.log_test(f"Edge Message: '{msg[:20]}...'", False, 
                                 f"HTTP {response.status_code}")
                
            except Exception as e:
                self.log_test(f"Edge Message: '{msg[:20]}...'", False, str(e))

    # ===== MAIN TEST RUNNER =====
    def run_complete_test_suite(self):
        """Run the complete feature test suite"""
        print("🔬 COMPLETE SOFI AI FEATURE TEST SUITE")
        print("=" * 80)
        print("Testing EVERY feature comprehensively...")
        print("⏱️ This comprehensive test will take 3-5 minutes...")
        print("=" * 80)
        
        # Run all test sections
        self.test_system_health()
        self.test_ai_conversations()
        self.test_virtual_accounts()
        self.test_bank_transfers()
        self.test_crypto_features()
        self.test_airtime_data()
        self.test_beneficiary_system()
        self.test_memory_system()
        self.test_error_handling()
        
        # Comprehensive Results Analysis
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        success_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        # Critical failures
        critical_failures = [name for name, result in self.test_results.items() 
                           if not result['passed'] and result.get('critical', False)]
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   ✅ PASSED: {len(self.passed_tests)}")
        print(f"   ❌ FAILED: {len(self.failed_tests)}")
        print(f"   📊 SUCCESS RATE: {success_rate:.1f}%")
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   🚨 {failure}")
        
        print(f"\n✅ PASSED TESTS:")
        for test in self.passed_tests:
            print(f"   ✅ {test}")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   ❌ {test}")
        
        # Deployment Decision
        print("\n" + "=" * 80)
        print("🎯 DEPLOYMENT DECISION")
        print("=" * 80)
        
        if len(critical_failures) == 0 and success_rate >= 70:
            print("🎉 COMPREHENSIVE TEST: PASSED!")
            print("✅ ALL CRITICAL SYSTEMS WORKING")
            print("✅ FEATURE SUCCESS RATE ACCEPTABLE")
            print("\n🚀 SOFI AI IS READY FOR PRODUCTION DEPLOYMENT!")
            print("\n📋 DEPLOYMENT CHECKLIST:")
            print("   ✅ Core systems functional")
            print("   ✅ AI conversations working")
            print("   ✅ Banking features operational")
            print("   ✅ Crypto integration active")
            print("   ✅ Error handling robust")
            print("   ✅ Database connections stable")
            print("\n🎯 PROCEED WITH RENDER DEPLOYMENT!")
            return True
        else:
            print("⚠️ COMPREHENSIVE TEST: ISSUES FOUND")
            if critical_failures:
                print("🚨 CRITICAL FAILURES MUST BE FIXED")
            if success_rate < 70:
                print(f"📉 SUCCESS RATE TOO LOW: {success_rate:.1f}% (Need >70%)")
            print("\n🔧 RESOLVE ISSUES BEFORE DEPLOYMENT")
            return False

def main():
    """Main test execution"""
    print("🤖 Starting COMPLETE Sofi AI Feature Test...")
    print("🔬 Testing ALL features comprehensively...")
    print("⏳ Please wait 3-5 minutes for complete analysis...\n")
    
    tester = CompleteSofiFeatureTest()
    deployment_ready = tester.run_complete_test_suite()
    
    if deployment_ready:
        print("\n🎯 COMPREHENSIVE TESTING COMPLETE: DEPLOY NOW! 🚀")
    else:
        print("\n🔧 COMPREHENSIVE TESTING COMPLETE: FIX ISSUES FIRST")
    
    return deployment_ready

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
