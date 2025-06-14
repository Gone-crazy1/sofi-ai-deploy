"""
SHARP SOFI AI - Intelligent Message Handler with Permanent Memory
This module handles all incoming messages with advanced memory and context awareness
"""

import asyncio
import json
import re
import openai
from datetime import datetime
from typing import Dict, Optional, List
from utils.sharp_memory import (
    sharp_memory, get_smart_greeting, get_spending_report, 
    remember_user_action, remember_transaction, save_conversation_context,
    get_current_date_time
)
from utils.bank_api import BankAPI
from utils.conversation_state import ConversationState
import openai

class SharpSofiAI:
    """Intelligent AI handler with permanent memory and context awareness"""
    
    def __init__(self):
        self.conversation_state = ConversationState()
        self.bank_api = BankAPI()
    
    async def process_message(self, chat_id: str, message: str, user_data: Dict = None) -> str:
        """
        Main message processing with sharp AI intelligence
        - Remembers everything permanently
        - Context-aware responses
        - Date/time awareness
        - Spending analytics
        """
        
        # Save the conversation context
        await save_conversation_context(chat_id, f"User: {message}")
          # Update user profile with current interaction
        await remember_user_action(chat_id, "sent_message")
        
        # Check for specific commands first
        response = await self._handle_special_commands(chat_id, message, user_data)
        if response:
            return response
        
        # Check for transfer requests (Xara-style intelligence)
        transfer_response = await self._handle_smart_transfer_detection(chat_id, message)
        if transfer_response:
            return transfer_response
        
        # Check for spending analysis requests
        analytics_response = await self._handle_spending_analytics(chat_id, message)
        if analytics_response:
            return analytics_response
        
        # Handle general conversation with context awareness
        return await self._handle_general_conversation(chat_id, message, user_data)
    
    async def _handle_special_commands(self, chat_id: str, message: str, user_data: Dict) -> Optional[str]:
        """Handle special commands with memory awareness"""
        
        message_lower = message.lower().strip()
        current_time = sharp_memory.get_current_datetime_info()
        
        # Greeting commands with smart context
        if any(cmd in message_lower for cmd in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']):
            greeting = await get_smart_greeting(chat_id)
            await remember_user_action(chat_id, "greeted_sofi")
            return greeting
        
        # Balance inquiry with context
        elif any(cmd in message_lower for cmd in ['balance', 'my balance', 'check balance']):
            # Get user's current balance (you'll need to implement this)
            balance_info = await self._get_user_balance_with_context(chat_id)
            await remember_user_action(chat_id, "checked_balance")
            return balance_info
        
        # Spending reports
        elif any(cmd in message_lower for cmd in ['spending', 'how much', 'spent', 'transactions']):
            report = await get_spending_report(chat_id)
            await remember_user_action(chat_id, "requested_spending_report")
            return report
        
        # Date/time awareness
        elif any(cmd in message_lower for cmd in ['date', 'time', 'today', 'what day']):
            await remember_user_action(chat_id, "asked_for_date_time")
            return f"📅 **Current Date & Time**\n\n{current_time['formatted_date']} at {current_time['formatted_time']}\n\n{current_time['greeting']}"
        
        # Memory/history commands
        elif any(cmd in message_lower for cmd in ['history', 'last time', 'yesterday', 'remember']):
            return await self._handle_memory_inquiry(chat_id, message)
        
        return None
    
    async def _handle_smart_transfer_detection(self, chat_id: str, message: str) -> Optional[str]:
        """Xara-style intelligent transfer detection with memory"""
        
        # Enhanced patterns for account detection
        account_patterns = [
            r'\b(\d{10,11})\b',  # 10-11 digit account numbers
            r'\b(\d{4}\s?\d{3}\s?\d{3,4})\b',  # Formatted account numbers
        ]
        
        # COMPREHENSIVE bank name patterns - ALL NIGERIAN BANKS & FINTECH
        bank_patterns = {
            # Traditional Banks
            'access': ['access', 'access bank'],
            'gtbank': ['gtb', 'gtbank', 'guaranty trust', 'gt bank', 'gtworld'],
            'zenith': ['zenith', 'zenith bank'],
            'uba': ['uba', 'united bank for africa'],
            'first bank': ['first bank', 'firstbank', 'fbn'],
            'fidelity': ['fidelity', 'fidelity bank'],
            'fcmb': ['fcmb', 'first city monument bank'],
            'sterling': ['sterling', 'sterling bank'],
            'wema': ['wema', 'wema bank', 'alat', 'alat by wema'],
            'union': ['union bank', 'union'],
            'polaris': ['polaris', 'polaris bank'],
            'keystone': ['keystone', 'keystone bank'],
            
            # Major Fintech Banks & Digital Banks
            'opay': ['opay', 'o pay'],
            'moniepoint': ['monie', 'moniepoint', 'monie point', 'moneypoint'],
            'kuda': ['kuda', 'kuda bank'],
            'palmpay': ['palmpay', 'palm pay'],
            'vfd': ['vfd', 'vfd microfinance bank', 'vfd bank'],
            '9psb': ['9psb', '9 psb', '9mobile psb', '9mobile'],
            'carbon': ['carbon', 'carbon microfinance bank'],
        }
        
        detected_account = None
        detected_bank = None
        
        # Find account number
        for pattern in account_patterns:
            match = re.search(pattern, message)
            if match:
                detected_account = re.sub(r'\s', '', match.group(1))
                break
        
        # Find bank name with fuzzy matching
        message_lower = message.lower()
        for bank_name, variations in bank_patterns.items():
            for variation in variations:
                if variation in message_lower:
                    detected_bank = bank_name
                    break
            if detected_bank:
                break
        
        # Auto-verify if both found
        if detected_account and detected_bank:
            # Get bank code
            bank_code = self.bank_api.get_bank_code(detected_bank)
            if not bank_code:
                return None
                
            try:
                # Verify account
                verification = await self.bank_api.verify_account(detected_account, bank_code)
                if not verification or not verification.get('verified'):
                    return None
                
                account_name = verification.get('account_name')
                
                # Extract amount from message
                amount = self._extract_amount_from_message(message)
                
                if amount and account_name:
                    # Remember this transfer attempt
                    await remember_user_action(
                        chat_id, 
                        f"attempted_transfer_to_{account_name}", 
                        amount=amount,
                        bank=detected_bank,
                        account=detected_account
                    )
                    
                    # Store transfer state for confirmation
                    self.conversation_state.set_state(chat_id, {
                        'step': 'confirm_xara_transfer',
                        'transfer': {
                            'account_number': detected_account,
                            'bank': detected_bank,
                            'recipient_name': account_name,
                            'amount': amount,
                            'auto_verified': True
                        }
                    })
                    
                    # XARA-STYLE RESPONSE with memory context
                    current_time = get_current_date_time()
                    xara_response = f"""🎯 **Transfer Details Detected** - {current_time}

**Click the Verify Transaction button below to complete transfer of ₦{amount:,.2f} to {account_name.upper()} ({detected_account}) at {detected_bank.title()}**

💳 **Account Verified:**
• Name: {account_name.upper()}
• Account: {detected_account}
• Bank: {detected_bank.title()}
• Amount: ₦{amount:,.2f}

🧠 **Sofi remembers**: This will be saved to your transaction history.

Proceed with this transfer? Type 'yes' to confirm or 'no' to cancel."""
                    
                    return xara_response
                    
            except Exception as e:
                print(f"Error in smart transfer detection: {e}")
        
        return None
    
    def _extract_amount_from_message(self, message: str) -> Optional[float]:
        """Extract amount from natural language message"""
        amount_patterns = [
            r'\b(\d+)k\b',  # Numbers followed by 'k' (like 2k, 10k)
            r'\bsend\s+(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # send 5000
            r'\btransfer\s+(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # transfer 1500
            r'\bpay\s+(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # pay 7500
            r'₦(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # ₦5000
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, message.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                # Handle 'k' for thousands
                if 'k' in pattern:
                    return float(amount_str) * 1000
                else:
                    return float(amount_str)
        return None
    
    async def _handle_spending_analytics(self, chat_id: str, message: str) -> Optional[str]:
        """Handle spending analytics requests with memory"""
        
        message_lower = message.lower()
        
        # Check for time-specific spending queries
        if any(phrase in message_lower for phrase in ['this week', 'week', 'weekly']):
            summary = await sharp_memory.get_spending_summary(chat_id, 'week')
            await remember_user_action(chat_id, "requested_weekly_spending")
            
        elif any(phrase in message_lower for phrase in ['this month', 'month', 'monthly']):
            summary = await sharp_memory.get_spending_summary(chat_id, 'month')
            await remember_user_action(chat_id, "requested_monthly_spending")
            
        elif any(phrase in message_lower for phrase in ['today', 'today\'s']):
            summary = await sharp_memory.get_spending_summary(chat_id, 'today')
            await remember_user_action(chat_id, "requested_daily_spending")
            
        elif any(phrase in message_lower for phrase in ['yesterday']):
            summary = await sharp_memory.get_spending_summary(chat_id, 'yesterday')
            await remember_user_action(chat_id, "requested_yesterday_spending")
            
        elif any(phrase in message_lower for phrase in ['3 months', 'quarter', 'quarterly']):
            summary = await sharp_memory.get_spending_summary(chat_id, 'quarter')
            await remember_user_action(chat_id, "requested_quarterly_spending")
            
        else:
            return None
        
        if summary and summary.get('total_spent', 0) > 0:
            return self._format_spending_summary(summary)
        else:
            return f"📊 No spending found for the requested period."
    
    def _format_spending_summary(self, summary: Dict) -> str:
        """Format spending summary with rich details"""
        period = summary['period_display']
        total = summary['total_spent']
        count = summary['transaction_count']
        avg = summary.get('average_per_transaction', 0)
        
        response = f"""💰 **{period} Spending Summary** - {get_current_date_time()}

📊 **Overview:**
• Total Spent: ₦{total:,.2f}
• Transactions: {count}
• Average per transaction: ₦{avg:,.2f}

"""
        
        # Add spending breakdown
        spending_by_type = summary.get('spending_by_type', {})
        if spending_by_type:
            response += "💳 **Breakdown by Type:**\n"
            for spend_type, amount in spending_by_type.items():
                percentage = (amount / total) * 100
                response += f"• {spend_type.title()}: ₦{amount:,.2f} ({percentage:.1f}%)\n"
        
        # Add top recipient/bank
        top_recipient = summary.get('top_recipient')
        top_bank = summary.get('top_bank')
        
        if top_recipient or top_bank:
            response += "\n🎯 **Top Activities:**\n"
            if top_recipient:
                response += f"• Most sent to: {top_recipient[0]} (₦{top_recipient[1]:,.2f})\n"
            if top_bank:
                response += f"• Most used bank: {top_bank[0]} (₦{top_bank[1]:,.2f})\n"
        
        return response
    
    async def _handle_memory_inquiry(self, chat_id: str, message: str) -> str:
        """Handle memory and history inquiries"""
        
        message_lower = message.lower()
        
        # Get user profile for context
        profile = await sharp_memory.get_user_profile(chat_id)
        recent_context = await sharp_memory.get_relevant_context(chat_id, days_back=7)
        
        if any(phrase in message_lower for phrase in ['last time', 'yesterday', 'what did i']):
            if profile and profile.get('last_action'):
                last_action = profile['last_action']
                last_time = profile.get('last_action_time')
                
                if last_time:
                    last_datetime = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                    relative_time = sharp_memory.get_relative_time_description(last_datetime)
                    
                    response = f"🧠 **Memory Recall**\n\n"
                    response += f"📝 {relative_time.title()}, you {last_action.lower()}\n"
                    response += f"🕐 Exact time: {last_datetime.strftime('%A, %B %d at %I:%M %p')}\n\n"
                    
                    # Add recent context if available
                    if recent_context:
                        response += "📋 **Recent Activities:**\n"
                        for ctx in recent_context[:3]:
                            ctx_time = datetime.fromisoformat(ctx['context_date'].replace('Z', '+00:00'))
                            ctx_relative = sharp_memory.get_relative_time_description(ctx_time)
                            response += f"• {ctx_relative}: {ctx['context_summary']}\n"
                    
                    await remember_user_action(chat_id, "recalled_memory")
                    return response
                    
        return "🧠 I remember everything! Ask me about your spending, transactions, or recent activities."
    
    async def _get_user_balance_with_context(self, chat_id: str) -> str:
        """Get user balance with spending context"""
        
        # Get current balance (implement this based on your system)
        # For now, return a template
        current_time = get_current_date_time()
        
        # Get recent spending for context
        today_summary = await sharp_memory.get_spending_summary(chat_id, 'today')
        week_summary = await sharp_memory.get_spending_summary(chat_id, 'week')
        
        response = f"💰 **Account Balance** - {current_time}\n\n"
        response += f"💳 Current Balance: ₦[BALANCE_HERE]\n\n"  # You'll need to implement balance lookup
        
        if today_summary['total_spent'] > 0:
            response += f"📊 Today's spending: ₦{today_summary['total_spent']:,.2f}\n"
        
        if week_summary['total_spent'] > 0:
            response += f"📈 This week's spending: ₦{week_summary['total_spent']:,.2f}\n"
        
        return response
    
    async def _handle_general_conversation(self, chat_id: str, message: str, user_data: Dict) -> str:
        """Handle general conversation with AI and context awareness"""
        
        try:
            # Get conversation context for AI
            recent_context = await sharp_memory.get_relevant_context(chat_id, days_back=3)
            profile = await sharp_memory.get_user_profile(chat_id)
            current_time = sharp_memory.get_current_datetime_info()
            
            # Build context for AI
            context_info = f"""
Current Date & Time: {current_time['formatted_date']} at {current_time['formatted_time']}
Day: {current_time['day_name']}
Time of day: {'Morning' if current_time['is_morning'] else 'Afternoon' if current_time['is_afternoon'] else 'Evening' if current_time['is_evening'] else 'Night'}
"""
            
            if profile:
                name = profile.get('full_name', '').split()[0] if profile.get('full_name') else 'there'
                context_info += f"User's name: {name}\n"
                
                if profile.get('last_action'):
                    last_action_time = profile.get('last_action_time')
                    if last_action_time:
                        last_datetime = datetime.fromisoformat(last_action_time.replace('Z', '+00:00'))
                        relative_time = sharp_memory.get_relative_time_description(last_datetime)
                        context_info += f"Last action: {relative_time}, {profile['last_action']}\n"
            
            # Add recent context
            if recent_context:
                context_info += "Recent conversation context:\n"
                for ctx in recent_context[:2]:
                    context_info += f"- {ctx['context_summary']}\n"
            
            # Create AI prompt with context
            system_prompt = f"""You are Sofi AI, a brilliant Nigerian fintech assistant with perfect memory and awareness.

CONTEXT AWARENESS:
{context_info}

PERSONALITY:
- Friendly, helpful, and intelligent
- Always aware of current date/time
- Remember past interactions
- Use Nigerian context and understanding
- Support all Nigerian banks and fintech platforms

CAPABILITIES:
- Bank transfers (all Nigerian banks: GTB, Access, UBA, Zenith, Opay, Kuda, PalmPay, Moniepoint, etc.)
- Account verification and name resolution
- Spending analytics and financial insights
- Permanent memory of all interactions
- Date/time awareness

Respond naturally and helpfully, using the context provided."""

            # Call OpenAI with context
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Save this interaction
            await save_conversation_context(
                chat_id, 
                f"General conversation: {message[:50]}... → {ai_response[:50]}...",
                importance=1
            )
            
            await remember_user_action(chat_id, "had_conversation")
            
            return ai_response
            
        except Exception as e:
            print(f"Error in AI conversation: {e}")
            return f"I'm here to help! {sharp_memory.get_current_datetime_info()['greeting']} What can I do for you today?"

# Initialize the sharp AI system
sharp_sofi = SharpSofiAI()

# Main function to handle incoming messages
async def handle_smart_message(chat_id: str, message: str, user_data: Dict = None) -> str:
    """
    Main entry point for handling messages with Sharp AI intelligence
    This replaces any existing message handlers with full memory awareness
    """
    return await sharp_sofi.process_message(chat_id, message, user_data)
