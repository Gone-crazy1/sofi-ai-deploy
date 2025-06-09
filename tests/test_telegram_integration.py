import pytest
import requests
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def client():
    from main import app
    app.testing = True
    with app.test_client() as client:
        yield client

def test_telegram_integration(client):
    # Simulate a Telegram message payload
    payload = {
        "message": {
            "chat": {"id": 123456789},
            "text": "Hello Sofi!"
        }
    }

    # Send the payload to the webhook endpoint
    response = client.post("/webhook_incoming", json=payload)

    # Assert the response status code
    assert response.status_code == 200

    # Log the response data for debugging
    response_data = response.get_json()
    print("Response Data:", response_data)  # Log the response data

    # Assert Sofi's reply for greeting intent
    assert "response" in response_data
    assert "Hello! How can I assist you today?" in response_data["response"]
