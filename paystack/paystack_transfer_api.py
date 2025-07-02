"""
Paystack Transfer API Integration
Handles money transfers, recipients, and transfer verification
Based on official Paystack documentation
"""

import os
import requests
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class PaystackTransferAPI:
    """Paystack Transfer API integration for sending money"""
    
    def __init__(self):
        """Initialize Paystack Transfer API"""
        self.secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        self.base_url = "https://api.paystack.co"
        
        if not self.secret_key:
            raise ValueError("PAYSTACK_SECRET_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        logger.info("✅ Paystack Transfer API initialized")
    
    def create_transfer_recipient(self, account_number: str, bank_code: str, 
                                name: str, currency: str = "NGN") -> Dict[str, Any]:
        """
        Create a transfer recipient
        
        Args:
            account_number: Recipient's account number
            bank_code: Bank code (e.g., "058" for GTB)
            name: Account holder's name
            currency: Currency (default: NGN)
            
        Returns:
            Dict containing recipient data or error
        """
        try:
            url = f"{self.base_url}/transferrecipient"
            
            payload = {
                "type": "nuban",
                "name": name,
                "account_number": account_number,
                "bank_code": bank_code,
                "currency": currency
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            result = response.json()
            
            # Debug logging
            logger.info(f"🔍 Recipient creation response: Status {response.status_code}, Data: {result}")
            
            if response.status_code in [200, 201] and result.get("status") is True:
                logger.info(f"✅ Transfer recipient created: {result['data']['recipient_code']}")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to create recipient: Status={response.status_code}, Result={result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating transfer recipient: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def initiate_transfer(self, recipient_code: str, amount: int, 
                         reason: str = "Transfer", reference: str = None) -> Dict[str, Any]:
        """
        Initiate a transfer to a recipient
        
        Args:
            recipient_code: Recipient code from create_transfer_recipient
            amount: Amount in kobo (e.g., 100000 = ₦1,000)
            reason: Transfer reason/description
            reference: Optional transfer reference
            
        Returns:
            Dict containing transfer data or error
        """
        try:
            url = f"{self.base_url}/transfer"
            
            payload = {
                "source": "balance",
                "amount": amount,
                "recipient": recipient_code,
                "reason": reason
            }
            
            if reference:
                payload["reference"] = reference
            
            response = requests.post(url, json=payload, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Transfer initiated: {result['data']['transfer_code']}")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to initiate transfer: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error initiating transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def finalize_transfer(self, transfer_code: str, otp: str) -> Dict[str, Any]:
        """
        Finalize a transfer that requires OTP
        
        Args:
            transfer_code: Transfer code from initiate_transfer
            otp: OTP received on registered phone number
            
        Returns:
            Dict containing finalized transfer data or error
        """
        try:
            url = f"{self.base_url}/transfer/finalize_transfer"
            
            payload = {
                "transfer_code": transfer_code,
                "otp": otp
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Transfer finalized: {transfer_code}")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to finalize transfer: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error finalizing transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_transfer(self, reference: str) -> Dict[str, Any]:
        """
        Verify the status of a transfer
        
        Args:
            reference: Transfer reference
            
        Returns:
            Dict containing transfer verification data
        """
        try:
            url = f"{self.base_url}/transfer/verify/{reference}"
            
            response = requests.get(url, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Transfer verified: {reference}")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to verify transfer: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error verifying transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def fetch_transfer(self, transfer_id_or_code: str) -> Dict[str, Any]:
        """
        Fetch details of a specific transfer
        
        Args:
            transfer_id_or_code: Transfer ID or code
            
        Returns:
            Dict containing transfer details
        """
        try:
            url = f"{self.base_url}/transfer/{transfer_id_or_code}"
            
            response = requests.get(url, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to fetch transfer: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_transfers(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        List transfers on your integration
        
        Args:
            page: Page number (default: 1)
            per_page: Records per page (default: 50)
            
        Returns:
            Dict containing list of transfers
        """
        try:
            url = f"{self.base_url}/transfer"
            params = {
                "page": page,
                "perPage": per_page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                return {
                    "success": True,
                    "data": result["data"],
                    "meta": result.get("meta", {})
                }
            else:
                logger.error(f"❌ Failed to list transfers: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error listing transfers: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_money(self, account_number: str, bank_code: str, account_name: str,
                   amount: float, reason: str = "Transfer") -> Dict[str, Any]:
        """
        Complete money transfer flow: create recipient + initiate transfer
        
        Args:
            account_number: Recipient's account number
            bank_code: Bank code
            account_name: Account holder's name
            amount: Amount in Naira (will be converted to kobo)
            reason: Transfer reason
            
        Returns:
            Dict containing transfer result
        """
        try:
            # Convert amount to kobo
            amount_kobo = int(amount * 100)
            
            # Step 1: Create transfer recipient
            recipient_result = self.create_transfer_recipient(
                account_number=account_number,
                bank_code=bank_code,
                name=account_name
            )
            
            if not recipient_result["success"]:
                return recipient_result
            
            recipient_code = recipient_result["data"]["recipient_code"]
            
            # Step 2: Initiate transfer
            transfer_result = self.initiate_transfer(
                recipient_code=recipient_code,
                amount=amount_kobo,
                reason=reason
            )
            
            if transfer_result["success"]:
                transfer_data = transfer_result["data"]
                
                # Check if OTP is required
                if transfer_data.get("status") == "otp":
                    return {
                        "success": True,
                        "requires_otp": True,
                        "transfer_code": transfer_data["transfer_code"],
                        "message": "Transfer requires OTP verification",
                        "data": transfer_data
                    }
                else:
                    return {
                        "success": True,
                        "requires_otp": False,
                        "message": "Transfer completed successfully",
                        "data": transfer_data
                    }
            else:
                return transfer_result
                
        except Exception as e:
            logger.error(f"❌ Error in send_money: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_banks(self) -> Dict[str, Any]:
        """
        Get list of supported banks (uses Paystack's bank list)
        
        Returns:
            Dict containing list of banks
        """
        try:
            url = f"{self.base_url}/bank"
            
            response = requests.get(url, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to get banks: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting banks: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def resolve_account(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """
        Resolve account number to get account name
        
        Args:
            account_number: Account number to resolve
            bank_code: Bank code
            
        Returns:
            Dict containing account details
        """
        try:
            url = f"{self.base_url}/bank/resolve"
            params = {
                "account_number": account_number,
                "bank_code": bank_code
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to resolve account: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error resolving account: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def initiate_bulk_transfer(self, transfers: List[Dict], currency: str = "NGN") -> Dict[str, Any]:
        """
        Initiate multiple transfers in a single request
        
        Args:
            transfers: List of transfer objects with amount, recipient, reference, reason
            currency: Currency (default: NGN)
            
        Returns:
            Dict containing bulk transfer results or error
        """
        try:
            url = f"{self.base_url}/transfer/bulk"
            
            payload = {
                "currency": currency,
                "source": "balance",
                "transfers": transfers
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Bulk transfer initiated: {len(transfers)} transfers")
                return {
                    "success": True,
                    "data": result["data"],
                    "message": result.get("message")
                }
            else:
                logger.error(f"❌ Failed to initiate bulk transfer: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error initiating bulk transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def bulk_create_transfer_recipients(self, recipients: List[Dict]) -> Dict[str, Any]:
        """
        Create multiple transfer recipients in batches
        
        Args:
            recipients: List of recipient objects with type, name, account_number, bank_code
            
        Returns:
            Dict containing created recipients data or error
        """
        try:
            url = f"{self.base_url}/transferrecipient/bulk"
            
            payload = {
                "batch": recipients
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Bulk recipients created: {len(result['data']['success'])} successful")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to create bulk recipients: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating bulk recipients: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_transfer_recipients(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        List transfer recipients available on your integration
        
        Args:
            page: Page number to retrieve
            per_page: Number of records per page
            
        Returns:
            Dict containing recipients list or error
        """
        try:
            url = f"{self.base_url}/transferrecipient"
            
            params = {
                "page": page,
                "perPage": per_page
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Retrieved {len(result['data'])} recipients")
                return {
                    "success": True,
                    "data": result["data"],
                    "meta": result.get("meta", {})
                }
            else:
                logger.error(f"❌ Failed to list recipients: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error listing recipients: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def fetch_transfer_recipient(self, recipient_id_or_code: str) -> Dict[str, Any]:
        """
        Fetch details of a transfer recipient
        
        Args:
            recipient_id_or_code: Recipient ID or code
            
        Returns:
            Dict containing recipient details or error
        """
        try:
            url = f"{self.base_url}/transferrecipient/{recipient_id_or_code}"
            
            response = requests.get(url, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Retrieved recipient: {result['data']['name']}")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to fetch recipient: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching recipient: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_transfer_recipient(self, recipient_id_or_code: str, 
                                name: str = None, email: str = None) -> Dict[str, Any]:
        """
        Update transfer recipient details
        
        Args:
            recipient_id_or_code: Recipient ID or code
            name: New name for recipient
            email: New email for recipient
            
        Returns:
            Dict containing updated recipient data or error
        """
        try:
            url = f"{self.base_url}/transferrecipient/{recipient_id_or_code}"
            
            payload = {}
            if name:
                payload["name"] = name
            if email:
                payload["email"] = email
            
            if not payload:
                return {
                    "success": False,
                    "error": "No update data provided"
                }
            
            response = requests.put(url, json=payload, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Updated recipient: {result['data']['name']}")
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                logger.error(f"❌ Failed to update recipient: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error updating recipient: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_transfer_recipient(self, recipient_id_or_code: str) -> Dict[str, Any]:
        """
        Delete a transfer recipient (sets recipient to inactive)
        
        Args:
            recipient_id_or_code: Recipient ID or code
            
        Returns:
            Dict containing deletion result or error
        """
        try:
            url = f"{self.base_url}/transferrecipient/{recipient_id_or_code}"
            
            response = requests.delete(url, headers=self.headers)
            result = response.json()
            
            if response.status_code == 200 and result.get("status"):
                logger.info(f"✅ Deleted recipient: {recipient_id_or_code}")
                return {
                    "success": True,
                    "message": result.get("message")
                }
            else:
                logger.error(f"❌ Failed to delete recipient: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error deleting recipient: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_transfer_balance(self) -> Dict[str, Any]:
        """
        Check Paystack balance for transfers
        Note: This endpoint may not be available in public API
        """
        try:
            url = f"{self.base_url}/balance"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Balance retrieved successfully")
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "message": data.get("message", "Balance retrieved")
                }
            else:
                error_message = f"Balance check failed: {response.status_code}"
                logger.error(f"❌ {error_message}")
                return {
                    "success": False,
                    "error": error_message,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking balance: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disable_otp_for_transfers(self) -> Dict[str, Any]:
        """
        Disable OTP requirement for transfers
        Note: This may require dashboard configuration
        """
        try:
            logger.info("🔧 OTP disabling requires Paystack dashboard configuration")
            return {
                "success": False,
                "error": "OTP disabling must be done via Paystack dashboard"
            }
        except Exception as e:
            logger.error(f"❌ Error disabling OTP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def resend_transfer_otp(self, transfer_code: str, reason: str = "resend_otp") -> Dict[str, Any]:
        """
        Resend OTP for transfer finalization
        
        Args:
            transfer_code: Transfer code requiring OTP
            reason: Reason for resending OTP
            
        Returns:
            Dict with resend result
        """
        try:
            url = f"{self.base_url}/transfer/resend_otp"
            
            payload = {
                "transfer_code": transfer_code,
                "reason": reason
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ OTP resent for transfer {transfer_code}")
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "message": data.get("message", "OTP resent successfully")
                }
            else:
                error_data = response.json()
                error_message = error_data.get("message", f"OTP resend failed: {response.status_code}")
                logger.error(f"❌ {error_message}")
                return {
                    "success": False,
                    "error": error_message,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Error resending OTP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def enable_otp_for_transfers(self) -> Dict[str, Any]:
        """
        Enable OTP requirement for transfers
        Note: This may require dashboard configuration
        """
        try:
            logger.info("🔧 OTP enabling requires Paystack dashboard configuration")
            return {
                "success": False,
                "error": "OTP enabling must be done via Paystack dashboard"
            }
        except Exception as e:
            logger.error(f"❌ Error enabling OTP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
