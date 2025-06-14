import os
import requests
from typing import Optional, Dict
from monnify.Auth import get_monnify_token

class BankAPI:
    def __init__(self):
        self.base_url = os.getenv("MONNIFY_BASE_URL", "https://sandbox.monnify.com")

    async def execute_transfer(self, transfer_data: dict) -> dict:
        """Execute a real transfer via Monnify disbursement API"""
        try:
            from monnify.Transfers import send_money
            from datetime import datetime
            import uuid
            
            # Get bank code from bank name
            bank_code = self.get_bank_code(transfer_data['recipient_bank'])
            if not bank_code:
                return {
                    'success': False,
                    'error': f"Unsupported bank: {transfer_data['recipient_bank']}"
                }
            
            # Generate unique reference
            reference = f"TRF_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Call Monnify disbursement API
            result = send_money(
                amount=transfer_data['amount'],
                bank_code=bank_code,
                account_number=transfer_data['recipient_account'],
                narration=transfer_data.get('narration', 'Transfer via Sofi AI'),
                reference=reference
            )
            
            # Process Monnify response
            if result.get('requestSuccessful'):
                return {
                    'success': True,
                    'transaction_id': reference,
                    'reference': reference,
                    'status': 'success',
                    'message': 'Transfer completed successfully',
                    'monnify_response': result
                }
            else:
                error_message = result.get('responseMessage', 'Transfer failed')
                return {
                    'success': False,
                    'error': error_message,
                    'monnify_response': result
                }
                
        except Exception as e:
            logger.error(f"Transfer execution error: {str(e)}")
            return {
                'success': False,
                'error': f"Transfer processing error: {str(e)}"
            }

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
                if data["requestSuccessful"]:                    return {
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
        """Get the bank code for a given bank name - COMPREHENSIVE NIGERIAN BANKS & FINTECH"""
        # Complete mapping of Nigerian banks and fintech platforms
        bank_codes = {
            # Traditional Banks
            "access": "044",
            "access bank": "044",
            "gtb": "058",
            "gtbank": "058",
            "guaranty trust": "058",
            "gt bank": "058",
            "zenith": "057",
            "zenith bank": "057",
            "first bank": "011",
            "firstbank": "011",
            "fbn": "011",
            "uba": "033",
            "united bank for africa": "033",
            "fidelity": "070",
            "fidelity bank": "070",
            "fcmb": "214",
            "first city monument bank": "214",
            "sterling": "232",
            "sterling bank": "232",
            "wema": "035",
            "wema bank": "035",
            "union": "032",
            "union bank": "032",
            "polaris": "076",
            "polaris bank": "076",
            "keystone": "082",
            "keystone bank": "082",
            "eco bank": "050",
            "ecobank": "050",
            "heritage": "030",
            "heritage bank": "030",
            "stanbic": "221",
            "stanbic ibtc": "221",
            "standard chartered": "068",
            "citi bank": "023",
            "citibank": "023",
            
            # Fintech Banks & Digital Banks
            "opay": "304",
            "moniepoint": "50515",
            "monie point": "50515",
            "moneypoint": "50515",
            "kuda": "50211",
            "kuda bank": "50211",
            "palmpay": "999991",
            "palm pay": "999991",
            "vfd": "566",
            "vfd microfinance bank": "566",
            "9psb": "120001",
            "9 psb": "120001",
            "9mobile psb": "120001",
            "carbon": "565",
            "carbon microfinance bank": "565",
            "rubies": "125",
            "rubies microfinance bank": "125",
            "microvis": "566",
            "microvis microfinance bank": "566",
            "raven": "50746",
            "raven bank": "50746",
            "mint": "50304",
            "mint finex": "50304",
            "sparkle": "51310",
            "sparkle microfinance bank": "51310",
            "taj": "302",
            "taj bank": "302",
            "sun trust": "100",
            "suntrust": "100",
            "titan": "102",
            "titan trust bank": "102",
            "coronation": "559",
            "coronation merchant bank": "559",
            "rand": "559",
            "rand merchant bank": "559",
            
            # Other Microfinance & Digital Platforms
            "alat": "035",  # Wema ALAT
            "alat by wema": "035",
            "gtworld": "058",  # GTBank digital
            "diamond": "063",
            "diamond bank": "063",  # Now part of Access
            "providus": "101",
            "providus bank": "101",
            "jaiz": "301",
            "jaiz bank": "301",
            "lotus": "303",
            "lotus bank": "303",
            
            # Add more as needed
        }
        return bank_codes.get(bank_name.lower())
