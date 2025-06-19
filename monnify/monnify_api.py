"""
Monnify API Integration for Sofi AI Banking Service
Official Banking Partner: Monnify

This module handles:
- Virtual account creation
- Bank transfers
- Transaction verification
- Webhook handling
"""

import os
import requests
import base64
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class MonnifyAPI:
    """Official Monnify API Integration for Sofi AI"""
    
    def __init__(self):
        """Initialize Monnify API with credentials"""
        self.api_key = os.getenv("MONNIFY_API_KEY")
        self.secret_key = os.getenv("MONNIFY_SECRET_KEY")
        self.contract_code = os.getenv("MONNIFY_CONTRACT_CODE")
        self.base_url = os.getenv("MONNIFY_BASE_URL", "https://sandbox.monnify.com")
        
        # Validate credentials
        if not all([self.api_key, self.secret_key, self.contract_code]):
            logger.error("Monnify credentials not found in environment variables")
            raise ValueError("Missing Monnify credentials")
        
        self.access_token = None
        self.token_expires_at = 0
        
        logger.info("Monnify API initialized successfully")
    
    def _get_access_token(self) -> str:
        """Get or refresh Monnify access token"""
        # Check if token is still valid (with 5 minute buffer)
        if self.access_token and time.time() < (self.token_expires_at - 300):
            return self.access_token
        
        # Get new token
        credentials = f"{self.api_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                if auth_data.get("requestSuccessful"):
                    self.access_token = auth_data["responseBody"]["accessToken"]
                    # Tokens typically last 1 hour
                    self.token_expires_at = time.time() + 3300  # 55 minutes
                    logger.info("Monnify access token obtained successfully")
                    return self.access_token
                else:
                    raise Exception(f"Authentication failed: {auth_data.get('responseMessage')}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get Monnify access token: {e}")
            raise
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to Monnify API"""
        access_token = self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.info(f"Monnify {method} {endpoint}: {response.status_code}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Monnify API error: {error_msg}")
                return {"requestSuccessful": False, "responseMessage": error_msg}
                
        except Exception as e:
            logger.error(f"Monnify API request failed: {e}")
            return {"requestSuccessful": False, "responseMessage": str(e)}
    
    def create_virtual_account(self, customer_data: Dict) -> Dict:
        """
        Create virtual account(s) for a customer
        
        Args:
            customer_data: Dict containing customer information
                - email: Customer email
                - first_name: Customer first name
                - last_name: Customer last name
                - phone: Customer phone (optional)
                - user_id: Unique user identifier
        
        Returns:
            Dict with success status and account details
        """
        try:
            # Generate unique account reference
            account_reference = f"sofi_{customer_data.get('user_id', uuid.uuid4().hex[:8])}_{int(time.time())}"
              # Optimize account name for Monnify's limitations
            optimized_name = self._optimize_account_name(
                customer_data['first_name'], 
                customer_data['last_name']
            )
            
            # Prepare account creation data
            account_data = {
                "accountReference": account_reference,
                "accountName": optimized_name,
                "currencyCode": "NGN",
                "contractCode": self.contract_code,
                "customerEmail": customer_data["email"],
                "customerName": optimized_name,
                "getAllAvailableBanks": True
            }
            
            # Add phone if provided
            if customer_data.get("phone"):
                account_data["customerPhoneNumber"] = customer_data["phone"]
            
            # Create virtual account
            response = self._make_request("POST", "/api/v2/bank-transfer/reserved-accounts", account_data)
            
            if response.get("requestSuccessful"):
                account_info = response["responseBody"]
                accounts = account_info.get("accounts", [])
                
                return {
                    "success": True,
                    "accounts": [
                        {
                            "bank_name": acc["bankName"],
                            "bank_code": acc["bankCode"],
                            "account_number": acc["accountNumber"],
                            "account_name": acc["accountName"],
                            "provider": "monnify"
                        }
                        for acc in accounts
                    ],
                    "account_reference": account_reference,
                    "customer_code": account_info.get("reservationReference"),
                    "status": account_info.get("status"),
                    "raw_response": response
                }
            else:
                return {
                    "success": False,
                    "error": response.get("responseMessage", "Failed to create virtual account")
                }
                
        except Exception as e:
            logger.error(f"Error creating virtual account: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_account_name(self, account_number: str, bank_code: str) -> Dict:
        """
        Verify account name for a given account number and bank
        
        Args:
            account_number: Account number to verify
            bank_code: Bank code
            
        Returns:
            Dict with account verification details
        """
        try:
            # Monnify account verification endpoint
            verify_data = {
                "accountNumber": account_number,
                "bankCode": bank_code
            }
            
            response = self._make_request("POST", "/api/v1/disbursements/account/validate?", verify_data)
            
            if response.get("requestSuccessful"):
                account_info = response["responseBody"]
                return {
                    "success": True,
                    "account_name": account_info.get("accountName"),
                    "account_number": account_info.get("accountNumber"),
                    "bank_code": account_info.get("bankCode")
                }
            else:
                return {
                    "success": False,
                    "error": response.get("responseMessage", "Account verification failed")
                }
                
        except Exception as e:
            logger.error(f"Error verifying account: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_transfer(self, transfer_data: Dict) -> Dict:
        """
        Execute bank transfer via Monnify
        
        Args:
            transfer_data: Dict containing transfer details
                - amount: Amount to transfer
                - recipient_account: Recipient account number
                - recipient_bank: Recipient bank code
                - recipient_name: Recipient name (optional)
                - narration: Transfer description
                - reference: Unique reference (optional)
        
        Returns:
            Dict with transfer status and details
        """
        try:
            # Generate unique reference if not provided
            reference = transfer_data.get("reference", f"SOFI_{uuid.uuid4().hex[:8]}")
            
            # Prepare transfer data
            disbursement_data = {
                "amount": transfer_data["amount"],
                "reference": reference,
                "narration": transfer_data.get("narration", "Transfer via Sofi AI"),
                "bankCode": transfer_data["recipient_bank"],
                "accountNumber": transfer_data["recipient_account"],
                "currency": "NGN",
                "sourceAccountNumber": self.contract_code
            }
            
            # Add recipient name if provided
            if transfer_data.get("recipient_name"):
                disbursement_data["accountName"] = transfer_data["recipient_name"]
            
            # Execute transfer
            response = self._make_request("POST", "/api/v2/disbursements/single", disbursement_data)
            
            if response.get("requestSuccessful"):
                transfer_info = response["responseBody"]
                return {
                    "success": True,
                    "transaction_id": transfer_info.get("reference"),
                    "reference": reference,
                    "status": transfer_info.get("status"),
                    "amount": transfer_info.get("amount"),
                    "fee": transfer_info.get("fee"),
                    "message": "Transfer initiated successfully",
                    "raw_response": response
                }
            else:
                return {
                    "success": False,
                    "error": response.get("responseMessage", "Transfer failed")
                }
                
        except Exception as e:
            logger.error(f"Error executing transfer: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_balance(self) -> Dict:
        """
        Get account balance from Monnify
        
        Returns:
            Dict with balance information
        """
        try:
            response = self._make_request("GET", f"/api/v2/disbursements/wallet-balance?accountNumber={self.contract_code}")
            
            if response.get("requestSuccessful"):
                balance_info = response["responseBody"]
                return {
                    "success": True,
                    "balance": balance_info.get("availableBalance", 0),
                    "currency": "NGN",
                    "account_number": self.contract_code
                }
            else:
                return {
                    "success": False,
                    "error": response.get("responseMessage", "Failed to get balance")
                }
                
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_banks(self) -> Dict:
        """
        Get list of supported banks
        
        Returns:
            Dict with list of banks
        """
        try:
            response = self._make_request("GET", "/api/v1/banks")
            
            if response.get("requestSuccessful"):
                banks = response["responseBody"]
                return {
                    "success": True,
                    "data": banks,
                    "count": len(banks)
                }
            else:
                return {
                    "success": False,
                    "error": response.get("responseMessage", "Failed to get banks")
                }
                
        except Exception as e:
            logger.error(f"Error getting banks: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_transaction(self, reference: str) -> Dict:
        """
        Verify transaction status
        
        Args:
            reference: Transaction reference
              Returns:
            Dict with transaction details
        """
        try:
            response = self._make_request("GET", f"/api/v2/transactions/{reference}")
            
            if response.get("requestSuccessful"):
                transaction_info = response["responseBody"]
                return {
                    "success": True,
                    "transaction": transaction_info,
                    "status": transaction_info.get("paymentStatus"),
                    "amount": transaction_info.get("amountPaid"),
                    "reference": transaction_info.get("transactionReference")
                }
            else:
                return {
                    "success": False,
                    "error": response.get("responseMessage", "Transaction not found")
                }
                
        except Exception as e:
            logger.error(f"Error verifying transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _optimize_account_name(self, first_name: str, last_name: str) -> str:
        """
        Optimize account name for Monnify's 3-character limitation
        
        Based on testing, Monnify truncates account names to exactly 3 characters.
        We need to work within this severe limitation.
        
        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            
        Returns:
            3-character optimized account name
        """
        # Remove extra spaces and convert to title case
        first_name = first_name.strip().title()
        last_name = last_name.strip().title()
        
        # Strategy 1: Use first 3 characters of first name if >= 3 chars
        if len(first_name) >= 3:
            return first_name[:3]
        
        # Strategy 2: First name + first char of last name (if space allows)
        if len(first_name) == 2 and last_name:
            return f"{first_name}{last_name[0]}"
        
        # Strategy 3: First name + space + first char of last name
        if len(first_name) == 1 and last_name:
            return f"{first_name} {last_name[0]}"
        
        # Strategy 4: Just the first name if no last name
        if len(first_name) <= 3:
            return first_name
        
        # Fallback: First 3 characters of first name
        return first_name[:3]
