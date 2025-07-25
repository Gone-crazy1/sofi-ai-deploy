# utils/waas_auth.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("NINEPSB_USERNAME")
PASSWORD = os.getenv("NINEPSB_PASSWORD")
CLIENT_ID = os.getenv("NINEPSB_CLIENT_ID")
CLIENT_SECRET = os.getenv("NINEPSB_CLIENT_SECRET")
AUTH_URL = os.getenv("NINEPSB_AUTH_URL")

def get_access_token():
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "clientId": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
    }
    try:
        response = requests.post(AUTH_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("accessToken")
    except requests.RequestException as e:
        print("❌ Token request failed:", e)
        print("🔁 Response:", response.text if 'response' in locals() else "No response")
        return None
