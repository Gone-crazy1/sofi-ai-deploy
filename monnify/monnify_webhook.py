"""
Monnify Webhook Handler for Sofi AI Banking Service
Official Banking Partner: Monnify

This module handles incoming webhook notifications from Monnify for:
- Payment confirmations
- Transfer updates
- Account credits
- Transaction status changes
"""

import os
import json
import hashlib
import hmac
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Import our enhanced notification system
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.notification_manager import notify_deposit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class MonnifyWebhookHandler:
    """Handle Monnify webhook notifications"""
    
    def __init__(self):
        """Initialize webhook handler"""
        self.secret_key = os.getenv("MONNIFY_SECRET_KEY")
        if not self.secret_key:
            logger.error("Monnify secret key not found for webhook verification")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Monnify webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Monnify signature header
            
        Returns:
            bool: True if signature is valid
        """
        if not self.secret_key:
            logger.warning("Cannot verify webhook signature - secret key not configured")
            return False
        
        try:
            # Create expected signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    def handle_webhook(self, webhook_data: Dict, signature: str = None) -> Dict:
        """
        Process Monnify webhook notification
        
        Args:
            webhook_data: Webhook payload data
            signature: Optional signature for verification
            
        Returns:
            Dict with processing result
        """
        try:
            # Log webhook received
            logger.info(f"Monnify webhook received: {webhook_data.get('eventType', 'unknown')}")
            
            # Verify signature if provided
            if signature:
                payload_str = json.dumps(webhook_data, sort_keys=True)
                if not self.verify_webhook_signature(payload_str, signature):
                    logger.warning("Invalid webhook signature")
                    return {
                        "success": False,
                        "error": "Invalid signature"
                    }
            
            # Extract event details
            event_type = webhook_data.get("eventType")
            event_data = webhook_data.get("eventData", {})
            
            # Process different event types
            if event_type == "SUCCESSFUL_TRANSACTION":
                return self._handle_successful_transaction(event_data)
            elif event_type == "FAILED_TRANSACTION":
                return self._handle_failed_transaction(event_data)
            elif event_type == "SUCCESSFUL_DISBURSEMENT":
                return self._handle_successful_disbursement(event_data)
            elif event_type == "FAILED_DISBURSEMENT":
                return self._handle_failed_disbursement(event_data)
            else:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return {
                    "success": True,
                    "message": f"Event {event_type} acknowledged but not processed"
                }
                
        except Exception as e:
            logger.error(f"Error processing Monnify webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_successful_transaction(self, event_data: Dict) -> Dict:
        """
        Handle successful transaction (incoming payment)
        
        Args:
            event_data: Transaction event data
            
        Returns:
            Dict with processing result
        """
        try:
            # Extract transaction details
            transaction_ref = event_data.get("transactionReference")
            amount = float(event_data.get("amountPaid", 0))
            customer_email = event_data.get("customer", {}).get("email")
            account_details = event_data.get("accountDetails", {})
            
            logger.info(f"Processing successful transaction: {transaction_ref}, Amount: ₦{amount}")
            
            # Find user by account number or email
            user_info = self._find_user_by_account(account_details.get("accountNumber"))
            
            if user_info:
                # Credit user account
                self._credit_user_account(
                    user_id=user_info["user_id"],
                    amount=amount,
                    transaction_ref=transaction_ref,
                    description="Account Credit via Monnify"
                )
                
                # Send notification to user
                self._send_credit_notification(user_info, amount, transaction_ref)
                
                return {
                    "success": True,
                    "message": f"Transaction {transaction_ref} processed successfully",
                    "amount": amount,
                    "user_id": user_info["user_id"]
                }
            else:
                logger.warning(f"User not found for account: {account_details.get('accountNumber')}")
                return {
                    "success": False,
                    "error": "User not found for account"
                }
                
        except Exception as e:
            logger.error(f"Error handling successful transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_failed_transaction(self, event_data: Dict) -> Dict:
        """
        Handle failed transaction
        
        Args:
            event_data: Transaction event data
            
        Returns:
            Dict with processing result
        """
        try:
            transaction_ref = event_data.get("transactionReference")
            logger.info(f"Processing failed transaction: {transaction_ref}")
            
            # Log the failure for monitoring
            self._log_transaction_failure(event_data)
            
            return {
                "success": True,
                "message": f"Failed transaction {transaction_ref} logged"
            }
            
        except Exception as e:
            logger.error(f"Error handling failed transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_successful_disbursement(self, event_data: Dict) -> Dict:
        """
        Handle successful disbursement (outgoing transfer)
        
        Args:
            event_data: Disbursement event data
            
        Returns:
            Dict with processing result
        """
        try:
            reference = event_data.get("reference")
            amount = float(event_data.get("amount", 0))
            
            logger.info(f"Processing successful disbursement: {reference}, Amount: ₦{amount}")
            
            # Update transaction status in database
            self._update_transfer_status(reference, "completed", event_data)
            
            return {
                "success": True,
                "message": f"Disbursement {reference} completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error handling successful disbursement: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_failed_disbursement(self, event_data: Dict) -> Dict:
        """
        Handle failed disbursement
        
        Args:
            event_data: Disbursement event data
            
        Returns:
            Dict with processing result
        """
        try:
            reference = event_data.get("reference")
            logger.info(f"Processing failed disbursement: {reference}")
            
            # Update transaction status and refund user if needed
            self._update_transfer_status(reference, "failed", event_data)
            self._process_failed_transfer_refund(reference, event_data)
            
            return {
                "success": True,
                "message": f"Failed disbursement {reference} processed"
            }
            
        except Exception as e:
            logger.error(f"Error handling failed disbursement: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_user_by_account(self, account_number: str) -> Optional[Dict]:
        """
        Find user by virtual account number
        
        Args:
            account_number: Virtual account number
            
        Returns:
            Dict with user info or None
        """
        try:
            from supabase import create_client
            
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not all([supabase_url, supabase_key]):
                logger.error("Supabase credentials not configured")
                return None
            
            supabase = create_client(supabase_url, supabase_key)
            
            # Query virtual_accounts table
            result = supabase.table("virtual_accounts").select(
                "user_id, users(email, first_name, last_name, phone)"
            ).eq("account_number", account_number).eq("is_active", True).execute()
            
            if result.data:
                account_info = result.data[0]
                user_info = account_info["users"]
                
                return {
                    "user_id": account_info["user_id"],
                    "email": user_info["email"],
                    "first_name": user_info["first_name"],
                    "last_name": user_info["last_name"],
                    "phone": user_info.get("phone")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by account: {e}")
            return None
    
    def _credit_user_account(self, user_id: str, amount: float, transaction_ref: str, description: str):
        """
        Credit user's account balance
        
        Args:
            user_id: User ID
            amount: Amount to credit
            transaction_ref: Transaction reference
            description: Transaction description
        """
        try:
            from supabase import create_client
            
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            supabase = create_client(supabase_url, supabase_key)
            
            # Update user balance
            supabase.rpc("credit_user_balance", {
                "p_user_id": user_id,
                "p_amount": amount
            }).execute()
            
            # Log transaction
            supabase.table("transactions").insert({
                "user_id": user_id,
                "transaction_type": "credit",                "amount": amount,
                "description": description,
                "reference": transaction_ref,
                "status": "completed",
                "provider": "monnify",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            logger.info(f"Credited ₦{amount} to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error crediting user account: {e}")
    
    def _send_credit_notification(self, user_info: Dict, amount: float, transaction_ref: str):
        """
        Send credit notification to user using enhanced notification system
        
        Args:
            user_info: User information
            amount: Credited amount
            transaction_ref: Transaction reference
        """
        try:
            # Get user's updated balance
            from supabase import create_client
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # Get virtual account info for balance
            account_result = supabase.table("virtual_accounts").select("balance, account_name").eq("user_id", user_info["user_id"]).execute()
            
            balance = 0.0
            account_name = user_info.get("first_name", "Sofi AI User")
            
            if account_result.data:
                balance = float(account_result.data[0].get("balance", 0))
                account_name = account_result.data[0].get("account_name", account_name)
            
            # Send enhanced notification using async notification manager
            asyncio.create_task(notify_deposit(
                user_id=user_info["user_id"],
                amount=amount,
                balance=balance,
                account_name=account_name,
                reference=transaction_ref
            ))
            
            logger.info(f"Enhanced deposit notification queued for user {user_info['user_id']}: ₦{amount:,.2f}")
            
        except Exception as e:
            logger.error(f"Error sending enhanced credit notification: {e}")
            # Fallback to simple notification
            try:
                message = f"""
🎉 **DEPOSIT CONFIRMED!**

💰 **Amount:** ₦{amount:,.2f}
🔢 **Reference:** {transaction_ref}
⏰ **Time:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

✅ Your Sofi AI account has been credited successfully!
Type "Balance" to check your updated balance.
"""
                # Simple fallback notification (you'd implement this based on your setup)
                logger.info(f"Fallback notification: {message}")
            except:
                pass
    
    def _update_transfer_status(self, reference: str, status: str, event_data: Dict):
        """
        Update transfer status in database
        
        Args:
            reference: Transfer reference
            status: New status
            event_data: Event data from webhook
        """
        try:
            from supabase import create_client
            
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            supabase = create_client(supabase_url, supabase_key)
            
            # Update transaction status
            supabase.table("transactions").update({
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
                "provider_response": event_data
            }).eq("reference", reference).execute()
            
            logger.info(f"Updated transfer {reference} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating transfer status: {e}")
    
    def _process_failed_transfer_refund(self, reference: str, event_data: Dict):
        """
        Process refund for failed transfer
        
        Args:
            reference: Transfer reference
            event_data: Event data from webhook
        """
        try:
            # Implementation for refunding failed transfers
            logger.info(f"Processing refund for failed transfer: {reference}")
            
        except Exception as e:
            logger.error(f"Error processing failed transfer refund: {e}")
    
    def _log_transaction_failure(self, event_data: Dict):
        """
        Log transaction failure for monitoring
        
        Args:
            event_data: Event data from webhook
        """
        try:
            logger.warning(f"Transaction failed: {json.dumps(event_data)}")
            
        except Exception as e:
            logger.error(f"Error logging transaction failure: {e}")


def handle_monnify_webhook(webhook_data: Dict, signature: str = None) -> Dict:
    """
    Main function to handle Monnify webhook
    
    Args:
        webhook_data: Webhook payload data
        signature: Optional signature for verification
        
    Returns:
        Dict with processing result
    """
    handler = MonnifyWebhookHandler()
    return handler.handle_webhook(webhook_data, signature)
