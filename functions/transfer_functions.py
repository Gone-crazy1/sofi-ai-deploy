"""
Transfer-related functions for Sofi AI Assistant
Handles money transfers using Paystack
"""

import logging
from typing import Dict, Any
from supabase import create_client
import os
from paystack.paystack_service import get_paystack_service
from utils.secure_transfer_handler import SecureTransferHandler
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

async def send_money(chat_id: str, amount: float, narration: str = None, pin: str = None, 
                    recipient_account: str = None, recipient_bank: str = None,
                    account_number: str = None, bank_name: str = None, **kwargs) -> Dict[str, Any]:
    """
    Send money to another bank account using Paystack
    
    Args:
        chat_id (str): Sender's Telegram chat ID
        amount (float): Amount to send
        narration (str, optional): Transfer description
        pin (str, optional): User's transaction PIN
        recipient_account (str, optional): Recipient's account number (old format)
        recipient_bank (str, optional): Recipient's bank code or name (old format)
        account_number (str, optional): Recipient's account number (new format)
        bank_name (str, optional): Recipient's bank code or name (new format)
        
    Returns:
        Dict containing transfer result
    """
    try:
        # Support both parameter name formats for compatibility
        recipient_account = recipient_account or account_number
        recipient_bank = recipient_bank or bank_name
        
        if not recipient_account:
            return {"success": False, "error": "Missing recipient account number"}
        
        if not recipient_bank:
            return {"success": False, "error": "Missing recipient bank"}
        
        logger.info(f"💸 Processing Paystack transfer from {chat_id}: ₦{amount} to {recipient_account} at {recipient_bank}")
        
        # Official Paystack bank codes (updated from API)
        bank_name_to_code = {
            # Major Commercial Banks
            "access bank": "044",
            "access bank plc": "044",
            "access bank (diamond)": "063",
            "citibank": "023",
            "citibank nigeria": "023",
            "ecobank": "050",
            "ecobank nigeria": "050",
            "fidelity bank": "070",
            "fidelity bank plc": "070",
            "first bank": "011",
            "first bank of nigeria": "011",
            "first bank nigeria": "011",
            "fcmb": "214",
            "first city monument bank": "214",
            "gtbank": "058",
            "gtb": "058",
            "guaranty trust bank": "058",
            "heritage bank": "030",
            "heritage banking company": "030",
            "keystone bank": "082",
            "polaris bank": "076",
            "polaris bank limited": "076",
            "stanbic ibtc": "221",
            "stanbic ibtc bank": "221",
            "sterling bank": "232",
            "sterling bank plc": "232",
            "uba": "033",
            "united bank for africa": "033",
            "union bank": "032",
            "union bank of nigeria": "032",
            "unity bank": "215",
            "unity bank plc": "215",
            "wema bank": "035",
            "wema bank plc": "035",
            "alat by wema": "035A",
            "alat": "035A",
            "zenith bank": "057",
            "zenith bank plc": "057",
            
            # Digital/Fintech Banks (verified from Paystack API)
            "opay": "999992",
            "opay digital services": "999992",
            "moniepoint": "50515",
            "moniepoint mfb": "50515",
            "palmpay": "999991",
            "palmpay limited": "999991",
            "kuda": "50211",
            "kuda bank": "50211",
            "kuda microfinance bank": "50211",
            "carbon": "565",
            "carbon microfinance bank": "565",
            "fairmoney": "51318",
            "fairmoney microfinance bank": "51318",
            "gomoney": "100022",
            "gomoney nigeria": "100022",
            "vfd": "566",
            "vfd microfinance bank": "566",
            "rubies": "125",
            "rubies microfinance bank": "125",
            "sparkle": "51310",
            "sparkle microfinance bank": "51310",
            "mint": "50304",
            "mint fintech": "50304",
            "eyowo": "50126",
            "eyowo microfinance bank": "50126",
            "aella mfb": "50315",
            "buypower mfb": "50645",
            "9mobile 9payment service bank": "120001",
            "airtel smartcash psb": "120004",
            
            # More Microfinance Banks (from Paystack API)
            "ab microfinance bank": "51204",
            "above only mfb": "51204",
            "accion microfinance bank": "602",
            "aku microfinance bank": "51336",
            "amju unique mfb": "50926",
            "aramoko mfb": "50083",
            "assets microfinance bank": "50092",
            "bainescredit mfb": "51229",
            "banc corp microfinance bank": "50117",
            "baobab microfinance bank": "MFB50992",
            "bellbank microfinance bank": "51100",
            "beststar microfinance bank": "50123",
            "bowen microfinance bank": "50931",
            "cemcs microfinance bank": "50823",
            "consumer microfinance bank": "50910",
            "corestep mfb": "50204",
            
            # Specialized Banks
            "jaiz bank": "301",
            "jaiz bank plc": "301",
            "providus bank": "101",
            "providus bank limited": "101",
            "suntrust bank": "100",
            "suntrust bank nigeria": "100",
            "taj bank": "302",
            "taj bank limited": "302",
            "lotus bank": "303",
            "lotus bank nigeria": "303",
            "coronation bank": "559",
            "coronation merchant bank": "559",
            "alpha morgan bank": "108",
            
            # Mortgage Banks
            "ag mortgage bank": "90077",
            "abbey mortgage bank": "404",
            "aso savings and loans": "401",
            
            # Development Finance Institutions
            "nexim bank": "304",
            "nigeria export import bank": "304",
            "federal mortgage bank": "413",
            "fmbn": "413",
            "bank of industry": "070",
            "boi": "070",
            "bank of agriculture": "044",
            "boa": "044"
        }
        
        # If recipient_bank is a name, convert to code
        if recipient_bank.lower() in bank_name_to_code:
            bank_code = bank_name_to_code[recipient_bank.lower()]
            logger.info(f"🔄 Converted bank name '{recipient_bank}' to code '{bank_code}'")
            recipient_bank = bank_code
        
        # Validate inputs
        if amount <= 0:
            return {
                "success": False,
                "error": "Invalid amount. Amount must be greater than 0."
            }
        
        if amount < 100:  # Paystack minimum
            return {
                "success": False,
                "error": "Minimum transfer amount is ₦100."
            }
        
        # Get Paystack service
        paystack = get_paystack_service()
        
        # Validate transfer amount
        validation = paystack.validate_transfer_amount(amount)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["errors"][0]
            }
        
        # Check if user exists
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            return {
                "success": False,
                "error": "User not found. Please complete registration first."
            }
        
        user_data = user_result.data[0]
        
        # Check if PIN is provided - if not, trigger PIN entry flow
        if not pin:
            # No PIN provided - start PIN entry flow
            from utils.pin_entry_system import pin_manager
            
            # Start PIN entry session
            transfer_data = {
                "account_number": recipient_account,
                "bank_name": recipient_bank,
                "amount": amount,
                "narration": narration or f"Transfer from {user_data.get('full_name', 'Sofi User')}",
                "temp_id": f"transfer_{chat_id}_{int(datetime.now().timestamp())}"
            }
            
            pin_manager.start_pin_session(chat_id, "transfer", transfer_data)
            
            # Return special response indicating PIN entry is needed
            return {
                "success": False,
                "requires_pin": True,
                "message": f"Please enter your 4-digit PIN to send ₦{amount:,.0f} to {recipient_account}",
                "show_pin_keyboard": True,
                "transfer_data": transfer_data
            }
        
        # Verify PIN if provided
        if pin:
            from functions.security_functions import verify_pin
            pin_result = await verify_pin(chat_id=chat_id, pin=pin)
            if not pin_result["valid"]:
                return {
                    "success": False,
                    "error": "Invalid PIN. Please check your PIN and try again."
                }
        
        # First verify the recipient account
        logger.info(f"🔍 Verifying recipient account: {recipient_account}")
        
        verify_result = paystack.verify_account_number(recipient_account, recipient_bank)
        if not verify_result["success"] or not verify_result["verified"]:
            return {
                "success": False,
                "error": f"Could not verify recipient account: {verify_result.get('error', 'Invalid account details')}"
            }
        
        recipient_name = verify_result["account_name"]
        logger.info(f"✅ Account verified: {recipient_name}")
        
        # Prepare transfer
        transfer_reason = narration or f"Transfer from {user_data.get('full_name', 'Sofi User')}"
        
        # Execute transfer using Paystack
        transfer_result = paystack.create_recipient_and_send(
            account_number=recipient_account,
            bank_code=recipient_bank,
            account_name=recipient_name,
            amount=amount,
            reason=transfer_reason
        )
        
        # 🎯 CRITICAL FIX: Check if Paystack operations actually succeeded
        # The create_recipient_and_send returns success=True even if recipient creation worked but transfer failed
        recipient_created = transfer_result.get("success") and transfer_result.get("recipient")
        actual_transfer_data = transfer_result.get("transfer")
        transfer_code = transfer_result.get("transfer_code")
        
        # Determine if the actual money transfer worked
        paystack_transfer_success = (
            recipient_created and 
            actual_transfer_data is not None and
            transfer_code is not None
        )
        
        logger.info(f"📊 Transfer Analysis:")
        logger.info(f"   Recipient created: {recipient_created}")
        logger.info(f"   Transfer data: {actual_transfer_data is not None}")
        logger.info(f"   Transfer code: {transfer_code}")
        logger.info(f"   Overall success: {paystack_transfer_success}")
        
        if paystack_transfer_success:
            # Generate transaction ID
            transaction_id = str(uuid.uuid4())
            
            # 🎯 CRITICAL: Check if Paystack transfer actually worked
            requires_otp = transfer_result.get("requires_otp", False)
            
            # Prepare transaction data for database (include both column name formats for compatibility)
            transaction_data = {
                "user_id": chat_id,
                "transaction_id": transaction_id,
                "type": "transfer_out", 
                "amount": amount,
                # Include both column name formats for compatibility
                "recipient_account": recipient_account,
                "account_number": recipient_account,  # Alternative column name
                "recipient_name": recipient_name,
                "recipient_bank": recipient_bank,
                "bank_name": recipient_bank,  # Alternative column name
                "narration": transfer_reason,
                "status": "completed" if paystack_transfer_success and not requires_otp else "pending_otp",
                "transfer_code": transfer_code,
                "created_at": datetime.now().isoformat()
            }
            
            # Try to save to database (but don't fail the whole transfer if this fails)
            db_save_success = False
            try:
                supabase.table("bank_transactions").insert(transaction_data).execute()
                db_save_success = True
                logger.info(f"✅ Transaction recorded in database: {transaction_id}")
            except Exception as db_error:
                logger.warning(f"⚠️ Could not save transaction to database: {db_error}")
                logger.info(f"💡 But Paystack transfer still worked! Transfer code: {transfer_code}")
                # Don't fail the transfer because of database issues
            
            # 🎯 Return success based on PAYSTACK result, not database result
            if paystack_transfer_success:
                if requires_otp:
                    return {
                        "success": True,
                        "requires_otp": True,
                        "transfer_code": transfer_code,
                        "message": f"Transfer requires OTP verification. Transfer code: {transfer_code}",
                        "amount": amount,
                        "recipient": recipient_name,
                        "transaction_id": transaction_id,
                        "db_saved": db_save_success
                    }
                else:
                    return {
                        "success": True,
                        "message": f"✅ ₦{amount:,.0f} sent to {recipient_name}",
                        "amount": amount,
                        "recipient": recipient_name,
                        "transaction_id": transaction_id,
                        "transfer_code": transfer_code,
                        "reference": transfer_code,
                        "status": "completed",
                        "db_saved": db_save_success
                    }
            else:
                return {
                    "success": False,
                    "error": f"Paystack transfer failed: {transfer_result.get('error', 'Unknown error')}"
                }
        else:
            return {
                "success": False,
                "error": f"Transfer failed: {transfer_result.get('error', 'Unknown error')}"
            }
        
    except Exception as e:
        logger.error(f"❌ Error in send_money: {str(e)}")
        return {
            "success": False,
            "error": f"Transfer failed due to system error: {str(e)}"
        }


async def calculate_transfer_fee(amount: float, **kwargs) -> Dict[str, Any]:
    """
    Calculate transfer fee for a given amount
    
    Args:
        amount (float): Transfer amount
        
    Returns:
        Dict containing fee information
    """
    try:
        # Sofi AI fee structure
        if amount <= 5000:
            fee = 10.0
        elif amount <= 50000:
            fee = 25.0
        else:
            fee = 50.0
        
        return {
            "amount": amount,
            "fee": fee,
            "total": amount + fee,
            "fee_percentage": (fee / amount) * 100 if amount > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating fee: {str(e)}")
        return {
            "amount": amount,
            "fee": 10.0,  # Default fee
            "total": amount + 10.0,
            "error": str(e)
        }
