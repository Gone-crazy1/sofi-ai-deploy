import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json
from PIL import Image
from io import BytesIO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

@pytest.fixture
def mock_openai():
    with patch('main.openai') as mock:
        # Mock image analysis
        mock.ChatCompletion.create.return_value = MagicMock(
            choices=[{
                'message': {
                    'content': json.dumps({
                        "intent": "analyze_image",
                        "details": {
                            "description": "An image of a bank statement showing recent transactions.",
                            "image_type": "bank_statement",
                            "transfer_type": "image"
                        }
                    })
                }
            }]
        )
        # Mock audio transcription
        mock.Audio.transcribe.return_value = {
            'text': 'Send five hundred naira to John'
        }
        # Mock the intent detection for voice message
        mock.ChatCompletion.create.side_effect = [
            MagicMock(
                choices=[{
                    'message': {
                        'content': json.dumps({
                            "intent": "transfer",
                            "details": {
                                "amount": 500,
                                "recipient_name": "John",
                                "account_number": None,
                                "bank": None,
                                "transfer_type": "voice"
                            }
                        })
                    }
                }]
            )
        ]
        yield mock

@pytest.fixture
def mock_audio_processor():
    with patch('utils.media_processor.AudioSegment') as mock:
        mock.from_file.return_value = MagicMock()
        mock.from_file.return_value.export.return_value = MagicMock()
        yield mock

def create_test_image():
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def test_image_processing(client, mock_openai):
    # Create a mock image file
    mock_image = create_test_image()
    
    # Mock Telegram photo message
    payload = {
        "message": {
            "chat": {"id": "123456789"},
            "photo": [{
                "file_id": "photo123",
                "file_size": 1234,
                "width": 800,
                "height": 600
            }]
        }
    }
    
    # Mock Telegram API calls
    with patch('requests.get') as mock_get, \
         patch('main.send_reply') as mock_send_reply:
        
        mock_get.return_value = MagicMock(content=mock_image)
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200
        
        # Verify response format
        response_data = response.get_json()
        assert response_data["success"] is True

def test_voice_processing(client, mock_openai, mock_audio_processor):
    # Create a mock voice file
    mock_voice = b'fake voice data'
    
    # Mock Telegram voice message
    payload = {
        "message": {
            "chat": {"id": "123456789"},
            "voice": {
                "file_id": "voice123",
                "duration": 5,
                "mime_type": "audio/ogg",
                "file_size": 1024
            }
        }
    }    # Mock file operations and chat message saving
    with patch('requests.get') as mock_get, \
         patch('builtins.open', mock_open(read_data=mock_voice)), \
         patch('os.path.exists') as mock_exists, \
         patch('main.save_chat_message') as mock_save_chat, \
         patch('main.check_virtual_account') as mock_check_virtual_account, \
         patch('main.get_chat_history') as mock_get_chat_history, \
         patch('main.send_reply') as mock_send_reply:
        
        mock_get.return_value = MagicMock(content=mock_voice)
        mock_exists.return_value = True
        mock_save_chat.return_value = True  # Mock successful save
        mock_check_virtual_account.return_value = {}  # No virtual account
        mock_get_chat_history.return_value = []  # Empty chat history
        mock_send_reply.return_value = None  # Mock send_reply
        
        response = client.post("/webhook_incoming", json=payload)
        assert response.status_code == 200
        
        response_data = response.get_json()
        assert response_data["success"] is True

def test_unsupported_media(client):
    # Test unsupported file type
    payload = {
        "message": {
            "chat": {"id": "123456789"},
            "document": {
                "file_id": "doc123",
                "file_name": "document.pdf",
                "mime_type": "application/pdf",
                "file_size": 1024
            }
        }
    }
    
    response = client.post("/webhook_incoming", json=payload)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["success"] is True
