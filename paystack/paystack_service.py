"""
Unified Paystack Service
Combines Dedicated Virtual Accounts and Transfer functionality
"""

import os
import logging
from typing import Dict, Optional, Any
from .paystack_dva_api import PaystackDVAAPI
from .paystack_transfer_api import PaystackTransferAPI

logger = logging.getLogger(__name__)

class PaystackService:
    """Unified Paystack service for DVA and Transfers"""
    
    def __init__(self):
        """Initialize both DVA and Transfer APIs"""
        self.dva_api = PaystackDVAAPI()
        self.transfer_api = PaystackTransferAPI()
        
        logger.info("✅ Paystack Service initialized (DVA + Transfers)")
    
    # === ACCOUNT CREATION ===
    
    def create_user_account(self, user_data: Dict) -> Dict[str, Any]:
        """
        Create user account with dedicated virtual account
        
        Args:
            user_data: Dict containing user information
            {
                "email": "user@email.com",
                "first_name": "John",
                "last_name": "Doe", 
                "phone": "+2348000000000",
                "preferred_bank": "wema-bank"  # optional
            }
            
        Returns:
            Dict with account creation result formatted for onboarding
        """
        try:
            # Use DVA API to create customer with virtual account
            result = self.dva_api.create_customer_with_dva(user_data)
            
            if result["success"]:
                logger.info(f"✅ Account created for {user_data.get('email')}")
                
                # Format response for onboarding system
                account_info = {
                    "customer_id": result.get("customer_id"),
                    "customer_code": result.get("customer_code"),
                    "account_number": result.get("account_number"),
                    "account_name": result.get("account_name"),
                    "bank_name": result.get("bank_name"),
                    "bank_code": result.get("bank_code"),
                    "dva_id": result.get("dva_id")
                }
                
                return {
                    "success": True,
                    "message": "Account creation successful",
                    "account_info": account_info,
                    "data": result.get("data", {})
                }
            else:
                logger.error(f"❌ Account creation failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Error in create_user_account: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get user's dedicated virtual account details
        
        Args:
            account_id: DVA ID from Paystack
            
        Returns:
            Dict with account details
        """
        try:
            return self.dva_api.fetch_dedicated_account(account_id)
        except Exception as e:
            logger.error(f"❌ Error getting user account: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_user_accounts(self) -> Dict[str, Any]:
        """Get list of all dedicated virtual accounts"""
        try:
            return self.dva_api.list_dedicated_accounts()
        except Exception as e:
            logger.error(f"❌ Error listing accounts: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # === MONEY TRANSFERS ===
    
    def send_money(self, sender_data: Dict, recipient_data: Dict, 
                   amount: float, reason: str = "Transfer") -> Dict[str, Any]:
        """
        Send money from user's balance to external account
        
        Args:
            sender_data: Dict with sender info (for logging)
            recipient_data: Dict with recipient details
            {
                "account_number": "0123456789",
                "bank_code": "058",
                "account_name": "John Doe"
            }
            amount: Amount in Naira
            reason: Transfer reason
            
        Returns:
            Dict with transfer result
        """
        try:
            logger.info(f"💸 Initiating transfer: ₦{amount:,.2f} to {recipient_data['account_name']}")
            
            result = self.transfer_api.send_money(
                account_number=recipient_data["account_number"],
                bank_code=recipient_data["bank_code"],
                account_name=recipient_data["account_name"],
                amount=amount,
                reason=reason
            )
            
            if result["success"]:
                if result.get("requires_otp"):
                    logger.info("🔐 Transfer requires OTP verification")
                else:
                    logger.info("✅ Transfer completed successfully")
            else:
                logger.error(f"❌ Transfer failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in send_money: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def complete_otp_transfer(self, transfer_code: str, otp: str) -> Dict[str, Any]:
        """
        Complete transfer that requires OTP
        
        Args:
            transfer_code: Transfer code from send_money
            otp: OTP from SMS
            
        Returns:
            Dict with finalization result
        """
        try:
            logger.info(f"🔐 Finalizing transfer with OTP: {transfer_code}")
            
            result = self.transfer_api.finalize_transfer(transfer_code, otp)
            
            if result["success"]:
                logger.info("✅ Transfer finalized successfully")
            else:
                logger.error(f"❌ OTP verification failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error completing OTP transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_transfer(self, reference: str) -> Dict[str, Any]:
        """Verify transfer status"""
        try:
            return self.transfer_api.verify_transfer(reference)
        except Exception as e:
            logger.error(f"❌ Error verifying transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_transfer_history(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """Get transfer history"""
        try:
            return self.transfer_api.list_transfers(page, per_page)
        except Exception as e:
            logger.error(f"❌ Error getting transfer history: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # === ACCOUNT VERIFICATION ===
    
    def verify_account_number(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """
        Verify account number and get account name
        
        Args:
            account_number: Account number to verify
            bank_code: Bank code
            
        Returns:
            Dict with account verification result
        """
        try:
            logger.info(f"🔍 Verifying account: {account_number} at bank {bank_code}")
            
            result = self.transfer_api.resolve_account(account_number, bank_code)
            
            if result["success"]:
                account_data = result["data"]
                logger.info(f"✅ Account verified: {account_data.get('account_name')}")
                return {
                    "success": True,
                    "verified": True,
                    "account_name": account_data.get("account_name"),
                    "account_number": account_data.get("account_number"),
                    "bank_code": bank_code
                }
            else:
                logger.error(f"❌ Account verification failed: {result.get('error')}")
                return {
                    "success": False,
                    "verified": False,
                    "error": result.get("error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error verifying account: {str(e)}")
            return {
                "success": False,
                "verified": False,
                "error": str(e)
            }
    
    def get_supported_banks(self) -> Dict[str, Any]:
        """Get list of supported banks"""
        try:
            return self.transfer_api.get_banks()
        except Exception as e:
            logger.error(f"❌ Error getting banks: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # === BALANCE & TRANSACTIONS ===
    
    def check_balance(self) -> Dict[str, Any]:
        """
        Check Paystack balance (for transfers)
        Note: This would require additional Paystack API endpoint
        """
        try:
            # Paystack doesn't have a direct balance endpoint in their public API
            # You might need to track this in your database or use their dashboard
            logger.warning("⚠️ Direct balance check not available via Paystack API")
            return {
                "success": False,
                "error": "Balance check not available via API. Check Paystack dashboard."
            }
        except Exception as e:
            logger.error(f"❌ Error checking balance: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def requery_account(self, account_number: str, provider_slug: str, 
                       date: str = None) -> Dict[str, Any]:
        """
        Requery dedicated account for new transactions
        
        Args:
            account_number: Virtual account number
            provider_slug: Bank slug (e.g., "wema-bank")
            date: Optional date to check from
            
        Returns:
            Dict with requery result
        """
        try:
            return self.dva_api.requery_dedicated_account(account_number, provider_slug, date)
        except Exception as e:
            logger.error(f"❌ Error requerying account: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== ASSISTANT HELPER METHODS ====================
    
    def verify_account_name(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """Verify account name with bank - used by AI Assistant"""
        return self.transfer_api.resolve_account(account_number, bank_code)
    
    def get_banks_list(self) -> Dict[str, Any]:
        """Get list of supported banks - used by AI Assistant"""
        return self.transfer_api.get_banks()
    
    def create_recipient_and_send(self, account_number: str, bank_code: str, 
                                  account_name: str, amount: float, 
                                  reason: str = "Transfer") -> Dict[str, Any]:
        """
        One-step method: Create recipient and send money
        Perfect for AI Assistant function calls
        """
        try:
            # Step 1: Create recipient
            recipient_result = self.transfer_api.create_transfer_recipient(
                account_number=account_number,
                bank_code=bank_code,
                name=account_name
            )
            
            if not recipient_result.get("success"):
                return recipient_result
            
            recipient_code = recipient_result["data"]["recipient_code"]
            
            # Step 2: Send money
            transfer_result = self.transfer_api.initiate_transfer(
                recipient_code=recipient_code,
                amount=int(amount * 100),  # Convert to kobo
                reason=reason
            )
            
            return {
                "success": True,
                "recipient": recipient_result["data"],
                "transfer": transfer_result["data"] if transfer_result.get("success") else None,
                "requires_otp": transfer_result.get("data", {}).get("status") == "otp",
                "transfer_code": transfer_result.get("data", {}).get("transfer_code")
            }
            
        except Exception as e:
            logger.error(f"❌ Error in create_recipient_and_send: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_transfer_status_by_code(self, transfer_code: str) -> Dict[str, Any]:
        """Get transfer status by transfer code - used by AI Assistant"""
        return self.transfer_api.fetch_transfer(transfer_code)
    
    def list_recent_transfers(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent transfers - used by AI Assistant"""
        return self.transfer_api.list_transfers(page=1, per_page=limit)
    
    def format_currency(self, amount: float) -> str:
        """Format amount for display"""
        return f"₦{amount:,.2f}"
    
    def validate_transfer_amount(self, amount: float) -> Dict[str, Any]:
        """Validate transfer amount"""
        errors = []
        
        if amount <= 0:
            errors.append("Amount must be greater than 0")
        
        if amount < 100:  # Minimum ₦100
            errors.append("Minimum transfer amount is ₦100")
        
        if amount > 5000000:  # Maximum ₦5M (adjust as needed)
            errors.append("Maximum transfer amount is ₦5,000,000")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "amount_in_kobo": int(amount * 100) if len(errors) == 0 else 0
        }
    
    def process_webhook_notification(self, webhook_data: Dict) -> Dict[str, Any]:
        """Process Paystack webhook notifications"""
        try:
            event = webhook_data.get("event")
            data = webhook_data.get("data", {})
            
            if event == "charge.success":
                # Handle successful payment to virtual account
                return {
                    "success": True,
                    "event_type": "payment_received",
                    "amount": data.get("amount", 0) / 100,  # Convert from kobo
                    "customer": data.get("customer", {}),
                    "reference": data.get("reference"),
                    "status": data.get("status")
                }
            
            elif event == "transfer.success":
                # Handle successful transfer
                return {
                    "success": True,
                    "event_type": "transfer_completed",
                    "amount": data.get("amount", 0) / 100,
                    "recipient": data.get("recipient", {}),
                    "reference": data.get("reference"),
                    "status": data.get("status")
                }
            
            elif event == "transfer.failed":
                # Handle failed transfer
                return {
                    "success": True,
                    "event_type": "transfer_failed",
                    "amount": data.get("amount", 0) / 100,
                    "recipient": data.get("recipient", {}),
                    "reference": data.get("reference"),
                    "failure_reason": data.get("gateway_response")
                }
            
            else:
                return {
                    "success": True,
                    "event_type": "unhandled",
                    "event": event
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    # Assistant-friendly helper methods
    async def get_user_virtual_account_summary(self, user_id: str) -> dict:
        """Get a user's virtual account summary for the assistant"""
        try:
            # Get user's virtual account
            accounts = await self.dva_api.list_dedicated_accounts()
            user_account = None
            
            for account in accounts.get('data', []):
                if account['customer']['email'] == f"user_{user_id}@sofi.ai":
                    user_account = account
                    break
            
            if not user_account:
                return {
                    "has_account": False,
                    "message": "No virtual account found. Please complete onboarding."
                }
            
            return {
                "has_account": True,
                "account_number": user_account['account_number'],
                "account_name": user_account['account_name'],
                "bank_name": user_account['bank']['name'],
                "currency": user_account['currency'],
                "status": "active" if user_account['active'] else "inactive"
            }
            
        except Exception as e:
            logger.error(f"Error getting user account summary: {e}")
            return {"has_account": False, "error": str(e)}

    async def send_money_simple(self, amount: float, account_number: str, bank_code: str, recipient_name: str, reason: str = "Transfer") -> dict:
        """Simplified money sending for the assistant"""
        try:
            # Convert amount to kobo
            amount_kobo = int(amount * 100)
            
            # Create recipient first
            recipient_result = await self.transfer_api.create_recipient(
                type="nuban",
                name=recipient_name,
                account_number=account_number,
                bank_code=bank_code
            )
            
            if not recipient_result['status']:
                return {
                    "success": False,
                    "message": f"Failed to create recipient: {recipient_result['message']}"
                }
            
            recipient_code = recipient_result['data']['recipient_code']
            
            # Initiate transfer
            transfer_result = await self.transfer_api.initiate_transfer(
                source="balance",
                amount=amount_kobo,
                recipient=recipient_code,
                reason=reason
            )
            
            if transfer_result['status']:
                return {
                    "success": True,
                    "transfer_code": transfer_result['data']['transfer_code'],
                    "status": transfer_result['data']['status'],
                    "amount": amount,
                    "recipient": recipient_name,
                    "message": "Transfer initiated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Transfer failed: {transfer_result['message']}"
                }
                
        except Exception as e:
            logger.error(f"Error in send_money_simple: {e}")
            return {"success": False, "error": str(e)}

    async def get_transaction_history(self, user_id: str, limit: int = 10) -> dict:
        """Get user's transaction history for the assistant"""
        try:
            # Get recent transfers
            transfers = await self.transfer_api.list_transfers(per_page=limit)
            
            if not transfers['status']:
                return {"success": False, "message": "Failed to fetch transactions"}
            
            transactions = []
            for transfer in transfers['data']:
                transactions.append({
                    "id": transfer['id'],
                    "amount": transfer['amount'] / 100,  # Convert from kobo
                    "recipient": transfer['recipient']['name'],
                    "status": transfer['status'],
                    "date": transfer['createdAt'],
                    "reason": transfer.get('reason', 'Transfer')
                })
            
            return {
                "success": True,
                "transactions": transactions,
                "total": len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return {"success": False, "error": str(e)}

    async def verify_recipient_account(self, account_number: str, bank_code: str) -> dict:
        """Verify account details for the assistant"""
        try:
            # Create a temporary recipient to verify the account
            result = await self.transfer_api.create_recipient(
                type="nuban",
                name="Temp Verification",
                account_number=account_number,
                bank_code=bank_code
            )
            
            if result['status']:
                return {
                    "verified": True,
                    "account_name": result['data']['details']['account_name'],
                    "bank_name": result['data']['details']['bank_name'],
                    "account_number": account_number
                }
            else:
                return {
                    "verified": False,
                    "message": result['message']
                }
                
        except Exception as e:
            logger.error(f"Error verifying account: {e}")
            return {"verified": False, "error": str(e)}

    async def get_balance_info(self) -> dict:
        """Get Paystack balance information"""
        try:
            # Note: This would require the Balance API endpoint
            # For now, return a placeholder
            return {
                "available": True,
                "message": "Balance check requires additional Paystack API access"
            }
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {"available": False, "error": str(e)}

    async def create_user_account_simple(self, user_data: dict) -> dict:
        """Simplified account creation for the assistant"""
        try:
            email = user_data.get('email') or f"user_{user_data['chat_id']}@sofi.ai"
            
            result = await self.dva_api.assign_dedicated_account(
                email=email,
                first_name=user_data.get('first_name', 'User'),
                last_name=user_data.get('last_name', 'Sofi'),
                phone=user_data.get('phone', '+2348000000000'),
                preferred_bank="wema-bank",  # Default to Wema
                country="NG"
            )
            
            if result['status']:
                return {
                    "success": True,
                    "message": "Virtual account created successfully",
                    "account_details": result.get('data', {})
                }
            else:
                return {
                    "success": False,
                    "message": f"Account creation failed: {result['message']}"
                }
                
        except Exception as e:
            logger.error(f"Error creating user account: {e}")
            return {"success": False, "error": str(e)}

    def get_user_dva_details(self, customer_code: str) -> Dict[str, Any]:
        """
        Get DVA details for a customer (useful for pending DVAs)
        
        Args:
            customer_code: Paystack customer code
            
        Returns:
            Dict with DVA details formatted for onboarding
        """
        try:
            result = self.dva_api.fetch_dva_by_customer(customer_code)
            
            if result["success"]:
                logger.info(f"✅ DVA details retrieved for {customer_code}")
                
                # Format response for onboarding system
                account_info = {
                    "customer_code": customer_code,
                    "account_number": result.get("account_number"),
                    "account_name": result.get("account_name"),
                    "bank_name": result.get("bank_name"),
                    "bank_code": result.get("bank_code"),
                    "dva_id": result.get("dva_id")
                }
                
                return {
                    "success": True,
                    "message": "DVA details retrieved successfully",
                    "account_info": account_info,
                    "data": result.get("data", {})
                }
            else:
                logger.error(f"❌ Failed to get DVA details: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Error getting DVA details: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
# Initialize global Paystack service instance
paystack_service = None

def get_paystack_service() -> PaystackService:
    """Get singleton Paystack service instance"""
    global paystack_service
    if paystack_service is None:
        paystack_service = PaystackService()
    return paystack_service
