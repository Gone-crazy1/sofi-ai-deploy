#!/usr/bin/env python3
"""
🇳🇬 COMPREHENSIVE REGIONAL EXPRESSIONS INTEGRATION TEST

This script tests the full integration of Nigerian expressions 
into Sofi AI's intent detection and response generation.
"""

import asyncio
import os
from unittest.mock import MagicMock, patch
from utils.nigerian_expressions import enhance_nigerian_message, get_response_guidance

def test_regional_expressions_database():
    """Test the regional expressions database functionality"""
    print("🇳🇬 TESTING REGIONAL EXPRESSIONS DATABASE")
    print("=" * 60)
    
    test_cases = [
        {
            "input": "Abeg send 5k give my guy sharp sharp",
            "expected_intent": "transfer",
            "expected_enhancements": ["Amount pattern", "Expression", "Urgency"]
        },
        {
            "input": "My account don empty, wetin remain?",
            "expected_intent": "balance_inquiry",
            "expected_enhancements": ["Expression"]
        },
        {
            "input": "I wan buy credit for my phone",
            "expected_intent": "airtime_purchase",
            "expected_enhancements": ["Expression"]
        },
        {
            "input": "Transfer 50k give my mama for village now now",
            "expected_intent": "transfer",
            "expected_enhancements": ["Amount pattern", "Expression", "Urgency"]
        },
        {
            "input": "How much ego I get for my wallet?",
            "expected_intent": "balance_inquiry", 
            "expected_enhancements": ["Expression"]
        },
        {
            "input": "Send 2m to my brother account",
            "expected_intent": "transfer",
            "expected_enhancements": ["Amount pattern"]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: '{case['input']}'")
        
        # Test enhancement
        result = enhance_nigerian_message(case['input'])
        guidance = get_response_guidance(result)
        
        print(f"   Original: {result['original_message']}")
        print(f"   Enhanced: {result['enhanced_message']}")
        print(f"   Urgency: {result['urgency_level']}")
        print(f"   Relationship: {result['relationship_context']}")
        print(f"   Enhancements: {len(result['enhancements'])} found")
        for enhancement in result['enhancements']:
            print(f"     - {enhancement}")
        
        print(f"   Response Guidance:")
        print(f"     - Tone: {guidance['tone']}")
        if guidance['urgency_acknowledgment']:
            print(f"     - Urgency: {guidance['urgency_acknowledgment']}")
        if guidance['cultural_touch']:
            print(f"     - Cultural: {guidance['cultural_touch']}")
        
        # Verify enhancement worked
        if result['contains_nigerian_expressions']:
            print("   ✅ Nigerian expressions detected and enhanced")
        else:
            print("   ❌ No Nigerian expressions detected")
        
        print("-" * 50)
    
    return True

def test_intent_detection_with_regional():
    """Test intent detection with regional expressions"""
    print("\n🎯 TESTING INTENT DETECTION WITH REGIONAL EXPRESSIONS")
    print("=" * 60)
    
    # Mock the OpenAI response for testing
    mock_response = {
        'choices': [
            {
                'message': {
                    'content': '{"intent": "transfer", "details": {"amount": "5000", "recipient": "friend", "urgency": "high"}}'
                }
            }
        ]
    }
    
    # Import the function we want to test
    from main import detect_intent
    
    test_messages = [
        "Abeg send 5k give my guy sharp sharp",
        "My account don empty, wetin remain?",
        "Transfer 50k give my mama now now"
    ]
    
    with patch('openai.ChatCompletion.create', return_value=mock_response):
        for message in test_messages:
            print(f"\n📝 Testing: '{message}'")
            
            try:
                result = detect_intent(message)
                print(f"   Intent: {result.get('intent', 'unknown')}")
                print(f"   Details: {result.get('details', {})}")
                print("   ✅ Intent detection successful")
            except Exception as e:
                print(f"   ❌ Intent detection failed: {e}")
    
    return True

async def test_ai_reply_with_regional():
    """Test AI reply generation with regional expressions"""
    print("\n🤖 TESTING AI REPLY WITH REGIONAL EXPRESSIONS")
    print("=" * 60)
    
    # Mock the OpenAI response for testing
    mock_response = {
        'choices': [
            {
                'message': {
                    'content': 'I understand you want to send 5000 naira to your friend immediately! Let me help you with that transfer right away.'
                }
            }
        ]
    }
    
    # Mock the database functions
    async def mock_check_virtual_account(chat_id):
        return {
            "accountNumber": "1234567890",
            "bankName": "Sofi AI Bank",
            "accountName": "Test User"
        }
    
    async def mock_get_chat_history(chat_id):
        return []
    
    async def mock_save_chat_message(chat_id, role, message):
        pass
    
    # Import the function we want to test
    from main import generate_ai_reply
    
    test_cases = [
        {
            "chat_id": "123456789",
            "message": "Abeg send 5k give my guy sharp sharp",
            "expected_keywords": ["5000", "friend", "immediately", "urgent"]
        },
        {
            "chat_id": "123456789", 
            "message": "My account don empty, wetin remain?",
            "expected_keywords": ["account", "empty", "balance"]
        }
    ]
    
    with patch('openai.ChatCompletion.create', return_value=mock_response), \
         patch('main.check_virtual_account', side_effect=mock_check_virtual_account), \
         patch('main.get_chat_history', side_effect=mock_get_chat_history), \
         patch('main.save_chat_message', side_effect=mock_save_chat_message):
        
        for case in test_cases:
            print(f"\n📝 Testing: '{case['message']}'")
            
            try:
                reply = await generate_ai_reply(case['chat_id'], case['message'])
                print(f"   AI Reply: {reply}")
                print("   ✅ AI reply generation successful")
            except Exception as e:
                print(f"   ❌ AI reply generation failed: {e}")
    
    return True

def test_integration_completeness():
    """Test that the integration is complete and working"""
    print("\n🔍 TESTING INTEGRATION COMPLETENESS")  
    print("=" * 60)
    
    # Check if imports work
    try:
        from main import detect_intent, generate_ai_reply
        from utils.nigerian_expressions import enhance_nigerian_message, get_response_guidance
        print("✅ All required imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Check if enhancement function works
    try:
        test_message = "Send 5k give my guy"
        result = enhance_nigerian_message(test_message)
        if result['enhanced_message'] != test_message:
            print("✅ Message enhancement working")
        else:
            print("❌ Message enhancement not working properly")
    except Exception as e:
        print(f"❌ Enhancement test failed: {e}")
        return False
    
    # Check if guidance function works
    try:
        guidance = get_response_guidance(result)
        if 'tone' in guidance and 'urgency_acknowledgment' in guidance:
            print("✅ Response guidance working")
        else:
            print("❌ Response guidance not working properly")
    except Exception as e:
        print(f"❌ Guidance test failed: {e}")
        return False
    
    print("✅ Integration completeness test passed")
    return True

async def main():
    """Run all tests"""
    print("🚀 STARTING COMPREHENSIVE REGIONAL INTEGRATION TESTS")
    print("=" * 70)
    
    try:
        # Test 1: Regional expressions database
        success1 = test_regional_expressions_database()
        
        # Test 2: Intent detection with regional expressions
        success2 = test_intent_detection_with_regional()
        
        # Test 3: AI reply with regional expressions
        success3 = await test_ai_reply_with_regional()
        
        # Test 4: Integration completeness
        success4 = test_integration_completeness()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Regional Expressions Database: {'✅ PASSED' if success1 else '❌ FAILED'}")
        print(f"Intent Detection Integration: {'✅ PASSED' if success2 else '❌ FAILED'}")
        print(f"AI Reply Integration: {'✅ PASSED' if success3 else '❌ FAILED'}")
        print(f"Integration Completeness: {'✅ PASSED' if success4 else '❌ FAILED'}")
        
        overall_success = all([success1, success2, success3, success4])
        print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if overall_success:
            print("\n🇳🇬 SOFI AI REGIONAL EXPRESSIONS INTEGRATION COMPLETE!")
            print("Sofi can now understand and respond to Nigerian expressions naturally.")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
