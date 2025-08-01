"""
WhatsApp Business Logic
Handles business operations for authenticated WhatsApp users
"""

import logging
from typing import Dict, Any, Optional, Tuple
from utils.whatsapp_database import whatsapp_db

logger = logging.getLogger(__name__)

class WhatsAppBusinessService:
    """Service for handling authenticated user business operations"""
    
    def __init__(self):
        self.db = whatsapp_db
    
    def get_user_balance(self, user: Dict[str, Any]) -> Tuple[bool, str]:
        """Get user's account balance"""
        try:
            user_id = user.get("id")
            first_name = user.get("first_name", "")
            
            # Get virtual account
            result = self.db.supabase.table("virtual_accounts").select("*").eq("user_id", user_id).execute()
            
            if not result.data:
                return False, f"❌ Sorry {first_name}, I couldn't find your account details. Please contact support."
            
            account = result.data[0]
            balance = account.get("balance", 0.0)
            account_number = account.get("account_number", "N/A")
            
            return True, f"""💰 **Account Balance**

👤 **Name**: {first_name} {user.get('last_name', '')}
🏦 **Account**: {account_number}
💵 **Balance**: ₦{balance:,.2f}

📱 What would you like to do next?
• Send money
• Buy airtime  
• Check transactions"""
            
        except Exception as e:
            logger.error(f"Error getting balance for user {user.get('id')}: {e}")
            return False, "❌ Sorry, I couldn't retrieve your balance right now. Please try again later."
    
    def process_money_transfer(self, user: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
        """Process money transfer request"""
        try:
            amount = params.get("amount")
            recipient = params.get("recipient")
            first_name = user.get("first_name", "")
            
            if not amount:
                return False, f"""💸 **Send Money**

{first_name}, please specify the amount you want to send.

Example: "Send 5000 to John"
Or: "Transfer 2000 to Mary"

How much would you like to send?"""
            
            if not recipient:
                return False, f"""💸 **Send Money**

{first_name}, please tell me who you want to send ₦{amount:,.2f} to.

Example: "Send {amount} to John"

Who would you like to send the money to?"""
            
            # For now, guide user to app for security
            return True, f"""💸 **Transfer Request**

Amount: ₦{amount:,.2f}
To: {recipient}

🔒 For security, please complete this transfer in the Sofi app:

📱 **Open Sofi App** → **Send Money** → Enter details

Or visit: https://pipinstallsofi.com

This ensures your transaction is secure and protected! 🛡️"""
            
        except Exception as e:
            logger.error(f"Error processing transfer for user {user.get('id')}: {e}")
            return False, "❌ Sorry, I couldn't process your transfer request. Please try again."
    
    def process_airtime_purchase(self, user: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
        """Process airtime purchase request"""
        try:
            amount = params.get("amount")
            phone_number = params.get("phone_number", user.get("whatsapp_number"))
            first_name = user.get("first_name", "")
            
            if not amount:
                return False, f"""📱 **Buy Airtime**

{first_name}, please specify the airtime amount.

Example: "Buy 1000 airtime"
Or: "Recharge 500"

How much airtime would you like to buy?"""
            
            if amount < 50 or amount > 10000:
                return False, f"""📱 **Airtime Amount**

Please choose an amount between ₦50 and ₦10,000.

Example: "Buy 1000 airtime"

How much airtime would you like to buy?"""
            
            # For now, guide to app for purchase
            return True, f"""📱 **Airtime Purchase**

Amount: ₦{amount:,.2f}
For: {phone_number}

🔒 Complete your airtime purchase in the Sofi app:

📱 **Open Sofi App** → **Buy Airtime** → Enter amount

Or visit: https://pipinstallsofi.com

Your airtime will be delivered instantly! ⚡"""
            
        except Exception as e:
            logger.error(f"Error processing airtime for user {user.get('id')}: {e}")
            return False, "❌ Sorry, I couldn't process your airtime request. Please try again."
    
    def process_crypto_request(self, user: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
        """Process crypto trading request"""
        try:
            crypto_type = params.get("crypto_type", "crypto")
            operation = params.get("operation", "trade")
            amount = params.get("amount")
            first_name = user.get("first_name", "")
            
            return True, f"""₿ **Crypto Trading**

{first_name}, crypto trading is available in the Sofi app!

🪙 **Available:**
• Bitcoin (BTC)
• Ethereum (ETH)  
• USDT (Tether)
• And more...

📱 **Get Started:**
Open Sofi App → **Crypto** → Start trading

Or visit: https://pipinstallsofi.com

Trade safely with real-time rates! 📈"""
            
        except Exception as e:
            logger.error(f"Error processing crypto for user {user.get('id')}: {e}")
            return False, "❌ Sorry, crypto trading is temporarily unavailable. Please try again later."
    
    def get_help_message(self, user: Dict[str, Any]) -> Tuple[bool, str]:
        """Get help message for authenticated user"""
        first_name = user.get("first_name", "")
        
        return True, f"""🤖 **Hi {first_name}! I'm Sofi, your AI banking assistant.**

💬 **Chat Commands:**
• "**balance**" - Check your account balance
• "**send 5000 to John**" - Send money to someone
• "**buy 1000 airtime**" - Purchase airtime
• "**crypto**" - Access crypto trading

🏦 **Banking Services:**
• Account management
• Money transfers
• Bill payments  
• Crypto trading
• Financial insights

📱 **Full Features:** Download the Sofi app at https://pipinstallsofi.com

What can I help you with today? 😊"""
    
    def get_general_response(self, user: Dict[str, Any], message: str) -> Tuple[bool, str]:
        """Handle general queries from authenticated users"""
        first_name = user.get("first_name", "")
        
        # Use GPT integration if available
        try:
            from utils.whatsapp_gpt_integration import sofi_whatsapp_gpt
            import asyncio
            
            # Add user context to the message
            enhanced_message = f"User {first_name} (authenticated) asks: {message}"
            response = asyncio.run(sofi_whatsapp_gpt.process_whatsapp_message(user.get("whatsapp_number"), enhanced_message))
            
            return True, response
            
        except Exception as e:
            logger.error(f"Error with GPT integration: {e}")
            
            # Fallback response
            return True, f"""🤖 Hi {first_name}!

I can help you with:
💰 Balance checking
💸 Money transfers
📱 Airtime purchases  
₿ Crypto trading

Try asking me something like:
• "What's my balance?"
• "Send 2000 to Sarah"
• "Buy 1000 airtime"

What would you like to do? 😊"""

# Global instance
whatsapp_business = WhatsAppBusinessService()
