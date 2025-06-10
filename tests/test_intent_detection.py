import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, detect_intent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def mock_openai():
    with patch('openai.ChatCompletion.create') as mock:
        yield mock

def test_basic_intents():
    with patch('main.openai.ChatCompletion.create') as mock_openai:
        test_cases = [
            {
                "input": "Hello Sofi!",
                "expected": {
                    "intent": "greeting",
                    "details": {
                        "greeting_type": "general"
                    }
                },
                "description": "Basic greeting"
            },
            {
                "input": "What's my balance?",
                "expected": {
                    "intent": "balance_inquiry",
                    "details": {}
                },
                "description": "Balance inquiry"
            },
            {
                "input": "Send 500 to John",
                "expected": {
                    "intent": "transfer",
                    "details": {
                        "amount": 500,
                        "recipient_name": "John",
                        "account_number": None,
                        "bank": None,
                        "transfer_type": "text"
                    }
                },
                "description": "Simple transfer"
            },
            {
                "input": "Help",
                "expected": {
                    "intent": "help",
                    "details": {}
                },
                "description": "Help request"
            }
        ]

        for case in test_cases:
            mock_openai.return_value = MagicMock(
                choices=[{
                    'message': {
                        'content': json.dumps(case["expected"])
                    }
                }]
            )
            
            result = detect_intent(case["input"])
            assert result["intent"] == case["expected"]["intent"], f"Failed: {case['description']}"

def test_complex_transfer_intents():
    with patch('main.openai.ChatCompletion.create') as mock_openai:
        test_cases = [
            {
                "input": "Send 500 to John at Access Bank, 0123456789",
                "expected": {
                    "intent": "transfer",
                    "details": {
                        "amount": 500,
                        "recipient_name": "John",
                        "bank": "Access Bank",
                        "account_number": "0123456789",
                        "transfer_type": "text"
                    }
                }
            },
            {
                "input": "Transfer 1000 naira to Mary's Zenith account 9876543210",
                "expected": {
                    "intent": "transfer",
                    "details": {
                        "amount": 1000,
                        "recipient_name": "Mary",
                        "bank": "Zenith Bank",
                        "account_number": "9876543210",
                        "transfer_type": "text"
                    }
                }
            }
        ]

        for case in test_cases:
            mock_openai.return_value = MagicMock(
                choices=[{
                    'message': {
                        'content': json.dumps(case["expected"])
                    }
                }]
            )
            result = detect_intent(case["input"])
            assert result["intent"] == "transfer"
            assert result["details"]["amount"] == case["expected"]["details"]["amount"]
            assert result["details"]["recipient_name"] == case["expected"]["details"]["recipient_name"]
            assert result["details"]["bank"] == case["expected"]["details"]["bank"]
            assert result["details"]["account_number"] == case["expected"]["details"]["account_number"]
            assert result["details"]["transfer_type"] == "text"

def test_multi_step_intents():
    with patch('main.openai.ChatCompletion.create') as mock_openai:
        test_cases = [
            {
                "input": "Yes, proceed with the transfer",
                "expected": {
                    "intent": "confirm_transfer",
                    "details": {}
                },
                "description": "Transfer confirmation"
            },
            {
                "input": "No, cancel the transfer",
                "expected": {
                    "intent": "cancel_transfer",
                    "details": {}
                },
                "description": "Transfer cancellation"
            },
            {
                "input": "Create a new account for me",
                "expected": {
                    "intent": "create_account",
                    "details": {}
                },
                "description": "Account creation"
            }
        ]

        for case in test_cases:
            mock_openai.return_value = MagicMock(
                choices=[{
                    'message': {
                        'content': json.dumps(case["expected"])
                    }
                }]
            )
            
            result = detect_intent(case["input"])
            assert result["intent"] == case["expected"]["intent"], f"Failed: {case['description']}"

def test_error_handling():
    # Test malformed API response
    with patch('main.openai.ChatCompletion.create') as mock_openai:
        mock_openai.return_value = MagicMock(
            choices=[{
                'message': {
                    'content': 'invalid json'
                }
            }]
        )
        
        result = detect_intent("Hello")
        assert result["intent"] == "unknown"
        
        # Test missing intent in response
        mock_openai.return_value = MagicMock(
            choices=[{
                'message': {
                    'content': '{"foo": "bar"}'
                }
            }]
        )
        
        result = detect_intent("Hello")
        assert result["intent"] == "unknown"
        
        # Test API error
        mock_openai.side_effect = Exception("API Error")
        result = detect_intent("Hello")
        assert result["intent"] == "unknown"
