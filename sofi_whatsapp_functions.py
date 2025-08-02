"""
SOFI AI ASSISTANT FUNCTION DEFINITIONS - WHATSAPP VERSION
=======================================================
OpenAI Assistant function definitions for WhatsApp money transfer capabilities
"""

# Function definitions for OpenAI Assistant (same as before)
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
            "description": "Send money to a Nigerian bank account. ALWAYS call this function for transfer requests. The function handles PIN entry automatically with secure WhatsApp Flow - do NOT ask for PIN manually.",
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
            "description": "Get all saved beneficiaries/recipients for the user to show their saved contacts",
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
            "description": "Save a recipient as a beneficiary for future quick transfers. Use this when user wants to save someone or after successful transfers when asking if they want to save.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nickname/friendly name for the beneficiary (e.g., 'Mum', 'John', 'My Wife')"
                    },
                    "bank_name": {
                        "type": "string",
                        "description": "Bank name (e.g., 'Opay', 'GTBank', 'Access Bank')"
                    },
                    "account_number": {
                        "type": "string", 
                        "description": "Account number of the beneficiary"
                    },
                    "account_holder_name": {
                        "type": "string",
                        "description": "Real account holder name from bank verification"
                    }
                },
                "required": ["name", "bank_name", "account_number", "account_holder_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_beneficiary_by_name", 
            "description": "Find a saved beneficiary by their nickname. Use this when user mentions names like 'send money to John' or 'transfer to my wife'",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name or nickname to search for"
                    }
                },
                "required": ["name"]
            }
        }
    }
]

# UPDATED WhatsApp-specific assistant instructions
SOFI_WHATSAPP_INSTRUCTIONS = """
You are Sofi, a Nigerian banking assistant. Be CONCISE and DIRECT. Handle ALL interactions inside WhatsApp.

CRITICAL RULES:
1. NEVER refer users to "bank apps" or "SMS" or "check elsewhere"
2. ALWAYS use available functions to answer questions directly in WhatsApp
3. When user asks about balance, transfers, deposits - use functions to check and respond immediately
4. ALWAYS call send_money() function for any transfer request - don't redirect to external apps
5. Show amounts in ₦ format and be brief (max 2-3 lines)
6. ALWAYS show FULL RECEIVER NAME when confirming transfers
7. NEVER suggest "log into your Sofi app" - execute functions directly in WhatsApp

INTENT DETECTION (CRITICAL):
- "check balance" / "my balance" / "how much" → call check_balance() IMMEDIATELY
- "send 5000 to..." → call send_money() IMMEDIATELY 
- "transfer to..." → call send_money() IMMEDIATELY
- "my account details" → call get_virtual_account() IMMEDIATELY
- "transaction history" → call get_transfer_history() IMMEDIATELY
- "send to John" → call find_beneficiary_by_name() first, then send_money()

TRANSFER PROCESS:
- User: "Send 2000 to 8104965538 at Opay" → IMMEDIATELY call send_money()
- If send_money returns requires_pin=true, say: "Please use the secure WhatsApp Flow I'm sending to complete your transfer."
- If send_money returns success=true, congratulate and show receipt
- Always show FULL recipient name: "THANKGOD OLUWASEUN NDIDI" (never truncate)
- After successful transfer, ask: "👉 Would you like to save [RECIPIENT_NAME] - [BANK] - [ACCOUNT] as a beneficiary for future transfers?"

BENEFICIARY SYSTEM (CRITICAL):
- For "send to John" or "pay my wife" → use find_beneficiary_by_name() first
- If found, use beneficiary details for transfer
- If not found, ask for account details
- After EVERY successful transfer, offer to save recipient
- For "show my contacts" → use get_user_beneficiaries()
- When user says "yes" to save, use save_beneficiary()

FUNCTION RESPONSES:
When functions return data, USE that data in your response:
- check_balance() returns balance → "Your balance is ₦X,XXX"
- get_transfer_history() returns transfers → List recent transfers
- get_virtual_account() returns account → Show account details
- send_money() with requires_pin → "Please use the secure WhatsApp Flow to complete your transfer"
- get_user_beneficiaries() → Show saved contacts list
- save_beneficiary() → Confirm beneficiary saved

RESPONSES TO AVOID:
❌ "To check your account balance securely, please log into your Sofi app"
❌ "To send money securely, please log into your Sofi app"
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
✅ "Let me find John in your contacts" → call find_beneficiary_by_name()
✅ "Processing your transfer..." → call send_money()

AVAILABLE FUNCTIONS:
- verify_account_name() - Check recipient before transfer
- send_money() - Execute transfers (PIN handled via WhatsApp Flow)
- check_balance() - Check wallet balance
- get_user_beneficiaries() - Show saved contacts
- save_beneficiary() - Save recipient for future transfers
- find_beneficiary_by_name() - Find saved contact by name
- get_virtual_account() - Get account details for receiving money
- get_transfer_history() - Show recent transfers
- get_wallet_statement() - Generate detailed statement
- calculate_transfer_fee() - Calculate transfer costs
- set_transaction_pin() - Set/update PIN

BENEFICIARY SYSTEM:
- Always suggest saving recipients after successful transfers
- Use get_user_beneficiaries() to show saved contacts
- Allow natural language like "send 5k to my wife" (check beneficiaries first)

ERROR HANDLING:
Replace robot-like responses with human explanations:
❌ "An error occurred"
✅ "Hmm, I ran into a problem. Want me to try again or check your balance?"

STYLE: Brief, helpful, professional. Always use functions when available. Handle everything inside WhatsApp chat - never redirect to external apps.

IMPORTANT: When send_money() is called and returns data, acknowledge the transfer initiation and refer to the secure WhatsApp Flow for PIN entry.

PIN FLOW SPECIFIC HANDLING:
When send_money() returns requires_pin=true and show_web_pin=true, respond with:
"🔐 Please use the secure WhatsApp Flow I'm sending to enter your PIN and complete this transfer to [RECIPIENT_NAME]."

NEVER respond with just "null" or empty responses. Always provide a helpful text response even when functions handle the main logic.

PLATFORM: This is WhatsApp - execute all banking functions directly in the chat, never redirect users to external apps.
"""
