"""
🏦 REAL MONNIFY TRANSFER INTEGRATION
===================================

This module integrates with Monnify's actual Transfer API to process real money transfers.
No more dummy endpoints - this calls the real Monnify API for transfers.
"""

import os
import requests
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from utils.nigerian_banks import get_bank_by_name, get_popular_banks

load_dotenv()
logger = logging.getLogger(__name__)

class MonnifyTransferAPI:
    """Real Monnify Transfer API integration"""
    
    def __init__(self):
        self.api_key = os.getenv("MONNIFY_API_KEY")
        self.secret_key = os.getenv("MONNIFY_SECRET_KEY")
        self.contract_code = os.getenv("MONNIFY_CONTRACT_CODE")
        self.base_url = "https://api.monnify.com"  # Production URL
        # For testing: "https://sandbox.monnify.com"
        
        if not all([self.api_key, self.secret_key, self.contract_code]):
            logger.error("Monnify credentials not configured properly")
    
    def _get_access_token(self):
        """Get OAuth access token from Monnify"""
        try:
            import base64
            
            # Create basic auth header
            credentials = f"{self.api_key}:{self.secret_key}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("responseBody", {}).get("accessToken")
            else:
                logger.error(f"Failed to get Monnify access token: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Monnify access token: {e}")
            return None
    
    def validate_account(self, account_number: str, bank_code: str) -> Dict:
        """Validate account number with bank using Monnify"""
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {"success": False, "error": "Authentication failed"}
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Monnify account validation endpoint
            response = requests.get(
                f"{self.base_url}/api/v1/disbursements/account/validate",
                headers=headers,
                params={
                    "accountNumber": account_number,
                    "bankCode": bank_code
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("requestSuccessful"):
                    account_info = data.get("responseBody", {})
                    return {
                        "success": True,
                        "account_name": account_info.get("accountName"),
                        "account_number": account_number,
                        "bank_code": bank_code
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("responseMessage", "Account validation failed")
                    }
            else:
                return {
                    "success": False,
                    "error": f"Validation request failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error validating account: {e}")
            return {"success": False, "error": str(e)}
    
    def initiate_transfer(self, amount: float, account_number: str, bank_code: str, 
                         narration: str = "Transfer from Sofi AI", reference: str = None) -> Dict:
        """Initiate real money transfer using Monnify API"""
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {"success": False, "error": "Authentication failed"}
            
            if not reference:
                reference = f"SOFI_{int(datetime.now().timestamp())}_{account_number[-4:]}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "amount": float(amount),
                "reference": reference,
                "narration": narration,
                "destinationBankCode": bank_code,
                "destinationAccountNumber": account_number,
                "currency": "NGN",
                "sourceAccountNumber": os.getenv("MONNIFY_SOURCE_ACCOUNT"),  # Your main account
                "async": False  # Wait for completion
            }
            
            logger.info(f"Initiating Monnify transfer: ₦{amount:,.2f} to {account_number}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/disbursements/single",
                headers=headers,
                json=payload,
                timeout=60  # Longer timeout for transfers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("requestSuccessful"):
                    transfer_data = data.get("responseBody", {})
                    return {
                        "success": True,
                        "reference": transfer_data.get("reference"),
                        "status": transfer_data.get("status"),
                        "amount": amount,
                        "fee": transfer_data.get("fee", 0),
                        "message": "Transfer initiated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("responseMessage", "Transfer failed")
                    }
            else:
                error_msg = f"Transfer request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error initiating transfer: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_transfer_status(self, reference: str) -> Dict:
        """Check transfer status using Monnify API"""
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {"success": False, "error": "Authentication failed"}
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/api/v1/disbursements/single/summary",
                headers=headers,
                params={"reference": reference},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("requestSuccessful"):
                    return {
                        "success": True,
                        "status_data": data.get("responseBody", {})
                    }
            
            return {"success": False, "error": "Failed to get transfer status"}
            
        except Exception as e:
            logger.error(f"Error getting transfer status: {e}")
            return {"success": False, "error": str(e)}

# Enhanced transfer processing function
async def process_real_transfer(chat_id: str, amount: float, account_number: str, 
                               bank_name: str = None, recipient_name: str = None) -> Dict:
    """
    Process real money transfer using Monnify API
    
    Args:
        chat_id: User's telegram chat ID
        amount: Transfer amount
        account_number: Recipient account number
        bank_name: Bank name (optional)
        recipient_name: Recipient name (optional)
    
    Returns:
        Dict with transfer result
    """
    try:
        # Initialize Monnify API
        monnify = MonnifyTransferAPI()
        
        # Step 1: Resolve bank code
        bank_info = None
        if bank_name:
            bank_info = get_bank_by_name(bank_name)
        
        if not bank_info:
            # If no bank provided or not found, try to detect from account number patterns
            # Some banks have specific account number patterns
            if account_number.startswith("810") and len(account_number) == 10:
                bank_info = get_bank_by_name("opay")
            elif account_number.startswith("617") and len(account_number) == 10:
                bank_info = get_bank_by_name("access")
            else:
                return {
                    "success": False,
                    "error": "Bank not specified or recognized. Please specify the bank name.",
                    "suggestion": "Try: 'Send 5k to 1234567890 Access Bank'"
                }
        
        bank_code = bank_info["code"]
        bank_display_name = bank_info["name"]
        
        # Step 2: Validate account number
        logger.info(f"Validating account {account_number} with {bank_display_name}")
        validation_result = monnify.validate_account(account_number, bank_code)
        
        if not validation_result["success"]:
            return {
                "success": False,
                "error": f"Invalid account number: {validation_result['error']}",
                "suggestion": "Please check the account number and try again."
            }
        
        validated_account_name = validation_result["account_name"]
        
        # Step 3: Check user balance (assuming this function exists)
        try:
            from utils.balance_helper import get_user_balance
            user_balance = await get_user_balance(chat_id)
        except:
            user_balance = 0
        
        if user_balance < amount:
            return {
                "success": False,
                "error": f"Insufficient balance. You have ₦{user_balance:,.2f}, but need ₦{amount:,.2f}",
                "balance": user_balance
            }
        
        # Step 4: Calculate fees (Monnify typically charges ₦10-50 for transfers)
        transfer_fee = 25.0  # Standard fee, could be dynamic based on amount
        total_deduction = amount + transfer_fee
        
        if user_balance < total_deduction:
            return {
                "success": False,
                "error": f"Insufficient balance including fee. Need ₦{total_deduction:,.2f} (₦{amount:,.2f} + ₦{transfer_fee} fee), but you have ₦{user_balance:,.2f}",
                "balance": user_balance,
                "fee": transfer_fee
            }
        
        # Step 5: Initiate transfer
        narration = f"Transfer from Sofi AI to {validated_account_name}"
        if recipient_name:
            narration = f"Transfer from Sofi AI to {recipient_name}"
        
        logger.info(f"Initiating transfer: ₦{amount} to {account_number} ({bank_display_name})")
        transfer_result = monnify.initiate_transfer(
            amount=amount,
            account_number=account_number,
            bank_code=bank_code,
            narration=narration
        )
        
        if transfer_result["success"]:
            # Step 6: Deduct from user balance
            try:
                from utils.balance_helper import deduct_from_balance
                await deduct_from_balance(chat_id, total_deduction)
            except Exception as e:
                logger.error(f"Failed to deduct balance: {e}")
            
            return {
                "success": True,
                "reference": transfer_result["reference"],
                "amount": amount,
                "fee": transfer_fee,
                "recipient": validated_account_name,
                "bank": bank_display_name,
                "account_number": account_number,
                "message": f"✅ Transfer successful! ₦{amount:,.2f} sent to {validated_account_name} ({bank_display_name})"
            }
        else:
            return {
                "success": False,
                "error": f"Transfer failed: {transfer_result['error']}"
            }
    
    except Exception as e:
        logger.error(f"Error processing transfer: {e}")
        return {
            "success": False,
            "error": f"Transfer processing failed: {str(e)}"
        }

# Get suggested banks for user
def get_bank_suggestions() -> str:
    """Get formatted list of popular banks"""
    popular_banks = get_popular_banks()
    banks_list = []
    
    for i, bank in enumerate(popular_banks[:10], 1):  # Top 10
        banks_list.append(f"{i}. {bank['name']} ({bank['type']})")
    
    return "Popular banks:\n" + "\n".join(banks_list)
