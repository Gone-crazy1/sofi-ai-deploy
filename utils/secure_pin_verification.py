"""
🔐 SECURE PIN VERIFICATION SYSTEM

Professional secure PIN verification system for Sofi AI transfers.
Implements web app-based PIN entry (like Kuda, Paystack, Moniepoint).

Flow:
1. User initiates transfer → Sofi shows inline keyboard
2. User clicks "Verify Transaction" → Opens secure web app
3. User enters PIN in web app → Submits securely
4. Backend verifies PIN → Processes transfer
5. Sofi sends: PIN approved → Transfer in progress → Success → Receipt
"""

import logging
import asyncio
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
    """Handles secure PIN verification for transfers using web app"""
    
    def __init__(self):
        self.bank_api = BankAPI()
        self.pending_transactions = {}  # Store pending transactions
        
    def store_pending_transaction(self, transaction_id: str, transaction_data: Dict):
        """Store transaction data for PIN verification"""
        # Add expiry time (15 minutes)
        transaction_data['expires_at'] = datetime.now() + timedelta(minutes=15)
        self.pending_transactions[transaction_id] = transaction_data
        logger.info(f"Stored pending transaction {transaction_id}")
        
    def get_pending_transaction(self, transaction_id: str) -> Optional[Dict]:
        """Get pending transaction data"""
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
            if not balance_check['sufficient']:
                await self._send_transfer_failed_message(
                    chat_id, f"Insufficient balance. Available: ₦{balance_check['available']:,.2f}"
                )
                return {'success': False, 'error': 'Insufficient balance'}
            
            limit_check = await validate_transaction_limits(str(user_id), amount)
            if not limit_check['valid']:
                await self._send_transfer_failed_message(
                    chat_id, limit_check['error']
                )
                return {'success': False, 'error': limit_check['error']}
            
            # Execute transfer via bank API
            transfer_result = await self.bank_api.transfer_money(
                amount=amount,
                account_number=transfer_data['account_number'],
                bank_name=transfer_data['bank'],
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
                    transaction_id, balance_check['new_balance']
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
        message = (
            f"✅ *Transfer Successful!*\n\n"
            f"₦{amount:,.2f} sent to *{transfer_data['recipient_name']}*\n"
            f"*{transfer_data['bank']}* ({transfer_data['account_number']})\n\n"
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

# Global instance
secure_pin_verification = SecurePinVerification()
