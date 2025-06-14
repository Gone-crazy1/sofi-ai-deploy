"""
SHARP AI MEMORY SYSTEM - Makes Sofi AI truly intelligent
Implements permanent memory, date awareness, and context understanding
Like ChatGPT/Siri but for Nigerian fintech
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import asyncio

# Load environment variables
load_dotenv()

class SharpMemory:
    """Comprehensive AI Memory System for Context-Aware Intelligence"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        self.supabase = create_client(supabase_url, supabase_key)
    
    # ============ DATE & TIME AWARENESS ============
    
    def get_current_datetime_info(self) -> Dict:
        """Get comprehensive current date/time information"""
        now = datetime.now()
        return {
            'current_datetime': now,
            'formatted_date': now.strftime("%A, %d %B %Y"),  # Saturday, 14 June 2025
            'formatted_time': now.strftime("%I:%M %p"),      # 02:30 PM
            'day_name': now.strftime("%A"),                  # Saturday
            'month_name': now.strftime("%B"),                # June
            'year': now.year,
            'hour': now.hour,
            'is_weekend': now.weekday() >= 5,
            'is_morning': 5 <= now.hour < 12,
            'is_afternoon': 12 <= now.hour < 17,
            'is_evening': 17 <= now.hour < 21,
            'is_night': now.hour >= 21 or now.hour < 5,
            'greeting': self._get_time_based_greeting(now)
        }
    
    def _get_time_based_greeting(self, now: datetime) -> str:
        """Get appropriate greeting based on time"""
        hour = now.hour
        day_name = now.strftime("%A")
        
        if 5 <= hour < 12:
            return f"Good morning! Happy {day_name}! 🌅"
        elif 12 <= hour < 17:
            return f"Good afternoon! Hope your {day_name} is going well! ☀️"
        elif 17 <= hour < 21:
            return f"Good evening! Winding down this {day_name}? 🌆"
        else:
            return f"Good evening! Late {day_name} vibes! 🌙"
    
    def get_relative_time_description(self, past_datetime: datetime) -> str:
        """Convert datetime to human-friendly relative description"""
        now = datetime.now()
        diff = now - past_datetime
        
        if diff.days == 0:
            if diff.seconds < 3600:  # Less than 1 hour
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
        elif diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
    
    # ============ USER PROFILE MEMORY ============
    
    async def update_user_profile(self, chat_id: str, **kwargs) -> bool:
        """Update or create user profile with memory"""
        try:
            current_time = datetime.now()
            
            # Check if profile exists
            existing = self.supabase.table("user_profiles")\
                .select("*")\
                .eq("telegram_chat_id", chat_id)\
                .execute()
            
            if existing.data:
                # Update existing profile
                update_data = {
                    "updated_at": current_time.isoformat(),
                    **kwargs
                }
                
                self.supabase.table("user_profiles")\
                    .update(update_data)\
                    .eq("telegram_chat_id", chat_id)\
                    .execute()
            else:
                # Create new profile
                profile_data = {
                    "telegram_chat_id": chat_id,
                    "created_at": current_time.isoformat(),
                    "updated_at": current_time.isoformat(),
                    **kwargs
                }
                
                self.supabase.table("user_profiles")\
                    .insert(profile_data)\
                    .execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    async def get_user_profile(self, chat_id: str) -> Optional[Dict]:
        """Get complete user profile and memory"""
        try:
            result = self.supabase.table("user_profiles")\
                .select("*")\
                .eq("telegram_chat_id", chat_id)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    # ============ TRANSACTION MEMORY ============
    
    async def record_transaction(self, chat_id: str, transaction_type: str, 
                               amount: float, **kwargs) -> bool:
        """Record transaction for permanent memory"""
        try:
            transaction_data = {
                "telegram_chat_id": chat_id,
                "transaction_type": transaction_type,
                "amount": amount,
                "transaction_date": datetime.now().isoformat(),
                **kwargs
            }
            
            self.supabase.table("transaction_memory")\
                .insert(transaction_data)\
                .execute()
            
            # Update user profile stats
            await self.update_user_profile(
                chat_id,
                total_transactions=f"total_transactions + 1",
                total_spent=f"total_spent + {amount}",
                last_action=f"{transaction_type} of ₦{amount:,.2f}",
                last_action_time=datetime.now().isoformat()
            )
            
            return True
            
        except Exception as e:
            print(f"Error recording transaction: {e}")
            return False
    
    async def get_transaction_history(self, chat_id: str, 
                                    days_back: int = 30) -> List[Dict]:
        """Get transaction history for analysis"""
        try:
            start_date = datetime.now() - timedelta(days=days_back)
            
            result = self.supabase.table("transaction_memory")\
                .select("*")\
                .eq("telegram_chat_id", chat_id)\
                .gte("transaction_date", start_date.isoformat())\
                .order("transaction_date", desc=True)\
                .execute()
            
            return result.data
            
        except Exception as e:
            print(f"Error getting transaction history: {e}")
            return []
    
    # ============ SPENDING ANALYTICS ============
    
    async def get_spending_summary(self, chat_id: str, 
                                 period: str = 'week') -> Dict:
        """Get intelligent spending summary"""
        try:
            now = datetime.now()
            
            # Define period ranges
            period_ranges = {
                'today': (now.replace(hour=0, minute=0, second=0), now),
                'yesterday': (
                    (now - timedelta(days=1)).replace(hour=0, minute=0, second=0),
                    (now - timedelta(days=1)).replace(hour=23, minute=59, second=59)
                ),
                'week': (now - timedelta(days=7), now),
                'month': (now - timedelta(days=30), now),
                'quarter': (now - timedelta(days=90), now),
                'year': (now - timedelta(days=365), now)
            }
            
            start_date, end_date = period_ranges.get(period, period_ranges['week'])
            
            # Get transactions in period
            transactions = self.supabase.table("transaction_memory")\
                .select("*")\
                .eq("telegram_chat_id", chat_id)\
                .gte("transaction_date", start_date.isoformat())\
                .lte("transaction_date", end_date.isoformat())\
                .execute()
            
            if not transactions.data:
                return {
                    'period': period,
                    'total_spent': 0,
                    'transaction_count': 0,
                    'message': f"No transactions found for the past {period}"
                }
            
            # Analyze spending
            total_spent = sum(t['amount'] for t in transactions.data)
            transaction_count = len(transactions.data)
            
            # Group by type
            by_type = {}
            top_recipients = {}
            top_banks = {}
            
            for t in transactions.data:
                t_type = t['transaction_type']
                by_type[t_type] = by_type.get(t_type, 0) + t['amount']
                
                if t.get('recipient_name'):
                    name = t['recipient_name']
                    top_recipients[name] = top_recipients.get(name, 0) + t['amount']
                
                if t.get('bank_name'):
                    bank = t['bank_name']
                    top_banks[bank] = top_banks.get(bank, 0) + t['amount']
            
            # Sort top recipients and banks
            top_recipient = max(top_recipients.items(), key=lambda x: x[1]) if top_recipients else None
            top_bank = max(top_banks.items(), key=lambda x: x[1]) if top_banks else None
            
            return {
                'period': period,
                'period_display': period.title(),
                'total_spent': total_spent,
                'transaction_count': transaction_count,
                'average_per_transaction': total_spent / transaction_count if transaction_count > 0 else 0,
                'spending_by_type': by_type,
                'top_recipient': top_recipient,
                'top_bank': top_bank,
                'start_date': start_date,
                'end_date': end_date
            }
            
        except Exception as e:
            print(f"Error getting spending summary: {e}")
            return {}
    
    # ============ CONTEXT AWARENESS ============
    
    async def save_context(self, chat_id: str, context_type: str, 
                          summary: str, full_context: str = None, 
                          importance: int = 1) -> bool:
        """Save conversation context for future reference"""
        try:
            context_data = {
                "telegram_chat_id": chat_id,
                "context_type": context_type,
                "context_summary": summary,
                "full_context": full_context or summary,
                "importance_level": importance,
                "context_date": datetime.now().isoformat()
            }
            
            self.supabase.table("conversation_context")\
                .insert(context_data)\
                .execute()
            
            return True
            
        except Exception as e:
            print(f"Error saving context: {e}")
            return False
    
    async def get_relevant_context(self, chat_id: str, 
                                 days_back: int = 7) -> List[Dict]:
        """Get relevant conversation context"""
        try:
            start_date = datetime.now() - timedelta(days=days_back)
            
            result = self.supabase.table("conversation_context")\
                .select("*")\
                .eq("telegram_chat_id", chat_id)\
                .gte("context_date", start_date.isoformat())\
                .order("importance_level", desc=True)\
                .order("context_date", desc=True)\
                .limit(5)\
                .execute()
            
            return result.data
            
        except Exception as e:
            print(f"Error getting context: {e}")
            return []
    
    # ============ SMART RESPONSES ============
    
    async def generate_smart_greeting(self, chat_id: str) -> str:
        """Generate intelligent, context-aware greeting"""
        try:
            # Get current time info
            time_info = self.get_current_datetime_info()
            
            # Get user profile
            profile = await self.get_user_profile(chat_id)
            
            # Get recent context
            recent_context = await self.get_relevant_context(chat_id, days_back=2)
            
            # Build smart greeting
            greeting = time_info['greeting']
            
            if profile:
                name = profile.get('full_name', '').split()[0] if profile.get('full_name') else ''
                if name:
                    greeting = f"{time_info['greeting']} {name}!"
                
                # Add context if available
                last_action = profile.get('last_action')
                last_time = profile.get('last_action_time')
                
                if last_action and last_time:
                    last_datetime = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                    relative_time = self.get_relative_time_description(last_datetime)
                    
                    greeting += f"\n\n💭 {relative_time.title()}, you {last_action.lower()}. Need help with anything else?"
            
            # Add date awareness
            greeting += f"\n\n📅 Today is {time_info['formatted_date']}"
            
            return greeting
            
        except Exception as e:
            print(f"Error generating smart greeting: {e}")
            return self.get_current_datetime_info()['greeting']
    
    async def generate_spending_report(self, chat_id: str) -> str:
        """Generate intelligent spending report"""
        try:
            current_time = self.get_current_datetime_info()
            
            # Get spending for different periods
            today = await self.get_spending_summary(chat_id, 'today')
            week = await self.get_spending_summary(chat_id, 'week')
            month = await self.get_spending_summary(chat_id, 'month')
            
            report = f"💰 **SPENDING REPORT** - {current_time['formatted_date']}\n\n"
            
            # Today's spending
            if today['total_spent'] > 0:
                report += f"📊 **Today**: ₦{today['total_spent']:,.2f} ({today['transaction_count']} transactions)\n"
            else:
                report += f"📊 **Today**: No transactions yet\n"
            
            # This week
            if week['total_spent'] > 0:
                report += f"📈 **This Week**: ₦{week['total_spent']:,.2f} ({week['transaction_count']} transactions)\n"
                
                if week['top_recipient']:
                    report += f"   • Top Recipient: {week['top_recipient'][0]} (₦{week['top_recipient'][1]:,.2f})\n"
                
                if week['top_bank']:
                    report += f"   • Most Used Bank: {week['top_bank'][0]} (₦{week['top_bank'][1]:,.2f})\n"
            
            # This month
            if month['total_spent'] > 0:
                report += f"\n📅 **This Month**: ₦{month['total_spent']:,.2f} ({month['transaction_count']} transactions)\n"
                report += f"   • Average per day: ₦{month['total_spent']/30:,.2f}\n"
                
                # Spending breakdown
                report += f"\n💳 **Spending Breakdown:**\n"
                for spend_type, amount in month['spending_by_type'].items():
                    percentage = (amount / month['total_spent']) * 100
                    report += f"   • {spend_type.title()}: ₦{amount:,.2f} ({percentage:.1f}%)\n"
            
            return report
            
        except Exception as e:
            print(f"Error generating spending report: {e}")
            return "Unable to generate spending report at this time."

# Initialize global memory instance
sharp_memory = SharpMemory()

# ============ CONVENIENCE FUNCTIONS ============

async def remember_user_action(chat_id: str, action: str, **kwargs):
    """Quick function to remember user actions"""
    return await sharp_memory.update_user_profile(
        chat_id,
        last_action=action,
        last_action_time=datetime.now().isoformat(),
        **kwargs
    )

async def remember_transaction(chat_id: str, transaction_type: str, amount: float, **kwargs):
    """Quick function to remember transactions"""
    return await sharp_memory.record_transaction(chat_id, transaction_type, amount, **kwargs)

async def get_smart_greeting(chat_id: str) -> str:
    """Quick function to get smart greeting"""
    return await sharp_memory.generate_smart_greeting(chat_id)

async def get_spending_report(chat_id: str) -> str:
    """Quick function to get spending report"""
    return await sharp_memory.generate_spending_report(chat_id)

async def save_conversation_context(chat_id: str, context: str, importance: int = 1):
    """Quick function to save conversation context"""
    return await sharp_memory.save_context(chat_id, "conversation", context, importance=importance)

def get_current_date_time() -> str:
    """Quick function to get current date and time"""
    time_info = sharp_memory.get_current_datetime_info()
    return f"{time_info['formatted_date']} at {time_info['formatted_time']}"
