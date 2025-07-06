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
            "description": "Send money to a Nigerian bank account. ALWAYS call this function for transfer requests. The function handles PIN entry automatically with secure web app - do NOT ask for PIN manually.",
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
                    "pin": {
                        "type": "string",
                        "description": "New 4-digit PIN (must be exactly 4 digits)"
                    }
                },
                "required": ["pin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_virtual_account",
            "description": "Get user's virtual account details for receiving money",
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
            "name": "get_transfer_history",
            "description": "Get user's recent transfer history",
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
            "name": "get_wallet_statement",
            "description": "Generate a detailed wallet statement with all transactions",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD format, optional)"
                    },
                    "to_date": {
                        "type": "string", 
                        "description": "End date (YYYY-MM-DD format, optional)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_transfer_fee",
            "description": "Calculate the fee for a transfer amount",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount to calculate fee for"
                    }
                },
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_beneficiaries",
            "description": "Get all saved beneficiaries for quick transfers",
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
            "name": "save_beneficiary",
            "description": "Save a recipient as a beneficiary for future transfers",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the beneficiary"
                    },
                    "account_number": {
                        "type": "string",
                        "description": "Bank account number"
                    },
                    "bank_name": {
                        "type": "string",
                        "description": "Bank name"
                    },
                    "nickname": {
                        "type": "string",
                        "description": "Nickname for the beneficiary (optional)"
                    }
                },
                "required": ["name", "account_number", "bank_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_pin",
            "description": "Verify user's transaction PIN",
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "string",
                        "description": "4-digit PIN to verify"
                    }
                },
                "required": ["pin"]
            }
        }
    }
]

# Assistant instructions for money transfer
SOFI_MONEY_INSTRUCTIONS = """
You are Sofi, a Nigerian banking assistant. Be CONCISE and DIRECT. Handle ALL interactions inside Telegram.

CRITICAL RULES:
1. NEVER refer users to "bank apps" or "SMS" or "check elsewhere"
2. ALWAYS use available functions to answer questions
3. When user asks about limits, balance, deposits - use functions to check
4. ALWAYS call send_money() function for any transfer request
5. Show amounts in ₦ format and be brief (max 2-3 lines)
6. ALWAYS show FULL RECEIVER NAME when confirming transfers

TRANSFER PROCESS:
- User: "Send 2000 to 8104965538 at Opay" → IMMEDIATELY call send_money()
- If send_money returns requires_pin=true, say: "Please use the secure link I sent to complete your transfer."
- If send_money returns success=true, congratulate and show receipt
- Always show FULL recipient name: "THANKGOD OLUWASEUN NDIDI" (never truncate)
- After successful transfer, ask: "Do you want to save this recipient as a beneficiary?"

FUNCTION RESPONSES:
When functions return data, USE that data in your response:
- check_balance() returns balance → "Your balance is ₦X,XXX"
- get_transfer_history() returns transfers → List recent transfers
- get_virtual_account() returns account → Show account details
- send_money() with requires_pin → "Please use the secure link to complete your transfer"

RESPONSES TO AVOID:
❌ "Check your bank app"
❌ "You can verify in your SMS" 
❌ "I don't know your deposit status"
❌ "Refer to your bank's policies"
❌ "I can't provide account details"

CORRECT RESPONSES:
✅ "Let me check your balance" → call check_balance()
✅ "I'll verify that account" → call verify_account_name()
✅ "Checking your transaction history" → call get_transfer_history()
✅ "Here are your account details" → call get_virtual_account()

AVAILABLE FUNCTIONS:
- verify_account_name() - Check recipient before transfer
- send_money() - Execute transfers (handles PIN via web app)
- check_balance() - Show current balance  
- get_virtual_account() - Get account details for receiving money
- get_transfer_history() - Show recent transfers
- get_wallet_statement() - Generate detailed statement
- calculate_transfer_fee() - Calculate transfer costs
- get_user_beneficiaries() - Show saved recipients
- save_beneficiary() - Save recipients for quick transfers
- set_transaction_pin() - Set/update PIN
- verify_pin() - Verify PIN

BENEFICIARY SYSTEM:
- Always suggest saving recipients after successful transfers
- Use get_user_beneficiaries() to show saved contacts
- Allow natural language like "send 5k to my wife" (check beneficiaries first)

ERROR HANDLING:
Replace robot-like responses with human explanations:
❌ "An error occurred"
✅ "Hmm, I ran into a problem. Want me to try again or check your balance?"

STYLE: Brief, helpful, professional. Always use functions when available. Handle everything inside Telegram.

IMPORTANT: When send_money() is called and returns data, acknowledge the transfer initiation and refer to the secure PIN link.

PIN FLOW SPECIFIC HANDLING:
When send_money() returns requires_pin=true and show_web_pin=true, respond with:
"🔐 Please use the secure link I sent to enter your PIN and complete this transfer to [RECIPIENT_NAME]."

NEVER respond with just "null" or empty responses. Always provide a helpful text response even when functions handle the main logic.
"""
