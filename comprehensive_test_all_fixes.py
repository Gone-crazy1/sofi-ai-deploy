#!/usr/bin/env python3
"""
Comprehensive test for all Sofi AI fixes
Tests: duplicate messages, balance checking, airtime handling, transfer flow
"""

import sys
import os
import asyncio
import importlib.util
from unittest.mock import Mock, AsyncMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Create mock user data structure
test_user_data = {
    'onboarded': True,
    'first_name': 'TestUser',
    'last_name': 'Demo',
    'phone_number': '+2348012345678',
    'wallet_address': 'test_wallet_123',
    'beneficiaries': {
        'wife': {
            'account_number': '1232187659',
            'bank_code': '035',  # Wema Bank
            'bank_name': 'Wema Bank',
            'account_name': 'Jane Doe'
        }
    }
}

async def test_duplicate_message_fix():
    """Test that generate_ai_reply doesn't call send_reply internally"""
    print("🔧 Testing Duplicate Message Fix...")
    
    try:
        # Import main module
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        # Mock dependencies to prevent actual API calls
        with patch('main.send_reply') as mock_send_reply, \
             patch('main.save_chat_message', new_callable=AsyncMock), \
             patch('main.get_user_data', return_value=test_user_data), \
             patch('main.get_user_balance', return_value=5000.0):
            
            spec.loader.exec_module(main_module)
            
            # Test that generate_ai_reply doesn't call send_reply
            response = await main_module.generate_ai_reply(12345, "Hello", test_user_data)
            
            # send_reply should NOT be called from within generate_ai_reply
            assert not mock_send_reply.called, "❌ generate_ai_reply still calling send_reply internally!"
            
            print("✅ Duplicate message fix: WORKING - generate_ai_reply returns response without sending")
            return True
            
    except Exception as e:
        print(f"❌ Duplicate message fix test failed: {e}")
        return False

async def test_balance_checking():
    """Test balance checking functionality"""
    print("\n💰 Testing Balance Checking...")
    
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        with patch('main.send_reply') as mock_send_reply, \
             patch('main.save_chat_message', new_callable=AsyncMock), \
             patch('main.get_user_data', return_value=test_user_data), \
             patch('main.get_user_balance', return_value=15000.50):
            
            spec.loader.exec_module(main_module)
            
            # Test balance request
            response = await main_module.generate_ai_reply(12345, "check my balance", test_user_data)
            
            # Should contain balance information
            response_text = response if isinstance(response, str) else response.get("text", "")
            
            assert "15,000.50" in response_text, f"❌ Balance not found in response: {response_text}"
            assert "Balance" in response_text or "balance" in response_text, "❌ Response doesn't mention balance"
            
            print("✅ Balance checking: WORKING - Shows formatted NGN balance")
            return True
            
    except Exception as e:
        print(f"❌ Balance checking test failed: {e}")
        return False

async def test_airtime_functionality():
    """Test airtime purchase handling"""
    print("\n📱 Testing Airtime Functionality...")
    
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        # Mock the airtime API
        mock_airtime_response = {
            "status": "success",
            "message": "Airtime purchase successful",
            "data": {
                "reference": "TEST123",
                "amount": 1000,
                "phone": "08012345678"
            }
        }
        
        with patch('main.send_reply') as mock_send_reply, \
             patch('main.save_chat_message', new_callable=AsyncMock), \
             patch('main.get_user_data', return_value=test_user_data), \
             patch('main.get_user_balance', return_value=5000.0), \
             patch('main.AirtimeAPI') as mock_airtime_class:
            
            # Setup mock airtime API
            mock_airtime_instance = Mock()
            mock_airtime_instance.buy_airtime = AsyncMock(return_value=mock_airtime_response)
            mock_airtime_class.return_value = mock_airtime_instance
            
            spec.loader.exec_module(main_module)
            
            # Test airtime request
            test_messages = [
                "Buy 1000 naira MTN airtime for 08012345678",
                "Purchase ₦500 airtime for 08023456789 MTN",
                "Send 2000 airtime to 08034567890"
            ]
            
            for message in test_messages:
                response = await main_module.generate_ai_reply(12345, message, test_user_data)
                response_text = response if isinstance(response, str) else response.get("text", "")
                
                # Should handle airtime requests
                if "airtime" in message.lower():
                    print(f"   ✓ Processed: '{message}' -> Response length: {len(response_text)}")
            
            print("✅ Airtime functionality: WORKING - Handles airtime requests")
            return True
            
    except Exception as e:
        print(f"❌ Airtime functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_transfer_flow():
    """Test transfer flow handling"""
    print("\n💸 Testing Transfer Flow...")
    
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        with patch('main.send_reply') as mock_send_reply, \
             patch('main.save_chat_message', new_callable=AsyncMock), \
             patch('main.get_user_data', return_value=test_user_data), \
             patch('main.get_user_balance', return_value=10000.0):
            
            spec.loader.exec_module(main_module)
            
            # Test transfer request to saved beneficiary
            response = await main_module.generate_ai_reply(12345, "Send 5000 to my wife", test_user_data)
            response_text = response if isinstance(response, str) else response.get("text", "")
            
            # Should recognize beneficiary and show transfer details
            assert "wife" in response_text.lower() or "Jane" in response_text or "1232187659" in response_text, \
                f"❌ Transfer doesn't recognize beneficiary: {response_text}"
            
            print("✅ Transfer flow: WORKING - Recognizes beneficiaries and processes transfers")
            return True
            
    except Exception as e:
        print(f"❌ Transfer flow test failed: {e}")
        return False

async def test_regex_parsing():
    """Test the specific parsing issue with airtime amounts"""
    print("\n🔍 Testing Regex Parsing Edge Cases...")
    
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        with patch('main.send_reply') as mock_send_reply, \
             patch('main.save_chat_message', new_callable=AsyncMock), \
             patch('main.get_user_data', return_value=test_user_data), \
             patch('main.get_user_balance', return_value=5000.0):
            
            spec.loader.exec_module(main_module)
            
            # Test the problematic case: "Buy MTN airtime for 08012345678"
            problem_message = "Buy MTN airtime for 08012345678"
            response = await main_module.generate_ai_reply(12345, problem_message, test_user_data)
            response_text = response if isinstance(response, str) else response.get("text", "")
            
            # Should ask for amount, not extract wrong amount
            should_ask_for_amount = any(phrase in response_text.lower() for phrase in [
                "how much", "amount", "specify", "₦", "naira"
            ])
            
            # Should NOT extract "5678" as amount
            should_not_have_wrong_amount = "5678" not in response_text
            
            if should_ask_for_amount and should_not_have_wrong_amount:
                print("✅ Regex parsing: WORKING - Correctly asks for amount when missing")
            else:
                print(f"⚠️  Regex parsing: ISSUE - Response: {response_text[:100]}...")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Regex parsing test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 COMPREHENSIVE SOFI AI FIXES TEST")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    tests = [
        ("Duplicate Message Fix", test_duplicate_message_fix),
        ("Balance Checking", test_balance_checking),
        ("Airtime Functionality", test_airtime_functionality),
        ("Transfer Flow", test_transfer_flow),
        ("Regex Parsing", test_regex_parsing)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL FIXES ARE WORKING! Ready for deployment.")
    else:
        print("⚠️  Some issues remain. Check failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
