import requests
from monnify.Auth import get_monnify_token as get_auth_token
import logging

logger = logging.getLogger(__name__)

def send_money(amount, bank_code, account_number, narration, reference):
    """Send money via Monnify disbursement API"""
    try:
        base_url = "https://sandbox.monnify.com/api/v2/disbursements/single"
        token = get_auth_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "amount": float(amount),
            "reference": reference,
            "narration": narration,
            "bankCode": bank_code,
            "accountNumber": account_number,
            "currency": "NGN",
            "sourceAccountNumber": "2385369716"  # your virtual wallet account number
        }

        logger.info(f"Initiating transfer: ₦{amount} to {account_number} ({bank_code}) - Ref: {reference}")
        
        response = requests.post(base_url, json=payload, headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('requestSuccessful'):
            logger.info(f"Transfer successful: {reference}")
            return {
                'requestSuccessful': True,
                'responseMessage': 'Transfer completed successfully',
                'responseBody': result.get('responseBody', {}),
                'status': 'success'
            }
        else:
            error_msg = result.get('responseMessage', 'Transfer failed')
            logger.error(f"Transfer failed: {error_msg} - Response: {result}")
            return {
                'requestSuccessful': False,
                'responseMessage': error_msg,
                'responseBody': result.get('responseBody', {}),
                'status': 'failed'
            }
            
    except Exception as e:
        logger.error(f"Transfer error: {str(e)}")
        return {
            'requestSuccessful': False,
            'responseMessage': f'Transfer processing error: {str(e)}',
            'status': 'error'
        }

def create_virtual_account(first_name, last_name, bvn, token):
    """Mock implementation for creating a virtual account."""
    return {
        "accountNumber": "1234567890",
        "bankName": "Mock Bank",
    }
