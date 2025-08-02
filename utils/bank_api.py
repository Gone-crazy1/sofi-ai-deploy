"""
🏦 PAYSTACK-ONLY BANKING API FOR SOFI AI
All banking operations powered by Paystack APIs only.
No Monnify code - pure Paystack implementation.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class BankAPI:
    """Paystack-powered banking operations for Sofi AI"""
    
    def __init__(self):
        self.provider = "paystack"  # Only Paystack
        self.paystack_secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        self.paystack_base_url = "https://api.paystack.co"
        
        if not self.paystack_secret_key:
            raise ValueError("PAYSTACK_SECRET_KEY is required")
            
        logger.info("BankAPI initialized with Paystack as the only banking partner")
    
    def _paystack_headers(self) -> Dict[str, str]:
        """Get Paystack API headers"""
        return {
            "Authorization": f"Bearer {self.paystack_secret_key}",
            "Content-Type": "application/json"
        }
    
    async def verify_account_name(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """
        Verify bank account using Paystack Account Resolution API
        
        Args:
            account_number: Account number to verify
            bank_code: Bank code (e.g., "044" for Access Bank)
            
        Returns:
            Dict with verification result
        """
        try:
            logger.info(f"🔍 Verifying account {account_number} with bank code {bank_code}")
            
            url = f"{self.paystack_base_url}/bank/resolve"
            params = {
                "account_number": account_number,
                "bank_code": bank_code
            }
            
            response = requests.get(url, headers=self._paystack_headers(), params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                account_name = result["data"]["account_name"]
                logger.info(f"✅ Account verified: {account_name}")
                
                return {
                    'success': True,
                    'account_name': account_name,
                    'account_number': account_number,
                    'bank_code': bank_code,
                    'provider': 'paystack'
                }
            else:
                error_msg = result.get("message", "Account verification failed")
                logger.error(f"❌ Account verification failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': 'paystack'
                }
                
        except Exception as e:
            logger.error(f"❌ Error verifying account: {e}")
            return {
                'success': False,
                'error': f"Verification error: {str(e)}",
                'provider': 'paystack'
            }
    
    async def transfer_money(self, amount: float, account_number: str, bank_name: str, 
                           narration: str = None, reference: str = None) -> Dict[str, Any]:
        """
        Transfer money using Paystack Transfer API
        
        Args:
            amount: Amount to transfer (in Naira)
            account_number: Recipient account number
            bank_name: Bank name (will be converted to bank code)
            narration: Transfer description
            reference: Unique reference for the transfer
            
        Returns:
            Dict with transfer result
        """
        try:
            # Convert bank name to bank code
            bank_code = self._get_bank_code(bank_name)
            if not bank_code:
                return {
                    'success': False,
                    'error': f"Unsupported bank: {bank_name}. Please try banks like UBA, GTB, Access, Opay, Kuda, etc."
                }
            
            # First verify the account
            verification = await self.verify_account_name(account_number, bank_code)
            if not verification['success']:
                return {
                    'success': False,
                    'error': f"Could not verify account: {verification['error']}"
                }
            
            # Create transfer recipient
            recipient_data = {
                "type": "nuban",
                "name": verification['account_name'],
                "account_number": account_number,
                "bank_code": bank_code,
                "currency": "NGN"
            }
            
            recipient_response = requests.post(
                f"{self.paystack_base_url}/transferrecipient",
                headers=self._paystack_headers(),
                json=recipient_data
            )
            
            if recipient_response.status_code != 201:
                return {
                    'success': False,
                    'error': "Failed to create transfer recipient"
                }
            
            recipient_code = recipient_response.json()["data"]["recipient_code"]
            
            # Initiate transfer
            transfer_data = {
                "source": "balance",
                "amount": int(amount * 100),  # Convert to kobo
                "recipient": recipient_code,
                "reason": narration or f"Transfer via Sofi AI",
                "reference": reference or f"SOFI_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            transfer_response = requests.post(
                f"{self.paystack_base_url}/transfer",
                headers=self._paystack_headers(),
                json=transfer_data
            )
            
            transfer_result = transfer_response.json()
            
            if transfer_response.status_code == 200 and transfer_result.get("status"):
                logger.info(f"✅ Transfer initiated: ₦{amount:,.2f} to {verification['account_name']}")
                return {
                    'success': True,
                    'transfer_code': transfer_result["data"]["transfer_code"],
                    'reference': transfer_result["data"]["reference"],
                    'amount': amount,
                    'recipient_name': verification['account_name'],
                    'status': transfer_result["data"]["status"],
                    'provider': 'paystack'
                }
            else:
                error_msg = transfer_result.get("message", "Transfer failed")
                logger.error(f"❌ Transfer failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': 'paystack'
                }
                
        except Exception as e:
            logger.error(f"❌ Transfer error: {e}")
            return {
                'success': False,
                'error': f"Transfer error: {str(e)}",
                'provider': 'paystack'
            }
    
    def _get_bank_code(self, bank_name: str) -> Optional[str]:
        """Convert bank name to Paystack bank code - INCLUDING OPAY"""
        bank_codes = {
            # Traditional Banks
            "access": "044", "access bank": "044",
            "gtb": "058", "gtbank": "058", "guaranty trust bank": "058",
            "zenith": "057", "zenith bank": "057",
            "uba": "033", "united bank for africa": "033",
            "firstbank": "011", "first bank": "011", "first bank of nigeria": "011",
            "union": "032", "union bank": "032",
            "fidelity": "070", "fidelity bank": "070",
            "sterling": "232", "sterling bank": "232",
            "stanbic": "221", "stanbic ibtc": "221",
            "wema": "035", "wema bank": "035",
            "heritage": "030", "heritage bank": "030",
            "keystone": "082", "keystone bank": "082",
            "fcmb": "214", "first city monument bank": "214",
            "unity": "215", "unity bank": "215",
            "polaris": "076", "polaris bank": "076",
            "citi": "023", "citibank": "023",
            "ecobank": "050",
            "standard chartered": "068",
            
            # Fintech & Digital Banks
            "opay": "999992",  # ✅ FIXED: Was 999991, now correct 999992
            "palmpay": "999991",  # ✅ CORRECT: PalmPay code
            "kuda": "50211", "kuda bank": "50211",
            "moniepoint": "50515", "moniepoint mfb": "50515",
            "monie point": "50515", "moniepoint bank": "50515",
            "moniepoint microfinance bank": "50515",
            "moniepont": "50515",  # common typo
            "moniepiont": "50515",  # common typo
            "carbon": "565", "carbon microfinance bank": "565",
            "rubies": "125", "rubies mfb": "125",
            "sparkle": "51310", "sparkle microfinance bank": "51310",
            "mint": "50304", "mint mfb": "50304",
            "vfd": "566", "vfd microfinance bank": "566",
            "taj": "302", "taj bank": "302",
            "lotus": "303", "lotus bank": "303",
            "coronation": "559", "coronation merchant bank": "559",
            "rand": "305", "rand merchant bank": "305",
            "9psb": "120001", "9 psb": "120001", "9mobile psb": "120001",
            "9mobile": "120001", "9payment service bank": "120001",
            "9mobile 9payment service bank": "120001"
        }
        
        return bank_codes.get(bank_name.lower().strip())
    
    def get_bank_code(self, bank_name: str) -> Optional[str]:
        """Public method to get bank code - wrapper for _get_bank_code"""
        return self._get_bank_code(bank_name)
    
    def verify_account(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """Synchronous wrapper for verify_account_name"""
        try:
            # Check if we're already in an async context
            import asyncio
            try:
                # If there's already a running loop, we can't use run_until_complete
                loop = asyncio.get_running_loop()
                logger.warning("Already in event loop - creating task instead")
                # Create a future and set the result
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._sync_verify_account_name, account_number, bank_code)
                    result = future.result(timeout=30)
            except RuntimeError:
                # No running loop, safe to create new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.verify_account_name(account_number, bank_code))
                loop.close()
            
            # Convert the result format to match expected format
            if result.get('success'):
                return {
                    'verified': True,
                    'account_name': result.get('account_name'),
                    'bank_name': result.get('bank_name'),
                    'account_number': account_number,
                    'bank_code': bank_code
                }
            else:
                return {
                    'verified': False,
                    'error': result.get('error', 'Account verification failed')
                }
        except Exception as e:
            logger.error(f"Error in synchronous verify_account: {e}")
            return {
                'verified': False,
                'error': f"Error verifying account: {str(e)}"
            }
    
    def _sync_verify_account_name(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """Synchronous version of verify_account_name for thread execution"""
        try:
            response = requests.get(
                f"{self.paystack_base_url}/bank/resolve",
                headers=self._paystack_headers(),
                params={
                    "account_number": account_number,
                    "bank_code": bank_code
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") and "data" in result:
                    account_data = result["data"]
                    return {
                        'success': True,
                        'account_name': account_data.get('account_name'),
                        'bank_name': account_data.get('bank_name', 'Unknown Bank'),
                        'account_number': account_number
                    }
            
            return {
                'success': False,
                'error': 'Account verification failed'
            }
            
        except Exception as e:
            logger.error(f"Error in sync verify_account_name: {e}")
            return {
                'success': False,
                'error': f"Error verifying account: {str(e)}"
            }
    
    async def get_banks(self) -> List[Dict[str, Any]]:
        """Get list of banks supported by Paystack"""
        try:
            response = requests.get(
                f"{self.paystack_base_url}/bank",
                headers=self._paystack_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") and "data" in result:
                    return result["data"]
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching banks: {e}")
            return []
    
    async def get_transaction_status(self, reference: str) -> Dict[str, Any]:
        """Get transaction status from Paystack"""
        try:
            response = requests.get(
                f"{self.paystack_base_url}/transaction/verify/{reference}",
                headers=self._paystack_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status"):
                    return {
                        'success': True,
                        'status': result["data"]["status"],
                        'amount': result["data"]["amount"] / 100,  # Convert from kobo
                        'reference': result["data"]["reference"],
                        'provider': 'paystack'
                    }
            
            return {
                'success': False,
                'error': "Transaction not found",
                'provider': 'paystack'
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'paystack'
            }
