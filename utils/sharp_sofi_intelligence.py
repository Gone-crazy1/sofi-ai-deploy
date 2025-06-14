"""
SHARP SOFI AI - Main Intelligence Processor
Integrates all memory, awareness, and intelligence features
Makes Sofi AI truly sharp like ChatGPT/Siri
"""

import os
import re
import asyncio
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Import our sharp memory system
from utils.sharp_memory import (
    sharp_memory, get_smart_greeting, get_spending_report,
    remember_user_action, remember_transaction, save_conversation_context,
    get_current_date_time
)

load_dotenv()

class SharpSofiAI:
    """Main Sharp AI processor for intelligent interactions"""
    
    def __init__(self):
        self.memory = sharp_memory
    
    async def process_message(self, chat_id: str, message: str, user_data: dict = None) -> str:
        """Process user message with full intelligence and memory"""
        
        # Save conversation context
        await save_conversation_context(chat_id, f"User said: {message}")
        
        # Get current time info for awareness
        time_info = self.memory.get_current_datetime_info()
        
        # Analyze message intent
        intent = self._analyze_intent(message)
        
        # Remember user's last action
        await remember_user_action(chat_id, f"sent_message: {intent}", last_intent=intent)
        
        # Generate response based on intent
        if intent == "greeting":
            return await self._handle_greeting(chat_id, message)
        elif intent == "balance_inquiry":
            return await self._handle_balance_inquiry(chat_id)
        elif intent == "spending_inquiry":
            return await self._handle_spending_inquiry(chat_id, message)
        elif intent == "date_time_inquiry":
            return await self._handle_date_time_inquiry(time_info)
        elif intent == "transfer_request":
            return await self._handle_transfer_request(chat_id, message)
        elif intent == "memory_inquiry":
            return await self._handle_memory_inquiry(chat_id, message)
        else:
            return await self._handle_general_conversation(chat_id, message, time_info)
    
    def _analyze_intent(self, message: str) -> str:
        """Analyze user message to determine intent"""
        message_lower = message.lower()
        
        # Greeting patterns
        greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\b(how are you|what\'s up)\b'
        ]
        
        # Balance inquiry patterns
        balance_patterns = [
            r'\b(balance|wallet|account balance|my balance|check balance)\b',
            r'\bwhat.*balance\b',
            r'\bhow much.*money\b'
        ]
        
        # Spending inquiry patterns
        spending_patterns = [
            r'\b(spent|spending|expenses|expenditure)\b',
            r'\bhow much.*spent\b',
            r'\bspending.*report\b',
            r'\b(this week|this month|today|yesterday).*spent\b'
        ]
        
        # Date/time inquiry patterns
        datetime_patterns = [
            r'\b(date|time|today|day|month|year)\b',
            r'\bwhat.*date\b',
            r'\bwhat.*time\b',
            r'\bwhat.*day\b'
        ]
        
        # Transfer request patterns
        transfer_patterns = [
            r'\b\d{10,11}\b.*\b(send|transfer|pay)\b',
            r'\b(send|transfer|pay)\b.*\b\d{10,11}\b',
            r'\b(moniepoint|opay|kuda|access|gtb|uba|zenith)\b.*\b(send|transfer)\b'
        ]
        
        # Memory inquiry patterns
        memory_patterns = [
            r'\b(remember|recall|what did|yesterday|last week|last month)\b',
            r'\bwhat.*yesterday\b',
            r'\blast.*transaction\b'
        ]
        
        # Check patterns
        for pattern in greeting_patterns:
            if re.search(pattern, message_lower):
                return "greeting"
        
        for pattern in balance_patterns:
            if re.search(pattern, message_lower):
                return "balance_inquiry"
        
        for pattern in spending_patterns:
            if re.search(pattern, message_lower):
                return "spending_inquiry"
        
        for pattern in datetime_patterns:
            if re.search(pattern, message_lower):
                return "date_time_inquiry"
        
        for pattern in transfer_patterns:
            if re.search(pattern, message_lower):
                return "transfer_request"
        
        for pattern in memory_patterns:
            if re.search(pattern, message_lower):
                return "memory_inquiry"
        
        return "general"
    
    async def _handle_greeting(self, chat_id: str, message: str) -> str:
        """Handle greeting with context and memory"""
        smart_greeting = await get_smart_greeting(chat_id)
        
        # Add personalized touch based on time
        time_info = self.memory.get_current_datetime_info()
        
        response = f"{smart_greeting}\n\n"
        
        # Get user profile for personalization
        profile = await self.memory.get_user_profile(chat_id)
        if profile and profile.get('full_name'):
            name = profile['full_name'].split()[0]
            response += f"Great to see you again, {name}! "
        
        response += f"What can I help you with this {time_info['day_name']}? 😊"
        
        return response
    
    async def _handle_balance_inquiry(self, chat_id: str) -> str:
        """Handle balance inquiry with spending context"""
        # This would integrate with actual balance checking
        profile = await self.memory.get_user_profile(chat_id)
        
        if profile:
            last_balance = profile.get('last_balance', 0)
            response = f"💰 **Your Account Balance**\n\n"
            response += f"Current Balance: ₦{last_balance:,.2f}\n\n"
            
            # Add spending insight
            week_summary = await self.memory.get_spending_summary(chat_id, 'week')
            if week_summary.get('total_spent', 0) > 0:
                response += f"📊 This week you've spent: ₦{week_summary['total_spent']:,.2f}\n"
                response += f"💳 Total transactions: {week_summary['transaction_count']}"
        else:
            response = "I don't have your balance information yet. Please check your account or make a transaction first."
        
        return response
    
    async def _handle_spending_inquiry(self, chat_id: str, message: str) -> str:
        """Handle spending inquiry with intelligent analysis"""
        # Determine time period from message
        message_lower = message.lower()
        
        if 'today' in message_lower:
            period = 'today'
        elif 'yesterday' in message_lower:
            period = 'yesterday'
        elif 'week' in message_lower:
            period = 'week'
        elif 'month' in message_lower:
            period = 'month'
        else:
            period = 'week'  # Default
        
        # Generate comprehensive spending report
        return await get_spending_report(chat_id)
    
    async def _handle_date_time_inquiry(self, time_info: Dict) -> str:
        """Handle date/time inquiries with full awareness"""
        response = f"📅 **Current Date & Time Information**\n\n"
        response += f"📅 Date: {time_info['formatted_date']}\n"
        response += f"🕐 Time: {time_info['formatted_time']}\n"
        response += f"📍 Day: {time_info['day_name']}\n"
        response += f"🗓️ Month: {time_info['month_name']}\n"
        response += f"📊 Year: {time_info['year']}\n\n"
        
        if time_info['is_weekend']:
            response += "🎉 It's the weekend! Time to relax! 😎"
        else:
            response += "💼 It's a weekday! Hope you're having a productive day! 💪"
        
        return response
    
    async def _handle_transfer_request(self, chat_id: str, message: str) -> str:
        """Handle transfer request with Xara-style intelligence"""
        # This would integrate with the existing transfer flow
        # For now, acknowledge and save context
        await save_conversation_context(
            chat_id, 
            f"Transfer request: {message}", 
            importance=3
        )
        
        response = "🎯 I detected a transfer request! Let me process that for you...\n\n"
        response += "This will be handled by our smart transfer system with account verification."
        
        return response
    
    async def _handle_memory_inquiry(self, chat_id: str, message: str) -> str:
        """Handle memory/history inquiries"""
        message_lower = message.lower()
        
        # Get recent context
        recent_context = await self.memory.get_relevant_context(chat_id, days_back=7)
        
        # Get transaction history
        transactions = await self.memory.get_transaction_history(chat_id, days_back=7)
        
        response = "🧠 **Your Recent Activity Memory**\n\n"
        
        if transactions:
            response += f"📊 Recent Transactions ({len(transactions)} found):\n"
            for i, tx in enumerate(transactions[:3], 1):  # Show top 3
                tx_date = datetime.fromisoformat(tx['transaction_date'].replace('Z', '+00:00'))
                relative_time = self.memory.get_relative_time_description(tx_date)
                response += f"{i}. {tx['transaction_type'].title()}: ₦{tx['amount']:,.2f} - {relative_time}\n"
        
        if recent_context:
            response += f"\n💭 Recent Context:\n"
            for context in recent_context[:2]:  # Show top 2
                ctx_date = datetime.fromisoformat(context['context_date'].replace('Z', '+00:00'))
                relative_time = self.memory.get_relative_time_description(ctx_date)
                response += f"• {context['context_summary']} - {relative_time}\n"
        
        if not transactions and not recent_context:
            response += "I don't have much history for you yet. As we interact more, I'll remember everything!"
        
        return response
    
    async def _handle_general_conversation(self, chat_id: str, message: str, time_info: Dict) -> str:
        """Handle general conversation with context awareness"""
        # Save the conversation
        await save_conversation_context(chat_id, f"General conversation: {message}")
        
        # Generate contextual response
        profile = await self.memory.get_user_profile(chat_id)
        
        response = f"I understand you said: \"{message}\"\n\n"
        
        if profile and profile.get('full_name'):
            name = profile['full_name'].split()[0]
            response += f"How can I help you today, {name}? "
        else:
            response += "How can I assist you? "
        
        response += f"It's {time_info['formatted_time']} on this {time_info['day_name']}.\n\n"
        response += "I can help you with:\n"
        response += "💰 Check balance & spending\n"
        response += "💸 Transfer money\n"
        response += "📱 Buy airtime/data\n"
        response += "🪙 Crypto transactions\n"
        response += "📊 Financial reports\n"
        response += "🧠 Remember our conversations"
        
        return response

# Global instance
sharp_sofi = SharpSofiAI()

# Convenience functions for integration
async def process_sharp_message(chat_id: str, message: str, user_data: dict = None) -> str:
    """Main function to process messages with Sharp AI"""
    return await sharp_sofi.process_message(chat_id, message, user_data)

async def get_intelligent_greeting(chat_id: str) -> str:
    """Get intelligent greeting with full context"""
    return await sharp_sofi._handle_greeting(chat_id, "hello")

async def analyze_message_intent(message: str) -> str:
    """Analyze message intent"""
    return sharp_sofi._analyze_intent(message)

async def get_memory_response(chat_id: str, query: str) -> str:
    """Get memory-based response"""
    return await sharp_sofi._handle_memory_inquiry(chat_id, query)
