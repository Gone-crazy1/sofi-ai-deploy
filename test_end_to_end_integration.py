#!/usr/bin/env python3
"""
End-to-End Integration Test for Sofi AI Project
Tests the complete flow from user input to AI response including airtime service
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_main_imports():
    """Test that all main imports work"""
    print("🔍 Testing main application imports...")
    try:
        from main import (
            handle_message, 
            handle_airtime_commands,
            process_confirmation_response
        )
        from utils.conversation_state import conversation_state
        from utils.enhanced_ai_responses import generate_ai_response
        from utils.airtime_service import (
            purchase_airtime_nellobytes,
            purchase_data_nellobytes,
            validate_phone_number,
            detect_network_from_phone
        )
        print("✅ All main imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_complete_user_flow():
    """Test complete user conversation flow with airtime service"""
    print("\n🔍 Testing complete user conversation flow...")
    
    try:
        from main import handle_message
        
        # Mock user data
        user_data = {
            'id': '12345',
            'first_name': 'TestUser',
            'username': 'testuser',
            'phone_number': '08012345678'
        }
        
        # Mock virtual account
        virtual_account = {
            'balance': 10000,
            'accountnumber': '1234567890',
            'bankname': 'Test Bank',
            'accountname': 'Test User'
        }
        
        # Test different user messages
        test_messages = [
            "Hello",
            "What can you do?",
            "Buy 1000 airtime",
            "Show data plans",
            "I need help with airtime"
        ]
        
        success_count = 0
        for message in test_messages:
            try:
                response = await handle_message("test_chat", message, user_data, virtual_account)
                if response and len(response) > 0:
                    print(f"✅ '{message}' -> Got response ({len(response)} chars)")
                    success_count += 1
                else:
                    print(f"❌ '{message}' -> No response")
            except Exception as e:
                print(f"❌ '{message}' -> Error: {e}")
        
        print(f"✅ Successfully handled {success_count}/{len(test_messages)} messages")
        return success_count >= len(test_messages) * 0.8  # 80% success rate
        
    except Exception as e:
        print(f"❌ Complete flow test failed: {e}")
        return False

async def test_airtime_confirmation_flow():
    """Test airtime confirmation flow"""
    print("\n🔍 Testing airtime confirmation flow...")
    
    try:
        from main import process_confirmation_response
        from utils.conversation_state import conversation_state
        
        chat_id = "test_confirmation_123"
        user_data = {
            'id': '12345',
            'first_name': 'TestUser',
            'phone_number': '08012345678'
        }
        
        virtual_account = {
            'balance': 5000,
            'accountnumber': '1234567890',
            'bankname': 'Test Bank',
            'accountname': 'Test User'
        }
        
        # Set up airtime confirmation state
        conversation_state.set_state(chat_id, {
            'step': 'confirm_airtime_purchase',
            'airtime': {
                'amount': 1000,
                'phone_number': '08012345678',
                'network': 'mtn'
            }
        })
        
        # Test YES confirmation
        response = await process_confirmation_response(chat_id, "YES", user_data, virtual_account)
        if response and "purchase" in response.lower():
            print("✅ YES confirmation handled correctly")
            result = True
        else:
            print("❌ YES confirmation failed")
            result = False
        
        # Test NO confirmation
        conversation_state.set_state(chat_id, {
            'step': 'confirm_airtime_purchase',
            'airtime': {
                'amount': 1000,
                'phone_number': '08012345678',
                'network': 'mtn'
            }
        })
        
        response = await process_confirmation_response(chat_id, "NO", user_data, virtual_account)
        if response and "cancelled" in response.lower():
            print("✅ NO confirmation handled correctly")
            result = result and True
        else:
            print("❌ NO confirmation failed")
            result = False
        
        return result
        
    except Exception as e:
        print(f"❌ Confirmation flow test failed: {e}")
        return False

async def run_all_tests():
    """Run all end-to-end tests"""
    print("="*50)
    print("   END-TO-END INTEGRATION TEST SUITE")
    print("="*50)
    
    tests = [
        ("Main Imports", test_main_imports),
        ("Complete User Flow", test_complete_user_flow),
        ("Airtime Confirmation Flow", test_airtime_confirmation_flow)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append(result)
        
        if result:
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"   TEST RESULTS: {passed}/{total} PASSED")
    print("="*50)
    
    if passed == total:
        print("🎉 ALL END-TO-END TESTS PASSED! Ready for production!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
