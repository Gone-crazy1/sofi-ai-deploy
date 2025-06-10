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
    print("Response Data:", response_data)  # Log the response data    # Verify the webhook was processed successfully
    assert "success" in response_data
    assert response_data["success"] is True
