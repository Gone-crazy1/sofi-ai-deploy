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
    validate_transaction_limits, SecureTransactionValidator
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
            
            # Debug logging for transfer_data
            logger.info(f"🔍 Retrieved transaction data:")
            logger.info(f"  - chat_id: {chat_id}")
            logger.info(f"  - amount: {amount}")
            logger.info(f"  - transfer_data: {transfer_data}")
            logger.info(f"  - transfer_data type: {type(transfer_data)}")
            if isinstance(transfer_data, dict):
                logger.info(f"  - transfer_data keys: {list(transfer_data.keys())}")
            
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
            
            # Initialize memory system to use the correct balance check method
            memory_system = SecureTransactionValidator()
            
            # Security checks - use the class method that returns Dict
            balance_check = await memory_system.check_sufficient_balance(str(user_id), amount)
            if not balance_check['sufficient']:
                await self._send_transfer_failed_message(
                    chat_id, f"Insufficient balance. Available: ₦{balance_check['balance']:,.2f}"
                )
                return {'success': False, 'error': 'Insufficient balance'}
            
            # Get current balance for receipt
            balance_info = await memory_system.get_user_balance(str(user_id))
            current_balance = balance_info.get('balance', 0.0) if balance_info.get('success') else 0.0
            new_balance = current_balance - amount
            
            limit_check = await validate_transaction_limits(str(user_id), amount)
            if not limit_check['valid']:
                await self._send_transfer_failed_message(
                    chat_id, limit_check['error']
                )
                return {'success': False, 'error': limit_check['error']}
            
            # Validate transfer_data has required fields before processing
            # Note: transfer_data uses 'bank_name' not 'bank'
            required_fields = ['account_number', 'bank_name', 'amount']
            missing_fields = [field for field in required_fields if field not in transfer_data]
            
            if missing_fields:
                error_msg = f"Missing required fields in transfer_data: {missing_fields}. Available fields: {list(transfer_data.keys())}"
                logger.error(error_msg)
                await self._send_transfer_failed_message(
                    chat_id, f"Transfer data incomplete: {missing_fields}"
                )
                return {'success': False, 'error': error_msg}
            
            # Log transfer_data for debugging
            logger.info(f"🔍 Processing transfer with data: {transfer_data}")
            
            # Execute transfer via bank API (use bank_name field)
            transfer_result = await self.bank_api.transfer_money(
                amount=amount,
                account_number=transfer_data['account_number'],
                bank_name=transfer_data['bank_name'],  # Changed from 'bank' to 'bank_name'
                narration=f"Transfer via Sofi AI - {transaction_id}",
                reference=transaction_id
            )
            
            if transfer_result.get('success'):
                # Step 4: Send success message
                await self._send_transfer_success_message(
                    chat_id, transfer_data, amount, transaction_id
                )
                
                # Step 5: Send beautiful receipt
                await self._send_transfer_receipt(
                    chat_id, user_data, transfer_data, amount, 
                    transaction_id, new_balance
                )
                
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
        # Safe access to transfer_data fields with fallbacks
        recipient_name = transfer_data.get('recipient_name', 'Unknown Recipient')
        bank_name = transfer_data.get('bank_name', 'Unknown Bank')  # Changed from 'bank' to 'bank_name'
        account_number = transfer_data.get('account_number', 'Unknown Account')
        
        message = (
            f"✅ *Transfer Successful!*\n\n"
            f"₦{amount:,.2f} sent to *{recipient_name}*\n"
            f"*{bank_name}* ({account_number})\n\n"
            f"📋 *Transaction Ref:* {transaction_id}"
        )
        
        await notification_service.send_telegram_message(
            chat_id, message, "Markdown"
        )
    
    async def _send_transfer_receipt(self, chat_id: str, user_data: Dict, 
                                   transfer_data: Dict, amount: float, 
                                   transaction_id: str, new_balance: float):
        """Send beautiful transfer receipt"""
        try:
            # Generate beautiful receipt with safe field access
            receipt_generator = SofiReceiptGenerator()
            receipt = receipt_generator.create_bank_transfer_receipt({
                'user_name': user_data.get('full_name', 'User'),
                'amount': amount,
                'recipient_name': transfer_data.get('recipient_name', 'Unknown Recipient'),
                'recipient_account': transfer_data.get('account_number', 'Unknown Account'),
                'bank': transfer_data.get('bank_name', 'Unknown Bank'),  # Changed from 'bank' to 'bank_name'
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

# Global instance
secure_pin_verification = SecurePinVerification()
