"""
📊 ENHANCED TRANSACTION SUMMARIZER FOR SOFI AI
==============================================

Provides intelligent transaction summaries and spending analysis with 2-month lookback capability.
Includes beneficiary spending patterns and smart financial insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from supabase import create_client
import os

logger = logging.getLogger(__name__)

class TransactionSummarizer:
    """Enhanced transaction summarizer with beneficiary insights"""
    
    def __init__(self):
        self.supabase = None
        if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
            self.supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    async def get_2_month_summary(self, chat_id: str, user_data: Dict = None) -> str:
        """Generate a comprehensive 2-month transaction summary"""
        try:
            # Calculate 2 months ago
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)
            
            # Get all transactions for 2 months
            transactions = await self._get_transactions_for_period(chat_id, start_date, end_date)
            
            if not transactions:
                return """📊 **2-Month Transaction Summary**

You haven't made any transactions in the past 2 months. When you start using Sofi for transfers, crypto trading, or airtime purchases, I'll provide detailed insights here!

💡 **Get started with:**
• Money transfers to family & friends
• Cryptocurrency trading
• Airtime & data purchases
• Account balance management"""
            
            # Analyze transactions
            analysis = self._analyze_transactions(transactions)
            
            # Get beneficiary spending patterns
            beneficiary_insights = await self._get_beneficiary_spending_patterns(chat_id, transactions)
            
            # Generate comprehensive report
            summary = self._generate_summary_report(analysis, beneficiary_insights, user_data)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating 2-month summary: {e}")
            return "I'm having trouble accessing your transaction history right now. Please try again in a moment! 😅"
    
    async def _get_transactions_for_period(self, chat_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get all transactions for the specified period"""
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
                .execute()
            
            for txn in bank_txns.data or []:
                transactions.append({
                    'type': 'bank',
                    'category': txn.get('transaction_type', 'transfer'),
                    'amount': float(txn.get('amount', 0)),
                    'description': txn.get('narration', 'Bank transaction'),
                    'recipient': txn.get('recipient_name', 'N/A'),
                    'bank': txn.get('bank_name', 'N/A'),
                    'fee': float(txn.get('fee', 0)),
                    'reference': txn.get('transaction_reference', ''),
                    'date': txn.get('created_at', ''),
                    'status': txn.get('status', 'completed')
                })
            
            # Get crypto transactions if available
            try:
                crypto_txns = self.supabase.table('crypto_transactions') \
                    .select('*') \
                    .eq('user_id', chat_id) \
                    .gte('created_at', start_date.isoformat()) \
                    .lte('created_at', end_date.isoformat()) \
                    .order('created_at', desc=True) \
                    .execute()
                
                for txn in crypto_txns.data or []:
                    transactions.append({
                        'type': 'crypto',
                        'category': 'crypto_trade',
                        'amount': float(txn.get('amount_naira', 0)),
                        'description': f"{txn.get('crypto_type', 'Crypto')} trade",
                        'crypto_amount': float(txn.get('amount_crypto', 0)),
                        'crypto_type': txn.get('crypto_type', ''),
                        'date': txn.get('created_at', ''),
                        'status': txn.get('status', 'completed')
                    })
            except Exception:
                pass  # Crypto table might not exist
            
            # Get airtime transactions if available
            try:
                airtime_txns = self.supabase.table('airtime_sales') \
                    .select('*') \
                    .eq('telegram_chat_id', chat_id) \
                    .gte('created_at', start_date.isoformat()) \
                    .lte('created_at', end_date.isoformat()) \
                    .order('created_at', desc=True) \
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
                pass  # Airtime table might not exist
                
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
        
        return transactions
    
    def _analyze_transactions(self, transactions: List[Dict]) -> Dict:
        """Analyze transactions for patterns and insights"""
        analysis = {
            'total_spent': 0,
            'total_received': 0,
            'total_fees': 0,
            'transaction_count': len(transactions),
            'spending_by_category': {},
            'spending_by_month': {},
            'top_recipients': {},
            'average_transaction': 0,
            'largest_transaction': 0,
            'spending_trend': 'stable'
        }
        
        current_month = datetime.now().strftime('%Y-%m')
        last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')
        
        for txn in transactions:
            amount = txn['amount']
            txn_date = datetime.fromisoformat(txn['date'].replace('Z', '+00:00'))
            month_key = txn_date.strftime('%Y-%m')
            
            # Track spending by month
            if month_key not in analysis['spending_by_month']:
                analysis['spending_by_month'][month_key] = {'spent': 0, 'received': 0, 'count': 0}
            
            if amount < 0:  # Outgoing
                abs_amount = abs(amount)
                analysis['total_spent'] += abs_amount
                analysis['spending_by_month'][month_key]['spent'] += abs_amount
                
                # Track by category
                category = txn['type']
                analysis['spending_by_category'][category] = analysis['spending_by_category'].get(category, 0) + abs_amount
                
                # Track recipients for transfers
                if txn['type'] == 'bank' and txn.get('recipient', 'N/A') != 'N/A':
                    recipient = txn['recipient']
                    analysis['top_recipients'][recipient] = analysis['top_recipients'].get(recipient, 0) + abs_amount
                
                # Track largest transaction
                if abs_amount > analysis['largest_transaction']:
                    analysis['largest_transaction'] = abs_amount
                    
            else:  # Incoming
                analysis['total_received'] += amount
                analysis['spending_by_month'][month_key]['received'] += amount
            
            # Track fees
            analysis['total_fees'] += txn.get('fee', 0)
            analysis['spending_by_month'][month_key]['count'] += 1
        
        # Calculate average transaction
        if analysis['transaction_count'] > 0:
            analysis['average_transaction'] = analysis['total_spent'] / analysis['transaction_count']
        
        # Calculate spending trend
        current_spending = analysis['spending_by_month'].get(current_month, {}).get('spent', 0)
        last_spending = analysis['spending_by_month'].get(last_month, {}).get('spent', 0)
        
        if last_spending > 0:
            change_percent = ((current_spending - last_spending) / last_spending) * 100
            if change_percent > 20:
                analysis['spending_trend'] = 'increasing'
            elif change_percent < -20:
                analysis['spending_trend'] = 'decreasing'
        
        return analysis
    
    async def _get_beneficiary_spending_patterns(self, chat_id: str, transactions: List[Dict]) -> Dict:
        """Analyze spending patterns with saved beneficiaries"""
        beneficiary_patterns = {
            'beneficiary_spending': {},
            'frequent_recipients': [],
            'savings_opportunity': 0
        }
        
        if not self.supabase:
            return beneficiary_patterns
        
        try:
            # Get user's beneficiaries
            user_result = self.supabase.table("users").select("id").eq("telegram_chat_id", chat_id).execute()
            if not user_result.data:
                return beneficiary_patterns
            
            user_id = user_result.data[0]["id"]
            beneficiaries_result = self.supabase.table("beneficiaries").select("*").eq("user_id", user_id).execute()
            beneficiaries = {b['account_number']: b for b in beneficiaries_result.data or []}
            
            # Analyze spending to recipients
            recipient_spending = {}
            unsaved_recipients = {}
            
            for txn in transactions:
                if txn['type'] == 'bank' and txn['amount'] < 0:  # Outgoing transfers
                    recipient = txn.get('recipient', 'Unknown')
                    amount = abs(txn['amount'])
                    
                    if recipient != 'N/A' and recipient != 'Unknown':
                        recipient_spending[recipient] = recipient_spending.get(recipient, 0) + amount
                        
                        # Check if this recipient is not saved as beneficiary
                        # (This is a simple check - in practice you'd match by account number)
                        if not any(b['account_name'].lower() == recipient.lower() for b in beneficiaries.values()):
                            unsaved_recipients[recipient] = unsaved_recipients.get(recipient, 0) + amount
            
            # Calculate potential savings (recipients you send to frequently but haven't saved)
            beneficiary_patterns['savings_opportunity'] = len([r for r, amount in unsaved_recipients.items() if amount > 10000])
            beneficiary_patterns['frequent_recipients'] = sorted(recipient_spending.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Map beneficiary spending
            for account_num, beneficiary in beneficiaries.items():
                beneficiary_name = beneficiary['name']
                spent_to_beneficiary = recipient_spending.get(beneficiary['account_name'], 0)
                if spent_to_beneficiary > 0:
                    beneficiary_patterns['beneficiary_spending'][beneficiary_name] = spent_to_beneficiary
                    
        except Exception as e:
            logger.error(f"Error analyzing beneficiary patterns: {e}")
        
        return beneficiary_patterns
    
    def _generate_summary_report(self, analysis: Dict, beneficiary_insights: Dict, user_data: Dict = None) -> str:
        """Generate comprehensive transaction summary report"""
        user_name = "there"
        if user_data:
            user_name = user_data.get('first_name', user_data.get('full_name', 'there')).split()[0]
        
        report = f"""📊 **2-Month Financial Summary for {user_name.title()}**

💰 **Overall Performance:**
• Total Spent: ₦{analysis['total_spent']:,.2f}
• Total Received: ₦{analysis['total_received']:,.2f}
• Net Movement: ₦{analysis['total_received'] - analysis['total_spent']:,.2f}
• Transaction Count: {analysis['transaction_count']:,}
• Fees Paid: ₦{analysis['total_fees']:,.2f}

"""
        
        # Spending by category
        if analysis['spending_by_category']:
            report += "📈 **Spending Breakdown:**\n"
            for category, amount in sorted(analysis['spending_by_category'].items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / analysis['total_spent']) * 100 if analysis['total_spent'] > 0 else 0
                category_name = {
                    'bank': 'Money Transfers',
                    'crypto': 'Crypto Trading',
                    'airtime': 'Airtime & Data'
                }.get(category, category.title())
                
                report += f"• {category_name}: ₦{amount:,.2f} ({percentage:.1f}%)\n"
            report += "\n"
        
        # Monthly trend
        if len(analysis['spending_by_month']) >= 2:
            report += "📅 **Monthly Trends:**\n"
            for month, data in sorted(analysis['spending_by_month'].items(), reverse=True):
                month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
                report += f"• {month_name}: ₦{data['spent']:,.2f} spent, {data['count']} transactions\n"
            
            trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}[analysis['spending_trend']]
            report += f"• Trend: {trend_emoji} {analysis['spending_trend'].title()}\n\n"
        
        # Top recipients
        if analysis['top_recipients']:
            report += "👥 **Top Recipients:**\n"
            for recipient, amount in sorted(analysis['top_recipients'].items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"• {recipient}: ₦{amount:,.2f}\n"
            report += "\n"
        
        # Beneficiary insights
        if beneficiary_insights['beneficiary_spending']:
            report += "💾 **Beneficiary Spending:**\n"
            for beneficiary_name, amount in sorted(beneficiary_insights['beneficiary_spending'].items(), key=lambda x: x[1], reverse=True):
                report += f"• {beneficiary_name}: ₦{amount:,.2f}\n"
            report += "\n"
        
        # Smart insights
        report += "🧠 **Smart Insights:**\n"
        
        if analysis['total_spent'] == 0:
            report += "• You're maintaining excellent spending discipline!\n"
            report += "• Consider exploring investment opportunities with your savings\n"
        else:
            avg_daily = analysis['total_spent'] / 60
            report += f"• Your daily average spending is ₦{avg_daily:,.2f}\n"
            
            if analysis['largest_transaction'] > 0:
                report += f"• Your largest transaction was ₦{analysis['largest_transaction']:,.2f}\n"
            
            if beneficiary_insights['savings_opportunity'] > 0:
                report += f"• You could save time by adding {beneficiary_insights['savings_opportunity']} frequent recipients as beneficiaries\n"
            
            # Spending efficiency
            if analysis['total_fees'] > 0:
                fee_percentage = (analysis['total_fees'] / analysis['total_spent']) * 100
                report += f"• Transaction fees represent {fee_percentage:.1f}% of your spending\n"
        
        # Recommendations
        report += "\n💡 **Recommendations:**\n"
        
        if beneficiary_insights['frequent_recipients']:
            top_recipient = beneficiary_insights['frequent_recipients'][0][0]
            report += f"• Consider saving '{top_recipient}' as a beneficiary for faster transfers\n"
        
        if analysis['spending_trend'] == 'increasing':
            report += "• Your spending has increased - consider setting monthly budgets\n"
        elif analysis['spending_trend'] == 'decreasing':
            report += "• Great job reducing your spending! Keep up the financial discipline\n"
        
        report += "• Use voice PIN or saved beneficiaries for even faster transactions\n"
        report += "• Check your balance regularly to stay on top of your finances\n"
        
        report += f"\n📱 Need specific details? Just ask:\n"
        report += f"• \"Show my transfers to John this month\"\n"
        report += f"• \"How much did I spend on crypto?\"\n"
        report += f"• \"List my beneficiaries\"\n"
        
        return report

# Global instance
transaction_summarizer = TransactionSummarizer()
