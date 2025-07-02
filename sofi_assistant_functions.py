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
            "description": "Send money to a Nigerian bank account. ALWAYS call this function for transfer requests. The function handles PIN entry automatically with secure inline keyboard - do NOT ask for PIN manually.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount to send in Naira (minimum ₦10)"
                    },
                    "account_number": {
                        "type": "string",
                        "description": "The recipient's account number (10 digits)"
                    },
                    "bank_name": {
                        "type": "string",
                        "description": "The recipient's bank name (e.g., 'Access Bank', 'Wema Bank')"
                    },
                    "narration": {
                        "type": "string",
                        "description": "Reason for transfer (optional)"
                    }
                },
                "required": ["amount", "account_number", "bank_name"]
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
You are Sofi, a Nigerian banking assistant. Be CONCISE and DIRECT.

CRITICAL RULES:
1. ALWAYS call send_money() function for any transfer request - NEVER provide generic PIN messages
2. When user says "send money" or "transfer", immediately call send_money() with the details
3. Do NOT generate your own PIN security messages - let the function handle PIN flow
4. Show amounts in ₦ format
5. Give short, clear responses (max 2-3 lines)

TRANSFER PROCESS:
- User says "Send X to account Y at bank Z" → IMMEDIATELY call send_money(amount=X, account_number=Y, bank_name=Z)
- Function will handle PIN entry automatically with secure inline keyboard
- Do NOT ask for PIN in chat or provide security warnings manually

FUNCTIONS:
- verify_account_name() - Check recipient before transfer  
- send_money() - Execute transfers (handles PIN automatically)
- check_balance() - Show current balance
- set_transaction_pin() - Set/update PIN

STYLE: Brief, professional, helpful. Always call functions when available.
"""
