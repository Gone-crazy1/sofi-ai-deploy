import pytest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_supabase():
    with patch('main.supabase') as mock:        # Mock virtual account data
        mock_response = MagicMock()
        mock_response.data = [{
            'id': 1,
            'user_id': 1,
            'accountNumber': '1234567890',  # Match the format used in production
            'accountName': 'John Doe',
            'bankName': 'Moniepoint MFB'
        }]
        mock.table().select().eq().execute.return_value = mock_response
        yield mock

@pytest.fixture
def mock_monnify():
    with patch('utils.bank_api.BankAPI') as mock:
        mock.return_value.create_virtual_account.return_value = {
            'accountNumber': '1234567890',
            'accountName': 'John Doe',
            'bankName': 'Moniepoint MFB',
            'accountReference': 'ref123'
        }
        yield mock

def test_create_virtual_account(client, mock_supabase, mock_monnify):
    # Test virtual account creation
    payload = {
        "message": {
            "chat": {"id": "123456789"},
            "text": "I want to create a virtual account"
        }
    }
    response = client.post("/webhook_incoming", json=payload)
    assert response.status_code == 200
    response_data = response.get_json()
    
    # Verify webhook success response
    assert response_data["success"] is True

def test_verify_virtual_account(client, mock_supabase):
    with patch('main.send_reply') as mock_send_reply, \
         patch('main.save_chat_message') as mock_save_chat, \
         patch('main.get_chat_history') as mock_history, \
         patch('main.check_virtual_account') as mock_check_va:
        
        mock_save_chat.return_value = True
        mock_history.return_value = []
        mock_check_va.return_value = {
            'accountNumber': '1234567890',
            'accountName': 'Test User',
            'bankName': 'Test Bank'
        }
        
        # Test account verification query
        payload = {
            "message": {
                "chat": {"id": "123456789"},
                "text": "What's my account number?"
            }
        }
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200
        response_data = response.get_json()
        
        # Verify webhook success response
        assert response_data["success"] is True
        
        # Verify that check_virtual_account was called to get account details
        mock_check_va.assert_called_once_with("123456789")
