#!/usr/bin/env python3
"""
Comprehensive test for airtime service integration
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work"""
    print("🔍 Testing imports...")
    
    try:
        from main import (
            handle_airtime_commands, process_airtime_purchase, process_data_purchase,
            get_airtime_help_message, get_data_help_message, get_airtime_data_info
        )
        print("✅ Airtime functions imported successfully")
        
        from utils.airtime_service import (
            validate_phone_number, detect_network_from_phone, purchase_airtime_nellobytes,
            purchase_data_nellobytes, generate_airtime_receipt, generate_data_receipt,
            get_available_data_plans, format_data_plans_message, NETWORKS
        )
        print("✅ Airtime service functions imported successfully")
        
        from utils.conversation_state import conversation_state
        print("✅ Conversation state imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_airtime_command_detection():
    """Test airtime command detection"""
    print("\n🔍 Testing airtime command detection...")
    
    try:
        from main import handle_airtime_commands
        from utils.conversation_state import conversation_state
        
        # Mock user data and virtual account
        user_data = {
            'id': '123',
            'first_name': 'TestUser',
            'phone_number': '08012345678'
        }
        
        virtual_account = {
            'balance': 5000,
            'accountnumber': '1234567890',
            'bankname': 'Test Bank',
            'accountname': 'Test User'
        }
        
        # Test cases
        test_cases = [
            "buy 1000 airtime",
            "get 500 naira data",
            "recharge 2000",
            "top up 1500",
            "show data plans",
            "airtime help"        ]
        
        async def run_test():
            success_count = 0
            for test_message in test_cases:
                try:
                    result = await handle_airtime_commands("test_chat", test_message, user_data, virtual_account)
                    if result:
                        print(f"✅ '{test_message}' -> Command detected")
                        success_count += 1
                    else:
                        print(f"❌ '{test_message}' -> No command detected")
                except Exception as e:
                    print(f"❌ '{test_message}' -> Error: {e}")
            
            return success_count > 0
        
        result = asyncio.run(run_test())
        return result
        
    except Exception as e:
        print(f"❌ Airtime command detection test failed: {e}")
        return False

def test_phone_validation():
    """Test phone number validation"""
    print("\n🔍 Testing phone number validation...")
    
    try:
        from utils.airtime_service import validate_phone_number, detect_network_from_phone
        
        # Valid phone numbers
        valid_phones = [
            "08012345678",
            "07012345678",
            "09012345678",
            "+2348012345678"
        ]
        
        # Invalid phone numbers
        invalid_phones = [
            "1234567890",  # Wrong prefix
            "080123456",   # Too short
            "08012345678901",  # Too long
            "abcd1234567",     # Contains letters
            ""                 # Empty
        ]
        
        print("Testing valid phone numbers:")
        for phone in valid_phones:
            result = validate_phone_number(phone)
            network = detect_network_from_phone(phone)
            print(f"  {phone}: Valid={result}, Network={network}")
            
        print("Testing invalid phone numbers:")
        for phone in invalid_phones:
            result = validate_phone_number(phone)
            print(f"  {phone}: Valid={result}")
            
        return True
        
    except Exception as e:
        print(f"❌ Phone validation test failed: {e}")
        return False

def test_conversation_states():
    """Test conversation state management for airtime"""
    print("\n🔍 Testing conversation state management...")
    
    try:
        from utils.conversation_state import conversation_state
        
        chat_id = "test_chat_123"
        
        # Test airtime confirmation state
        airtime_state = {
            'step': 'confirm_airtime_purchase',
            'airtime': {
                'amount': 1000,
                'phone_number': '08012345678',
                'network': 'MTN'
            }
        }
        
        conversation_state.set_state(chat_id, airtime_state)
        retrieved_state = conversation_state.get_state(chat_id)
        
        if retrieved_state == airtime_state:
            print("✅ Airtime state management working")
        else:
            print("❌ Airtime state management failed")
            return False
            
        # Test data confirmation state
        data_state = {
            'step': 'confirm_data_purchase',
            'data': {
                'amount': 2000,
                'phone_number': '07012345678',
                'network': 'Airtel',
                'plans': [{'data_size': '2GB', 'validity': '30 days'}]
            }
        }
        
        conversation_state.set_state(chat_id, data_state)
        retrieved_state = conversation_state.get_state(chat_id)
        
        if retrieved_state == data_state:
            print("✅ Data state management working")
        else:
            print("❌ Data state management failed")
            return False
            
        # Test state clearing
        conversation_state.clear_state(chat_id)
        cleared_state = conversation_state.get_state(chat_id)
        
        if not cleared_state:
            print("✅ State clearing working")
        else:
            print("❌ State clearing failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Conversation state test failed: {e}")
        return False

def test_data_plans():
    """Test data plans functionality"""
    print("\n🔍 Testing data plans functionality...")
    
    try:
        from utils.airtime_service import get_available_data_plans, format_data_plans_message        # Test getting data plans
        plans_result = get_available_data_plans('mtn')
        if plans_result and plans_result.get('success'):
            plans = plans_result.get('plans', [])
            print(f"✅ Got {len(plans)} data plans")
            
            # Test formatting data plans
            formatted = format_data_plans_message('mtn')  # Format function takes network name
            if formatted and len(formatted) > 0:
                print("✅ Data plans formatting working")
                print(f"Sample formatted plans:\n{formatted[:200]}...")
            else:
                print("❌ Data plans formatting failed")
                return False
        else:
            print("❌ No data plans retrieved")
            return False
              # Test network-specific plans
        test_networks = ['mtn', 'airtel', 'glo', '9mobile']
        
        for network in test_networks:
            network_plans = get_available_data_plans(network)
            if network_plans and network_plans.get('success'):
                plans = network_plans.get('plans', [])
                print(f"✅ {network.upper()} has {len(plans)} data plans available")
            else:
                print(f"⚠️ No plans found for {network.upper()}")
                
        return True
        
    except Exception as e:
        print(f"❌ Data plans test failed: {e}")
        return False

def test_help_messages():
    """Test help message generation"""
    print("\n🔍 Testing help message generation...")
    
    try:
        from main import get_airtime_help_message, get_data_help_message, get_airtime_data_info
        
        # Test airtime help message
        airtime_help = get_airtime_help_message()
        if airtime_help and "airtime" in airtime_help.lower():
            print("✅ Airtime help message generated")
        else:
            print("❌ Airtime help message failed")
            return False
            
        # Test data help message
        data_help = get_data_help_message()
        if data_help and "data" in data_help.lower():
            print("✅ Data help message generated")
        else:
            print("❌ Data help message failed")
            return False
            
        # Test general info message
        general_info = get_airtime_data_info()
        if general_info and ("airtime" in general_info.lower() or "data" in general_info.lower()):
            print("✅ General info message generated")
        else:
            print("❌ General info message failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Help messages test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("   AIRTIME INTEGRATION TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Airtime Command Detection", test_airtime_command_detection),
        ("Phone Validation", test_phone_validation),
        ("Conversation States", test_conversation_states),
        ("Data Plans", test_data_plans),
        ("Help Messages", test_help_messages)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"💥 {test_name} test CRASHED: {e}")
            
    print("\n" + "=" * 50)
    print(f"   TEST RESULTS: {passed}/{total} PASSED")
    print("=" * 50)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Airtime integration is working correctly!")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
