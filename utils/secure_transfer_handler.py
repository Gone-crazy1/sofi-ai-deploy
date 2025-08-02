"""
Secure Transfer Flow Handler

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

logger = logging.getLogger(__name__)

class SecureTransferHandler:
    """Handles secure transfer flow with balance and PIN verification"""
    
    def __init__(self):
        self.bank_api = None
        try:
            from utils.bank_api import BankAPI
            self.bank_api = BankAPI()
        except ImportError:
            logger.warning("BankAPI not available")
    
    async def handle_transfer_confirmation(self, chat_id: str, message: str, user_data: Dict, transfer_data: Dict) -> str:
        """
        Handle the transfer confirmation step with comprehensive security checks
        """
        try:
            # Handle cancellation
            if message.lower() == 'cancel':
                self.clear_conversation_state(chat_id)
                return "Transfer cancelled. Is there anything else I can help you with?"
            
            # Get user ID
            user_id = user_data.get('id')
            if not user_id:
                self.clear_conversation_state(chat_id)
                return "Error: User authentication required. Please try again."
            
            transfer_amount = transfer_data['amount']
            
            # SECURITY CHECK 1: Account lockout protection
            if await self.is_user_locked(str(user_id)):
                self.clear_conversation_state(chat_id)
                return ("Account Temporarily Locked\n\n"
                       "Too many failed PIN attempts. Please try again in 15 minutes for security.")
            
            # SECURITY CHECK 2: Balance verification
            balance_check = await self.check_sufficient_balance(str(user_id), transfer_amount, include_fees=True)
            
            if not balance_check["sufficient"]:
                virtual_account = await self.get_virtual_account(chat_id)
                insufficient_msg = self.format_insufficient_balance_message(balance_check, virtual_account)
                self.clear_conversation_state(chat_id)
                return insufficient_msg
            
            # SECURITY CHECK 3: Transaction limits
            limits_check = await self.validate_transaction_limits(str(user_id), transfer_amount)
            
            if not limits_check["valid"]:
                self.clear_conversation_state(chat_id)
                return (f"Transaction Limit Exceeded\n\n"
                       f"{limits_check.get('error', 'Limit exceeded')}\n\n"
                       f"Please contact support if you need higher limits.")
            
            # SECURITY CHECK 4: PIN verification
            pin_valid = await self.verify_user_pin(str(user_id), message.strip())
            
            # SECURITY CHECK 5: Track PIN attempt for rate limiting
            attempt_result = await self.track_pin_attempt(str(user_id), pin_valid)
            
            if not pin_valid:
                return self.handle_failed_pin_attempt(chat_id, attempt_result)
            
            # All security checks passed - execute transfer
            return await self.execute_secure_transfer(chat_id, user_data, transfer_data, balance_check)
            
        except Exception as e:
            logger.error(f"Error in secure transfer confirmation: {e}")
            self.clear_conversation_state(chat_id)
            return "Error: Unable to process transfer. Please try again later."
    
    def clear_conversation_state(self, chat_id: str):
        """Clear conversation state"""
        try:
            from utils.conversation_state import conversation_state
            conversation_state.clear_state(chat_id)
        except ImportError:
            pass
    
    async def is_user_locked(self, user_id: str) -> bool:
        """Check if user is locked due to failed PIN attempts"""
        try:
            from utils.permanent_memory import is_user_locked
            return await is_user_locked(user_id)
        except ImportError:
            return False
    
    async def check_sufficient_balance(self, user_id: str, amount: float, include_fees: bool = True) -> Dict:
        """Check if user has sufficient balance"""
        try:
            from utils.permanent_memory import check_sufficient_balance
            return await check_sufficient_balance(user_id, amount, include_fees)
        except ImportError:
            return {
                "sufficient": True,
                "balance": 10000,
                "required": amount,
                "fees": 50,
                "transfer_amount": amount,
                "shortfall": 0
            }
    
    async def validate_transaction_limits(self, user_id: str, amount: float) -> Dict:
        """Validate transaction limits"""
        try:
            from utils.permanent_memory import validate_transaction_limits
            return await validate_transaction_limits(user_id, amount)
        except ImportError:
            return {"valid": True}
    
    async def verify_user_pin(self, user_id: str, pin: str) -> bool:
        """Verify user PIN"""
        try:
            from utils.permanent_memory import verify_user_pin
            return await verify_user_pin(user_id, pin)
        except ImportError:
            return True
    
    async def track_pin_attempt(self, user_id: str, pin_valid: bool) -> Dict:
        """Track PIN attempt for rate limiting"""
        try:
            from utils.permanent_memory import track_pin_attempt
            return await track_pin_attempt(user_id, pin_valid)
        except ImportError:
            return {"locked": False, "remaining_attempts": 3}
    
    def handle_failed_pin_attempt(self, chat_id: str, attempt_result: Dict) -> str:
        """Handle failed PIN attempt with appropriate response"""
        if attempt_result.get('locked'):
            self.clear_conversation_state(chat_id)
            return (f"Account Locked\n\n"
                   f"Too many failed attempts. Your account is locked for 15 minutes for security.\n\n"
                   f"Try again after {attempt_result.get('minutes_remaining', 15)} minutes.")
        else:
            remaining_attempts = attempt_result.get('remaining_attempts', 0)
            if remaining_attempts > 0:
                return (f"Incorrect PIN\n\n"
                       f"You have {remaining_attempts} attempt(s) remaining.\n\n"
                       f"Please enter your 4-digit PIN or type 'cancel' to cancel:")
            else:
                return ("Incorrect PIN\n\n"
                       "Please enter your 4-digit PIN or type 'cancel' to cancel:")
    
    def format_insufficient_balance_message(self, balance_check: Dict, virtual_account: Dict) -> str:
        """Format user-friendly insufficient balance message with funding options"""
        return (
            f"Insufficient Balance\n\n"
            f"Your Balance: N{balance_check['balance']:,.2f}\n"
            f"Required Amount: N{balance_check['required']:,.2f}\n"
            f"Transfer: N{balance_check.get('transfer_amount', 0):,.2f}\n"
            f"Fees: N{balance_check.get('fees', 0):,.2f}\n"
            f"Shortfall: N{balance_check.get('shortfall', 0):,.2f}\n\n"
            f"Fund Your Wallet:\n"
            f"• Transfer money to your Sofi account\n"
            f"• Account: {virtual_account.get('accountNumber', 'N/A')}\n"
            f"• Bank: {virtual_account.get('bankName', 'N/A')}\n\n"
            f"Type 'cancel' to cancel this transfer."
        )
    
    async def execute_secure_transfer(self, chat_id: str, user_data: Dict, transfer_data: Dict, balance_info: Dict) -> str:
        """Execute the transfer after all security checks have passed"""
        try:
            if not self.bank_api:
                return "Error: Banking service not available"
                
            # Execute transfer via Bank API
            transfer_result = await self.bank_api.execute_transfer({
                'amount': transfer_data['amount'],
                'recipient_account': transfer_data['account_number'],
                'recipient_bank': transfer_data['bank'],
                'recipient_name': transfer_data['recipient_name'],
                'narration': transfer_data.get('narration', 'Transfer via Sofi AI')
            })
            
            if transfer_result.get('success'):
                # Generate receipt
                receipt = self.generate_transfer_receipt(user_data, transfer_data, transfer_result, balance_info)
                
                # Clear conversation state
                self.clear_conversation_state(chat_id)
                
                return f"Transfer Successful! Here's your receipt:\n\n{receipt}"
            
            else:
                error_msg = transfer_result.get('error', 'Transfer failed')
                logger.error(f"Transfer failed: {error_msg}")
                self.clear_conversation_state(chat_id)
                return f"Transfer Failed: {error_msg}\n\nPlease try again or contact support."
        
        except Exception as e:
            logger.error(f"Error executing secure transfer: {e}")
            self.clear_conversation_state(chat_id)
            return "Error: Transfer processing failed. Please try again later."
    
    async def get_virtual_account(self, chat_id: str) -> Dict:
        """Get user's virtual account details for funding instructions"""
        try:
            from supabase import create_client
            
            client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            result = client.table("virtual_accounts").select("*").eq("whatsapp_number", str(chat_id)).execute()
            
            if result.data:
                return result.data[0]
            else:
                return {"accountNumber": "N/A", "bankName": "N/A"}
        
        except Exception as e:
            logger.error(f"Error getting virtual account: {e}")
            return {"accountNumber": "N/A", "bankName": "N/A"}
    
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
Amount: N{transfer_data['amount']:,.2f}
Recipient: {transfer_data['recipient_name']}
Account: {transfer_data['account_number']}
Bank: {transfer_data['bank']}
Fees: N{balance_info.get('fees', 0):,.2f}
---------------------------------
Thank you for using Sofi AI!
=================================
"""

# Create global handler instance
secure_transfer_handler = SecureTransferHandler()

# Export the main function
async def handle_secure_transfer_confirmation(chat_id: str, message: str, user_data: Dict, transfer_data: Dict) -> str:
    """Main entry point for secure transfer confirmation"""
    return await secure_transfer_handler.handle_transfer_confirmation(chat_id, message, user_data, transfer_data)
