"""
💰 ADMIN PROFIT WITHDRAWAL SYSTEM

This module handles:
1. Profit calculation and tracking
2. Virtual withdrawal processing 
3. Opay completion tracking
4. Admin profit reports and reminders
"""

import os
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from supabase import create_client

logger = logging.getLogger(__name__)

class AdminProfitManager:
    """Manages admin profit tracking and withdrawal system"""
    
    def __init__(self):
        """Initialize with Supabase connection and admin security"""
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        )
        # Load authorized admin chat IDs for security validation
        self.authorized_admins = self._load_admin_chat_ids()
    
    def _load_admin_chat_ids(self):
        """Load authorized admin chat IDs"""
        try:
            admin_ids_str = os.getenv("ADMIN_CHAT_IDS", "")
            if admin_ids_str and admin_ids_str != "YOUR_TELEGRAM_CHAT_ID":
                return [id.strip() for id in admin_ids_str.split(",") if id.strip()]
            return []
        except Exception as e:
            logger.error(f"Error loading admin IDs: {e}")
            return []
    
    def _validate_admin_access(self, admin_id: str = None) -> bool:
        """Validate admin access for sensitive operations"""
        if not admin_id:
            return True  # For internal system operations
        
        if not self.authorized_admins:
            logger.warning("🚨 Admin access denied: No authorized admins configured")
            return False
        
        is_authorized = str(admin_id) in self.authorized_admins
        if not is_authorized:
            logger.warning(f"🚨 Unauthorized admin access attempt: {admin_id}")
        
        return is_authorized
    
    async def record_profit(self, transaction_type: str, base_amount: float, 
                          fee_amount: float, profit_amount: float, 
                          transaction_id: str = None, user_id: str = None, 
                          metadata: Dict = None) -> bool:
        """Record a new profit transaction"""
        try:
            profit_data = {
                'transaction_type': transaction_type,
                'base_amount': base_amount,
                'fee_amount': fee_amount,
                'profit_amount': profit_amount,
                'transaction_id': transaction_id,
                'user_id': user_id,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('admin_profits').insert(profit_data).execute()
            logger.info(f"Profit recorded: {profit_amount} from {transaction_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording profit: {e}")
            return False
    
    async def get_profit_summary(self) -> Dict:
        """Get comprehensive profit summary"""
        try:
            # Get profit summary from view
            summary_result = self.supabase.table('admin_profit_summary').select('*').execute()
            
            if not summary_result.data:
                return {
                    'total_profit_earned': 0.0,
                    'total_withdrawn': 0.0,
                    'available_profit': 0.0,
                    'total_profit_transactions': 0,
                    'last_profit_date': None
                }
            
            summary = summary_result.data[0]
            
            # Get pending withdrawals
            pending_result = self.supabase.table('admin_withdrawals')\
                .select('*')\
                .eq('status', 'pending')\
                .execute()
            
            # Get recent profit breakdown
            breakdown_result = self.supabase.table('admin_profits')\
                .select('transaction_type, profit_amount')\
                .gte('created_at', (datetime.now() - timedelta(days=30)).isoformat())\
                .execute()
            
            # Calculate breakdown by type
            profit_by_type = {}
            for record in breakdown_result.data:
                trans_type = record['transaction_type']
                profit_by_type[trans_type] = profit_by_type.get(trans_type, 0) + float(record['profit_amount'])
            
            return {
                'total_profit_earned': float(summary.get('total_profit_earned', 0)),
                'total_withdrawn': float(summary.get('total_withdrawn', 0)),
                'available_profit': float(summary.get('available_profit', 0)),
                'total_profit_transactions': summary.get('total_profit_transactions', 0),
                'last_profit_date': summary.get('last_profit_date'),
                'pending_withdrawals': pending_result.data,
                'profit_breakdown_30days': profit_by_type
            }
        except Exception as e:
            logger.error(f"Error getting profit summary: {e}")
            return {'error': str(e)}
    
    async def process_virtual_withdrawal(self, amount: float, admin_id: str = "admin") -> Dict:
        """Process a virtual profit withdrawal with admin validation"""
        try:
            # SECURITY: Validate admin access for withdrawals
            if not self._validate_admin_access(admin_id):
                return {
                    'success': False, 
                    'error': '🚨 Access denied: Unauthorized admin access attempt'
                }
            
            # Get current profit balance
            summary = await self.get_profit_summary()
            available_profit = summary.get('available_profit', 0)
            
            # Validate withdrawal amount
            if amount <= 0:
                return {'success': False, 'error': 'Withdrawal amount must be greater than 0'}
            
            if amount > available_profit:
                return {
                    'success': False, 
                    'error': f'Insufficient profit balance. Available: ₦{available_profit:,.2f}, Requested: ₦{amount:,.2f}'
                }
            
            # Record the withdrawal
            withdrawal_data = {
                'withdrawal_amount': amount,
                'profit_balance_before': available_profit,
                'profit_balance_after': available_profit - amount,
                'withdrawal_date': datetime.now().isoformat(),
                'status': 'pending',
                'opay_completed': False,
                'created_by': admin_id,
                'notes': f'Virtual withdrawal processed via Sofi AI on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'
            }
            
            result = self.supabase.table('admin_withdrawals').insert(withdrawal_data).execute()
            
            if result.data:
                withdrawal_id = result.data[0]['id']
                logger.info(f"Virtual withdrawal processed: ₦{amount:,.2f}")
                
                return {
                    'success': True,
                    'withdrawal_id': withdrawal_id,
                    'amount': amount,
                    'balance_before': available_profit,
                    'balance_after': available_profit - amount,
                    'message': f"Boss, I've deducted ₦{amount:,.2f} from your profit records. Don't forget to complete the withdrawal manually via your Opay Merchant App or Dashboard."
                }
            else:
                return {'success': False, 'error': 'Failed to record withdrawal'}
                
        except Exception as e:
            logger.error(f"Error processing virtual withdrawal: {e}")
            return {'success': False, 'error': str(e)}
    
    async def mark_opay_completion(self, withdrawal_id: int, completed: bool = True) -> Dict:
        """Mark an Opay withdrawal as completed"""
        try:
            update_data = {
                'opay_completed': completed,
                'opay_completion_date': datetime.now().isoformat() if completed else None,
                'status': 'completed' if completed else 'pending'
            }
            
            result = self.supabase.table('admin_withdrawals')\
                .update(update_data)\
                .eq('id', withdrawal_id)\
                .execute()
            
            if result.data:
                return {'success': True, 'message': f'Withdrawal marked as {"completed" if completed else "pending"}'}
            else:
                return {'success': False, 'error': 'Withdrawal not found'}
                
        except Exception as e:
            logger.error(f"Error updating withdrawal completion: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_pending_withdrawals(self) -> List[Dict]:
        """Get all pending withdrawals that need Opay completion"""
        try:
            result = self.supabase.table('admin_withdrawals')\
                .select('*')\
                .eq('status', 'pending')\
                .order('withdrawal_date', desc=True)\
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting pending withdrawals: {e}")
            return []
    
    async def generate_profit_report(self, days: int = 30) -> str:
        """Generate a comprehensive profit report"""
        try:
            summary = await self.get_profit_summary()
            
            if 'error' in summary:
                return f"❌ Error generating report: {summary['error']}"
            
            # Get recent transactions
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            recent_result = self.supabase.table('admin_profits')\
                .select('*')\
                .gte('created_at', since_date)\
                .order('created_at', desc=True)\
                .execute()
            
            # Build report
            report = f"""
💰 **SOFI AI PROFIT REPORT**
📅 Report Period: Last {days} days
🕒 Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 **PROFIT SUMMARY:**
• Total Profit Earned: ₦{summary['total_profit_earned']:,.2f}
• Total Withdrawn: ₦{summary['total_withdrawn']:,.2f}
• Available Balance: ₦{summary['available_profit']:,.2f}
• Total Transactions: {summary['total_profit_transactions']:,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **PROFIT BREAKDOWN (Last 30 Days):**"""
            
            for trans_type, amount in summary.get('profit_breakdown_30days', {}).items():
                report += f"\n• {trans_type.title()}: ₦{amount:,.2f}"
            
            # Add pending withdrawals info
            pending = summary.get('pending_withdrawals', [])
            if pending:
                report += f"\n\n⏳ **PENDING WITHDRAWALS:**"
                for withdrawal in pending:
                    date = datetime.fromisoformat(withdrawal['withdrawal_date']).strftime("%b %d, %Y")
                    report += f"\n• ₦{withdrawal['withdrawal_amount']:,.2f} - {date}"
                    if not withdrawal['opay_completed']:
                        report += " (Needs Opay completion)"
            
            report += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            report += f"\n✅ Report complete! Your Sofi AI business is tracking {summary['total_profit_transactions']} profit transactions."
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating profit report: {e}")
            return f"❌ Error generating report: {str(e)}"

# Global instance
profit_manager = AdminProfitManager()
