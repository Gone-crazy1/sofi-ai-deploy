import pytest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.memory import save_chat_message, get_chat_history, clear_chat_history
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def mock_supabase():
    with patch('utils.memory.supabase') as mock:
        yield mock

def test_save_chat_message(mock_supabase):
    # Test saving a chat message
    chat_id = "123456789"
    role = "user"
    content = "Hello Sofi!"
    
    mock_supabase.table.return_value.insert.return_value.execute.return_value = True
    
    result = asyncio.run(save_chat_message(chat_id, role, content))
    assert result == True
    
    # Verify Supabase insert was called with correct data
    mock_supabase.table.assert_called_once_with("chat_history")
    mock_supabase.table.return_value.insert.assert_called_once()
    insert_data = mock_supabase.table.return_value.insert.call_args[0][0]
    assert insert_data["chat_id"] == chat_id
    assert insert_data["role"] == role
    assert insert_data["content"] == content

def test_get_chat_history(mock_supabase):
    # Mock chat history data
    mock_data = [
        {"role": "assistant", "content": "Hi!", "timestamp": "2024-01-01T00:00:01"},
        {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"}
    ]
    
    mock_result = MagicMock()
    mock_result.data = mock_data
    mock_supabase.table.return_value.select.return_value.eq.return_value.order\
        .return_value.limit.return_value.execute.return_value = mock_result
    
    # Test retrieving chat history
    chat_id = "123456789"
    history = asyncio.run(get_chat_history(chat_id))
    
    # Verify correct number of messages returned
    assert len(history) == 2
    
    # Verify message format - order should be reversed for chronological display
    assert history[0]["role"] == "user"  # Oldest message first
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi!"

def test_clear_chat_history(mock_supabase):
    # Test clearing chat history
    chat_id = "123456789"
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = True
    
    result = asyncio.run(clear_chat_history(chat_id))
    assert result == True
    
    # Verify Supabase delete was called
    mock_supabase.table.assert_called_once_with("chat_history")
    mock_supabase.table.return_value.delete.assert_called_once()
    mock_supabase.table.return_value.delete.return_value.eq.assert_called_once_with("chat_id", chat_id)

def test_conversation_memory_integration(mock_supabase):
    chat_id = "123456789"
    
    # Mock successful message saving
    mock_supabase.table.return_value.insert.return_value.execute.return_value = True
    
    # Save a sequence of messages
    messages = [
        ("user", "Hi Sofi!"),
        ("assistant", "Hello! How can I help you?"),
        ("user", "What's my balance?"),
        ("assistant", "Your balance is 5,000")
    ]
    
    for role, content in messages:
        result = asyncio.run(save_chat_message(chat_id, role, content))
        assert result == True
    
    # Mock chat history retrieval - reverse order for chronological display
    mock_history = [
        {"role": role, "content": content, "timestamp": f"2024-01-01T00:00:0{i}"}
        for i, (role, content) in enumerate(reversed(messages))  # Reverse to simulate DB ordering
    ]
    
    mock_result = MagicMock()
    mock_result.data = mock_history
    mock_supabase.table.return_value.select.return_value.eq.return_value.order\
        .return_value.limit.return_value.execute.return_value = mock_result
    
    # Retrieve and verify chat history
    history = asyncio.run(get_chat_history(chat_id))
    assert len(history) == len(messages)
    
    # Verify messages are in chronological order (oldest first)
    for i, msg in enumerate(history):
        assert msg["role"] == messages[i][0]
        assert msg["content"] == messages[i][1]
