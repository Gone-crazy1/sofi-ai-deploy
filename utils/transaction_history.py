#!/usr/bin/env python3
"""
🧠 SOFI AI INTELLIGENT TRANSACTION HISTORY SYSTEM
================================================

This module handles all transaction history queries with human-like intelligence.
It distinguishes between transfer requests and history requests, providing
context-aware responses that don't sound like a bot.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

@dataclass
class TransactionQuery:
    """Structure for parsed transaction history queries"""
    intent: str  # 'history', 'summary', 'spending_analysis'
    time_period: str  # 'today', 'week', 'month', 'year', 'all'
    query_type: str  # 'list', 'summary', 'analysis', 'spending_pattern'
    filters: Dict  # Additional filters like transaction type, amount range
    confidence: float  # Confidence level of the parsing

class IntelligentTransactionHistory:
    """Intelligent transaction history system with human-like responses"""
    
    def __init__(self):
        self.supabase = None
        if SUPABASE_URL and SUPABASE_KEY:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def parse_history_query(self, message: str) -> Optional[TransactionQuery]:
        """
        Parse user message to understand what kind of transaction history they want
        
        Returns None if this is NOT a transaction history query
        """
        message_lower = message.lower().strip()
          # History intent keywords - prioritize these to avoid confusion with transfers
        history_indicators = [
            # Direct history requests
            "transaction history", "my transactions", "transaction list", "recent transactions",
            "payment history", "transfer history", "spending history", "my payments",
            
            # Time-based history requests  
            "last week transactions", "this month transactions", "today transactions",
            "recent activity", "transaction summary", "spending summary", "what i spent",
              # Analysis requests
            "how much i spent", "where my money went", "spending analysis", "money summary",
            "show my spending", "analyze my transactions", "breakdown my spending",
            "tell me about my spending", "summarize my transactions",
            "how did i spend", "how did i spend my money", "breakdown of my spending",
            "give me a breakdown", "financial activity", "recent financial activity",
            
            # Natural language patterns
            "what did i spend", "where did my money go", "how i spent my money",
            "show me what i paid for", "list my payments", "my financial activity"
        ]
        
        # Check if this is clearly a history request
        is_history_request = any(indicator in message_lower for indicator in history_indicators)
          # Additional patterns that indicate history (not transfer)
        history_patterns = [
            r"send.*my.*history",  # "send my transaction history"
            r"show.*my.*transactions",  # "show my transactions"
            r"tell.*me.*about.*my.*spending",  # "tell me about my spending"
            r"what.*i.*spent.*last",  # "what i spent last week"
            r"how.*much.*did.*i.*spend",  # "how much did i spend"
            r"how.*did.*i.*spend.*my.*money",  # "how did I spend my money"
            r"my.*last.*\d+.*transactions",  # "my last 10 transactions"
            r"transactions.*for.*last",  # "transactions for last month"
        ]
        
        pattern_match = any(re.search(pattern, message_lower) for pattern in history_patterns)
        
        if not (is_history_request or pattern_match):
            return None
        
        # Parse time period
        time_period = "week"  # default
        if any(word in message_lower for word in ["today", "this day"]):
            time_period = "today"
        elif any(word in message_lower for word in ["week", "last week", "this week"]):
            time_period = "week"
        elif any(word in message_lower for word in ["month", "last month", "this month"]):
            time_period = "month"
        elif any(word in message_lower for word in ["year", "last year", "this year"]):
            time_period = "year"
        elif any(word in message_lower for word in ["all", "everything", "complete", "entire"]):
            time_period = "all"
        
        # Parse query type
        query_type = "list"  # default
        if any(word in message_lower for word in ["summary", "summarize", "breakdown", "analyze"]):
            query_type = "summary"
        elif any(word in message_lower for word in ["how much", "total", "spent", "spending"]):
            query_type = "analysis"
        elif any(word in message_lower for word in ["pattern", "trends", "behavior"]):
            query_type = "spending_pattern"
        
        # Determine intent
        intent = "history"
        if query_type in ["summary", "analysis", "spending_pattern"]:
            intent = "summary"
        
        return TransactionQuery(
            intent=intent,
            time_period=time_period,
            query_type=query_type,
            filters={},
            confidence=0.9 if is_history_request else 0.7
        )
    
    def get_date_range(self, period: str) -> Tuple[datetime, datetime]:
        """Get start and end dates for the specified period"""
        now = datetime.now()
        
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "week":
            start = now - timedelta(days=7)
            end = now
        elif period == "month":
            start = now - timedelta(days=30)
            end = now
        elif period == "year":
            start = now - timedelta(days=365)
            end = now
        else:  # "all"
            start = datetime(2020, 1, 1)  # Far back enough
            end = now
        
        return start, end
    
    async def get_user_transactions(self, chat_id: str, start_date: datetime, 
                                  end_date: datetime, limit: int = 50) -> List[Dict]:
        """Get user transactions from multiple sources"""
        transactions = []
        
        if not self.supabase:
            return transactions
        
        try:
            # Get bank transactions (transfers, deposits)
            bank_txns = self.supabase.table('bank_transactions') \
                .select('*') \
                .eq('user_id', chat_id) \
                .gte('created_at', start_date.isoformat()) \
                .lte('created_at', end_date.isoformat()) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
            
            for txn in bank_txns.data or []:
                transactions.append({
                    'type': 'bank',
                    'category': txn.get('transaction_type', 'transfer'),
                    'amount': float(txn.get('amount', 0)),
                    'description': txn.get('narration', 'Bank transaction'),
                    'recipient': txn.get('recipient_name', 'N/A'),
                    'bank': txn.get('bank_name', 'N/A'),
                    'reference': txn.get('transaction_reference', ''),
                    'date': txn.get('created_at', ''),
                    'status': txn.get('status', 'completed')
                })
            
            # Get crypto transactions
            crypto_txns = self.supabase.table('crypto_transactions') \
                .select('*') \
                .eq('user_id', chat_id) \
                .gte('created_at', start_date.isoformat()) \
                .lte('created_at', end_date.isoformat()) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
            
            for txn in crypto_txns.data or []:
                transactions.append({
                    'type': 'crypto',
                    'category': 'crypto_deposit',
                    'amount': float(txn.get('amount_naira', 0)),
                    'description': f"{txn.get('crypto_type', 'Crypto')} deposit",
                    'crypto_amount': float(txn.get('amount_crypto', 0)),
                    'crypto_type': txn.get('crypto_type', ''),
                    'date': txn.get('created_at', ''),
                    'status': txn.get('status', 'completed')
                })
            
            # Get airtime/data purchases (if tables exist)
            try:
                airtime_txns = self.supabase.table('airtime_sales') \
                    .select('*') \
                    .eq('telegram_chat_id', chat_id) \
                    .gte('created_at', start_date.isoformat()) \
                    .lte('created_at', end_date.isoformat()) \
                    .order('created_at', desc=True) \
                    .limit(limit) \
                    .execute()
                
                for txn in airtime_txns.data or []:
                    transactions.append({
                        'type': 'airtime',
                        'category': 'airtime_purchase',
                        'amount': float(txn.get('amount_sold', 0)),
                        'description': f"{txn.get('network', 'Network')} airtime",
                        'network': txn.get('network', ''),
                        'date': txn.get('created_at', ''),
                        'status': 'completed'
                    })
            except Exception:
                pass  # Table might not exist yet
            
            # Sort all transactions by date
            transactions.sort(key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
        
        return transactions
    
    def generate_transaction_list(self, transactions: List[Dict], 
                                period: str, user_name: str = "there") -> str:
        """Generate a human-like transaction list"""
        if not transactions:
            period_text = {
                "today": "today",
                "week": "this week", 
                "month": "this month",
                "year": "this year",
                "all": "in your account"
            }.get(period, "recently")
            
            return f"Hey {user_name}! I checked your account and you haven't made any transactions {period_text}. " \
                   f"When you start using your wallet for transfers, crypto, or airtime purchases, " \
                   f"I'll keep track of everything for you! 📊"
        
        # Generate header
        period_text = {
            "today": "Today's",
            "week": "This Week's", 
            "month": "This Month's",
            "year": "This Year's",
            "all": "Complete"
        }.get(period, "Recent")
        
        response = f"📊 **{period_text} Transaction History**\n\n"
        
        # Add summary stats
        total_spent = sum(abs(txn['amount']) for txn in transactions if txn['amount'] < 0)
        total_received = sum(txn['amount'] for txn in transactions if txn['amount'] > 0)
        
        response += f"💰 **Quick Summary:**\n"
        response += f"• Total Spent: ₦{total_spent:,.2f}\n"
        response += f"• Total Received: ₦{total_received:,.2f}\n"
        response += f"• Transactions: {len(transactions)}\n\n"
        
        # Group transactions by type
        response += f"📋 **Transaction Details:**\n\n"
        
        for i, txn in enumerate(transactions[:15], 1):  # Show max 15 transactions
            date_obj = datetime.fromisoformat(txn['date'].replace('Z', '+00:00'))
            date_str = date_obj.strftime('%b %d, %I:%M %p')
            
            amount = txn['amount']
            if amount > 0:
                amount_str = f"+₦{amount:,.2f} 📈"
                icon = "💸" if txn['type'] == 'crypto' else "💰"
            else:
                amount_str = f"-₦{abs(amount):,.2f} 📉"
                icon = "🏦" if txn['type'] == 'bank' else "📱"
            
            # Format description based on transaction type
            if txn['type'] == 'bank':
                if amount > 0:
                    desc = f"Bank deposit"
                else:
                    desc = f"Transfer to {txn.get('recipient', 'Account')}"
                    if txn.get('bank') != 'N/A':
                        desc += f" ({txn.get('bank')})"
            elif txn['type'] == 'crypto':
                crypto_amt = txn.get('crypto_amount', 0)
                crypto_type = txn.get('crypto_type', 'Crypto')
                desc = f"{crypto_amt} {crypto_type} → NGN conversion"
            elif txn['type'] == 'airtime':
                network = txn.get('network', 'Network')
                desc = f"{network} airtime purchase"
            else:
                desc = txn.get('description', 'Transaction')
            
            response += f"{icon} **{desc}**\n"
            response += f"   {amount_str} • {date_str}\n"
            if txn.get('reference'):
                response += f"   📝 Ref: {txn['reference'][:15]}...\n"
            response += "\n"
        
        if len(transactions) > 15:
            response += f"📄 *Showing 15 of {len(transactions)} transactions*\n\n"
        
        response += f"💡 **Need something specific?** Just ask me like:\n"
        response += f"• \"How much did I spend on transfers this month?\"\n"
        response += f"• \"Show me my crypto transactions\"\n"
        response += f"• \"Summarize my spending patterns\"\n\n"
        response += f"I'm here to help you understand your finances better! 😊"
        
        return response
    
    def generate_spending_summary(self, transactions: List[Dict], 
                                period: str, user_name: str = "there") -> str:
        """Generate intelligent spending analysis"""
        if not transactions:
            return f"Hey {user_name}! You haven't spent any money {period} - your wallet is staying nice and full! 💰"
        
        # Calculate spending by category
        spending_by_type = {}
        total_spent = 0
        total_received = 0
        
        for txn in transactions:
            amount = txn['amount']
            if amount < 0:  # Outgoing
                total_spent += abs(amount)
                category = txn['type']
                spending_by_type[category] = spending_by_type.get(category, 0) + abs(amount)
            else:  # Incoming
                total_received += amount
        
        period_text = {
            "today": "today",
            "week": "this week",
            "month": "this month", 
            "year": "this year",
            "all": "overall"
        }.get(period, "recently")
        
        response = f"📈 **Your Spending Analysis**\n\n"
        
        if total_spent == 0:
            response += f"Great news! You haven't spent any money {period_text}. "
            response += f"Your financial discipline is on point! 🎯\n\n"
        else:
            response += f"💸 **Total Spent {period_text.title()}:** ₦{total_spent:,.2f}\n"
            response += f"💰 **Total Received:** ₦{total_received:,.2f}\n"
            net = total_received - total_spent
            if net > 0:
                response += f"📊 **Net Change:** +₦{net:,.2f} (You're up! 📈)\n\n"
            else:
                response += f"📊 **Net Change:** ₦{net:,.2f} (You spent more than you received)\n\n"
        
        # Spending breakdown
        if spending_by_type:
            response += f"💳 **Spending Breakdown:**\n"
            for category, amount in sorted(spending_by_type.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_spent) * 100 if total_spent > 0 else 0
                category_name = {
                    'bank': 'Money Transfers',
                    'crypto': 'Crypto Trading', 
                    'airtime': 'Airtime & Data'
                }.get(category, category.title())
                
                response += f"• **{category_name}:** ₦{amount:,.2f} ({percentage:.1f}%)\n"
            
            response += "\n"
        
        # Smart insights
        response += f"🧠 **Smart Insights:**\n"
        
        if total_spent == 0:
            response += f"• You're being very careful with your spending {period_text}\n"
            response += f"• Consider investing some of your savings in crypto or transfers to grow your wealth\n"
        else:
            # Find top spending category
            if spending_by_type:
                top_category = max(spending_by_type.keys(), key=lambda k: spending_by_type[k])
                top_amount = spending_by_type[top_category]
                top_percentage = (top_amount / total_spent) * 100
                
                category_insights = {
                    'bank': f"• Most of your spending ({top_percentage:.1f}%) went to money transfers\n" +
                           f"• You're actively helping others - that's awesome! 💝\n",
                    'crypto': f"• You invested {top_percentage:.1f}% in cryptocurrency\n" +
                             f"• Smart move diversifying your portfolio! 📈\n",
                    'airtime': f"• {top_percentage:.1f}% went to airtime and data\n" +
                              f"• Staying connected is important! 📱\n"
                }
                
                response += category_insights.get(top_category, 
                    f"• Your main spending category was {top_category} ({top_percentage:.1f}%)\n")
        
        # Financial advice
        if period == "month":
            if total_spent > 50000:  # High spender
                response += f"• You're an active user! Consider setting monthly spending goals\n"
            elif total_spent < 5000:  # Conservative spender
                response += f"• You're quite conservative with spending - that's great for savings!\n"
        
        response += f"\n💡 **Want more details?** Ask me:\n"
        response += f"• \"Show me my transfer history this month\"\n"
        response += f"• \"How much crypto did I buy this year?\"\n"
        response += f"• \"Compare my spending to last month\"\n\n"
        response += f"I'm here to help you make smarter financial decisions! 🎯"
        
        return response

# Main function to handle transaction history queries
async def handle_transaction_history_query(chat_id: str, message: str, 
                                         user_data: Dict = None) -> Optional[str]:
    """
    Main function to handle transaction history queries
    
    Returns None if this is not a transaction history query
    Returns response string if it is a transaction history query
    """
    try:
        history_system = IntelligentTransactionHistory()
        
        # Parse the query
        query = history_system.parse_history_query(message)
        if not query:
            return None  # Not a transaction history query
        
        logger.info(f"Transaction history query detected: {query.intent} for {query.time_period}")
        
        # Get date range
        start_date, end_date = history_system.get_date_range(query.time_period)
        
        # Get transactions
        transactions = await history_system.get_user_transactions(chat_id, start_date, end_date)
        
        # Get user's first name for personalization
        user_name = "there"
        if user_data:
            user_name = user_data.get('first_name', 'there')
        
        # Generate response based on query type
        if query.intent == "summary" or query.query_type in ["summary", "analysis"]:
            response = history_system.generate_spending_summary(transactions, query.time_period, user_name)
        else:
            response = history_system.generate_transaction_list(transactions, query.time_period, user_name)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling transaction history query: {e}")
        return "I'm having trouble accessing your transaction history right now. Please try again in a moment! 😅"

# Additional utility functions for advanced queries
async def get_spending_by_category(chat_id: str, period: str = "month") -> Dict:
    """Get spending breakdown by category"""
    history_system = IntelligentTransactionHistory()
    start_date, end_date = history_system.get_date_range(period)
    transactions = await history_system.get_user_transactions(chat_id, start_date, end_date)
    
    spending = {}
    for txn in transactions:
        if txn['amount'] < 0:  # Outgoing
            category = txn['type']
            spending[category] = spending.get(category, 0) + abs(txn['amount'])
    
    return spending

async def get_transaction_trends(chat_id: str, periods: int = 3) -> Dict:
    """Get spending trends over multiple periods"""
    # This would implement trend analysis over multiple months/weeks
    # For now, return basic structure
    return {
        "current_period": 0,
        "previous_period": 0,
        "trend": "stable",
        "percentage_change": 0
    }

# Export main function
__all__ = ['handle_transaction_history_query', 'get_spending_by_category', 'get_transaction_trends']
