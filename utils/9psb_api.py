# utils/9psb_api.py

import requests
import logging

class NINEPSBApi:
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url

    def create_virtual_account(self, user_id: str, user_data: dict) -> dict:
        url = f"{self.base_url}/api/v1/virtual-accounts/create"
        headers = {
            "Content-Type": "application/json",
            "apiKey": self.api_key,
            "secretKey": self.secret_key
        }
        payload = {
            "customerId": user_id,
            "firstName": user_data.get("first_name"),
            "lastName": user_data.get("last_name"),
            "email": user_data.get("email"),
            "phoneNumber": user_data.get("phone")
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()  # or .get("data") if needed
        except Exception as e:
            logging.error(f"9PSB create_virtual_account error: {e}")
            return {"success": False, "error": str(e)}

    def verify_deposit(self, account_number: str, amount: float) -> dict:
        # Implement when 9PSB gives webhook or status-check endpoint
        pass
