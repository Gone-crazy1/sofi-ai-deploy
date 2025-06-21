"""
📊 ADMIN DASHBOARD BACKEND CONNECTOR
===================================

Connects Sofi AI to live Supabase data for real-time admin stats
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AdminDashboardConnector:
    """Live admin dashboard data connector"""
    
    def __init__(self):
        """Initialize Supabase connection"""
        try:
            self.supabase: Client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_KEY")
            )
            logger.info("✅ Admin Dashboard connected to Supabase")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            self.supabase = None
    
    async def get_today_deposits(self) -> Dict:
        """Get today's deposit statistics"""
        try:
            today = datetime.now().date()
            
            # Query virtual account funding (deposits)
            response = self.supabase.table("bank_transactions").select(
                "amount, transaction_type, created_at, status"
            ).eq("transaction_type", "deposit").gte(
                "created_at", f"{today}T00:00:00"
            ).lt(
                "created_at", f"{today}T23:59:59"
            ).eq("status", "completed").execute()
            
            if response.data:
                deposits = response.data
                total_amount = sum(float(d['amount']) for d in deposits)
                total_count = len(deposits)
                
                return {
                    "success": True,
                    "count": total_count,
                    "total_amount": total_amount,
                    "deposits": deposits
                }
            else:
                return {
                    "success": True,
                    "count": 0,
                    "total_amount": 0.0,
                    "deposits": []
                }
                
        except Exception as e:
            logger.error(f"Error fetching today's deposits: {e}")
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "total_amount": 0.0
            }
    
    async def get_today_transfers(self) -> Dict:
        """Get today's transfer statistics"""
        try:
            today = datetime.now().date()
            
            response = self.supabase.table("bank_transactions").select(
                "amount, transaction_type, created_at, status, transaction_fee"
            ).eq("transaction_type", "transfer").gte(
                "created_at", f"{today}T00:00:00"
            ).lt(
                "created_at", f"{today}T23:59:59"
            ).eq("status", "completed").execute()
            
            if response.data:
                transfers = response.data
                total_amount = sum(float(t['amount']) for t in transfers)
                total_fees = sum(float(t.get('transaction_fee', 0)) for t in transfers)
                total_count = len(transfers)
                
                return {
                    "success": True,
                    "count": total_count,
                    "total_amount": total_amount,
                    "total_fees": total_fees,
                    "transfers": transfers
                }
            else:
                return {
                    "success": True,
                    "count": 0,
                    "total_amount": 0.0,
                    "total_fees": 0.0,
                    "transfers": []
                }
                
        except Exception as e:
            logger.error(f"Error fetching today's transfers: {e}")
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "total_amount": 0.0
            }
    
    async def get_today_airtime_purchases(self) -> Dict:
        """Get today's airtime purchases"""
        try:
            today = datetime.now().date()
            
            response = self.supabase.table("bank_transactions").select(
                "amount, transaction_type, created_at, status, transaction_fee"
            ).eq("transaction_type", "airtime").gte(
                "created_at", f"{today}T00:00:00"
            ).lt(
                "created_at", f"{today}T23:59:59"
            ).eq("status", "completed").execute()
            
            if response.data:
                airtime = response.data
                total_amount = sum(float(a['amount']) for a in airtime)
                total_fees = sum(float(a.get('transaction_fee', 0)) for a in airtime)
                total_count = len(airtime)
                
                return {
                    "success": True,
                    "count": total_count,
                    "total_amount": total_amount,
                    "total_fees": total_fees,
                    "airtime": airtime
                }
            else:
                return {
                    "success": True,
                    "count": 0,
                    "total_amount": 0.0,
                    "total_fees": 0.0,
                    "airtime": []
                }
                
        except Exception as e:
            logger.error(f"Error fetching today's airtime: {e}")
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "total_amount": 0.0
            }
    
    async def get_total_active_users(self) -> Dict:
        """Get total active users"""
        try:
            response = self.supabase.table("users").select("id").execute()
            
            total_users = len(response.data) if response.data else 0
            
            return {
                "success": True,
                "total_users": total_users
            }
            
        except Exception as e:
            logger.error(f"Error fetching user count: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_users": 0
            }
    
    async def get_today_profit(self) -> Dict:
        """Calculate today's profit from fees"""
        try:
            deposits = await self.get_today_deposits()
            transfers = await self.get_today_transfers()
            airtime = await self.get_today_airtime_purchases()
            
            # Calculate profit (from fees)
            transfer_profit = transfers.get('total_fees', 0.0)
            airtime_profit = airtime.get('total_fees', 0.0)
            
            # Add any other profit sources
            total_profit = transfer_profit + airtime_profit
            
            return {
                "success": True,
                "total_profit": total_profit,
                "transfer_profit": transfer_profit,
                "airtime_profit": airtime_profit,
                "breakdown": {
                    "deposits": deposits.get('count', 0),
                    "transfers": transfers.get('count', 0),
                    "airtime": airtime.get('count', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating profit: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_profit": 0.0
            }
    
    async def generate_admin_dashboard_summary(self) -> str:
        """Generate complete admin dashboard summary"""
        try:
            # Get all stats
            deposits = await self.get_today_deposits()
            transfers = await self.get_today_transfers()
            airtime = await self.get_today_airtime_purchases()
            users = await self.get_total_active_users()
            profit = await self.get_today_profit()
            
            # Format today's date
            today = datetime.now().strftime("%d %B %Y")
            
            # Build admin summary
            summary = f"""📊 **SOFI AI ADMIN DASHBOARD**
📅 **{today}**

💰 **TODAY'S BUSINESS SUMMARY:**
┌─────────────────────────────────
│ 🟢 **Deposits:** {deposits['count']} users
│ 💸 **Amount:** ₦{deposits['total_amount']:,.2f}
│
│ 🔄 **Transfers:** {transfers['count']} transactions  
│ 💸 **Amount:** ₦{transfers['total_amount']:,.2f}
│ 💵 **Fees:** ₦{transfers.get('total_fees', 0):,.2f}
│
│ 📱 **Airtime:** {airtime['count']} purchases
│ 💸 **Amount:** ₦{airtime['total_amount']:,.2f}
│ 💵 **Fees:** ₦{airtime.get('total_fees', 0):,.2f}
└─────────────────────────────────

🎯 **PROFIT TODAY:** ₦{profit['total_profit']:,.2f}

👥 **TOTAL USERS:** {users['total_users']} registered

🔥 **QUICK ACTIONS:**
• `/admin_withdrawals` - Check pending withdrawals
• `/admin_users` - View recent user activity  
• `/admin_transactions` - Recent transactions
• `/admin_profit_week` - Weekly profit report"""

            return summary
            
        except Exception as e:
            logger.error(f"Error generating admin summary: {e}")
            return f"❌ **Error generating dashboard:** {str(e)}"

# Global instance
admin_dashboard = AdminDashboardConnector()
