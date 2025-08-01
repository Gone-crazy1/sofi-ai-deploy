# 9PSB Webhook Handler for WAAS Notifications

import json
import hashlib
import hmac
import logging
from datetime import datetime
from flask import request, jsonify
from supabase import create_client
import os

logger = logging.getLogger(__name__)

class NINEPSBWebhookHandler:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        )
        self.webhook_secret = os.getenv("NINEPSB_SECRET_KEY")
    
    def verify_webhook_signature(self, payload, signature, timestamp=None):
        """Verify webhook signature from 9PSB"""
        try:
            if not self.webhook_secret:
                logger.warning("No webhook secret configured")
                return True  # Allow during testing
            
            # Create expected signature
            message = f"{timestamp}{payload}" if timestamp else payload
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def handle_webhook(self, request_data):
        """Handle incoming webhook from 9PSB"""
        try:
            # Parse webhook data
            if isinstance(request_data, str):
                webhook_data = json.loads(request_data)
            else:
                webhook_data = request_data
            
            logger.info(f"🔔 9PSB Webhook received: {webhook_data}")
            
            # Extract event type and data
            event_type = webhook_data.get('eventType') or webhook_data.get('type')
            data = webhook_data.get('data') or webhook_data
            
            # Route to appropriate handler
            if event_type in ['wallet.created', 'account.created']:
                return self._handle_wallet_created(data)
            elif event_type in ['wallet.funded', 'credit', 'deposit']:
                return self._handle_wallet_funded(data)
            elif event_type in ['wallet.debited', 'debit', 'withdrawal']:
                return self._handle_wallet_debited(data)
            elif event_type in ['transfer.completed', 'transfer.success']:
                return self._handle_transfer_completed(data)
            elif event_type in ['transfer.failed', 'transfer.error']:
                return self._handle_transfer_failed(data)
            elif event_type in ['wallet.upgraded', 'tier.upgraded']:
                return self._handle_wallet_upgraded(data)
            elif event_type in ['transaction.status']:
                return self._handle_transaction_status(data)
            else:
                logger.warning(f"Unhandled webhook event type: {event_type}")
                return {"status": "ignored", "message": f"Event type {event_type} not handled"}
                
        except Exception as e:
            logger.error(f"Webhook handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_wallet_created(self, data):
        """Handle wallet creation notification"""
        try:
            user_id = data.get('userId')
            account_number = data.get('accountNumber')
            account_name = data.get('accountName')
            bank_name = data.get('bankName') or "9PSB"
            wallet_id = data.get('walletId')
            
            if user_id:
                # Update user's virtual account in Supabase
                result = self.supabase.table("users").update({
                    "virtual_account_number": account_number,
                    "virtual_account_name": account_name,
                    "virtual_bank_name": bank_name,
                    "ninepsb_wallet_id": wallet_id,
                    "account_status": "active",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("telegram_chat_id", str(user_id)).execute()
                
                logger.info(f"✅ Wallet created for user {user_id}: {account_number}")
                
                # Send notification to user (if Telegram chat ID available)
                self._notify_user(user_id, "wallet_created", {
                    "account_number": account_number,
                    "account_name": account_name,
                    "bank_name": bank_name
                })
                
            return {"status": "success", "message": "Wallet creation processed"}
            
        except Exception as e:
            logger.error(f"Failed to handle wallet creation: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_wallet_funded(self, data):
        """Handle wallet funding notification"""
        try:
            user_id = data.get('userId')
            amount = data.get('amount')
            reference = data.get('reference')
            balance = data.get('balance')
            transaction_id = data.get('transactionId')
            
            # Record transaction in Supabase
            if user_id:
                # Get user UUID from telegram_chat_id
                user_result = self.supabase.table("users").select("id").eq("telegram_chat_id", str(user_id)).execute()
                
                if user_result.data:
                    user_uuid = user_result.data[0]["id"]
                    
                    # Insert transaction record
                    self.supabase.table("bank_transactions").insert({
                        "user_id": user_uuid,
                        "transaction_type": "credit",
                        "amount": float(amount),
                        "reference": reference,
                        "ninepsb_transaction_id": transaction_id,
                        "status": "completed",
                        "description": f"Wallet funding - ₦{amount:,.2f}",
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                    
                    # Update user balance
                    self.supabase.table("users").update({
                        "balance": float(balance) if balance else None,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", user_uuid).execute()
                    
                    logger.info(f"💰 Wallet funded for user {user_id}: ₦{amount}")
                    
                    # Notify user
                    self._notify_user(user_id, "wallet_funded", {
                        "amount": amount,
                        "balance": balance,
                        "reference": reference
                    })
                    
            return {"status": "success", "message": "Wallet funding processed"}
            
        except Exception as e:
            logger.error(f"Failed to handle wallet funding: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_wallet_debited(self, data):
        """Handle wallet debit notification"""
        try:
            user_id = data.get('userId')
            amount = data.get('amount')
            reference = data.get('reference')
            balance = data.get('balance')
            transaction_id = data.get('transactionId')
            description = data.get('description') or data.get('narration')
            
            if user_id:
                # Get user UUID
                user_result = self.supabase.table("users").select("id").eq("telegram_chat_id", str(user_id)).execute()
                
                if user_result.data:
                    user_uuid = user_result.data[0]["id"]
                    
                    # Insert transaction record
                    self.supabase.table("bank_transactions").insert({
                        "user_id": user_uuid,
                        "transaction_type": "debit",
                        "amount": float(amount),
                        "reference": reference,
                        "ninepsb_transaction_id": transaction_id,
                        "status": "completed",
                        "description": description or f"Wallet debit - ₦{amount:,.2f}",
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                    
                    # Update user balance
                    self.supabase.table("users").update({
                        "balance": float(balance) if balance else None,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", user_uuid).execute()
                    
                    logger.info(f"💸 Wallet debited for user {user_id}: ₦{amount}")
                    
                    # Notify user
                    self._notify_user(user_id, "wallet_debited", {
                        "amount": amount,
                        "balance": balance,
                        "description": description
                    })
                    
            return {"status": "success", "message": "Wallet debit processed"}
            
        except Exception as e:
            logger.error(f"Failed to handle wallet debit: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_transfer_completed(self, data):
        """Handle successful transfer notification"""
        try:
            user_id = data.get('userId')
            amount = data.get('amount')
            recipient_account = data.get('recipientAccount')
            recipient_name = data.get('recipientName')
            reference = data.get('reference')
            transaction_id = data.get('transactionId')
            
            logger.info(f"✅ Transfer completed for user {user_id}: ₦{amount} to {recipient_account}")
            
            # Notify user of successful transfer
            self._notify_user(user_id, "transfer_completed", {
                "amount": amount,
                "recipient_account": recipient_account,
                "recipient_name": recipient_name,
                "reference": reference
            })
            
            return {"status": "success", "message": "Transfer completion processed"}
            
        except Exception as e:
            logger.error(f"Failed to handle transfer completion: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_transfer_failed(self, data):
        """Handle failed transfer notification"""
        try:
            user_id = data.get('userId')
            amount = data.get('amount')
            error_message = data.get('errorMessage') or data.get('message')
            reference = data.get('reference')
            
            logger.warning(f"❌ Transfer failed for user {user_id}: {error_message}")
            
            # Notify user of failed transfer
            self._notify_user(user_id, "transfer_failed", {
                "amount": amount,
                "error_message": error_message,
                "reference": reference
            })
            
            return {"status": "success", "message": "Transfer failure processed"}
            
        except Exception as e:
            logger.error(f"Failed to handle transfer failure: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_wallet_upgraded(self, data):
        """Handle wallet tier upgrade notification"""
        try:
            user_id = data.get('userId')
            new_tier = data.get('tierLevel') or data.get('newTier')
            old_tier = data.get('oldTier')
            
            if user_id:
                # Update user's tier in Supabase
                self.supabase.table("users").update({
                    "wallet_tier": int(new_tier) if new_tier else None,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("telegram_chat_id", str(user_id)).execute()
                
                logger.info(f"🆙 Wallet upgraded for user {user_id}: Tier {old_tier} → Tier {new_tier}")
                
                # Notify user
                self._notify_user(user_id, "wallet_upgraded", {
                    "old_tier": old_tier,
                    "new_tier": new_tier
                })
                
            return {"status": "success", "message": "Wallet upgrade processed"}
            
        except Exception as e:
            logger.error(f"Failed to handle wallet upgrade: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_transaction_status(self, data):
        """Handle transaction status update"""
        try:
            transaction_id = data.get('transactionId')
            status = data.get('status')
            user_id = data.get('userId')
            
            logger.info(f"📊 Transaction status update: {transaction_id} → {status}")
            
            if user_id and transaction_id:
                # Update transaction status in Supabase
                self.supabase.table("bank_transactions").update({
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("ninepsb_transaction_id", transaction_id).execute()
            
            return {"status": "success", "message": "Transaction status updated"}
            
        except Exception as e:
            logger.error(f"Failed to handle transaction status: {e}")
            return {"status": "error", "message": str(e)}
    
    def _notify_user(self, user_id, event_type, data):
        """Send notification to user via Telegram (optional)"""
        try:
            # This can be implemented to send Telegram notifications
            # For now, just log the notification
            logger.info(f"📱 Notification for user {user_id}: {event_type} - {data}")
            
            # TODO: Implement actual Telegram notification
            # Example:
            # from utils.telegram_notifier import send_notification
            # send_notification(user_id, event_type, data)
            
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")

# Global instance
ninepsb_webhook_handler = NINEPSBWebhookHandler()
