import os
import requests
from typing import Optional, Dict
from monnify.Auth import get_monnify_token

class BankAPI:
    def __init__(self):
        self.base_url = os.getenv("MONNIFY_BASE_URL", "https://sandbox.monnify.com")

    async def verify_account(self, account_number: str, bank_code: str) -> Optional[Dict]:
        """Verify a bank account and return the account holder's name using Monnify's API"""
        try:
            token = get_monnify_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Monnify name enquiry endpoint
            url = f"{self.base_url}/api/v2/disbursements/account/validate"
            
            response = requests.get(
                url,
                params={
                    "accountNumber": account_number,
                    "bankCode": bank_code
                },
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["requestSuccessful"]:
                    return {
                        "account_name": data["responseBody"]["accountName"],
                        "account_number": account_number,
                        "bank_code": bank_code,
                        "verified": True
                    }
            return None
        except Exception as e:
            print(f"Error verifying account: {str(e)}")
            return None

    def get_bank_code(self, bank_name: str) -> Optional[str]:
        """Get the bank code for a given bank name"""
        # This would normally fetch from an API or database
        # For now, using a simple mapping of common Nigerian banks
        bank_codes = {
            "access": "044",
            "gtb": "058",
            "gtbank": "058",
            "zenith": "057",
            "first bank": "011",
            "uba": "033",
            "opay": "304",
            # Add more banks as needed
        }
        return bank_codes.get(bank_name.lower())
