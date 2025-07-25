# Renamed from 9psb_api.py to ninepsb_api.py

from utils.waas_auth import get_access_token
import requests
import os


class NINEPSBApi:
    def lookup_existing_wallet(self, bvn=None, phone=None):
        """
        Lookup an existing wallet in 9PSB by BVN or phone number.
        Returns wallet details if found, else None.
        """
        # You may need to adjust the endpoint and params to match 9PSB API docs
        if bvn:
            url = f"{self.base_url}/api/v1/wallet/bvn/{bvn}"
        elif phone:
            url = f"{self.base_url}/api/v1/wallet/phone/{phone}"
        else:
            return None
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "x-api-key": self.api_key,
            "x-secret-key": self.secret_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None
    def __init__(self, api_key, secret_key, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        # base_url should be the API root, e.g. 'http://102.216.128.75:9090/bank9ja/api/v2/k1'
        # NOT the /authenticate endpoint
        self.base_url = base_url

    def create_virtual_account(self, user_id, user_data):
        """
        Create a virtual account for a user.
        Usage:
            - Ensure .env NINEPSB_BASE_URL is set to API root, e.g. 'http://102.216.128.75:9090/bank9ja/api/v2/k1'
            - Do NOT use the /authenticate endpoint as base_url
        """
        token = get_access_token()
        url = f"{self.base_url}/api/v1/open_wallet"  # Correct endpoint for virtual account creation
        headers = {
            "Authorization": f"Bearer {token}",
            "x-api-key": self.api_key,
            "x-secret-key": self.secret_key,
            "Content-Type": "application/json"
        }
        import uuid
        # Ensure all required fields are present with sensible defaults
        # Map all required fields for 9PSB API
        # Convert dateOfBirth to dd/mm/yyyy if needed
        dob = user_data.get("dateOfBirth") or "05/05/1988"
        if dob and ("-" in dob and "/" not in dob):
            # Convert 'dd-mm-yyyy' to 'dd/mm/yyyy'
            dob = dob.replace("-", "/")
        # Map gender string to int: 1 for male, 2 for female
        gender_raw = user_data.get("gender") or "M"
        gender_map = {"M": 1, "F": 2, "male": 1, "female": 2, 1: 1, 2: 2}
        gender = gender_map.get(str(gender_raw).strip().lower().capitalize(), 1)
        phone_value = user_data.get("phoneNo") or user_data.get("phoneNumber") or user_data.get("phone") or "08055006199"
        other_names_value = user_data.get("otherNames")
        if other_names_value is None or str(other_names_value).strip() == "":
            other_names_value = user_data.get("middleName") or user_data.get("other_names") or "N/A"
        if other_names_value is None or str(other_names_value).strip() == "":
            other_names_value = "N/A"
        payload = {
            "userId": user_id,
            "firstName": user_data.get("firstName") or user_data.get("first_name") or "David",
            "lastName": user_data.get("lastName") or user_data.get("last_name") or "Adeleke",
            "otherNames": other_names_value,
            "gender": gender,
            "dateOfBirth": dob,
            "phoneNo": phone_value,
            "phoneNumber": phone_value,
            "email": user_data.get("email") or "david.adeleke@email.com",
            "bvn": user_data.get("bvn") or "22190239861",
            "channel": user_data.get("channel") or "APP",
            # "userName": user_data.get("userName") or user_data.get("username") or "pipinstall",  # REMOVED to fix fullName
            "password": user_data.get("password") or "Sofi@1234",
            "transactionTrackingRef": user_data.get("transactionTrackingRef") or str(uuid.uuid4()),
            **user_data
        }
        # Remove userName if present in user_data
        if "userName" in payload:
            del payload["userName"]
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        try:
            return response.json()
        except Exception:
            return {"error": "Invalid response", "status_code": response.status_code, "text": response.text}

    # Placeholder for other 9PSB API methods
    def verify_deposit(self, transaction_id):
        pass
