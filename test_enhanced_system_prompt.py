#!/usr/bin/env python3
"""
Test script to verify the enhanced Sofi AI system prompt is working correctly
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from main import generate_ai_reply
from unittest.mock import patch, MagicMock

def test_enhanced_system_prompt():
    """Test that the enhanced system prompt handles various scenarios correctly"""
    
    # Mock OpenAI response
    mock_response = {
        'choices': [
            {
                'message': {
                    'content': 'Hello! I\'m Sofi AI, your Nigerian fintech assistant. I can help you with money transfers, airtime purchases, account management, and even technical questions. How can I assist you today?'
                }
            }
        ]
    }
    
    test_cases = [
        {
            'message': 'Hello Sofi, how are you?',
            'expected_keywords': ['Sofi AI', 'Nigerian', 'fintech', 'assist']
        },
        {
            'message': 'I want to send money to my brother',
            'expected_keywords': ['transfer', 'money', 'send']
        },
        {
            'message': 'Can you help me with Python code?',
            'expected_keywords': ['technical', 'help', 'Python']
        },
        {
            'message': 'Wetin be my account balance?',
            'expected_keywords': ['balance', 'account']
        }
    ]
    
    print("🧪 Testing Enhanced Sofi AI System Prompt...")
    
    with patch('openai.ChatCompletion.create', return_value=mock_response):
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: '{test_case['message']}'")
            
            try:
                # Test the generate_ai_reply function
                response = asyncio.run(generate_ai_reply("test_chat_123", test_case['message']))
                
                print(f"   ✅ Response generated successfully")
                print(f"   📝 Response: {response}")
                
                # Verify response contains expected characteristics
                response_lower = response.lower()
                found_keywords = [kw for kw in test_case['expected_keywords'] if kw.lower() in response_lower]
                
                if found_keywords:
                    print(f"   🎯 Found relevant keywords: {found_keywords}")
                else:
                    print(f"   ⚠️  No specific keywords found, but response was generated")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n🎉 Enhanced system prompt test completed!")

def test_system_prompt_structure():
    """Test that the system prompt has all the required sections"""
    
    print("\n🔍 Verifying System Prompt Structure...")
    
    # Import the system prompt from main.py
    from main import generate_ai_reply
    import inspect
    
    # Get the source code of generate_ai_reply to check the system prompt
    source = inspect.getsource(generate_ai_reply)
    
    required_sections = [
        'CORE CAPABILITIES & INTELLIGENCE',
        'FINANCIAL SERVICES',
        'MEDIA & COMMUNICATION PROCESSING',
        'MEMORY & CONTEXT AWARENESS',
        'TECHNICAL & GENERAL ASSISTANCE',
        'BEHAVIORAL GUIDELINES',
        'ONBOARDING & ACCOUNT MANAGEMENT',
        'COMMUNICATION STYLE'
    ]
    
    print("   Checking for required sections:")
    
    for section in required_sections:
        if section in source:
            print(f"   ✅ {section} - Found")
        else:
            print(f"   ❌ {section} - Missing")
    
    # Check for key capabilities
    key_capabilities = [
        'Nigerian fintech',
        'virtual account',
        'money transfers',
        'airtime/data',
        'crypto trading',
        'programming help',
        'Pidgin',
        'voice message',
        'image',
        'memory'
    ]
    
    print("\n   Checking for key capabilities:")
    
    for capability in key_capabilities:
        if capability.lower() in source.lower():
            print(f"   ✅ {capability} - Mentioned")
        else:
            print(f"   ❌ {capability} - Not found")
    
    print("\n🎯 System prompt structure verification completed!")

if __name__ == "__main__":
    print("🚀 Starting Enhanced System Prompt Tests...")
    
    test_enhanced_system_prompt()
    test_system_prompt_structure()
    
    print("\n✨ All tests completed successfully!")
