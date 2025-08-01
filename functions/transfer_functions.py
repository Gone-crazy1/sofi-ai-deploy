"""
Transfer-related functions for Sofi AI Assistant
Handles money transfers using Paystack
"""

import logging
from typing import Dict, Any, Optional
from supabase import create_client
import os
from paystack.paystack_service import get_paystack_service
from utils.secure_transfer_handler import SecureTransferHandler
from datetime import datetime
import uuid
from flask import current_app as app

logger = logging.getLogger(__name__)

# Bank code to name mapping for user-friendly display
BANK_CODE_TO_NAME = {
    # Major Commercial Banks
    "044": "Access Bank",
    "063": "Access Bank (Diamond)",
    "023": "Citibank",
    "050": "Ecobank",
    "070": "Fidelity Bank",
    "011": "First Bank",
    "214": "FCMB",
    "058": "GTBank",
    "030": "Heritage Bank",
    "082": "Keystone Bank",
    "076": "Polaris Bank",
    "221": "Stanbic IBTC",
    "232": "Sterling Bank",
    "033": "UBA",
    "032": "Union Bank",
    "215": "Unity Bank",
    "035": "Wema Bank",
    "035A": "Alat by Wema",
    "057": "Zenith Bank",
    
    # Digital/Fintech Banks
    "999992": "OPay",
    "50515": "Moniepoint",
    "999991": "PalmPay",
    "50211": "Kuda Bank",
    "565": "Carbon",
    "51318": "FairMoney",
    "100022": "GoMoney",
    "566": "VFD",
    "125": "Rubies Bank",
    "51310": "Sparkle",
    "50304": "Mint",
    "50126": "Eyowo",
    "50315": "Aella MFB",
    "50645": "BuyPower MFB",
    "120001": "9PSB",  # 9mobile 9Payment Service Bank
    "120004": "Airtel SmartCash PSB",
    
    # More Microfinance Banks
    "51204": "AB Microfinance Bank",
    "602": "Accion MFB",
    "51336": "Aku MFB",
    "50926": "Amju Unique MFB",
    "50083": "Aramoko MFB",
    "50092": "Assets MFB",
    "51229": "BainesCredit MFB",
    "50117": "Banc Corp MFB",
    "MFB50992": "Baobab MFB",
    "51100": "BellBank MFB",
    "50123": "BestStar MFB",
    "50931": "Bowen MFB",
    "50823": "CEMCS MFB",
    "50910": "Consumer MFB",
    "50204": "CoreStep MFB",
    
    # Specialized Banks
    "301": "Jaiz Bank",
    "101": "Providus Bank",
    "100": "SunTrust Bank",
    "302": "TAJ Bank",
    "303": "Lotus Bank",
    "559": "Coronation Bank",
    "108": "Alpha Morgan Bank",
    
    # Mortgage Banks
    "90077": "AG Mortgage Bank",
    "404": "Abbey Mortgage Bank",
    "401": "ASO Savings & Loans",
    
    # Development Finance Institutions
    "304": "NEXIM Bank",
    "413": "Federal Mortgage Bank",
    "070": "Bank of Industry",
}

async def send_money(chat_id: str, amount: float, narration: str = None, pin: str = None, 
                    recipient_account: str = None, recipient_bank: str = None,
                    account_number: str = None, bank_name: str = None, **kwargs) -> Dict[str, Any]:
    """
    Send money to another bank account using Paystack
    
    Args:
        chat_id (str): Sender's WhatsApp chat ID
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
    # 🔧 FIX: Wrap in Flask app context to prevent "Working outside of application context" error
    try:
        with app.app_context():
            return await _send_money_internal(chat_id, amount, narration, pin, 
                                            recipient_account, recipient_bank,
                                            account_number, bank_name, **kwargs)
    except RuntimeError as e:
        if "working outside of application context" in str(e).lower():
            # Fallback: try without context wrapper
            logger.warning(f"⚠️  Flask context error, attempting fallback: {e}")
            return await _send_money_internal(chat_id, amount, narration, pin, 
                                            recipient_account, recipient_bank,
                                            account_number, bank_name, **kwargs)
        else:
            raise e

async def _send_money_internal(chat_id: str, amount: float, narration: str = None, pin: str = None, 
                              recipient_account: str = None, recipient_bank: str = None,
                              account_number: str = None, bank_name: str = None, **kwargs) -> Dict[str, Any]:
    """Internal transfer function - wrapped by send_money for Flask context"""
    try:
        # Support both parameter name formats for compatibility
        recipient_account = recipient_account or account_number
        recipient_bank = recipient_bank or bank_name
        
        if not recipient_account:
            return {"success": False, "error": "Missing recipient account number"}
        
        if not recipient_bank:
            return {"success": False, "error": "Missing recipient bank"}
        
        logger.info(f"💸 Processing Paystack transfer from {chat_id}: ₦{amount} to {recipient_account} at {recipient_bank}")
        
        # If recipient_bank is a name, convert to code
        bank_code = get_bank_code_from_name(recipient_bank)
        if bank_code:
            logger.info(f"🔄 Converted bank name '{recipient_bank}' to code '{bank_code}'")
            recipient_bank = bank_code
        else:
            # If not in mapping, assume it's already a bank code
            bank_code = recipient_bank
        
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
        user_result = supabase.table("users").select("*").eq("whatsapp_number", str(chat_id)).execute()
        
        if not user_result.data:
            return {
                "success": False,
                "error": "User not found. Please complete registration first."
            }
        
        user_data = user_result.data[0]
        
        # Check if user has sufficient balance (including transfer fees)
        current_balance = user_data.get("wallet_balance", 0)
        
        # Calculate transfer fees (Sofi profit + Paystack charges)
        fee_calculation = await calculate_transfer_fee(amount)
        sofi_fee = fee_calculation["sofi_fee"]      # Your profit
        paystack_fee = fee_calculation["paystack_fee"]  # Paystack cost (10 naira)
        total_fees = fee_calculation["total_fee"]   # Total fees to deduct
        total_cost = fee_calculation["total"]       # Amount + all fees
        
        if current_balance < total_cost:
            return {
                "success": False,
                "error": f"Insufficient balance. You need ₦{total_cost:,.2f} (₦{amount:,.2f} + ₦{total_fees:,.2f} fee) but have ₦{current_balance:,.2f}."
            }
        
        # Check if PIN is provided - if not, trigger web PIN entry flow
        if not pin:
            # No PIN provided - start web PIN entry flow
            
            # First verify the recipient account before showing PIN entry
            logger.info(f"🔍 Verifying recipient account: {recipient_account}")
            
            verify_result = paystack.verify_account_number(recipient_account, recipient_bank)
            if not verify_result["success"] or not verify_result["verified"]:
                return {
                    "success": False,
                    "error": f"Could not verify recipient account: {verify_result.get('error', 'Invalid account details')}"
                }
            
            recipient_name = verify_result["account_name"]
            logger.info(f"✅ Account verified: {recipient_name}")
            
            # Calculate transfer fees for display
            fee_calculation = await calculate_transfer_fee(amount)
            total_fees = fee_calculation["total_fee"]
            
            # Create transaction ID for web PIN entry
            transaction_id = f"transfer_{chat_id}_{int(datetime.now().timestamp())}"
            
            # Store transfer data temporarily for PIN verification
            transfer_data = {
                "account_number": recipient_account,
                "bank_name": recipient_bank,
                "amount": amount,
                "recipient_name": recipient_name,
                "narration": narration or f"Transfer from {user_data.get('full_name', 'Sofi User')}",
                "fee": total_fees,
                "transaction_id": transaction_id,
                "chat_id": chat_id,
                "user_id": user_data.get("id"),
                "created_at": datetime.now().isoformat()
            }
            
            # Store transaction for secure verification and get secure token
            from utils.secure_pin_verification import secure_pin_verification
            secure_token = secure_pin_verification.store_pending_transaction(transaction_id, {
                'chat_id': chat_id,
                'user_data': user_data,
                'transfer_data': transfer_data,
                'amount': amount
            })
            
            # Create PIN verification URL with secure token
            pin_url = f"https://pipinstallsofi.com/verify-pin?token={secure_token}"
            
            # Return web PIN entry response with keyboard
            # Convert bank code to friendly name for display
            bank_display_name = BANK_CODE_TO_NAME.get(recipient_bank, recipient_bank)
            
            return {
                "success": False,
                "requires_pin": True,
                "show_web_pin": True,
                "message": f"""💸 You're about to send ₦{amount:,.0f} to:
👤 Name: *{recipient_name}*
🏦 Bank: {bank_display_name}
🔢 Account: {recipient_account}
💰 Fee: ₦{total_fees:,.0f}
💵 Total: ₦{amount + total_fees:,.0f}

🔐 *Choose how to enter your PIN:*
• Tap the button below for secure web entry
• Or send a voice note saying your 4-digit PIN clearly""",
                "pin_url": pin_url,
                "keyboard": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🔐 Enter PIN",
                                "web_app": {"url": pin_url}
                            }
                        ],
                        [
                            {
                                "text": "❌ Cancel Transfer",
                                "callback_data": f"cancel_transfer_{transaction_id}"
                            }
                        ]
                    ]
                },
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
            
            # Calculate fees for transaction recording and balance update
            fee_calculation = await calculate_transfer_fee(amount)
            sofi_fee = fee_calculation["sofi_fee"]      # Your profit
            paystack_fee = fee_calculation["paystack_fee"]  # Paystack cost
            total_deduction = fee_calculation["total"]  # Amount + all fees
            
            # Calculate new balance after deducting transfer + all fees
            current_balance = user_data.get("wallet_balance", 0)
            new_balance = current_balance - total_deduction
            
            # Prepare transaction data for database
            transaction_data = {
                "user_id": chat_id,
                "transaction_id": transaction_id,
                "type": "transfer_out", 
                "amount": amount,
                "fee": sofi_fee,  # Legacy column - keep for compatibility
                "sofi_fee": sofi_fee,  # Your profit (new column)
                "paystack_fee": paystack_fee,  # Paystack costs (new column)
                "total_amount": total_deduction,  # Total amount deducted from user
                # Include both column name formats for compatibility
                "recipient_account": recipient_account,
                "account_number": recipient_account,  # Alternative column name
                "recipient_name": recipient_name,
                "bank_code": bank_code,  # Use bank_code instead of recipient_bank
                "bank_name": recipient_bank,  # Alternative column name
                "narration": transfer_reason,
                "status": "completed" if paystack_transfer_success and not requires_otp else "pending_otp",
                "transfer_code": transfer_code,
                "balance_before": current_balance,
                "balance_after": new_balance,
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
            
            # 🎯 CRITICAL: Update user's wallet balance after successful transfer (including all fees)
            current_balance = user_data.get("wallet_balance", 0)
            fee_calculation = await calculate_transfer_fee(amount)
            sofi_fee = fee_calculation["sofi_fee"]      # Your profit
            paystack_fee = fee_calculation["paystack_fee"]  # Paystack cost (10 naira)
            total_fees = fee_calculation["total_fee"]   # Total fees to deduct
            total_deduction = fee_calculation["total"]  # Amount + all fees
            new_balance = current_balance - total_deduction
            balance_updated = False
            
            try:
                # Update user's wallet balance
                supabase.table("users").update({
                    "wallet_balance": new_balance
                }).eq("whatsapp_number", str(chat_id)).execute()
                
                logger.info(f"💰 Balance updated: ₦{current_balance:,.2f} → ₦{new_balance:,.2f}")
                balance_updated = True
                
            except Exception as balance_error:
                logger.error(f"❌ Failed to update user balance: {balance_error}")
                # Don't fail the transfer, but log the error
            
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
                    # Generate detailed receipt message (simplified for users)
                    balance_display = new_balance if balance_updated else current_balance
                    total_fee_display = sofi_fee + paystack_fee  # Combined fee for user display
                    
                    # Generate beautiful receipt using new receipt generator
                    from utils.receipt_generator import create_transaction_receipt
                    
                    receipt_data = {
                        'amount': amount,
                        'fee': total_fee_display,
                        'total_charged': total_deduction,
                        'new_balance': balance_display,
                        'recipient_name': recipient_name,
                        'bank_name': recipient_bank,
                        'account_number': recipient_account,
                        'reference': transfer_code,
                        'transaction_id': transaction_id,
                        'transaction_time': datetime.now().strftime('%d/%m/%Y %I:%M %p'),
                        'narration': narration or "Transfer via Sofi AI"
                    }
                    
                    # Generate beautiful WhatsApp receipt
                    receipt_message = create_transaction_receipt(receipt_data, "whatsapp")
                    
                    return {
                        "success": True,
                        "message": receipt_message,
                        "amount": amount,
                        "recipient": recipient_name,
                        "transaction_id": transaction_id,
                        "transfer_code": transfer_code,
                        "reference": transfer_code,
                        "status": "completed",
                        "db_saved": db_save_success,
                        "balance_updated": balance_updated,
                        "new_balance": new_balance,
                        "receipt_data": receipt_data,  # For potential HTML/PDF generation
                        "auto_send_receipt": True  # Flag to indicate receipt should be sent
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
    Includes both Sofi fee (profit) and Paystack fee (cost)
    
    Args:
        amount (float): Transfer amount
        
    Returns:
        Dict containing fee information
    """
    try:
        # Sofi AI fee structure (your profit)
        if amount <= 5000:
            sofi_fee = 10.0
        elif amount <= 50000:
            sofi_fee = 25.0
        else:
            sofi_fee = 50.0
        
        # Paystack fee (always 10 naira - our cost)
        paystack_fee = 10.0
        
        # Total fee charged to user
        total_fee = sofi_fee + paystack_fee
        
        return {
            "amount": amount,
            "sofi_fee": sofi_fee,      # Your profit (internal)
            "paystack_fee": paystack_fee,  # Paystack cost (internal)
            "total_fee": total_fee,    # Total fee shown to user
            "total": amount + total_fee,  # Amount + all fees
            "fee_percentage": (total_fee / amount) * 100 if amount > 0 else 0,
            # User-friendly display values
            "user_fee_display": total_fee,  # What user sees as "fee"
            "user_total_display": amount + total_fee  # What user sees as "total charge"
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating fee: {str(e)}")
        return {
            "amount": amount,
            "sofi_fee": 10.0,      # Default Sofi fee
            "paystack_fee": 10.0,  # Paystack fee
            "total_fee": 20.0,     # Total default fee
            "total": amount + 20.0,
            "error": str(e)
        }

def get_bank_code_from_name(bank_name: str) -> Optional[str]:
    """
    Get bank code from bank name for API verification
    
    Args:
        bank_name (str): Bank name to lookup
        
    Returns:
        str: Bank code if found, None otherwise
    """
    # Official Paystack bank codes (same as in send_money function)
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
        
        # Digital/Fintech Banks
        "opay": "999992",
        "opay digital services": "999992",
        "opay digital services limited": "999992",
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
        
        # More banks...
        "jaiz bank": "301",
        "providus bank": "101",
        "suntrust bank": "100",
        "taj bank": "302",
        "lotus bank": "303",
        "coronation bank": "559"
    }
    
    # Convert to lowercase for matching
    bank_lower = bank_name.lower().strip()
    
    # Direct match
    if bank_lower in bank_name_to_code:
        return bank_name_to_code[bank_lower]
    
    # Partial match for common variations
    for key in bank_name_to_code:
        if bank_lower in key or key in bank_lower:
            return bank_name_to_code[key]
    
    return None

def get_bank_name_from_code(bank_code: str) -> str:
    """Return the human-readable bank name for a given code."""
    code_to_name = {v: k.title() for k, v in bank_name_to_code.items()}
    # Prefer shortest name for each code
    shortest = {}
    for code, name in code_to_name.items():
        if code not in shortest or len(name) < len(shortest[code]):
            shortest[code] = name
    return shortest.get(bank_code, bank_code)
