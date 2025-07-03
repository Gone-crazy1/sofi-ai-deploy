#!/usr/bin/env python3
"""
Complete implementation of Xara-style transfer flow with clean confirmation and PIN entry
"""

# Import necessary modules
import os
import logging
from flask import jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XaraStyleTransferFlow:
    """Implementation of Xara-style transfer flow with clean confirmation and PIN entry"""
    
    def __init__(self, send_reply_func, answer_callback_func, paystack_api):
        """Initialize with necessary functions and APIs"""
        self.send_reply = send_reply_func
        self.answer_callback_query = answer_callback_func
        self.paystack = paystack_api
    
    def parse_transfer_command(self, message):
        """Parse Xara-style transfer command: account bank send amount"""
        try:
            parts = message.strip().split()
            
            if len(parts) >= 4:
                # Pattern: account bank send amount
                if parts[-2].lower() == "send":
                    account_number = parts[0]
                    bank_name = parts[-3]
                    amount = float(parts[-1])
                    
                    if account_number.isdigit() and len(account_number) >= 10:
                        return {
                            "account_number": account_number,
                            "bank": bank_name,
                            "amount": amount
                        }
            
            return None
                
        except Exception as e:
            logger.error(f"Error parsing transfer command: {e}")
            return None
    
    def normalize_bank_name(self, bank):
        """Normalize bank name to standard format"""
        bank = bank.lower()
        
        # Common bank name mappings
        bank_mappings = {
            "gtb": "gtbank",
            "uba": "united bank for africa",
            "fcmb": "first city monument bank",
            "fbn": "first bank",
            "firstbank": "first bank",
            "access": "access bank",
            "stanbic": "stanbic ibtc bank",
            "zenith": "zenith bank",
            "sterling": "sterling bank",
            "union": "union bank",
            "wema": "wema bank",
            "eco": "ecobank",
            "fidelity": "fidelity bank",
            "heritage": "heritage bank",
            "keystone": "keystone bank",
            "polaris": "polaris bank",
            "providus": "providus bank",
            "titan": "titan bank",
            "unity": "unity bank",
            "jaiz": "jaiz bank",
            "kuda": "kuda bank",
            "opay": "opay",
            "palmpay": "palmpay",
            "moniepoint": "moniepoint",
        }
        
        return bank_mappings.get(bank, bank)
    
    def get_bank_code(self, bank_name):
        """Get bank code from bank name"""
        # This function should be implemented by calling a bank code lookup service
        # For this example, we'll just return some common codes
        
        bank_codes = {
            "gtbank": "058",
            "first bank": "011",
            "zenith bank": "057",
            "access bank": "044",
            "united bank for africa": "033",
            "opay": "999992",
            "palmpay": "100004",
            "moniepoint": "50515",
            "kuda bank": "50211",
        }
        
        normalized_bank = self.normalize_bank_name(bank_name)
        return bank_codes.get(normalized_bank, "")
    
    async def handle_transfer_command(self, chat_id, message):
        """Handle Xara-style transfer command"""
        try:
            # Parse the command
            parsed = self.parse_transfer_command(message)
            
            if not parsed:
                return
                
            logger.info(f"🎯 Smart transfer command detected: {parsed}")
            
            # Get bank code from name
            bank_name = self.normalize_bank_name(parsed['bank'])
            bank_code = self.get_bank_code(bank_name)
            
            if not bank_code:
                self.send_reply(chat_id, f"❌ *Bank not supported*\n\nBank '{parsed['bank']}' is not supported. Please use a valid bank name.")
                return
                
            # Step 1: Auto-verify account (silently)
            verify_result = self.paystack.verify_account_number(parsed['account_number'], bank_code)
            
            if not verify_result.get("success") or not verify_result.get("verified"):
                self.send_reply(chat_id, f"❌ *Account verification failed*\n\n{verify_result.get('error', 'Invalid account details')}")
                return
                
            verified_name = verify_result["account_name"]
            
            # Step 2: Show professional confirmation with account name
            confirmation_msg = f"""✅ *Account Verified: {verified_name}*

You're about to send ₦{parsed['amount']:,.2f} to:
🏦 {verified_name} — {parsed['account_number']} ({bank_name.title()})

👉 Please click the button below to verify this transaction:"""
            
            # Send confirmation with verify button
            verify_keyboard = {
                "inline_keyboard": [[
                    {"text": "✅ Verify Transaction", "callback_data": f"verify_transfer_{chat_id}_{parsed['account_number']}_{bank_code}_{parsed['amount']}_{verified_name.replace(' ', '_')}"}
                ]]
            }
            
            self.send_reply(chat_id, confirmation_msg, verify_keyboard)
            return "Transfer confirmation sent"
                
        except Exception as e:
            logger.error(f"Error handling smart transfer command: {e}")
            self.send_reply(chat_id, f"❌ *Error*\n\nCouldn't process your transfer request: {str(e)}")
    
    async def handle_verify_callback(self, query_id, callback_data, chat_id):
        """Handle verification button callback"""
        try:
            # Parse callback data: verify_transfer_chatid_account_bankcode_amount_name
            parts = callback_data.split("_")
            
            if len(parts) >= 6:
                # Extract data
                verify_chat_id = parts[2]
                account_number = parts[3]
                bank_code = parts[4]
                amount = float(parts[5])
                verified_name = "_".join(parts[6:]).replace("_", " ")
                
                # Get bank name from code (should be implemented)
                bank_name = "Unknown Bank"  # This should be looked up from bank_code
                
                # Validate user
                if verify_chat_id != chat_id:
                    await self.answer_callback_query(query_id, "❌ Invalid verification request")
                    return jsonify({"error": "Invalid request"}), 400
                
                # Show "Processing" feedback
                await self.answer_callback_query(query_id, "Processing verification...")
                
                # Create PIN entry button
                pin_link_keyboard = {
                    "inline_keyboard": [[
                        {"text": "🔐 Enter My PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                    ]]
                }
                
                # Send PIN entry request
                pin_message = f"""✅ *Account Verified: {verified_name}*

You're about to send ₦{amount:,.2f} to:
🏦 {verified_name} — {account_number} ({bank_name})

👉 Please click the button below to enter your 4-digit transaction PIN securely:"""
                
                self.send_reply(chat_id, pin_message, pin_link_keyboard)
                return jsonify({"success": True}), 200
                
        except Exception as e:
            logger.error(f"Error handling verification: {e}")
            await self.answer_callback_query(query_id, "❌ Verification failed")
            self.send_reply(chat_id, f"❌ *Error*\n\nVerification failed: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    async def handle_pin_entry_callback(self, query_id, callback_data, chat_id):
        """Handle PIN entry button callback"""
        try:
            # Parse callback data: pin_entry_chatid_amount_account_bank_name
            parts = callback_data.split("_")
            
            if len(parts) >= 3:
                # Extract data
                entry_chat_id = parts[2]
                amount = float(parts[3]) if len(parts) > 3 else 0
                account = parts[4] if len(parts) > 4 else ""
                bank = parts[5] if len(parts) > 5 else ""
                verified_name = "_".join(parts[6:]).replace("_", " ") if len(parts) > 6 else ""
                
                # Validate user
                if entry_chat_id != chat_id:
                    await self.answer_callback_query(query_id, "❌ Invalid PIN entry request")
                    return jsonify({"error": "Invalid request"}), 400
                
                # Create PIN entry keyboard
                from utils.pin_entry_system import create_pin_entry_keyboard, initialize_pin_session
                pin_keyboard = create_pin_entry_keyboard()
                
                # Send PIN entry request privately
                pin_message = f"🔐 *Enter your 4-digit PIN*\n\nPlease enter your PIN securely to complete the transfer of ₦{amount:,.2f} to {verified_name}"
                self.send_reply(chat_id, pin_message, pin_keyboard)
                
                # Store transfer details in pin session
                initialize_pin_session(chat_id, "transfer", {
                    "amount": amount,
                    "account_number": account,
                    "bank_code": bank,
                    "verified_name": verified_name
                })
                
                # Acknowledge callback
                await self.answer_callback_query(query_id, "PIN entry ready")
                return jsonify({"success": True}), 200
                
        except Exception as e:
            logger.error(f"Error handling PIN entry link: {e}")
            await self.answer_callback_query(query_id, "❌ PIN entry failed")
            self.send_reply(chat_id, f"❌ PIN entry failed: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    async def handle_pin_digit_callback(self, query_id, callback_data, chat_id):
        """Handle PIN digit button callback"""
        try:
            # Parse callback data to get the digit
            digit = callback_data.replace("pin_", "")
            
            if digit in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "clear", "submit", "cancel"]:
                from utils.pin_entry_system import PINManager
                pin_manager = PINManager()
                
                if digit == "clear":
                    # Handle clear button
                    pin_manager.clear_pin(chat_id)
                    await self.answer_callback_query(query_id, "PIN cleared")
                    return jsonify({"success": True}), 200
                    
                elif digit == "cancel":
                    # Handle cancel button
                    pin_manager.clear_pin(chat_id)
                    await self.answer_callback_query(query_id, "Transfer cancelled")
                    self.send_reply(chat_id, "❌ *Transfer cancelled*\n\nYour transfer has been cancelled.")
                    return jsonify({"success": True}), 200
                    
                elif digit == "submit":
                    # Handle submit button
                    result = await self.handle_pin_submit(chat_id)
                    
                    if result.get("success"):
                        await self.answer_callback_query(query_id, "Transfer completed!")
                    else:
                        await self.answer_callback_query(query_id, "PIN verification failed")
                        
                    return jsonify({"success": True}), 200
                    
                else:
                    # Handle digit button
                    result = pin_manager.add_pin_digit(chat_id, digit)
                    
                    if result.get("status") == "complete":
                        # Auto-submit when 4 digits entered
                        await self.answer_callback_query(query_id, "PIN complete - submitting...")
                        submit_result = await self.handle_pin_submit(chat_id)
                        
                        if submit_result.get("success"):
                            # Send basic confirmation
                            self.send_reply(chat_id, "✅ Transfer completed successfully!")
                            
                            # Then send beautiful receipt if available
                            if submit_result.get("receipt_sent"):
                                logger.info(f"📧 Beautiful receipt already sent to {chat_id}")
                            
                        else:
                            self.send_reply(chat_id, f"❌ {submit_result.get('error', 'Transfer failed')}")
                            
                    else:
                        # Show PIN progress
                        pin_display = "•" * result.get("length", 0)
                        await self.answer_callback_query(query_id, f"PIN: {pin_display}")
                    
                    return jsonify({"success": True}), 200
                    
        except Exception as e:
            logger.error(f"Error in PIN callback: {e}")
            await self.answer_callback_query(query_id, "❌ PIN error")
            return jsonify({"error": str(e)}), 500
    
    async def handle_pin_submit(self, chat_id):
        """Handle PIN submission"""
        try:
            from utils.pin_entry_system import PINManager, get_pin_session
            pin_manager = PINManager()
            
            # Verify PIN
            from functions.security_functions import verify_pin
            pin_code = pin_manager.get_current_pin(chat_id)
            verify_result = verify_pin(chat_id, pin_code)
            
            if not verify_result.get("success"):
                self.send_reply(chat_id, "❌ *Invalid PIN*\n\nPlease check your PIN and try again.")
                pin_manager.clear_pin(chat_id)
                return {"success": False, "error": "Invalid PIN"}
            
            # Get transfer details from session
            session = get_pin_session(chat_id)
            transfer_data = session.get("transfer_data", {})
            
            if not transfer_data:
                self.send_reply(chat_id, "❌ *Transfer failed*\n\nNo transfer details found. Please try again.")
                pin_manager.clear_pin(chat_id)
                return {"success": False, "error": "No transfer details"}
            
            # Process the transfer
            from functions.transfer_functions import send_money_internal
            transfer_result = send_money_internal(
                chat_id, 
                transfer_data.get("account_number"),
                transfer_data.get("bank_code"),
                transfer_data.get("amount"),
                transfer_data.get("verified_name", "")
            )
            
            # Clear PIN session
            pin_manager.clear_pin(chat_id)
            
            if transfer_result.get("success"):
                # Generate and send receipt
                from utils.receipt_generator import generate_transfer_receipt
                receipt_path = generate_transfer_receipt(
                    chat_id,
                    transfer_data.get("amount"),
                    transfer_data.get("account_number"),
                    transfer_data.get("bank_code"),
                    transfer_data.get("verified_name", ""),
                    transfer_result.get("reference", "")
                )
                
                if receipt_path:
                    # Send receipt as image
                    self.send_photo(chat_id, receipt_path)
                    
                    # Send text receipt as well
                    receipt_text = f"""✅ *Transfer Successful*

💰 Amount: ₦{transfer_data.get("amount"):,.2f}
👤 Recipient: {transfer_data.get("verified_name")}
🏦 Bank: {transfer_data.get("bank_code")}
🔢 Account: {transfer_data.get("account_number")}
🔑 Reference: {transfer_result.get("reference")}
⏱️ Date: {datetime.now().strftime("%d/%m/%Y %H:%M")}

Thank you for using Sofi AI!"""
                    
                    self.send_reply(chat_id, receipt_text)
                    return {"success": True, "receipt_sent": True}
                
                return {"success": True, "receipt_sent": False}
            else:
                self.send_reply(chat_id, f"❌ *Transfer failed*\n\n{transfer_result.get('error', 'Unknown error')}")
                return {"success": False, "error": transfer_result.get("error", "Unknown error")}
            
        except Exception as e:
            logger.error(f"Error in PIN submit: {e}")
            self.send_reply(chat_id, f"❌ *Transfer failed*\n\nAn error occurred: {str(e)}")
            return {"success": False, "error": str(e)}
