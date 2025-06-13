#!/usr/bin/env python3
"""
Nigerian User Conversation Flow Test
Tests conversation handling for Nigerian users who may not speak perfect English
Includes Pidgin, broken English, and common Nigerian expressions
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class NigerianUserFlowTest:
    def __init__(self):
        self.chat_id = "test_nigerian_user_123"
        self.user_data = {
            'id': '12345',
            'first_name': 'Chinedu',
            'username': 'chinedu_test',
            'phone_number': '08012345678'
        }
        
        self.virtual_account = {
            'balance': 15000,
            'accountnumber': '1234567890',
            'bankname': 'Opay',
            'accountname': 'Chinedu Okafor'
        }
        
    async def test_greeting_variations(self):
        """Test various Nigerian greeting patterns"""
        print("\n🇳🇬 Testing Nigerian Greetings...")
        
        greetings = [
            "hello",
            "hi there",
            "good morning",
            "good evening", 
            "hey sofi",
            "morning o",
            "evening",
            "how far",
            "how you dey",
            "wetin dey sup",
            "how market",
            "how body",
            "oya talk",
            "abeg talk to me",
            "i wan talk to you",
            "make i ask you something"
        ]
        
        from main import handle_message
        
        success_count = 0
        for greeting in greetings:
            try:
                response = await handle_message(self.chat_id, greeting, self.user_data, self.virtual_account)
                if response and len(response) > 10:
                    print(f"✅ '{greeting}' -> Got response")
                    success_count += 1
                else:
                    print(f"❌ '{greeting}' -> No/short response")
            except Exception as e:
                print(f"❌ '{greeting}' -> Error: {e}")
        
        print(f"Greetings test: {success_count}/{len(greetings)} passed")
        return success_count >= len(greetings) * 0.8  # 80% success rate

    async def test_broken_english_requests(self):
        """Test handling of broken English and poor grammar"""
        print("\n📝 Testing Broken English & Poor Grammar...")
        
        broken_english_requests = [
            "i want send money",
            "how i go send money",
            "i wan check my balance",
            "wetin be my balance",
            "abeg check my money",
            "i want buy credit",
            "buy me credit",
            "i need recharge card",
            "give me recharge",
            "data bundle i want",
            "i want data",
            "show me my money",
            "account details",
            "my account number",
            "how much money i get",
            "i wan know my balance",
            "send money to my brother",
            "transfer money help me",
            "help me buy airtime",
            "i need help for transfer"
        ]
        
        from main import handle_message
        
        success_count = 0
        for request in broken_english_requests:
            try:
                response = await handle_message(self.chat_id, request, self.user_data, self.virtual_account)
                if response and len(response) > 20:
                    print(f"✅ '{request}' -> Got meaningful response")
                    success_count += 1
                else:
                    print(f"❌ '{request}' -> No/short response")
            except Exception as e:
                print(f"❌ '{request}' -> Error: {e}")
        
        print(f"Broken English test: {success_count}/{len(broken_english_requests)} passed")
        return success_count >= len(broken_english_requests) * 0.7  # 70% success rate

    async def test_pidgin_expressions(self):
        """Test Nigerian Pidgin understanding"""
        print("\n🗣️ Testing Nigerian Pidgin Expressions...")
        
        pidgin_requests = [
            "abeg send money for me",
            "i wan send money",
            "check my account abeg",
            "wetin be my balance",
            "buy me recharge card",
            "make you help me send money",
            "i dey need data bundle",
            "abeg buy credit for me",
            "how i go transfer money",
            "show me my account details",
            "wetin be my account number",
            "i wan know how much money i get",
            "make i check my balance",
            "oya send money for my friend",
            "abeg help me with transfer",
            "i need small data",
            "buy me small credit",
            "check money for my account",
            "how i go fund my account",
            "show me my wallet"
        ]
        
        from main import handle_message
        
        success_count = 0
        for request in pidgin_requests:
            try:
                response = await handle_message(self.chat_id, request, self.user_data, self.virtual_account)
                if response and len(response) > 20:
                    print(f"✅ '{request}' -> Got meaningful response")
                    success_count += 1
                else:
                    print(f"❌ '{request}' -> No/short response")
            except Exception as e:
                print(f"❌ '{request}' -> Error: {e}")
        
        print(f"Pidgin test: {success_count}/{len(pidgin_requests)} passed")
        return success_count >= len(pidgin_requests) * 0.7  # 70% success rate

    async def test_airtime_data_variations(self):
        """Test airtime and data purchase with Nigerian expressions"""
        print("\n📱 Testing Airtime/Data Nigerian Expressions...")
        
        airtime_data_requests = [
            "buy me 1000 credit",
            "i want 500 recharge card",
            "load 2000 for my phone",
            "recharge my line with 1500",
            "top up my phone",
            "buy credit for me",
            "i need recharge",
            "give me airtime",
            "load me credit",
            "buy 1000 naira data",
            "i want data bundle",
            "buy me internet",
            "load data for me",
            "i need browsing bundle",
            "give me 2gb data",
            "buy me whatsapp bundle",
            "i want facebook bundle",
            "load me internet bundle",
            "buy small data for me",
            "i need data to browse"
        ]
        
        from main import handle_message
        
        success_count = 0
        for request in airtime_data_requests:
            try:
                response = await handle_message(self.chat_id, request, self.user_data, self.virtual_account)
                if response and ("airtime" in response.lower() or "data" in response.lower() or "recharge" in response.lower()):
                    print(f"✅ '{request}' -> Got airtime/data response")
                    success_count += 1
                else:
                    print(f"❌ '{request}' -> Non-relevant response")
            except Exception as e:
                print(f"❌ '{request}' -> Error: {e}")
        
        print(f"Airtime/Data test: {success_count}/{len(airtime_data_requests)} passed")
        return success_count >= len(airtime_data_requests) * 0.6  # 60% success rate

    async def test_money_transfer_variations(self):
        """Test money transfer with Nigerian expressions"""
        print("\n💰 Testing Money Transfer Nigerian Expressions...")
        
        transfer_requests = [
            "send money to my brother",
            "transfer 5000 to my friend",
            "i want send money",
            "make i send money give my friend",
            "abeg help me send money",
            "transfer money for me",
            "send money to access bank",
            "i wan transfer money",
            "help me pay somebody",
            "send 2000 to my sister",
            "make you help me transfer",
            "i need to send money",
            "pay money for somebody",
            "send money give person",
            "transfer fund",
            "send cash",
            "move money",
            "pay person",
            "wire transfer",
            "bank transfer"
        ]
        
        from main import handle_message
        
        success_count = 0
        for request in transfer_requests:
            try:
                response = await handle_message(self.chat_id, request, self.user_data, self.virtual_account)
                if response and ("transfer" in response.lower() or "send" in response.lower() or "bank" in response.lower() or "account" in response.lower()):
                    print(f"✅ '{request}' -> Got transfer response")
                    success_count += 1
                else:
                    print(f"❌ '{request}' -> Non-relevant response")
            except Exception as e:
                print(f"❌ '{request}' -> Error: {e}")
        
        print(f"Transfer test: {success_count}/{len(transfer_requests)} passed")
        return success_count >= len(transfer_requests) * 0.6  # 60% success rate

    async def test_confirmation_responses(self):
        """Test Nigerian-style YES/NO confirmations"""
        print("\n✅ Testing Nigerian Confirmation Responses...")
        
        from utils.conversation_state import conversation_state
        from main import process_confirmation_response
        
        # Set up airtime confirmation state
        conversation_state.set_state(self.chat_id, {
            'step': 'confirm_airtime_purchase',
            'airtime': {
                'amount': 1000,
                'phone_number': '08012345678',
                'network': 'mtn'
            }
        })
        
        yes_variations = [
            "yes", "ok", "sure", "proceed", "go ahead", "do it",
            "oya", "abeg do it", "make you do am", "why not",
            "of course", "walahi yes", "oya do am", "send am"
        ]
        
        no_variations = [
            "no", "cancel", "stop", "forget it", "not now",
            "abeg no", "cancel am", "stop am", "forget that thing",
            "no be like that", "wait first", "later"
        ]
        
        success_count = 0
        total_tests = len(yes_variations) + len(no_variations)
        
        # Test YES variations
        for yes_response in yes_variations:
            try:
                # Reset state for each test
                conversation_state.set_state(self.chat_id, {
                    'step': 'confirm_airtime_purchase',
                    'airtime': {
                        'amount': 1000,
                        'phone_number': '08012345678',
                        'network': 'mtn'
                    }
                })
                
                response = await process_confirmation_response(self.chat_id, yes_response, self.user_data, self.virtual_account)
                if response and ("purchase" in response.lower() or "successful" in response.lower() or "failed" in response.lower()):
                    print(f"✅ YES: '{yes_response}' -> Purchase attempted")
                    success_count += 1
                else:
                    print(f"❌ YES: '{yes_response}' -> Unexpected response")
            except Exception as e:
                print(f"❌ YES: '{yes_response}' -> Error: {e}")
        
        # Test NO variations
        for no_response in no_variations:
            try:
                # Reset state for each test
                conversation_state.set_state(self.chat_id, {
                    'step': 'confirm_airtime_purchase',
                    'airtime': {
                        'amount': 1000,
                        'phone_number': '08012345678',
                        'network': 'mtn'
                    }
                })
                
                response = await process_confirmation_response(self.chat_id, no_response, self.user_data, self.virtual_account)
                if response and ("cancelled" in response.lower() or "cancel" in response.lower()):
                    print(f"✅ NO: '{no_response}' -> Purchase cancelled")
                    success_count += 1
                else:
                    print(f"❌ NO: '{no_response}' -> Unexpected response")
            except Exception as e:
                print(f"❌ NO: '{no_response}' -> Error: {e}")
        
        print(f"Confirmation test: {success_count}/{total_tests} passed")
        return success_count >= total_tests * 0.7  # 70% success rate

    async def test_help_requests(self):
        """Test help requests in Nigerian style"""
        print("\n❓ Testing Nigerian Help Requests...")
        
        help_requests = [
            "help me",
            "i need help",
            "what can you do",
            "wetin you fit do",
            "how you go help me",
            "make you help me",
            "abeg help me",
            "i wan know wetin you fit do",
            "show me what you can do",
            "what services you get",
            "how you take work",
            "how i go use you",
            "teach me how to use",
            "explain how to transfer",
            "how to buy airtime",
            "how to check balance",
            "i no sabi how to use",
            "show me features",
            "what you fit do for me",
            "guide me"
        ]
        
        from main import handle_message
        
        success_count = 0
        for request in help_requests:
            try:
                response = await handle_message(self.chat_id, request, self.user_data, self.virtual_account)
                if response and len(response) > 50 and ("help" in response.lower() or "can" in response.lower() or "transfer" in response.lower()):
                    print(f"✅ '{request}' -> Got helpful response")
                    success_count += 1
                else:
                    print(f"❌ '{request}' -> Poor help response")
            except Exception as e:
                print(f"❌ '{request}' -> Error: {e}")
        
        print(f"Help test: {success_count}/{len(help_requests)} passed")
        return success_count >= len(help_requests) * 0.7  # 70% success rate

    async def run_all_tests(self):
        """Run all Nigerian user conversation flow tests"""
        print("="*60)
        print("   NIGERIAN USER CONVERSATION FLOW TEST SUITE")
        print("   Testing: Poor English, Pidgin, Common Expressions")
        print("="*60)
        
        tests = [
            ("Nigerian Greetings", self.test_greeting_variations),
            ("Broken English Requests", self.test_broken_english_requests),
            ("Nigerian Pidgin", self.test_pidgin_expressions),
            ("Airtime/Data Expressions", self.test_airtime_data_variations),
            ("Money Transfer Expressions", self.test_money_transfer_variations),
            ("Nigerian Confirmations", self.test_confirmation_responses),
            ("Help Requests", self.test_help_requests)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name} test...")
            try:
                result = await test_func()
                results.append(result)
                
                if result:
                    print(f"✅ {test_name} test PASSED")
                else:
                    print(f"❌ {test_name} test FAILED")
            except Exception as e:
                print(f"❌ {test_name} test ERROR: {e}")
                results.append(False)
        
        print("\n" + "="*60)
        passed = sum(results)
        total = len(results)
        print(f"   NIGERIAN USER FLOW RESULTS: {passed}/{total} PASSED")
        print("="*60)
        
        if passed >= total * 0.7:  # 70% success rate
            print("🎉 NIGERIAN USER CONVERSATION FLOW: EXCELLENT!")
            print("✅ Sofi can handle Nigerian users effectively!")
            print("✅ Good understanding of broken English and Pidgin")
            print("✅ Robust conversation flow for all features")
            return True
        else:
            print("⚠️ NIGERIAN USER CONVERSATION FLOW: NEEDS IMPROVEMENT")
            print("❌ Some Nigerian expressions not properly handled")
            print("❌ Conversation flow may frustrate Nigerian users")
            return False

async def main():
    """Run the Nigerian user conversation flow test"""
    test_suite = NigerianUserFlowTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🇳🇬 READY FOR NIGERIAN USERS! 🇳🇬")
        print("Sofi AI can handle Nigerian users with poor English skills effectively.")
    else:
        print("\n⚠️ IMPROVEMENTS NEEDED")
        print("Consider enhancing conversation patterns for Nigerian users.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
