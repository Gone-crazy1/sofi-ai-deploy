"""
🔐 SECURE TRANSFER FLOW HANDLER

This module provides a clean, secure transfer flow that:
1. Checks balance before allowing transfers
2. Implements proper PIN verification
3. Validates transaction limits
4. Prevents users from going into debt
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional
from utils.conversation_state import conversation_state
from utils.bank_api import BankAPI
from utils.permanent_memory import (
    verify_user_pin, track_pin_attempt, is_user_locked,
    check_sufficient_balance, validate_transaction_limits
)

logger = logging.getLogger(__name__)

class SecureTransferHandler:
    """Handles secure transfer flow with balance and PIN verification"""
    
    def __init__(self):
        self.bank_api = BankAPI()
    
    async def handle_transfer_confirmation(self, chat_id: str, message: str, user_data: Dict, transfer_data: Dict) -> str:
        """
        Handle the transfer confirmation step with comprehensive security checks
        
        Args:
            chat_id: Telegram chat ID
            message: User's message (PIN or 'cancel')
            user_data: User information from database
            transfer_data: Transfer details
            
        Returns:
            str: Response message to user
        """
        try:
            # Handle cancellation
            if message.lower() == 'cancel':
                conversation_state.clear_state(chat_id)
                return "Transfer cancelled. Is there anything else I can help you with?"
            
            # Get user ID
            user_id = user_data.get('id')
            if not user_id:
                conversation_state.clear_state(chat_id)
                return "❌ **Error:** User authentication required. Please try again."
            
            transfer_amount = transfer_data['amount']
            
            # SECURITY CHECK 1: Account lockout protection
            if await is_user_locked(str(user_id)):
                conversation_state.clear_state(chat_id)
                return ("🔒 **Account Temporarily Locked**\n\n"
                       "Too many failed PIN attempts. Please try again in 15 minutes for security.")
            
            # SECURITY CHECK 2: Balance verification (most important!)
            balance_check = await check_sufficient_balance(str(user_id), transfer_amount, include_fees=True)
            
            if not balance_check["sufficient"]:
                virtual_account = await self.get_virtual_account(chat_id)
                insufficient_msg = self.format_insufficient_balance_message(balance_check, virtual_account)
                conversation_state.clear_state(chat_id)
                return insufficient_msg
            
            # SECURITY CHECK 3: Transaction limits
            limits_check = await validate_transaction_limits(str(user_id), transfer_amount)
            
            if not limits_check["valid"]:
                conversation_state.clear_state(chat_id)
                return (f"❌ **Transaction Limit Exceeded**\n\n"
                       f"{limits_check['error']}\n\n"
                       f"Please contact support if you need higher limits.")
            
            # SECURITY CHECK 4: PIN verification
            pin_valid = await verify_user_pin(str(user_id), message.strip())
            
            # SECURITY CHECK 5: Track PIN attempt for rate limiting
            attempt_result = await track_pin_attempt(str(user_id), pin_valid)
            
            if not pin_valid:
                return self.handle_failed_pin_attempt(chat_id, attempt_result)
            
            # All security checks passed - execute transfer
            return await self.execute_secure_transfer(chat_id, user_data, transfer_data, balance_check)
            
        except Exception as e:
            logger.error(f"Error in secure transfer confirmation: {e}")
            conversation_state.clear_state(chat_id)
            return "❌ **Error:** Unable to process transfer. Please try again later."
    
    def handle_failed_pin_attempt(self, chat_id: str, attempt_result: Dict) -> str:
        """Handle failed PIN attempt with appropriate response"""
        if attempt_result.get('locked'):
            conversation_state.clear_state(chat_id)
            return (f"🔒 **Account Locked**\n\n"
                   f"Too many failed attempts. Your account is locked for 15 minutes for security.\n\n"
                   f"Try again after {attempt_result.get('minutes_remaining', 15)} minutes.")
        else:
            remaining_attempts = attempt_result.get('remaining_attempts', 0)
            if remaining_attempts > 0:
                return (f"❌ **Incorrect PIN**\n\n"
                       f"You have {remaining_attempts} attempt(s) remaining.\n\n"
                       f"Please enter your 4-digit PIN or type 'cancel' to cancel:")
            else:
                return ("❌ **Incorrect PIN**\n\n"
                       "Please enter your 4-digit PIN or type 'cancel' to cancel:")
    
    def format_insufficient_balance_message(self, balance_check: Dict, virtual_account: Dict) -> str:
        """Format user-friendly insufficient balance message with funding options"""
        return (
            f"❌ **Insufficient Balance**\n\n"
            f"💰 **Your Balance:** ₦{balance_check['balance']:,.2f}\n"
            f"💸 **Required Amount:** ₦{balance_check['required']:,.2f}\n"
            f"📊 **Transfer:** ₦{balance_check['transfer_amount']:,.2f}\n"
            f"💳 **Fees:** ₦{balance_check['fees']:,.2f}\n"
            f"📉 **Shortfall:** ₦{balance_check['shortfall']:,.2f}\n\n"
            f"**🏦 Fund Your Wallet:**\n"
            f"• Transfer money to your Sofi account\n"
            f"• Account: {virtual_account.get('accountNumber', 'N/A')}\n"
            f"• Bank: {virtual_account.get('bankName', 'N/A')}\n\n"
            f"**💎 Or Create Crypto Wallet:**\n"
            f"• Type 'create wallet' for instant funding\n"
            f"• Deposit BTC/USDT for immediate NGN credit\n\n"
            f"Type 'cancel' to cancel this transfer."
        )
    
    async def execute_secure_transfer(self, chat_id: str, user_data: Dict, transfer_data: Dict, balance_info: Dict) -> str:
        """Execute the transfer after all security checks have passed"""
        try:
            # Execute transfer via OPay API
            transfer_result = await self.bank_api.execute_transfer({
                'amount': transfer_data['amount'],
                'recipient_account': transfer_data['account_number'],
                'recipient_bank': transfer_data['bank'],
                'recipient_name': transfer_data['recipient_name'],
                'narration': transfer_data.get('narration', 'Transfer via Sofi AI')
            })
            
            if transfer_result.get('success'):
                # Update user balance (deduct transfer amount + fees)
                await self.update_user_balance_after_transfer(
                    user_data.get('id'), 
                    balance_info['required']  # Total amount including fees
                )
                
                # Generate and send receipt
                receipt = self.generate_transfer_receipt(user_data, transfer_data, transfer_result, balance_info)
                
                # Log successful transaction
                await self.log_successful_transaction(user_data, transfer_data, transfer_result)
                  # Clear conversation state
                conversation_state.clear_state(chat_id)
                
                return f"✅ **Transfer Successful!** Here's your receipt:\n\n{receipt}"
            
            else:
                error_msg = transfer_result.get('error', 'Transfer failed')
                logger.error(f"Transfer failed: {error_msg}")
                conversation_state.clear_state(chat_id)
                return f"❌ **Transfer Failed:** {error_msg}\n\nPlease try again or contact support."
        
        except Exception as e:
            logger.error(f"Error executing secure transfer: {e}")
            conversation_state.clear_state(chat_id)
            return "❌ **Error:** Transfer processing failed. Please try again later."
    
    async def get_virtual_account(self, chat_id: str) -> Dict:
        """Get user's virtual account details for funding instructions"""
        try:
            from supabase import create_client
            
            client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            result = client.table("virtual_accounts").select("*").eq("telegram_chat_id", str(chat_id)).execute()
            
            if result.data:
                return result.data[0]
            else:
                return {"accountNumber": "N/A", "bankName": "N/A"}
        
        except Exception as e:
            logger.error(f"Error getting virtual account: {e}")
            return {"accountNumber": "N/A", "bankName": "N/A"}
    
    async def update_user_balance_after_transfer(self, user_id: str, deduct_amount: float):
        """Update user balance after successful transfer"""
        try:
            from supabase import create_client
            
            client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            # Get current balance
            result = client.table("virtual_accounts").select("balance").eq("user_id", user_id).execute()
            
            if result.data:
                current_balance = float(result.data[0].get("balance", 0))
                new_balance = max(0, current_balance - deduct_amount)  # Never go negative
                
                # Update balance
                client.table("virtual_accounts").update({
                    "balance": new_balance,
                    "updated_at": datetime.now().isoformat()
                }).eq("user_id", user_id).execute()
                
                logger.info(f"Updated balance for user {user_id}: ₦{current_balance:,.2f} → ₦{new_balance:,.2f}")
                
        except Exception as e:
            logger.error(f"Error updating balance for user {user_id}: {e}")
    
    def generate_transfer_receipt(self, user_data: Dict, transfer_data: Dict, transfer_result: Dict, balance_info: Dict) -> str:
        """Generate a professional transfer receipt"""
        return f"""
=================================
      SOFI AI TRANSFER RECEIPT
=================================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Transaction ID: {transfer_result.get('transaction_id', 'N/A')}
---------------------------------
Sender: {user_data.get('first_name', 'User')}
Amount: ₦{transfer_data['amount']:,.2f}
Recipient: {transfer_data['recipient_name']}
Account: {transfer_data['account_number']}
Bank: {transfer_data['bank']}
Fees: ₦{balance_info['fees']:,.2f}
---------------------------------
New Balance: ₦{balance_info['balance'] - balance_info['required']:,.2f}
=================================
    Thank you for using Sofi AI!
=================================
"""
    
    async def log_successful_transaction(self, user_data: Dict, transfer_data: Dict, transfer_result: Dict):
        """Log the successful transaction for audit trail"""
        try:
            from supabase import create_client
            import os
            
            client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            transaction_data = {
                "user_id": user_data.get('id'),
                "transaction_type": "debit",
                "amount": transfer_data['amount'],
                "recipient_account": transfer_data['account_number'],
                "recipient_bank": transfer_data['bank'],
                "transaction_reference": transfer_result.get('transaction_id'),
                "status": "success",
                "created_at": datetime.now().isoformat(),
                "webhook_data": transfer_result
            }
            
            client.table("bank_transactions").insert(transaction_data).execute()
            logger.info(f"Logged successful transaction for user {user_data.get('id')}")
            
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")

# Create global handler instance
secure_transfer_handler = SecureTransferHandler()

# Export the main function
async def handle_secure_transfer_confirmation(chat_id: str, message: str, user_data: Dict, transfer_data: Dict) -> str:
    """Main entry point for secure transfer confirmation"""
    return await secure_transfer_handler.handle_transfer_confirmation(chat_id, message, user_data, transfer_data)
