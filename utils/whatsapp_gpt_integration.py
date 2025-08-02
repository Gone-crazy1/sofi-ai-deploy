"""
WhatsApp GPT-3.5 Turbo Integration for Sofi AI
===============================================
Connects WhatsApp messages to OpenAI GPT-3.5 Turbo for intelligent responses
"""

import os
import json
import logging
import asyncio
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

class SofiWhatsAppGPT:
    """Intelligent WhatsApp integration using GPT-3.5 Turbo"""
    
    def __init__(self):
        """Initialize GPT-3.5 Turbo for WhatsApp responses"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Store conversation context for each WhatsApp user
        self.user_conversations: Dict[str, list] = {}
        
        # Sofi AI system prompt for banking assistant
        self.system_prompt = """You are Sofi, an intelligent Nigerian banking AI assistant operating via WhatsApp.

CORE IDENTITY:
- You help users with banking, money transfers, account creation, and financial services
- You're connected to Paystack banking APIs and can assist with real transactions
- You communicate in a friendly, helpful, and professional manner
- You understand Nigerian banking context and speak both English and Pidgin when appropriate

CAPABILITIES:
- Account creation and onboarding via WhatsApp
- Balance checking and account inquiries  
- Virtual account setup with Paystack
- Money transfers between accounts and banks
- Airtime purchases and bill payments
- BVN verification and KYC processes
- Financial advice and banking education

RESPONSE GUIDELINES:
- Keep responses concise but helpful (max 2-3 sentences for simple queries)
- Use emojis appropriately (💰 for money, 📱 for phones, ✅ for success, etc.)
- For complex transactions, guide users step-by-step
- Always prioritize security - never ask for PINs or passwords via WhatsApp
- If users need to perform secure actions, direct them to the official Sofi app

ACCOUNT CREATION:
- When users ask about creating accounts, help them create accounts directly via WhatsApp
- Guide them through the simple onboarding process
- Collect: full name, email (optional), and they can set PIN later
- Always explain benefits of having a Sofi virtual account

ACCOUNT CREATION TRIGGERS:
- "create account" / "open account" / "signup" / "register"
- "I want to bank with sofi" / "get started" / "onboard me"
- "create sofi account" / "setup account"

COMMON QUERIES:
- "balance" → Check account balance
- "send money" → Guide money transfer process  
- "signup" → Start account creation process
- "airtime" → Airtime purchase assistance
- "help" → Show available commands
- Banking questions → Provide helpful financial guidance

Always respond as Sofi AI, be helpful, and maintain a professional but friendly tone."""

        logger.info("✅ Sofi WhatsApp GPT-3.5 integration initialized")
    
    def get_user_context(self, phone_number: str) -> list:
        """Get conversation context for user"""
        if phone_number not in self.user_conversations:
            self.user_conversations[phone_number] = []
        return self.user_conversations[phone_number]
    
    def add_to_context(self, phone_number: str, role: str, content: str):
        """Add message to user's conversation context"""
        context = self.get_user_context(phone_number)
        context.append({"role": role, "content": content})
        
        # Keep only last 10 messages to avoid token limits
        if len(context) > 10:
            context = context[-10:]
        
        self.user_conversations[phone_number] = context
    
    async def process_whatsapp_message(self, phone_number: str, message: str) -> tuple:
        """Process WhatsApp message using GPT-3.5 Turbo and return (response, button_data)"""
        try:
            # Check for account creation intent
            if self.is_account_creation_request(message):
                return await self.handle_account_creation(phone_number, message)
            
            # Add user message to context
            self.add_to_context(phone_number, "user", message)
            
            # Get conversation context
            context = self.get_user_context(phone_number)
            
            # Prepare messages for GPT
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + context
            
            # Enhanced prompt for specific banking queries
            enhanced_message = self.enhance_banking_context(message)
            if enhanced_message != message:
                messages[-1]["content"] = enhanced_message
            
            # Call GPT-3.5 Turbo
            response = await self.call_gpt_async(messages)
            
            # Add AI response to context
            self.add_to_context(phone_number, "assistant", response)
            
            # Check if response suggests account creation
            button_data = None
            if self.contains_account_creation_suggestion(response):
                response = self.clean_response_for_button(response)
                button_data = {
                    "title": "🚀 Create Account Now",
                    "url": f"https://pipinstallsofi.com/whatsapp-onboard?whatsapp={phone_number}",
                    "id": "create_account_whatsapp"
                }
            
            return response, button_data
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            return "❌ Sorry, I'm experiencing some technical issues. Please try again in a moment.", None
    
    def enhance_banking_context(self, message: str) -> str:
        """Enhance message with banking context for better responses"""
        message_lower = message.lower()
        
        # Balance inquiry
        if "balance" in message_lower:
            return f"{message}\n\nContext: User wants to check their account balance. Provide helpful guidance about balance checking and mention they may need to log into the Sofi app for secure balance access."
        
        # Money transfer
        elif any(word in message_lower for word in ["send", "transfer", "money"]):
            return f"{message}\n\nContext: User wants to send money. Guide them through the transfer process, mention security considerations, and direct them to the Sofi app for secure transactions."
        
        # Account creation
        elif any(word in message_lower for word in ["signup", "sign up", "create", "account", "register"]):
            return f"{message}\n\nContext: User wants to create a new account. Provide a warm welcome and direct them to complete registration at https://pipinstallsofi.com/onboard to get started with Sofi's banking services."
        
        # Airtime purchase
        elif "airtime" in message_lower:
            return f"{message}\n\nContext: User wants to buy airtime. Help them with airtime purchase and mention convenient options through Sofi."
        
        # Help request
        elif any(word in message_lower for word in ["help", "what", "how", "commands"]):
            return f"{message}\n\nContext: User needs help. Provide a clear overview of Sofi's banking services and available commands."
        
        return message
    
    async def call_gpt_async(self, messages: list) -> str:
        """Make async call to GPT-3.5 Turbo"""
        try:
            loop = asyncio.get_event_loop()
            
            # Run GPT call in thread pool to avoid blocking
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=300,  # Keep responses concise for WhatsApp
                    temperature=0.7,  # Balanced creativity and consistency
                    top_p=0.9
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"GPT API error: {e}")
            return "❌ I'm having trouble processing your request right now. Please try again."
    
    def clear_user_context(self, phone_number: str):
        """Clear conversation context for user (useful for new sessions)"""
        if phone_number in self.user_conversations:
            del self.user_conversations[phone_number]
    
    async def send_welcome_message(self, phone_number: str) -> tuple:
        """Generate personalized welcome message for new users and return (response, button_data)"""
        welcome_prompt = f"""Generate a warm welcome message for a new Sofi AI banking user on WhatsApp. 
        
        Include:
        - Friendly greeting
        - Brief intro to Sofi's banking services
        - 3-4 key things they can do (balance, transfers, airtime, account creation)
        - Encourage them to ask questions
        
        Keep it concise and use appropriate emojis. Make it feel personal and helpful."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": welcome_prompt}
        ]
        
        response = await self.call_gpt_async(messages)
        
        # Always add button for new users to complete registration
        button_data = {
            "title": "🚀 Get Started", 
            "url": f"https://pipinstallsofi.com/whatsapp-onboard?whatsapp={phone_number}",
            "id": "get_started"
        }
        
        return response, button_data
    
    def is_account_creation_request(self, message: str) -> bool:
        """Check if message is requesting account creation"""
        account_keywords = [
            'create account', 'open account', 'signup', 'sign up', 'register', 
            'registration', 'new account', 'account creation', 'onboard', 'get started',
            'i want to bank', 'create sofi account', 'setup account', 'join sofi',
            'bank with sofi', 'start banking', 'create wallet'
        ]
        
        message_lower = message.lower().strip()
        return any(keyword in message_lower for keyword in account_keywords)
    
    def contains_account_creation_suggestion(self, response: str) -> bool:
        """Check if GPT response suggests account creation"""
        suggestion_phrases = [
            'create an account', 'sign up', 'register', 'get started',
            'open an account', 'complete registration', 'onboard'
        ]
        
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in suggestion_phrases)
    
    def clean_response_for_button(self, response: str) -> str:
        """Clean response text when adding account creation button"""
        # Remove common phrases that will be replaced by button
        phrases_to_remove = [
            'create an account', 'sign up now', 'get started today',
            'complete registration', 'register now', 'open an account'
        ]
        
        cleaned = response
        for phrase in phrases_to_remove:
            cleaned = re.sub(rf'\b{re.escape(phrase)}\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'[.!?]\s*[.!?]+', '.', cleaned)
        
        return cleaned
    
    async def handle_account_creation(self, phone_number: str, message: str) -> Tuple[str, Optional[Dict]]:
        """Handle account creation request via WhatsApp"""
        try:
            from utils.whatsapp_account_manager_simple import whatsapp_account_manager
            
            # Check if user already has an account
            existing_user = await whatsapp_account_manager.get_user_by_whatsapp(phone_number)
            if existing_user:
                account = await whatsapp_account_manager.get_virtual_account(phone_number)
                
                return f"""✅ **Welcome back!**

You already have a Sofi account:
🏦 **Account:** {account.get('account_number', 'N/A')}
💰 **Balance:** ₦{account.get('balance', 0):,.2f}
🏪 **Bank:** {account.get('bank_name', 'Wema Bank')}

What would you like to do today? I can help you check balance, send money, or buy airtime! 💫""", None
            
            # Extract name from message if provided
            name_patterns = [
                r"my name is ([a-zA-Z\s]+)",
                r"i am ([a-zA-Z\s]+)",
                r"i'm ([a-zA-Z\s]+)",
                r"call me ([a-zA-Z\s]+)"
            ]
            
            full_name = None
            for pattern in name_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    full_name = match.group(1).title().strip()
                    break
            
            if not full_name:
                # Ask for name
                return """🎉 **Welcome to Sofi AI!**

I'd love to create your account right now! What's your full name?

Just reply with something like: *"My name is John Doe"*

I'll create your virtual account instantly! 🚀""", None
            
            # Create account with extracted name
            account_data = {
                'whatsapp_number': phone_number,
                'full_name': full_name
            }
            
            result = await whatsapp_account_manager.create_whatsapp_account(account_data)
            
            if result['success']:
                # Format success message
                account_message = whatsapp_account_manager.format_account_message(result)
                
                return account_message, {
                    "title": "💳 Check Balance",
                    "url": f"https://pipinstallsofi.com/whatsapp-onboard?whatsapp={phone_number}",
                    "id": "check_balance"
                }
            else:
                return f"❌ **Account Creation Failed**\n\n{result.get('error', 'Unknown error occurred')}\n\nPlease try again or contact support.", None
                
        except Exception as e:
            logger.error(f"Error in account creation: {e}")
            return "❌ Sorry, I had trouble creating your account. Please try again in a moment.", None

# Global instance for use in main application
sofi_whatsapp_gpt = SofiWhatsAppGPT()

async def main():
    """Demo/test function for the WhatsApp GPT integration"""
    print("🚀 Sofi WhatsApp GPT Integration - Test Mode")
    print("=" * 50)
    
    # Test phone number
    test_phone = "+2348012345678"
    
    try:
        # Test welcome message
        print("\n📱 Testing welcome message...")
        welcome = await sofi_whatsapp_gpt.send_welcome_message(test_phone)
        print(f"Welcome: {welcome}")
        
        # Test various banking queries
        test_messages = [
            "Hello",
            "What's my balance?",
            "I want to send money",
            "How do I create an account?",
            "Buy airtime",
            "Help me"
        ]
        
        print("\n💬 Testing banking queries...")
        for message in test_messages:
            print(f"\nUser: {message}")
            response = await sofi_whatsapp_gpt.process_whatsapp_message(test_phone, message)
            print(f"Sofi: {response}")
            print("-" * 40)
        
        print("\n✅ WhatsApp GPT integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    print("Starting Sofi WhatsApp GPT Integration...")
    asyncio.run(main())
