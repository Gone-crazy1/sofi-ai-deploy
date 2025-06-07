import requests
from monnify.Auth import get_monnify_token as get_auth_token

def send_money(amount, bank_code, account_number, narration, reference):
    base_url = "https://sandbox.monnify.com/api/v2/disbursements/single"
    token = get_auth_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "amount": amount,
        "reference": reference,
        "narration": narration,
        "bankCode": bank_code,
        "accountNumber": account_number,
        "currency": "NGN",
        "sourceAccountNumber": "2385369716"  # your virtual wallet account number
    }

    response = requests.post(base_url, json=payload, headers=headers)
    return response.json()

def create_virtual_account(first_name, last_name, bvn, token):
    """Mock implementation for creating a virtual account."""
    return {
        "accountNumber": "1234567890",
        "bankName": "Mock Bank",
    }
