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
def test_detect_transfer_intent(mock_openai):
    mock_openai.return_value = MagicMock(
        choices=[{
            'message': {
                'content': '{"intent": "transfer", "amount": 500, "recipient": {"name": "John", "bank": "Access Bank", "account": "0123456789"}}'
            }
        }]
    )

    user_message = "Send ₦500 to John at Access Bank, 0123456789"
    response = detect_intent(user_message)
    assert "intent" in response
    assert response["intent"] == "transfer"
    assert response["amount"] == 500
    assert response["recipient"]["name"] == "John"
    assert response["recipient"]["bank"] == "Access Bank"
    assert response["recipient"]["account"] == "0123456789"

@pytest.fixture
def mock_supabase():
    with patch('main.save_chat_message') as save_mock, \
         patch('main.get_chat_history') as history_mock, \
         patch('main.supabase') as mock_supabase, \
         patch('utils.memory.save_chat_message') as memory_save_mock, \
         patch('utils.memory.get_chat_history') as memory_history_mock:
        
        save_mock.return_value = True
        memory_save_mock.return_value = True
        history_mock.return_value = []
        memory_history_mock.return_value = []
        
        # Mock virtual account check
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{
                'telegram_chat_id': '123456789',
                'accountNumber': '1234567890',
                'accountName': 'Test User',
                'balance': 5000.0,
                'bankName': 'Test Bank'
            }]
        )
        
        # Mock user existence check  
        mock_user_response = MagicMock()
        mock_user_response.data = [{
            'telegram_chat_id': '123456789',
            'first_name': 'Test User'
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_response
        
        yield mock_supabase

@pytest.fixture
def mock_openai():
    with patch('main.openai.ChatCompletion.create') as mock:
        # Set up default response structure that matches real OpenAI API
        mock.return_value = {
            'choices': [{
                'message': {
                    'content': '{"intent": "general", "response": "I understand your request."}'
                }
            }]
        }
        yield mock

def test_detect_other_intents(mock_openai):
    mock_openai.return_value = MagicMock(
        choices=[{
            'message': {
                'content': '{"intent": "greeting"}'
            }
        }]
    )
    assert detect_intent("Hello Sofi!")["intent"] == "greeting"

    mock_openai.return_value = MagicMock(
        choices=[{
            'message': {
                'content': '{"intent": "inquiry"}'
            }
        }]
    )
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
    assert "4,500.00" in receipt  # Check for formatted balance

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

@pytest.fixture
def mock_bank_api():
    with patch('main.BankAPI') as mock:
        mock_instance = MagicMock()
        mock_instance.execute_transfer.return_value = {'success': True, 'transaction_id': 'TEST123'}
        mock_instance.verify_account.return_value = {
            'account_name': 'John Doe',
            'bank_name': 'Access Bank',
            'account_number': '0123456789'
        }
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def mock_supabase():
    with patch('main.supabase') as mock:
        # Mock the table select chain
        table_mock = MagicMock()
        mock.table.return_value = table_mock

        select_mock = MagicMock()
        table_mock.select.return_value = select_mock

        # Mock the user query response
        user_response = MagicMock()
        user_response.data = [{
            'id': 1,
            'telegram_chat_id': '123456789',
            'first_name': 'Test',
            'last_name': 'User',
            'balance': 10000,
            'pin': '1234'
        }]

        # Mock the virtual account query response
        va_response = MagicMock()
        va_response.data = [{
            'id': 1,
            'user_id': 1,
            'account_number': '1234567890',
            'account_name': 'Test User',
            'bank_name': 'Test Bank'
        }]

        # Set up the mock chain
        select_mock.eq.return_value.execute.side_effect = [user_response, va_response]
        yield mock

def test_complete_transfer_flow(client, mock_openai, mock_bank_api, mock_supabase):
    with patch('main.send_reply') as mock_send_reply, \
         patch('main.save_chat_message') as mock_save_chat, \
         patch('main.get_chat_history') as mock_history, \
         patch('main.check_virtual_account') as mock_check_va:
        
        mock_save_chat.return_value = True
        mock_history.return_value = []
        mock_check_va.return_value = {
            'accountNumber': '1234567890',
            'accountName': 'Test User',
            'bankName': 'Test Bank',
            'balance': 5000.0
        }
        
        # Mock transfer intent detection with correct response structure
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'I can help you with your transfer request. Let me process that for you.'
                }
            }]
        }

        # Test the initial transfer request
        payload = {
            "message": {
                "chat": {"id": "123456789"},
                "text": "Send ₦500 to John at Access Bank, 0123456789"
            }
        }
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200
        
        # Mock confirmation intent
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'Transfer has been processed successfully.'
                }
            }]
        }
        
        # Test transfer confirmation
        payload = {
            "message": {
                "chat": {"id": "123456789"},
                "text": "Yes, proceed with the transfer"
            }
        }
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200

def test_insufficient_balance_transfer(client, mock_openai, mock_bank_api, mock_supabase):
    with patch('main.send_reply') as mock_send_reply, \
         patch('main.save_chat_message') as mock_save_chat, \
         patch('main.get_chat_history') as mock_history, \
         patch('main.check_virtual_account') as mock_check_va:
        
        mock_save_chat.return_value = True
        mock_history.return_value = []
        mock_check_va.return_value = {
            'accountNumber': '1234567890',
            'accountName': 'Test User',
            'bankName': 'Test Bank',
            'balance': 1000.0  # Lower balance than requested
        }
        
        # Mock transfer intent with amount larger than balance
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'Sorry, you have insufficient balance for this transfer.'
                }
            }]
        }

        payload = {
            "message": {
                "chat": {"id": "123456789"},
                "text": "Send ₦10,000 to John at Access Bank, 0123456789"
            }
        }
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200
        
        # Verify the response indicates insufficient balance
        mock_send_reply.assert_called()
        call_args = mock_send_reply.call_args[0][1]  # Get the message argument
        assert "insufficient" in call_args.lower() or "balance" in call_args.lower()
    
    # Verify bank API was not called
    mock_bank_api.return_value.initiate_transfer.assert_not_called()

def test_transfer_cancellation(client, mock_openai, mock_bank_api, mock_supabase):
    with patch('main.send_reply') as mock_send_reply, \
         patch('main.save_chat_message') as mock_save_chat, \
         patch('main.get_chat_history') as mock_history, \
         patch('main.check_virtual_account') as mock_check_va:
        
        mock_save_chat.return_value = True
        mock_history.return_value = []
        mock_check_va.return_value = {
            'accountNumber': '1234567890',
            'accountName': 'Test User',
            'bankName': 'Test Bank',
            'balance': 5000.0
        }
        
        # Mock transfer intent
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'I can help you with your transfer. Please provide more details.'
                }
            }]
        }
        
        # Initial transfer request
        payload = {
            "message": {
                "chat": {"id": "123456789"},
                "text": "Send ₦500 to John at Access Bank, 0123456789"
            }
        }
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200
        
        # Mock cancellation intent
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'Transfer has been cancelled successfully.'
                }
            }]
        }
        
        # Test transfer cancellation
        payload = {
            "message": {
                "chat": {"id": "123456789"},
                "text": "No, cancel the transfer"
            }
        }
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200
