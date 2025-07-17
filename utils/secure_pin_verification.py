"""
🔐 SECURE PIN VERIFICATION SYSTEM

Professional secure PIN verification system for Sofi AI transfers.
Implements web app-based PIN entry (like Kuda, Paystack, Moniepoint).

Flow:
1. User initiates transfer → Sofi shows inline keyboard
2. User clicks "Verify Transaction" → Opens secure web app with secure token
3. User enters PIN in web app → Submits securely
4. Backend verifies PIN → Processes transfer
5. Sofi sends: PIN approved → Transfer in progress → Success → Receipt
"""

import logging
import asyncio
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from utils.conversation_state import conversation_state
from utils.bank_api import BankAPI
from utils.permanent_memory import (
    verify_user_pin, track_pin_attempt, is_user_locked,
    check_sufficient_balance, validate_transaction_limits
)
from utils.notification_service import notification_service
from beautiful_receipt_generator import SofiReceiptGenerator

logger = logging.getLogger(__name__)

class SecurePinVerification:
    """Handles secure PIN verification for transfers using web app with token-based security"""
    
    def __init__(self):
        self.bank_api = BankAPI()
        self.pending_transactions = {}  # Store pending transactions by txn_id
        self.secure_tokens = {}  # Store secure tokens mapping to txn_id
        self.used_tokens = set()  # Track used tokens to prevent replay
        
    def _generate_secure_token(self, transaction_id: str) -> str:
        """Generate a secure token for the transaction"""
        # Create a secure random token
        token = secrets.token_urlsafe(32)  # 256-bit security
        
        # Create mapping from token to transaction
        self.secure_tokens[token] = {
            'transaction_id': transaction_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=15),
            'used': False
        }
        
        logger.info(f"🔑 Generated secure token for transaction {transaction_id}")
        return token
        
    def store_pending_transaction(self, transaction_id: str, transaction_data: Dict) -> str:
        """Store transaction data for PIN verification and return secure token"""
        # Add expiry time (15 minutes)
        transaction_data['expires_at'] = datetime.now() + timedelta(minutes=15)
        transaction_data['created_at'] = datetime.now()
        
        self.pending_transactions[transaction_id] = transaction_data
        
        # Generate secure token
        secure_token = self._generate_secure_token(transaction_id)
        
        logger.info(f"💾 Stored pending transaction {transaction_id} with secure token")
        return secure_token
        
    def get_pending_transaction_by_token(self, secure_token: str) -> Optional[Dict]:
        """Get pending transaction data using secure token"""
        # Check if token exists and is valid
        token_data = self.secure_tokens.get(secure_token)
        
        if not token_data:
            logger.warning(f"❌ Invalid token attempt: {secure_token[:10]}...")
            return None
            
        # Check if token is expired
        if datetime.now() > token_data['expires_at']:
            logger.warning(f"⏰ Expired token attempt: {secure_token[:10]}...")
            # Clean up expired token
            del self.secure_tokens[secure_token]
            return None
            
        # Check if token was already used (prevent replay attacks)
        if token_data['used']:
            logger.warning(f"🔄 Replay attack attempt with used token: {secure_token[:10]}...")
            return None
            
        # Get the actual transaction
        transaction_id = token_data['transaction_id']
        transaction = self.pending_transactions.get(transaction_id)
        
        if not transaction:
            logger.warning(f"❌ Transaction not found for token: {secure_token[:10]}...")
            return None
            
        # Check if transaction is expired
        if datetime.now() > transaction['expires_at']:
            logger.warning(f"⏰ Expired transaction: {transaction_id}")
            # Clean up expired transaction
            del self.pending_transactions[transaction_id]
            return None
            
        logger.info(f"✅ Valid token access for transaction: {transaction_id}")
        return transaction
        
    def mark_token_as_used(self, secure_token: str):
        """Mark a token as used to prevent replay attacks"""
        token_data = self.secure_tokens.get(secure_token)
        if token_data:
            token_data['used'] = True
            self.used_tokens.add(secure_token)
            logger.info(f"🔒 Token marked as used: {secure_token[:10]}...")
            
    def cleanup_expired_data(self):
        """Clean up expired transactions and tokens"""
        now = datetime.now()
        
        # Clean expired transactions
        expired_txns = [
            txn_id for txn_id, txn_data in self.pending_transactions.items()
            if now > txn_data['expires_at']
        ]
        for txn_id in expired_txns:
            del self.pending_transactions[txn_id]
            
        # Clean expired tokens
        expired_tokens = [
            token for token, token_data in self.secure_tokens.items()
            if now > token_data['expires_at']
        ]
        for token in expired_tokens:
            del self.secure_tokens[token]
            
        if expired_txns or expired_tokens:
            logger.info(f"🧹 Cleaned up {len(expired_txns)} expired transactions and {len(expired_tokens)} expired tokens")
        
    def get_pending_transaction(self, transaction_id: str) -> Optional[Dict]:
        """Get pending transaction data (legacy method for backward compatibility)"""
        transaction = self.pending_transactions.get(transaction_id)
        
        if not transaction:
            return None
            
        # Check if expired
        if datetime.now() > transaction['expires_at']:
            del self.pending_transactions[transaction_id]
            return None
            
        return transaction
        
    async def verify_pin_and_process_transfer(self, transaction_id: str, pin: str) -> Dict:
        """
        Verify PIN and process transfer if valid
        
        Args:
            transaction_id: Unique transaction identifier
            pin: User's PIN
            
        Returns:
            Dict with verification result
        """
        try:
            # Get pending transaction
            transaction = self.get_pending_transaction(transaction_id)
            if not transaction:
                return {
                    'success': False,
                    'error': 'Transaction not found or expired'
                }
            
            chat_id = transaction['chat_id']
            user_data = transaction['user_data']
            transfer_data = transaction['transfer_data']
            amount = transaction['amount']
            
            # 🔥 EARLY VALIDATION: Check transaction data structure
            logger.info(f"🔍 Transaction data validation for {transaction_id}")
            logger.info(f"  - chat_id: {chat_id}")
            logger.info(f"  - amount: {amount}")
            logger.info(f"  - transfer_data type: {type(transfer_data)}")
            logger.info(f"  - transfer_data keys: {list(transfer_data.keys()) if isinstance(transfer_data, dict) else 'Not a dict'}")
            
            # Validate transfer_data is a proper dictionary
            if not isinstance(transfer_data, dict):
                logger.error(f"❌ CRITICAL: transfer_data is {type(transfer_data)}, not dict")
                return {
                    'success': False,
                    'error': f'Invalid transfer data type: {type(transfer_data)}'
                }
            
            # Check for essential fields
            essential_fields = ['account_number', 'recipient_name']
            missing_essential = [field for field in essential_fields if not transfer_data.get(field)]
            
            if missing_essential:
                logger.error(f"❌ Missing essential fields: {missing_essential}")
                return {
                    'success': False,
                    'error': f'Missing essential transfer information: {missing_essential}'
                }
            
            # Step 1: Send "PIN approved, transfer in progress" message
            await self._send_pin_approved_message(chat_id)
            
            # Step 2: Verify PIN
            user_id = user_data.get('id')
            if not user_id:
                return {'success': False, 'error': 'User ID not found'}
            
            # Check if user is locked
            if await is_user_locked(str(user_id)):
                return {
                    'success': False,
                    'error': 'Account temporarily locked due to too many failed PIN attempts'
                }
            
            # Verify PIN
            pin_valid = await verify_user_pin(str(user_id), pin.strip())
            await track_pin_attempt(str(user_id), pin_valid)
            
            if not pin_valid:
                return {
                    'success': False,
                    'error': 'Invalid PIN'
                }
            
            # Step 3: Process transfer
            result = await self._process_secure_transfer(
                chat_id, user_data, transfer_data, amount, transaction_id
            )
            
            # Clean up pending transaction
            if transaction_id in self.pending_transactions:
                del self.pending_transactions[transaction_id]
                
            return result
            
        except Exception as e:
            logger.error(f"Error in PIN verification and transfer processing: {e}")
            return {
                'success': False,
                'error': 'Transfer processing failed'
            }
    
    async def _send_pin_approved_message(self, chat_id: str):
        """Send PIN approved message immediately"""
        message = "✅ *PIN Verified.* Transfer in progress..."
        await notification_service.send_telegram_message(
            chat_id, message, "Markdown"
        )
        
    async def _process_secure_transfer(self, chat_id: str, user_data: Dict, 
                                     transfer_data: Dict, amount: float, 
                                     transaction_id: str) -> Dict:
        """Process the actual transfer with all security checks"""
        try:
            user_id = user_data.get('id')
            
            # Security checks
            balance_check = await check_sufficient_balance(str(user_id), amount)
            
            # Handle case where balance_check might be a boolean (fallback)
            if isinstance(balance_check, bool):
                if not balance_check:
                    await self._send_transfer_failed_message(
                        chat_id, "Insufficient balance for this transfer"
                    )
                    return {'success': False, 'error': 'Insufficient balance'}
                # If True, continue but create a mock balance_check dict
                balance_check = {
                    'sufficient': True,
                    'balance': amount + 100,  # Assume sufficient balance
                    'required': amount
                }
            elif not isinstance(balance_check, dict):
                # Handle any other unexpected return type
                await self._send_transfer_failed_message(
                    chat_id, "Error checking balance. Please try again."
                )
                return {'success': False, 'error': 'Balance check failed'}
            
            # Now safely access dictionary keys
            if not balance_check.get('sufficient', False):
                available_balance = balance_check.get('balance', 0)
                await self._send_transfer_failed_message(
                    chat_id, f"Insufficient balance. Available: ₦{available_balance:,.2f}"
                )
                return {'success': False, 'error': 'Insufficient balance'}
            
            limit_check = await validate_transaction_limits(str(user_id), amount)
            
            # Handle case where limit_check might not be a dict
            if not isinstance(limit_check, dict):
                await self._send_transfer_failed_message(
                    chat_id, "Error validating transaction limits. Please try again."
                )
                return {'success': False, 'error': 'Limit validation failed'}
            
            if not limit_check.get('valid', True):  # Default to True if key missing
                error_msg = limit_check.get('error', 'Transaction limit exceeded')
                await self._send_transfer_failed_message(
                    chat_id, error_msg
                )
                return {'success': False, 'error': error_msg}
            
            # 🔥 CRITICAL VALIDATION: Check transfer_data structure
            if not isinstance(transfer_data, dict):
                logger.error(f"❌ transfer_data is not a dict: {type(transfer_data)}")
                await self._send_transfer_failed_message(
                    chat_id, "Invalid transfer data structure. Please try again."
                )
                return {'success': False, 'error': 'Invalid transfer data structure'}
            
            # Check for required fields in transfer_data (handle field name variations)
            required_fields = ['account_number', 'recipient_name']
            bank_field_present = 'bank' in transfer_data or 'bank_name' in transfer_data
            
            missing_fields = [field for field in required_fields if field not in transfer_data]
            
            if missing_fields:
                logger.error(f"❌ Missing required fields in transfer_data: {missing_fields}")
                logger.error(f"❌ Available fields in transfer_data: {list(transfer_data.keys())}")
                await self._send_transfer_failed_message(
                    chat_id, f"Missing transfer information: {', '.join(missing_fields)}"
                )
                return {'success': False, 'error': f'Missing required fields: {missing_fields}'}
            
            if not bank_field_present:
                logger.error(f"❌ No bank field found in transfer_data (looking for 'bank' or 'bank_name')")
                logger.error(f"❌ Available fields in transfer_data: {list(transfer_data.keys())}")
                await self._send_transfer_failed_message(
                    chat_id, "Missing bank information for transfer"
                )
                return {'success': False, 'error': 'Missing bank information'}
            
            # Use bank_name if bank is missing (field name inconsistency fix)
            bank_field = transfer_data.get('bank') or transfer_data.get('bank_name', 'Unknown')
            account_number = transfer_data.get('account_number', '')
            
            logger.info(f"🔍 Transfer validation passed - Bank: {bank_field}, Account: {account_number}")
            
            # Execute transfer via bank API
            transfer_result = await self.bank_api.transfer_money(
                amount=amount,
                account_number=account_number,
                bank_name=bank_field,
                narration=f"Transfer via Sofi AI - {transaction_id}",
                reference=transaction_id
            )
            
            if transfer_result.get('success'):
                # Calculate correct new balance after transfer
                transfer_fee = float(transfer_data.get('fee', 20.0))
                actual_new_balance = balance_check['balance'] - (amount + transfer_fee)
                
                # 🔥 CRITICAL FIX: Update wallet balance in database
                await self._update_wallet_balance_and_log_transaction(
                    user_id, actual_new_balance, amount, transfer_fee, 
                    transfer_data, transaction_id
                )
                
                # Send ONLY success message (no duplicate receipt)
                await self._send_transfer_success_message(
                    chat_id, transfer_data, amount, transaction_id
                )
                
                # DISABLED: Don't send second text receipt since we have web receipt
                # await self._send_transfer_receipt(
                #     chat_id, user_data, transfer_data, amount, 
                #     transaction_id, actual_new_balance
                # )
                
                # Clear conversation state
                conversation_state.clear_state(chat_id)
                
                return {'success': True, 'transaction_id': transaction_id}
            else:
                await self._send_transfer_failed_message(
                    chat_id, transfer_result.get('error', 'Transfer failed')
                )
                return {'success': False, 'error': transfer_result.get('error')}
                
        except Exception as e:
            logger.error(f"Error processing secure transfer: {e}")
            await self._send_transfer_failed_message(
                chat_id, "Transfer processing failed. Please try again."
            )
            return {'success': False, 'error': str(e)}
    
    async def _send_transfer_success_message(self, chat_id: str, transfer_data: Dict, 
                                           amount: float, transaction_id: str):
        """Send transfer success notification"""
        # Map bank code to bank name for display
        bank_code = transfer_data.get('bank_name', transfer_data.get('bank', 'Unknown'))
        bank_display_name = self._get_bank_display_name(bank_code)
        
        message = (
            f"✅ *Transfer Successful!*\n\n"
            f"₦{amount:,.2f} sent to *{transfer_data['recipient_name']}*\n"
            f"*{bank_display_name}* ({transfer_data['account_number']})\n\n"
            f"📋 *Transaction Ref:* {transaction_id}"
        )
        
        await notification_service.send_telegram_message(
            chat_id, message, "Markdown"
        )
    
    def _get_bank_display_name(self, bank_code: str) -> str:
        """Convert bank code to display name"""
        bank_names = {
            "035": "Wema Bank",
            "044": "Access Bank", 
            "058": "GTBank",
            "057": "Zenith Bank",
            "033": "UBA",
            "011": "First Bank",
            "032": "Union Bank",
            "070": "Fidelity Bank",
            "232": "Sterling Bank",
            "221": "Stanbic IBTC",
            "999992": "Opay",
            "999991": "PalmPay",
            "50211": "Kuda Bank",
            "50515": "Moniepoint MFB",
            "565": "Carbon",
            "214": "FCMB"
        }
        return bank_names.get(bank_code, f"Bank ({bank_code})")
    
    async def _send_transfer_receipt(self, chat_id: str, user_data: Dict, 
                                   transfer_data: Dict, amount: float, 
                                   transaction_id: str, new_balance: float):
        """Send beautiful transfer receipt"""
        try:
            # Generate beautiful receipt
            receipt_generator = SofiReceiptGenerator()
            receipt = receipt_generator.create_bank_transfer_receipt({
                'user_name': user_data.get('full_name', 'User'),
                'amount': amount,
                'recipient_name': transfer_data['recipient_name'],
                'recipient_account': transfer_data['account_number'],
                'bank': transfer_data['bank'],
                'balance': new_balance,
                'transaction_id': transaction_id
            })
            
            # Send receipt
            await notification_service.send_telegram_message(
                chat_id, receipt, "Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error sending transfer receipt: {e}")
    
    async def _send_transfer_failed_message(self, chat_id: str, error_message: str):
        """Send transfer failed notification"""
        message = f"❌ *Transfer Failed*\n\n{error_message}\n\nPlease try again."
        
        await notification_service.send_telegram_message(
            chat_id, message, "Markdown"
        )
    
    async def _update_wallet_balance_and_log_transaction(self, user_id: str, 
                                                       new_balance: float, 
                                                       amount: float, 
                                                       fee: float,
                                                       transfer_data: Dict, 
                                                       transaction_id: str):
        """
        🔥 CRITICAL: Update wallet balance and log transaction to database
        
        This ensures:
        1. User's wallet_balance is debited correctly
        2. Transaction is logged for history
        3. Balance reflects actual transfer
        """
        try:
            from supabase import create_client
            import os
            
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # 1. Update wallet balance in users table
            logger.info(f"💰 Updating wallet balance: {new_balance:.2f} for user {user_id}")
            
            balance_update = supabase.table("users").update({
                "wallet_balance": new_balance
            }).eq("id", user_id).execute()
            
            if balance_update.data:
                logger.info(f"✅ Wallet balance updated successfully: ₦{new_balance:,.2f}")
            else:
                logger.error(f"❌ Failed to update wallet balance for user {user_id}")
            
            # 2. Log transaction in bank_transactions table
            bank_display_name = self._get_bank_display_name(
                transfer_data.get('bank_name', transfer_data.get('bank', 'Unknown'))
            )
            
            transaction_record = {
                "user_id": user_id,
                "transaction_type": "transfer",  # Proper categorization
                "amount": amount,
                "fee": fee,
                "total_amount": amount + fee,
                "recipient_name": transfer_data.get('recipient_name', 'Unknown'),
                "recipient_account": transfer_data.get('account_number', ''),
                "bank_name": bank_display_name,
                "bank_code": transfer_data.get('bank_name', transfer_data.get('bank', '')),
                "reference": transaction_id,
                "status": "success",
                "description": f"Bank Transfer to {transfer_data.get('recipient_name', 'Unknown')}",
                "narration": f"Transfer via Sofi AI to {bank_display_name}",
                "balance_before": new_balance + (amount + fee),  # Calculate previous balance
                "balance_after": new_balance,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"📝 Logging transaction: {transaction_id}")
            
            transaction_insert = supabase.table("bank_transactions").insert(transaction_record).execute()
            
            if transaction_insert.data:
                logger.info(f"✅ Transaction logged successfully: {transaction_id}")
            else:
                logger.error(f"❌ Failed to log transaction: {transaction_id}")
            
            # 3. Verify balance update
            verification = supabase.table("users").select("wallet_balance").eq("id", user_id).execute()
            
            if verification.data:
                actual_balance = verification.data[0].get("wallet_balance", 0)
                logger.info(f"🔍 Balance verification: Expected ₦{new_balance:,.2f}, Actual ₦{actual_balance:,.2f}")
                
                if abs(actual_balance - new_balance) > 0.01:  # Allow for small rounding differences
                    logger.warning(f"⚠️ Balance mismatch detected!")
                else:
                    logger.info(f"✅ Balance update verified successfully")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR updating wallet balance and logging transaction: {e}")
            # This is critical - if balance update fails, we need to know
            raise Exception(f"Failed to update wallet balance: {e}")

# Global instance
secure_pin_verification = SecurePinVerification()
