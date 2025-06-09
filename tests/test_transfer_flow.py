import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from main import app, detect_intent, generate_pos_style_receipt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test Intent Detection
@patch('main.openai.ChatCompletion.create')
def test_detect_intent(mock_openai):
    mock_openai.return_value = MagicMock(
        choices=[{
            'message': {
                'content': '{"intent": "transfer"}'
            }
        }]
    )

    user_message = "Send ₦500 to John at Access Bank, 0123456789"
    response = detect_intent(user_message)
    assert "intent" in response
    assert response["intent"] == "transfer"

def test_detect_intent():
    assert detect_intent("Hello Sofi!")["intent"] == "greeting"
    assert detect_intent("What is the weather?")["intent"] == "inquiry"

# Test Receipt Generation
def test_generate_pos_style_receipt():
    receipt = generate_pos_style_receipt(
        sender_name="Adeola",
        amount=500,
        recipient_name="John",
        recipient_account="0123456789",
        recipient_bank="Access Bank",
        balance=4500,
        transaction_id="12345678"
    )
    assert "Adeola" in receipt
    assert "₦500.00" in receipt
    assert "John" in receipt
    assert "0123456789" in receipt
    assert "Access Bank" in receipt
    assert "4500" in receipt

# Mock required environment variables for testing
@patch.dict(os.environ, {
    "TELEGRAM_BOT_TOKEN": "mock_token",
    "OPENAI_API_KEY": "mock_api_key",
    "SUPABASE_URL": "mock_url",
    "SUPABASE_KEY": "mock_key",
})
def test_environment_variables():
    # Ensure the application initializes without missing environment variables
    from main import app  # Re-import to apply mocked environment
    assert app is not None

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Automatically mock environment variables for all tests."""
    with patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "mock_token",
        "OPENAI_API_KEY": "mock_api_key",
        "SUPABASE_URL": "mock_url",
        "SUPABASE_KEY": "mock_key",
    }):
        yield
