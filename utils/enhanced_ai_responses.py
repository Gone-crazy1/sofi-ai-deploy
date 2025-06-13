# Enhanced Intent Detection and Response System for Sofi AI
# This fixes all identified issues with poor understanding and wrong responses

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

# Setup logger
logger = logging.getLogger(__name__)

def enhanced_detect_intent(message: str) -> Dict:
    """
    Enhanced intent detection with better understanding of user messages
    Fixes issue #1: Poor Intent Detection
    """
    message_lower = message.lower().strip()
    
    # Deposit/Incoming Transfer Detection (Fix for Issue #2)
    deposit_patterns = [
        r'did you receive.*(transfer|money|payment)',
        r'i sent money.*to.*account',
        r'i just.*transferred.*money',
        r'have you.*received.*transfer',
        r'money.*sent.*to.*my account',
        r'transfer.*to my.*account',
        r'deposit.*arrived',
        r'funding.*my.*wallet'
    ]
    
    for pattern in deposit_patterns:
        if re.search(pattern, message_lower):
            return {"intent": "check_deposit", "details": {"message": message}}
    
    # Balance Check Detection (Fix for Issue #3)
    balance_patterns = [
        r'what.*is.*my.*balance',
        r'current.*balance',
        r'check.*balance',
        r'my.*wallet.*balance',
        r'account.*balance',
        r'how much.*do i have',
        r'balance.*enquiry'
    ]
    
    for pattern in balance_patterns:
        if re.search(pattern, message_lower):
            return {"intent": "check_balance", "details": {}}
    
    # Enhanced Transfer Detection (Fix for Issue #4)
    # Pattern: "Transfer/Send [amount] to [account] [bank]"
    transfer_pattern = r'(?:transfer|send)\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:to|naira to)?\s*([0-9]{10,11})\s+(.+?)(?:\s|$)'
    match = re.search(transfer_pattern, message_lower)
    
    if match:
        amount = match.group(1).replace(',', '')
        account_number = match.group(2)
        bank_part = match.group(3).strip()
        
        # Extract bank name from the bank part
        bank_keywords = {
            'access': 'Access Bank',
            'gtb': 'GTBank',
            'first': 'First Bank',
            'zenith': 'Zenith Bank',
            'uba': 'UBA',
            'fidelity': 'Fidelity Bank',
            'fcmb': 'FCMB',
            'union': 'Union Bank',
            'sterling': 'Sterling Bank',
            'stanbic': 'Stanbic IBTC',
            'wema': 'Wema Bank',
            'polaris': 'Polaris Bank',
            'keystone': 'Keystone Bank',
            'opay': 'Opay',
            'kuda': 'Kuda Bank',
            'palmpay': 'PalmPay'
        }
        
        detected_bank = None
        for keyword, full_name in bank_keywords.items():
            if keyword in bank_part:
                detected_bank = full_name
                break
        
        if not detected_bank and 'bank' in bank_part:
            # If "bank" is mentioned, treat the whole string as bank name
            detected_bank = bank_part.title()
        
        return {
            "intent": "transfer",
            "details": {
                "amount": float(amount),
                "account_number": account_number,
                "bank": detected_bank,
                "transfer_type": "parsed"
            }
        }
    
    # Fallback transfer detection
    transfer_keywords = ["transfer", "send money", "send cash", "pay", "remit"]
    if any(keyword in message_lower for keyword in transfer_keywords):
        return {"intent": "transfer", "details": {"transfer_type": "incomplete"}}
    
    # Account details request
    account_keywords = ["my account", "account details", "account number", "virtual account"]
    if any(keyword in message_lower for keyword in account_keywords):
        return {"intent": "show_account", "details": {}}
    
    # General conversation
    return {"intent": "general", "details": {"message": message}}

async def check_recent_deposits(chat_id: str, user_data: dict) -> Dict:
    """
    Check for recent deposits via Monnify webhook
    Fixes issue #2: No deposit awareness
    """
    try:
        from webhooks.monnify_webhook import get_recent_bank_transactions
        
        user_id = user_data.get('id')
        if not user_id:
            return {"found": False, "message": "User not found"}
        
        # Check for transactions in the last 30 minutes
        recent_transactions = get_recent_bank_transactions(user_id, minutes=30)
        
        if recent_transactions:
            latest_txn = recent_transactions[0]
            amount = latest_txn.get('amount', 0)
            status = latest_txn.get('status', 'pending')
            created_at = latest_txn.get('created_at', '')
            
            if status == 'successful':
                return {
                    "found": True,
                    "status": "successful",
                    "amount": amount,
                    "message": f"✅ Yes! I received your transfer of ₦{amount:,.2f}. Your wallet has been credited successfully.",
                    "time": created_at
                }
            else:
                return {
                    "found": True,
                    "status": "pending",
                    "amount": amount,
                    "message": f"⏳ I can see your transfer of ₦{amount:,.2f} is processing. I'll notify you immediately once it's confirmed!",
                    "time": created_at
                }
        else:
            return {
                "found": False,
                "message": "I haven't received any new deposits in the last 30 minutes. Please ensure you sent to the correct account details, and I'll notify you immediately when the transfer arrives! 📱"
            }
            
    except Exception as e:
        logger.error(f"Error checking recent deposits: {e}")
        return {
            "found": False,
            "message": "I'm checking for your deposit. If you just sent money, please wait a few minutes for confirmation. I'll notify you immediately when it arrives! ⏰"
        }

async def get_real_user_balance(chat_id: str, user_data: dict) -> Dict:
    """
    Get real user balance from database
    Fixes issue #3: Wrong balance display
    """
    try:
        # Method 1: Try wallet_balances table (crypto integration)
        from crypto.wallet import get_user_ngn_balance
        
        user_id = user_data.get('id')
        if user_id:
            balance_info = get_user_ngn_balance(str(user_id))
            if balance_info.get("success"):
                balance = float(balance_info.get("balance_naira", 0))
                return {
                    "success": True,
                    "balance": balance,
                    "source": "wallet_balances"
                }
        
        # Method 2: Calculate from bank transactions
        from webhooks.monnify_webhook import calculate_user_balance
        
        calculated_balance = calculate_user_balance(user_id)
        if calculated_balance is not None:
            return {
                "success": True,
                "balance": calculated_balance,
                "source": "calculated"
            }
        
        # Method 3: Default to 0 if no transactions found
        return {
            "success": True,
            "balance": 0.0,
            "source": "default"
        }
        
    except Exception as e:
        logger.error(f"Error getting real balance: {e}")
        return {
            "success": False,
            "balance": 0.0,
            "error": str(e)
        }

def generate_transfer_receipt(sender_name: str, recipient_details: dict, amount: float, 
                            balance_before: float, balance_after: float, 
                            transaction_id: str) -> str:
    """
    Generate POS-style receipt after successful transfer
    Fixes issue #6: No receipt generation
    """
    receipt = f"""
┌─────────────────────────────────────┐
│        SOFI AI TRANSFER RECEIPT     │
└─────────────────────────────────────┘

💳 TRANSACTION SUCCESSFUL ✅

📋 DETAILS:
• Amount: ₦{amount:,.2f}
• To: {recipient_details.get('name', 'Account Holder')}
• Bank: {recipient_details.get('bank', 'N/A')}
• Account: {recipient_details.get('account_number', 'N/A')}

🕐 TRANSACTION INFO:
• Date: {datetime.now().strftime('%B %d, %Y')}
• Time: {datetime.now().strftime('%I:%M %p')}
• Reference: {transaction_id}

💰 BALANCE UPDATE:
• Before: ₦{balance_before:,.2f}
• After: ₦{balance_after:,.2f}

┌─────────────────────────────────────┐
│   Thank you for using Sofi AI! 🚀  │
│      Your trusted finance partner   │
└─────────────────────────────────────┘

Need help? Just type 'help' anytime! 💬"""
    
    return receipt

async def validate_transfer_pin(chat_id: str, pin: str, user_data: dict) -> bool:
    """
    Validate user's transaction PIN
    Fixes issue #5: Missing PIN verification
    """
    try:
        import hashlib
        
        # Get stored PIN hash from database
        user_pin_hash = user_data.get('pin')
        if not user_pin_hash:
            return False
        
        # Hash the provided PIN
        provided_pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        # Compare hashes
        return user_pin_hash == provided_pin_hash
        
    except Exception as e:
        logger.error(f"Error validating PIN: {e}")
        return False

def extract_complete_transfer_details(message: str) -> Optional[Dict]:
    """
    Extract complete transfer details from a single message
    Fixes issue #4: Transfer parsing failure
    """
    message_lower = message.lower().strip()
    
    # Enhanced patterns for different formats
    patterns = [
        # "Transfer 2000 to 0803228575 access bank"
        r'(?:transfer|send)\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:to|naira to)?\s*([0-9]{10,11})\s+(.+?)(?:\s|$)',
        # "Send 5000 to Access Bank 0123456789"
        r'(?:transfer|send)\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:to)?\s*(.+?)\s+([0-9]{10,11})',
        # "Transfer 1000 naira to John Doe 0123456789 GTB"
        r'(?:transfer|send)\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:naira)?\s+(?:to)?\s*(.+?)\s+([0-9]{10,11})\s+(.+?)(?:\s|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            groups = match.groups()
            
            if len(groups) == 3:
                amount, account_or_name, bank_or_account = groups
                
                # Determine which is account number
                if re.match(r'^[0-9]{10,11}$', account_or_name):
                    account_number = account_or_name
                    bank_name = bank_or_account
                    recipient_name = None
                else:
                    account_number = bank_or_account if re.match(r'^[0-9]{10,11}$', bank_or_account) else None
                    bank_name = account_or_name
                    recipient_name = None
                
                if account_number:
                    return {
                        "amount": float(amount.replace(',', '')),
                        "account_number": account_number,
                        "bank": normalize_bank_name(bank_name),
                        "recipient_name": recipient_name
                    }
    
    return None

def normalize_bank_name(bank_input: str) -> str:
    """Normalize bank name variations to standard names"""
    bank_input = bank_input.lower().strip()
    
    bank_mapping = {
        'access': 'Access Bank',
        'gtb': 'GTBank',
        'guaranty': 'GTBank',
        'first': 'First Bank',
        'firstbank': 'First Bank',
        'zenith': 'Zenith Bank',
        'uba': 'UBA',
        'fidelity': 'Fidelity Bank',
        'fcmb': 'FCMB',
        'union': 'Union Bank',
        'sterling': 'Sterling Bank',
        'stanbic': 'Stanbic IBTC',
        'wema': 'Wema Bank',
        'polaris': 'Polaris Bank',
        'keystone': 'Keystone Bank',
        'opay': 'Opay',
        'kuda': 'Kuda Bank',
        'palmpay': 'PalmPay'
    }
    
    for key, full_name in bank_mapping.items():
        if key in bank_input:
            return full_name
    
    # If no exact match, capitalize the input
    return bank_input.title() + (' Bank' if 'bank' not in bank_input else '')
