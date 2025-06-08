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
                'content': '{"intent": "transfer", "amount": 500, "recipient_name": "John", "account_number": "0123456789", "bank_name": "Access Bank"}'
            }
        }]
    )

    user_message = "Send ₦500 to John at Access Bank, 0123456789"
    response = detect_intent(user_message)
    assert "intent" in response
    assert "transfer" in response

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

# Test Full Transfer Flow
@patch('main.send_money')
@patch('main.supabase.table')
def test_full_transfer_flow(mock_supabase, mock_send_money, client):
    # Mock Supabase PIN validation
    mock_supabase.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = {
        'data': {'pin': '1234'}
    }

    # Mock Monnify API response
    mock_send_money.return_value = {
        'requestSuccessful': True,
        'responseBody': {'status': 'SUCCESS'}
    }

    # Simulate user interaction
    chat_id = 12345
    user_state = {
        chat_id: {
            "intent": "transfer",
            "step": "awaiting_pin",
            "transfer_data": {
                "amount": 500,
                "recipient_name": "John",
                "account_number": "0123456789",
                "bank_name": "Access Bank"
            }
        }
    }

    with patch('main.user_state', user_state):
        response = client.post('/process_transfer', json={"chat_id": chat_id})
        assert response.status_code == 200
        assert "status" in response.json
        assert response.json["status"] == "ok"

# Mock required environment variables for testing
@patch.dict(os.environ, {
    "TELEGRAM_BOT_TOKEN": "mock_token",
    "OPENAI_API_KEY": "mock_api_key",
    "SUPABASE_URL": "mock_url",
    "SUPABASE_KEY": "mock_key",
    "MONNIFY_API_KEY": "mock_api_key",
    "MONNIFY_SECRET_KEY": "mock_secret_key",
    "MONNIFY_CONTRACT_CODE": "mock_contract_code"
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
        "MONNIFY_API_KEY": "mock_api_key",
        "MONNIFY_SECRET_KEY": "mock_secret_key",
        "MONNIFY_CONTRACT_CODE": "mock_contract_code"
    }):
        yield
