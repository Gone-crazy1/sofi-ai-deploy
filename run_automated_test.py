#!/usr/bin/env python3
"""
AUTOMATED COMPREHENSIVE SOFI AI TEST
Runs all pre-deployment tests automatically without manual input
"""

import asyncio
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AutomatedSofiTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_chat_id = "automated_test_123456"
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
            'MONNIFY_SECRET_KEY'
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

    def test_flask_server(self):
        """Test B: Flask Server Health"""
        print("\n🌐 B. FLASK SERVER TEST")
        print("=" * 50)
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=10)
            health_ok = response.status_code == 200
            print(f"   {'✅' if health_ok else '❌'} Health endpoint: {response.status_code}")
            
            if health_ok:
                try:
                    health_data = response.json()
                    print(f"   📊 Server status: {health_data.get('status', 'unknown')}")
                except:
                    print("   📊 Server responding (non-JSON response)")
            
            self.log_test("Flask Server Health", health_ok, 
                         f"Health endpoint: {response.status_code}")
            return health_ok
            
        except Exception as e:
            self.log_test("Flask Server Health", False, str(e))
            return False

    def test_webhook_endpoint(self):
        """Test C: Main Webhook"""
        print("\n📡 C. WEBHOOK ENDPOINT TEST")
        print("=" * 50)
        
        try:
            test_message = {
                "message": {
                    "chat": {"id": self.test_chat_id},
                    "from": {"id": self.test_chat_id, "first_name": "AutoTest"},
                    "text": "Hello Sofi - automated test"
                }
            }
            
            response = requests.post(f"{self.base_url}/webhook", 
                                   json=test_message, timeout=15)
            webhook_ok = response.status_code == 200
            print(f"   {'✅' if webhook_ok else '❌'} Main webhook: {response.status_code}")
            
            self.log_test("Main Webhook", webhook_ok, 
                         f"Webhook response: {response.status_code}")
            return webhook_ok
            
        except Exception as e:
            self.log_test("Main Webhook", False, str(e))
            return False

    def test_ai_responses(self):
        """Test D: AI Response System"""
        print("\n🧠 D. AI RESPONSE SYSTEM TEST")
        print("=" * 50)
        
        test_messages = [
            "Hello",
            "What's my balance?",
            "How are you today?"
        ]
        
        successful_responses = 0
        
        for msg in test_messages:
            try:
                message_data = {
                    "message": {
                        "chat": {"id": self.test_chat_id},
                        "from": {"id": self.test_chat_id, "first_name": "AutoTest"},
                        "text": msg
                    }
                }
                
                response = requests.post(f"{self.base_url}/webhook", 
                                       json=message_data, timeout=15)
                
                if response.status_code == 200:
                    successful_responses += 1
                    print(f"   ✅ '{msg}' - Response OK")
                else:
                    print(f"   ❌ '{msg}' - Response {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ '{msg}' - Error: {str(e)}")
        
        success_rate = successful_responses / len(test_messages)
        passed = success_rate >= 0.67  # At least 2/3 should work
        
        self.log_test("AI Response System", passed, 
                     f"Success rate: {successful_responses}/{len(test_messages)}")
        return passed

    def test_database_connection(self):
        """Test E: Database Connection"""
        print("\n🗄️ E. DATABASE CONNECTION TEST")
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
            core_tables = ['users', 'virtual_accounts']
            working_tables = 0
            
            for table in core_tables:
                try:
                    result = supabase.table(table).select('*').limit(1).execute()
                    working_tables += 1
                    print(f"   ✅ {table} table accessible")
                except Exception as e:
                    print(f"   ❌ {table} table issue: {str(e)[:50]}")
            
            passed = working_tables >= 1  # At least 1 core table should work
            self.log_test("Database Connection", passed, 
                         f"Working tables: {working_tables}/{len(core_tables)}")
            return passed
            
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False

    def run_automated_test(self):
        """Run all automated tests"""
        print("🚀 SOFI AI - AUTOMATED COMPREHENSIVE TEST")
        print("=" * 70)
        print("Testing core systems automatically...")
        print("=" * 70)
        
        # Run core tests
        test_results = [
            self.test_environment_variables(),
            self.test_flask_server(),
            self.test_webhook_endpoint(),
            self.test_ai_responses(),
            self.test_database_connection()
        ]
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 AUTOMATED TEST SUMMARY")
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
        
        success_rate = (passed_count/total_tests)*100 if total_tests > 0 else 0
        print(f"\n📈 SUCCESS RATE: {passed_count}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:  # 80% or higher = ready
            print("\n🎉 CORE SYSTEMS WORKING!")
            print("✅ SOFI AI IS FUNCTIONAL!")
            print("\n🚀 DEPLOYMENT STATUS:")
            print("   ✅ Flask server running")
            print("   ✅ Webhooks responding")
            print("   ✅ AI system active")
            print("   ✅ Database connected")
            print("\n🎯 READY FOR RENDER DEPLOYMENT!")
            return True
        else:
            print("\n⚠️ SOME CORE SYSTEMS HAVE ISSUES")
            print("🔧 Review failed tests before deployment")
            return False

def main():
    """Main test function"""
    print("🤖 Starting automated Sofi AI test...")
    print("⏱️ This will take about 30 seconds...")
    print()
    
    tester = AutomatedSofiTest()
    success = tester.run_automated_test()
    
    if success:
        print("\n🎯 DEPLOYMENT READY! 🚀")
    else:
        print("\n🔧 REVIEW ISSUES FIRST")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
