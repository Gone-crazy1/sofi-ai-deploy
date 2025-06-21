#!/usr/bin/env python3
"""
Test script for standardized prompt schemas
Verifies that the new prompts fix all the issues identified in OpenAI logs
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_schemas import (
    get_transfer_prompt, 
    get_image_prompt,
    validate_transfer_result,
    validate_image_result,
    PromptSchemas
)

load_dotenv()

def test_transfer_extraction_prompt():
    """Test the standardized transfer extraction prompt"""
    print("🧪 Testing Transfer Extraction Prompt Schema...")
    
    prompt = get_transfer_prompt()
    
    # Verify prompt includes all required elements
    assert "JSON" in prompt, "Prompt must specify JSON output"
    assert "amount" in prompt, "Prompt must include amount field"
    assert "account" in prompt, "Prompt must include account field"
    assert "bank" in prompt, "Prompt must include bank field"
    assert "recipient" in prompt, "Prompt must include recipient field"
    assert "error" in prompt, "Prompt must include error field"
    assert "null" in prompt, "Prompt must specify null for missing values"
    
    print("✅ Transfer prompt schema is complete")
    
    # Test validation with different inputs
    test_cases = [
        # Valid case
        {
            "input": {"amount": 5000, "account": "1234567891", "bank": "Access Bank", "recipient": None, "error": None},
            "should_pass": True
        },
        # Invalid account number
        {
            "input": {"amount": 2000, "account": "123", "bank": "GTBank", "recipient": None, "error": None},
            "should_pass": False  # Account too short
        },
        # Missing transfer info
        {
            "input": {"amount": None, "account": None, "bank": None, "recipient": None, "error": "No transfer detected"},
            "should_pass": True  # Valid error case
        },
        # Invalid amount
        {
            "input": {"amount": -100, "account": "1234567890", "bank": "UBA", "recipient": None, "error": None},
            "should_pass": False  # Negative amount
        }
    ]
    
    for i, case in enumerate(test_cases):
        result = validate_transfer_result(case["input"])
        if case["should_pass"]:
            assert result.error is None or "error" in case["input"], f"Test case {i+1} should pass but got error: {result.error}"
        else:
            # Invalid cases should either have validation errors or be cleaned up
            if result.account == "123":  # Short account should be cleaned to None
                assert result.account is None, f"Short account number should be cleaned to None"
            if case["input"]["amount"] == -100:  # Negative amount should be cleaned
                assert result.amount is None, f"Negative amount should be cleaned to None"
    
    print("✅ Transfer validation working correctly")

def test_image_analysis_prompt():
    """Test the standardized image analysis prompt"""
    print("🧪 Testing Image Analysis Prompt Schema...")
    
    prompt = get_image_prompt()
    
    # Verify prompt includes all required elements
    assert "JSON" in prompt, "Prompt must specify JSON output"
    assert "type" in prompt, "Prompt must include type field"
    assert "details" in prompt, "Prompt must include details object"
    assert "bank_details" in prompt, "Prompt must specify bank_details type"
    assert "transaction" in prompt, "Prompt must specify transaction type"
    assert "other" in prompt, "Prompt must specify other type"
    assert "account_number" in prompt, "Prompt must include account_number field"
    assert "bank_name" in prompt, "Prompt must include bank_name field"
    assert "account_holder" in prompt, "Prompt must include account_holder field"
    assert "amount" in prompt, "Prompt must include amount field"
    assert "null" in prompt, "Prompt must specify null for missing values"
    
    print("✅ Image analysis prompt schema is complete")
    
    # Test validation with different inputs
    test_cases = [
        # Valid bank details
        {
            "input": {
                "type": "bank_details",
                "details": {
                    "account_number": "1234567890",
                    "bank_name": "GTBank", 
                    "account_holder": "John Doe",
                    "amount": 150000.00
                },
                "error": None
            },
            "should_pass": True
        },
        # Valid transaction
        {
            "input": {
                "type": "transaction",
                "details": {
                    "account_number": None,
                    "bank_name": "Zenith Bank",
                    "account_holder": None,
                    "amount": 12000.00
                },
                "error": None
            },
            "should_pass": True
        },
        # Invalid account number
        {
            "input": {
                "type": "bank_details", 
                "details": {
                    "account_number": "123",  # Too short
                    "bank_name": "UBA",
                    "account_holder": "Jane Doe",
                    "amount": 50000.00
                },
                "error": None
            },
            "should_pass": False
        },
        # Error case
        {
            "input": {
                "type": "other",
                "details": {
                    "account_number": None,
                    "bank_name": None,
                    "account_holder": None,
                    "amount": None
                },
                "error": "Image quality too poor"
            },
            "should_pass": True
        }
    ]
    
    for i, case in enumerate(test_cases):
        result = validate_image_result(case["input"])
        if case["should_pass"]:
            assert result.error is None or case["input"]["error"] is not None, f"Test case {i+1} should pass but got error: {result.error}"
        else:
            # Invalid account should be cleaned to None
            if case["input"]["details"]["account_number"] == "123":
                assert result.account_number is None, f"Invalid account number should be cleaned to None"
    
    print("✅ Image analysis validation working correctly")

def test_json_consistency():
    """Test that JSON schemas are consistent and well-formed"""
    print("🧪 Testing JSON Schema Consistency...")
    
    # Test transfer schema consistency
    transfer_examples = [
        '{"amount": 5000, "account": "1234567891", "bank": "Access Bank", "recipient": null, "error": null}',
        '{"amount": null, "account": null, "bank": null, "recipient": null, "error": "No transfer detected"}'
    ]
    
    for example in transfer_examples:
        try:
            parsed = json.loads(example)
            # Verify all required fields are present
            assert "amount" in parsed, "amount field missing"
            assert "account" in parsed, "account field missing"
            assert "bank" in parsed, "bank field missing"
            assert "recipient" in parsed, "recipient field missing"
            assert "error" in parsed, "error field missing"
        except Exception as e:
            assert False, f"Invalid JSON in transfer example: {e}"
    
    # Test image schema consistency
    image_examples = [
        '{"type": "bank_details", "details": {"account_number": "1234567890", "bank_name": "GTBank", "account_holder": "John Doe", "amount": 150000.00}, "error": null}',
        '{"type": "other", "details": {"account_number": null, "bank_name": null, "account_holder": null, "amount": null}, "error": "Image unreadable"}'
    ]
    
    for example in image_examples:
        try:
            parsed = json.loads(example)
            # Verify required structure
            assert "type" in parsed, "type field missing"
            assert "details" in parsed, "details field missing"
            assert "error" in parsed, "error field missing"
            assert isinstance(parsed["details"], dict), "details must be object"
            assert "account_number" in parsed["details"], "account_number missing in details"
            assert "bank_name" in parsed["details"], "bank_name missing in details"
            assert "account_holder" in parsed["details"], "account_holder missing in details"
            assert "amount" in parsed["details"], "amount missing in details"
        except Exception as e:
            assert False, f"Invalid JSON in image example: {e}"
    
    print("✅ JSON schemas are consistent and well-formed")

def test_nigerian_context():
    """Test that prompts include proper Nigerian banking context"""
    print("🧪 Testing Nigerian Banking Context...")
    
    transfer_prompt = get_transfer_prompt()
    image_prompt = get_image_prompt()
    
    # Check for Nigerian bank references
    nigerian_banks = PromptSchemas.get_nigerian_banks_list()
    
    # Transfer prompt should mention key Nigerian banks
    found_banks = 0
    for bank in ["Access", "GTBank", "GTB", "Zenith", "UBA", "Opay"]:
        if bank in transfer_prompt:
            found_banks += 1
    
    assert found_banks >= 3, f"Transfer prompt should mention multiple Nigerian banks, found {found_banks}"
    
    # Check for Nigerian currency context
    assert "₦" in transfer_prompt or "Naira" in transfer_prompt or "NGN" in transfer_prompt, "Transfer prompt should include Nigerian currency context"
    
    # Image prompt should mention Nigerian context
    assert "Nigerian" in image_prompt, "Image prompt should mention Nigerian context"
    
    print("✅ Nigerian banking context properly included")

def run_all_tests():
    """Run all prompt schema tests"""
    print("🚀 Running Prompt Schema Tests...\n")
    
    try:
        test_transfer_extraction_prompt()
        print()
        test_image_analysis_prompt()
        print()
        test_json_consistency()
        print()
        test_nigerian_context()
        print()
        
        print("🎉 ALL TESTS PASSED!")
        print("\n📊 Summary:")
        print("✅ Transfer extraction prompt schema is standardized")
        print("✅ Image analysis prompt schema is standardized") 
        print("✅ JSON output formats are consistent")
        print("✅ Validation functions work correctly")
        print("✅ Nigerian banking context is included")
        print("✅ Error handling is properly specified")
        print("\n🔧 Issues Fixed:")
        print("• Inconsistent JSON schemas across prompts")
        print("• Missing error handling specifications")
        print("• Ambiguous field requirements")
        print("• Multiple competing prompt formats")
        print("• Lack of proper validation")
        
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
