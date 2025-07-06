"""
Paystack Webhook Handler for Sofi AI
====================================
Handles incoming webhooks from Paystack for payments and transfers
"""

import os
import json
import logging
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any
from supabase import create_client

logger = logging.getLogger(__name__)

class PaystackWebhookHandler:
    """Handle Paystack webhooks for Sofi AI"""
    
    def __init__(self):
        """Initialize webhook handler"""
        self.webhook_secret = os.getenv("PAYSTACK_WEBHOOK_SECRET")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.webhook_secret:
            logger.warning("PAYSTACK_WEBHOOK_SECRET not set - webhook verification disabled")
        
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
        else:
            logger.error("Supabase credentials missing")
            self.supabase = None
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Paystack webhook signature"""
        if not self.webhook_secret:
            logger.warning("⚠️ PAYSTACK_WEBHOOK_SECRET not configured - skipping verification (DEVELOPMENT MODE)")
            logger.warning("⚠️ For production, please set PAYSTACK_WEBHOOK_SECRET in your .env file")
            return True  # Allow for development/testing
        
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    async def handle_webhook(self, payload: Dict, signature: str = None) -> Dict:
        """Handle incoming Paystack webhook"""
        try:
            event = payload.get("event")
            data = payload.get("data", {})
            
            logger.info(f"🔔 Received Paystack webhook: {event}")
            
            # Skip signature verification for development (webhook secret not configured)
            if signature and self.webhook_secret:
                payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
                if not self.verify_signature(payload_bytes, signature):
                    logger.error("❌ Invalid webhook signature")
                    return {"success": False, "error": "Invalid signature"}
            else:
                logger.info("⚠️ Skipping webhook signature verification (development mode)")
            
            # Route to appropriate handler
            if event == "charge.success":
                return await self.handle_charge_success(data)
            elif event == "transfer.success":
                return await self.handle_transfer_success(data)
            elif event == "transfer.failed":
                return await self.handle_transfer_failed(data)
            elif event == "dedicated_account.assign":
                return await self.handle_dedicated_account_assign(data)
            else:
                logger.info(f"📝 Unhandled webhook event: {event}")
                return {"success": True, "message": f"Unhandled event: {event}"}
        
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_charge_success(self, data: Dict) -> Dict:
        """Handle successful payment to dedicated account"""
        try:
            if not data or not isinstance(data, dict):
                logger.error("❌ Invalid data received in charge.success handler")
                return {"success": False, "error": "Invalid data format"}
            
            # Extract payment details with safe defaults
            amount = data.get("amount", 0)
            if amount:
                amount = amount / 100  # Convert from kobo
            
            reference = data.get("reference", "")
            customer = data.get("customer") or {}
            customer_code = customer.get("customer_code", "") if isinstance(customer, dict) else ""
            
            # Extract sender information from the payment data  
            sender_name = (data.get("payer_name") or 
                          customer.get("email") if isinstance(customer, dict) else "" or 
                          "Unknown Sender")
            
            payer_bank_details = data.get("payer_bank_details") or {}
            source = data.get("source") or {}
            sender_bank = (payer_bank_details.get("bank_name") if isinstance(payer_bank_details, dict) else "" or
                          source.get("bank") if isinstance(source, dict) else "" or 
                          "Unknown Bank")
            narration = data.get("narration") or data.get("description") or "Money Transfer"
            
            # Get account details
            dedicated_account = data.get("authorization", {})
            account_number = dedicated_account.get("receiver_bank_account_number")
            
            logger.info(f"💰 Payment received: ₦{amount:,.2f} to account {account_number}")
            
            if not self.supabase:
                logger.error("Supabase not configured")
                return {"success": False, "error": "Database not configured"}
            
            # Find user by customer code or account number
            user_query = self.supabase.table("users").select("*").eq("paystack_customer_code", customer_code).execute()
            
            if not user_query.data:
                # Try finding by account number
                user_query = self.supabase.table("virtual_accounts").select("*, users(*)").eq("account_number", account_number).execute()
                
                if not user_query.data:
                    logger.error(f"User not found for payment: {reference}")
                    return {"success": False, "error": "User not found"}
            
            # Find user by customer code or account number and get their UUID
            user_query = self.supabase.table("users").select("id, telegram_chat_id, wallet_balance").eq("paystack_customer_code", customer_code).execute()
            
            if not user_query.data:
                # Try finding by account number via virtual_accounts table
                account_query = self.supabase.table("virtual_accounts").select("telegram_chat_id").eq("account_number", account_number).execute()
                
                if not account_query.data:
                    logger.error(f"User not found for payment: {reference}")
                    return {"success": False, "error": "User not found"}
                
                # Get telegram_chat_id from virtual_accounts, then find user
                telegram_chat_id = account_query.data[0]["telegram_chat_id"]
                user_query = self.supabase.table("users").select("id, telegram_chat_id, wallet_balance").eq("telegram_chat_id", telegram_chat_id).execute()
                
                if not user_query.data:
                    logger.error(f"User not found for telegram_chat_id: {telegram_chat_id}")
                    return {"success": False, "error": "User not found"}
                
                user_data = user_query.data[0]
            else:
                # User found directly
                user_data = user_query.data[0]
            
            user_uuid = user_data["id"]  # This is the actual UUID
            telegram_chat_id = user_data["telegram_chat_id"]  # This is the Telegram ID for notifications
            current_balance = float(user_data.get("wallet_balance", 0))
            new_balance = current_balance + amount
            
            # Record transaction with correct UUID and all required fields
            transaction_data = {
                "user_id": user_uuid,  # Use actual UUID from users table
                "transaction_type": "credit",  # This is a deposit/credit
                "amount": amount,
                "reference": reference,
                "status": "success",
                "description": f"Deposit from {sender_name} via {sender_bank}",
                "bank_code": "999999",  # Paystack internal code
                "bank_name": sender_bank,  # Sender's bank name
                "account_number": account_number,  # Recipient account number
                "sender_name": sender_name,  # Store sender name
                "narration": narration,  # Store narration/description
                "created_at": data.get("created_at")
            }
            
            try:
                self.supabase.table("bank_transactions").insert(transaction_data).execute()
                logger.info(f"✅ Transaction recorded for user {user_uuid}")
            except Exception as e:
                logger.warning(f"Could not record transaction: {e}")
                # Continue anyway - the balance update is more important
            
            # Update user balance using UUID
            self.supabase.table("users").update({"wallet_balance": new_balance}).eq("id", user_uuid).execute()
            
            # ALSO update virtual_accounts balance for consistency
            try:
                self.supabase.table("virtual_accounts").update({"balance": new_balance}).eq("account_number", account_number).execute()
                logger.info(f"✅ Virtual account balance updated: ₦{new_balance:,.2f}")
            except Exception as e:
                logger.warning(f"Could not update virtual account balance: {e}")
            
            # Send notification to user via Telegram with sender details
            await self.send_credit_notification(
                telegram_chat_id, 
                amount, 
                new_balance, 
                sender_name, 
                sender_bank, 
                narration
            )
            
            logger.info(f"✅ Credit processed: ₦{amount:,.2f} for user {telegram_chat_id}")
            return {"success": True, "message": "Credit processed successfully"}
        
        except Exception as e:
            logger.error(f"❌ Error processing charge success: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_transfer_success(self, data: Dict) -> Dict:
        """Handle successful outgoing transfer"""
        try:
            reference = data.get("reference")
            amount = data.get("amount", 0) / 100
            recipient = data.get("recipient", {})
            
            logger.info(f"✅ Transfer successful: ₦{amount:,.2f} - {reference}")
            
            if not self.supabase:
                return {"success": False, "error": "Database not configured"}
            
            # Update transaction status with available columns
            self.supabase.table("bank_transactions").update({"status": "success"}).eq("reference", reference).execute()
            
            # Send notification (implement as needed)
            return {"success": True, "message": "Transfer success processed"}
        
        except Exception as e:
            logger.error(f"❌ Error processing transfer success: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_transfer_failed(self, data: Dict) -> Dict:
        """Handle failed outgoing transfer"""
        try:
            reference = data.get("reference")
            amount = data.get("amount", 0) / 100
            
            logger.warning(f"❌ Transfer failed: ₦{amount:,.2f} - {reference}")
            
            if not self.supabase:
                return {"success": False, "error": "Database not configured"}
            
            # Update transaction status and potentially refund user
            transaction_query = self.supabase.table("bank_transactions") \
                .select("*") \
                .eq("reference", reference) \
                .execute()
            
            if transaction_query.data:
                transaction = transaction_query.data[0]
                user_id = transaction.get("user_id")
                
                # Update status with available columns
                self.supabase.table("bank_transactions").update({"status": "failed"}).eq("reference", reference).execute()
                
                # Refund user balance and record the refund
                current_balance = await self.get_user_balance(user_id)
                new_balance = current_balance + amount
                
                # Update user balance
                self.supabase.table("users").update({"wallet_balance": new_balance}).eq("telegram_chat_id", user_id).execute()
                
                # Record refund transaction
                refund_data = {
                    "user_id": user_id,
                    "amount": amount,
                    "reference": f"{reference}_refund",
                    "status": "success",
                    "wallet_balance_before": current_balance,
                    "wallet_balance_after": new_balance,
                    "created_at": datetime.now().isoformat()
                }
                self.supabase.table("bank_transactions").insert(refund_data).execute()
                
                logger.info(f"💰 Refunded ₦{amount:,.2f} to user {user_id}")
            
            return {"success": True, "message": "Transfer failure processed"}
        
        except Exception as e:
            logger.error(f"❌ Error processing transfer failure: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_dedicated_account_assign(self, data: Dict) -> Dict:
        """Handle dedicated account assignment"""
        try:
            customer = data.get("customer", {})
            customer_code = customer.get("customer_code")
            account_number = data.get("account_number")
            bank_name = data.get("bank", {}).get("name")
            
            logger.info(f"🏦 Dedicated account assigned: {account_number} for {customer_code}")
            
            # Update virtual account record (implement as needed)
            return {"success": True, "message": "Dedicated account assignment processed"}
        
        except Exception as e:
            logger.error(f"❌ Error processing account assignment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_balance(self, user_id: str) -> float:
        """Get current user balance"""
        try:
            if not self.supabase:
                return 0.0
            
            result = self.supabase.table("users").select("wallet_balance").eq("telegram_chat_id", user_id).execute()
            
            if result.data:
                return float(result.data[0].get("wallet_balance", 0))
            return 0.0
        
        except Exception as e:
            logger.error(f"Error getting user balance: {str(e)}")
            return 0.0
    
    async def send_credit_notification(self, user_id: str, amount: float, new_balance: float, sender_name: str = "Unknown", sender_bank: str = "Unknown Bank", narration: str = "Transfer"):
        """Send beautiful, friendly credit notification to user via Telegram"""
        try:
            from main import send_reply  # Import from main app
            
            # Get user's first name for personalization
            user_name = "there"  # Default greeting
            try:
                if self.supabase:
                    user_query = self.supabase.table("users").select("full_name").eq("telegram_chat_id", user_id).execute()
                    if user_query.data:
                        full_name = user_query.data[0].get("full_name", "")
                        user_name = full_name.split()[0] if full_name else "there"
            except Exception as e:
                logger.warning(f"Could not get user name: {e}")
            
            # Create short, friendly, emoji-rich message
            message = f"""
🎉 Hey {user_name}, you received ₦{amount:,.0f} from {sender_name} at {sender_bank}! 

� Your new balance: ₦{new_balance:,.0f}

Say "balance" to check your wallet or "transfer" to send money! 🚀
"""
            
            send_reply(user_id, message)
            logger.info(f"📱 Enhanced credit notification sent to {user_id}")
        
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")

# Global instance
paystack_webhook_handler = PaystackWebhookHandler()

def handle_paystack_webhook(payload: Dict, signature: str = None) -> Dict:
    """Handle Paystack webhook (sync wrapper)"""
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            paystack_webhook_handler.handle_webhook(payload, signature)
        )
    except Exception as e:
        logger.error(f"Webhook handling error: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        loop.close()
