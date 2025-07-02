"""
Paystack API Integration for Sofi AI
====================================
Handles virtual accounts, transfers, and customer management
"""

import os
import requests
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PaystackAPI:
    """Paystack API integration for Sofi AI banking services"""
    
    def __init__(self):
        """Initialize Paystack API with credentials"""
        self.secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        self.public_key = os.getenv("PAYSTACK_PUBLIC_KEY")
        self.base_url = "https://api.paystack.co"
        
        if not self.secret_key:
            raise ValueError("PAYSTACK_SECRET_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        logger.info("✅ Paystack API initialized")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request to Paystack"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            else:
                response = requests.request(
                    method.upper(), 
                    url, 
                    headers=self.headers, 
                    json=data
                )
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("status"):
                logger.error(f"Paystack API error: {result.get('message')}")
                return {"success": False, "error": result.get("message")}
            
            return {"success": True, "data": result.get("data")}
            
        except requests.RequestException as e:
            logger.error(f"Paystack request error: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Paystack unexpected error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_customer(self, email: str, first_name: str, last_name: str, phone: str = None) -> Dict:
        """Create a customer on Paystack"""
        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }
        
        if phone:
            data["phone"] = phone
        
        logger.info(f"Creating Paystack customer: {email}")
        return self._make_request("POST", "/customer", data)
    
    def create_dedicated_account(self, customer_code: str, preferred_bank: str = "wema-bank") -> Dict:
        """Create a dedicated virtual account for a customer"""
        data = {
            "customer": customer_code,
            "preferred_bank": preferred_bank
        }
        
        logger.info(f"Creating dedicated account for customer: {customer_code}")
        return self._make_request("POST", "/dedicated_account", data)
    
    def list_banks(self) -> Dict:
        """Get list of available banks"""
        logger.info("Fetching bank list from Paystack")
        return self._make_request("GET", "/bank", {"country": "nigeria"})
    
    def resolve_account_number(self, account_number: str, bank_code: str) -> Dict:
        """Resolve account number to get account holder name"""
        data = {
            "account_number": account_number,
            "bank_code": bank_code
        }
        
        logger.info(f"Resolving account: {account_number} at {bank_code}")
        return self._make_request("GET", "/bank/resolve", data)
    
    def create_transfer_recipient(self, name: str, account_number: str, bank_code: str) -> Dict:
        """Create a transfer recipient"""
        data = {
            "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN"
        }
        
        logger.info(f"Creating transfer recipient: {name} - {account_number}")
        return self._make_request("POST", "/transferrecipient", data)
    
    def initiate_transfer(self, amount: int, recipient_code: str, reason: str = "Sofi Transfer") -> Dict:
        """Initiate a transfer to a recipient"""
        data = {
            "source": "balance",
            "amount": amount * 100,  # Convert to kobo
            "recipient": recipient_code,
            "reason": reason
        }
        
        logger.info(f"Initiating transfer: ₦{amount} to {recipient_code}")
        return self._make_request("POST", "/transfer", data)
    
    def finalize_transfer(self, transfer_code: str, otp: str) -> Dict:
        """Finalize transfer with OTP (if required)"""
        data = {
            "transfer_code": transfer_code,
            "otp": otp
        }
        
        logger.info(f"Finalizing transfer: {transfer_code}")
        return self._make_request("POST", "/transfer/finalize_transfer", data)
    
    def verify_transaction(self, reference: str) -> Dict:
        """Verify a transaction by reference"""
        logger.info(f"Verifying transaction: {reference}")
        return self._make_request("GET", f"/transaction/verify/{reference}")
    
    def get_customer_dedicated_accounts(self, customer_code: str) -> Dict:
        """Get all dedicated accounts for a customer"""
        logger.info(f"Getting dedicated accounts for: {customer_code}")
        return self._make_request("GET", f"/dedicated_account", {"customer": customer_code})
    
    def send_money(self, amount: float, account_number: str, bank_code: str, 
                   account_name: str, narration: str = "Sofi Transfer") -> Dict:
        """Complete money transfer process"""
        try:
            # Step 1: Create transfer recipient
            recipient_result = self.create_transfer_recipient(
                name=account_name,
                account_number=account_number,
                bank_code=bank_code
            )
            
            if not recipient_result["success"]:
                return recipient_result
            
            recipient_code = recipient_result["data"]["recipient_code"]
            
            # Step 2: Initiate transfer
            transfer_result = self.initiate_transfer(
                amount=int(amount),
                recipient_code=recipient_code,
                reason=narration
            )
            
            if not transfer_result["success"]:
                return transfer_result
            
            transfer_data = transfer_result["data"]
            
            # Check if OTP is required
            if transfer_data.get("status") == "otp":
                return {
                    "success": True,
                    "requires_otp": True,
                    "transfer_code": transfer_data.get("transfer_code"),
                    "message": "OTP required to complete transfer"
                }
            
            return {
                "success": True,
                "requires_otp": False,
                "transfer_code": transfer_data.get("transfer_code"),
                "reference": transfer_data.get("reference"),
                "status": transfer_data.get("status"),
                "message": "Transfer initiated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error in send_money: {str(e)}")
            return {
                "success": False,
                "error": f"Transfer failed: {str(e)}"
            }

# Global instance
paystack_api = PaystackAPI()
