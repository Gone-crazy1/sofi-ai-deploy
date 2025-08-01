"""
WhatsApp GPT-3.5 Turbo Integration for Sofi AI
===============================================
Connects WhatsApp messages to OpenAI GPT-3.5 Turbo for intelligent responses
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
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
- You're connected to 9PSB banking APIs and can assist with real transactions
- You communicate in a friendly, helpful, and professional manner
- You understand Nigerian banking context and speak both English and Pidgin when appropriate

CAPABILITIES:
- Account creation and onboarding
- Balance checking and account inquiries  
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

COMMON QUERIES:
- "balance" → Check account balance
- "send money" → Guide money transfer process  
- "signup" / "create account" → Start onboarding
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
    
    async def process_whatsapp_message(self, phone_number: str, message: str) -> str:
        """Process WhatsApp message using GPT-3.5 Turbo"""
        try:
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
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            return "❌ Sorry, I'm experiencing some technical issues. Please try again in a moment."
    
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
            return f"{message}\n\nContext: User wants to create a new account. Start the friendly onboarding process and explain Sofi's banking services."
        
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
    
    async def send_welcome_message(self, phone_number: str) -> str:
        """Generate personalized welcome message for new users"""
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
        
        return await self.call_gpt_async(messages)

# Global instance for use in main application
sofi_whatsapp_gpt = SofiWhatsAppGPT()
