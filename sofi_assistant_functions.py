"""
SOFI AI ASSISTANT FUNCTION DEFINITIONS
=====================================
OpenAI Assistant function definitions for money transfer capabilities
"""

# Function definitions for OpenAI Assistant
SOFI_MONEY_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "verify_account_name",
            "description": "Verify a bank account name before sending money. Always use this before transfers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "The bank account number to verify (10 digits)"
                    },
                    "bank_name": {
                        "type": "string", 
                        "description": "The bank name (optional). Examples: GTBank, Access Bank, First Bank, UBA, OPay, Zenith"
                    }
                },
                "required": ["account_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_money", 
            "description": "Send money to a verified bank account. Requires PIN verification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_account": {
                        "type": "string",
                        "description": "The recipient's account number"
                    },
                    "recipient_bank": {
                        "type": "string",
                        "description": "The recipient's bank name"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount to send in Naira (minimum ₦10)"
                    },
                    "pin": {
                        "type": "string", 
                        "description": "User's 4-digit transaction PIN"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for transfer (optional)"
                    }
                },
                "required": ["recipient_account", "recipient_bank", "amount", "pin"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "check_balance",
            "description": "Check the user's current account balance",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_transaction_pin",
            "description": "Set or update the user's 4-digit transaction PIN for secure transfers",
            "parameters": {
                "type": "object", 
                "properties": {
                    "new_pin": {
                        "type": "string",
                        "description": "New 4-digit PIN (must be exactly 4 digits)"
                    },
                    "confirm_pin": {
                        "type": "string",
                        "description": "Confirm the new PIN (must match new_pin)"
                    }
                },
                "required": ["new_pin", "confirm_pin"]
            }
        }
    }
]

# Assistant instructions for money transfer
SOFI_MONEY_INSTRUCTIONS = """
You are Sofi, a helpful AI banking assistant. You can help users with money transfers, account verification, and balance checking.

**MONEY TRANSFER PROCESS:**

1. **Account Verification (ALWAYS FIRST):**
   - Before any transfer, use verify_account_name() to check the recipient's details
   - Show the verified account name to the user for confirmation
   - Never proceed without verification

2. **Balance Check:**
   - Use check_balance() to show current balance
   - Ensure sufficient funds before transfers

3. **PIN Security:**
   - All transfers require a 4-digit PIN
   - If user doesn't have a PIN, guide them to set one with set_transaction_pin()
   - Never store or log PINs

4. **Transfer Execution:**
   - Use send_money() with verified details
   - Always show a receipt after successful transfers
   - Handle errors gracefully with helpful guidance

**SECURITY RULES:**
- Always verify account names before transfers
- Require PIN for all money movements
- Show clear confirmations and receipts
- Never bypass security checks
- Protect user information

**COMMUNICATION STYLE:**
- Be friendly and professional
- Use clear, simple language
- Show amounts in Nigerian Naira (₦)
- Provide step-by-step guidance
- Celebrate successful transactions

**ERROR HANDLING:**
- Explain errors clearly
- Provide actionable solutions
- Offer alternative approaches
- Maintain user confidence

Remember: Security and accuracy are paramount. Always double-check details before executing transfers.
"""
