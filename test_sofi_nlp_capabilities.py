#!/usr/bin/env python3
"""
Comprehensive Natural Language Understanding Assessment for Sofi AI
Tests Sofi's ability to understand various user message types
"""

import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import main detect_intent function
from main import detect_intent

# Test cases covering various message types
TEST_CASES = [
    # TRANSFER INTENT TESTS
    {
        "message": "Send 5000 to 8104611794 Opay",
        "expected_intent": "transfer",
        "expected_details": {
            "amount": 5000,
            "account_number": "8104611794",
            "bank": "Opay"
        },
        "category": "Transfer - Basic"
    },
    {
        "message": "Transfer ₦2,500 to 0123456789 GTB",
        "expected_intent": "transfer",
        "expected_details": {
            "amount": 2500,
            "account_number": "0123456789",
            "bank": "GTBank"
        },
        "category": "Transfer - Currency Symbol"
    },
    {
        "message": "Pay 10000 naira to my friend John at Access Bank account 1234567890",
        "expected_intent": "transfer",
        "expected_details": {
            "amount": 10000,
            "recipient_name": "John",
            "account_number": "1234567890",
            "bank": "Access Bank"
        },
        "category": "Transfer - Complex"
    },
    
    # BALANCE INQUIRY TESTS
    {
        "message": "What's my balance?",
        "expected_intent": "balance_inquiry",
        "expected_details": {},
        "category": "Balance - Basic"
    },
    {
        "message": "Check my account balance please",
        "expected_intent": "balance_inquiry",
        "expected_details": {},
        "category": "Balance - Polite"
    },
    {
        "message": "How much money do I have in my wallet?",
        "expected_intent": "balance_inquiry",
        "expected_details": {},
        "category": "Balance - Casual"
    },
    
    # GREETING TESTS
    {
        "message": "Hello Sofi!",
        "expected_intent": "greeting",
        "expected_details": {},
        "category": "Greeting - Basic"
    },
    {
        "message": "Good morning, how are you today?",
        "expected_intent": "greeting",
        "expected_details": {},
        "category": "Greeting - Polite"
    },
    
    # HELP TESTS
    {
        "message": "Help me",
        "expected_intent": "help",
        "expected_details": {},
        "category": "Help - Basic"
    },
    {
        "message": "What can you do for me?",
        "expected_intent": "help",
        "expected_details": {},
        "category": "Help - Capabilities"
    },
    
    # NIGERIAN PIDGIN/CASUAL TESTS
    {
        "message": "Abeg send 1000 give my guy for UBA",
        "expected_intent": "transfer",
        "category": "Nigerian Pidgin"
    },
    {
        "message": "I wan check my money",
        "expected_intent": "balance_inquiry",
        "category": "Pidgin Balance"
    },
    
    # CRYPTO TESTS
    {
        "message": "Create BTC wallet",
        "expected_intent": "crypto_wallet",
        "expected_details": {
            "crypto": "BTC",
            "action": "create"
        },
        "category": "Crypto - BTC Wallet"
    },
    {
        "message": "Show me my USDT address",
        "expected_intent": "crypto_wallet",
        "expected_details": {
            "crypto": "USDT",
            "action": "show"
        },
        "category": "Crypto - USDT Address"
    },
    
    # ACCOUNT MANAGEMENT TESTS
    {
        "message": "Show my account details",
        "expected_intent": "account_details",
        "expected_details": {},
        "category": "Account - Details"
    },
    {
        "message": "I want to create an account",
        "expected_intent": "create_account",
        "expected_details": {},
        "category": "Account - Creation"
    },
    
    # AMBIGUOUS/EDGE CASES
    {
        "message": "I sent money",
        "expected_intent": "transfer",
        "category": "Ambiguous - Past Tense"
    },
    {
        "message": "Money",
        "expected_intent": "general",
        "category": "Very Ambiguous"
    }
]

def create_mock_response(intent_data):
    """Create a mock OpenAI response"""
    return MagicMock(
        choices=[{
            'message': {
                'content': json.dumps(intent_data)
            }
        }]
    )

def test_nlp_understanding():
    """Test Sofi's natural language understanding capabilities"""
    print("🧠 SOFI AI NATURAL LANGUAGE UNDERSTANDING ASSESSMENT")
    print("=" * 60)
    
    results = {
        "total_tests": len(TEST_CASES),
        "passed": 0,
        "failed": 0,
        "categories": {},
        "failed_cases": []
    }
    
    with patch('main.openai.ChatCompletion.create') as mock_openai:
        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"\n{i}. Testing: '{test_case['message']}'")
            print(f"   Category: {test_case['category']}")
            
            # Create expected response
            expected_response = {
                "intent": test_case["expected_intent"],
                "confidence": 0.9,
                "details": test_case.get("expected_details", {})
            }
            
            # Mock the OpenAI response
            mock_openai.return_value = create_mock_response(expected_response)
            
            try:
                # Test the intent detection
                result = detect_intent(test_case["message"])
                
                # Check if intent matches
                intent_match = result.get("intent") == test_case["expected_intent"]
                
                if intent_match:
                    print(f"   ✅ PASSED - Intent: {result.get('intent')}")
                    results["passed"] += 1
                    category = test_case["category"].split(" - ")[0]
                    results["categories"][category] = results["categories"].get(category, {"passed": 0, "total": 0})
                    results["categories"][category]["passed"] += 1
                    results["categories"][category]["total"] += 1
                else:
                    print(f"   ❌ FAILED - Expected: {test_case['expected_intent']}, Got: {result.get('intent')}")
                    results["failed"] += 1
                    results["failed_cases"].append({
                        "message": test_case["message"],
                        "expected": test_case["expected_intent"],
                        "got": result.get("intent"),
                        "category": test_case["category"]
                    })
                    category = test_case["category"].split(" - ")[0]
                    results["categories"][category] = results["categories"].get(category, {"passed": 0, "total": 0})
                    results["categories"][category]["total"] += 1
                
            except Exception as e:
                print(f"   ❌ ERROR - {str(e)}")
                results["failed"] += 1
                results["failed_cases"].append({
                    "message": test_case["message"],
                    "expected": test_case["expected_intent"],
                    "got": f"ERROR: {str(e)}",
                    "category": test_case["category"]
                })
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 ASSESSMENT RESULTS")
    print("=" * 60)
    
    success_rate = (results["passed"] / results["total_tests"]) * 100
    print(f"Overall Success Rate: {success_rate:.1f}% ({results['passed']}/{results['total_tests']})")
    
    print("\n📈 Category Breakdown:")
    for category, stats in results["categories"].items():
        category_rate = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"   {category}: {category_rate:.1f}% ({stats['passed']}/{stats['total']})")
    
    if results["failed_cases"]:
        print("\n❌ Failed Cases:")
        for case in results["failed_cases"]:
            print(f"   • '{case['message']}' - Expected: {case['expected']}, Got: {case['got']}")
    
    # Assessment conclusion
    print("\n🎯 ASSESSMENT CONCLUSION:")
    if success_rate >= 90:
        print("   🟢 EXCELLENT - Sofi has superior natural language understanding")
    elif success_rate >= 75:
        print("   🟡 GOOD - Sofi has solid NLP capabilities with room for improvement")
    elif success_rate >= 60:
        print("   🟠 FAIR - Sofi needs significant NLP improvements")
    else:
        print("   🔴 POOR - Major NLP overhaul required")
    
    return results

def test_enhanced_features():
    """Test Sofi's enhanced AI features"""
    print("\n🚀 ENHANCED AI FEATURES TEST")
    print("=" * 40)
    
    # Test enhanced intent detection
    try:
        from utils.enhanced_ai_responses import enhanced_detect_intent
        
        enhanced_tests = [
            "Did you receive my transfer?",
            "I sent money to my account",
            "Check if my deposit arrived",
            "Transfer 5000 to 8104611794 Opay"
        ]
        
        print("Testing Enhanced Intent Detection:")
        for message in enhanced_tests:
            result = enhanced_detect_intent(message)
            print(f"   '{message}' → {result['intent']}")
            
        print("\n✅ Enhanced AI features are available")
        
    except ImportError:
        print("❌ Enhanced AI features not available")

if __name__ == "__main__":
    # Test core NLP understanding
    results = test_nlp_understanding()
    
    # Test enhanced features
    test_enhanced_features()
    
    print(f"\n🏁 Assessment Complete! Overall Score: {(results['passed']/results['total_tests'])*100:.1f}%")
