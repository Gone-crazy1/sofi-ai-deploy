"""
🏢 SOFI AI ADMIN DASHBOARD & BUSINESS METRICS

This provides comprehensive admin queries to monitor:
1. Total profits from all features
2. New user registrations
3. Feature-specific revenue
4. Transaction volumes
5. Growth metrics
6. User engagement stats
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import logging
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SofiAdminDashboard:
    """Comprehensive admin dashboard for Sofi AI business metrics"""
    
    def __init__(self):
        self.client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    async def get_total_profits(self) -> Dict:
        """Get total profits from all revenue streams"""
        try:
            profits = {
                "transfer_fees": 0.0,
                "airtime_profits": 0.0,
                "crypto_profits": 0.0,
                "data_profits": 0.0,
                "total_profit": 0.0
            }
            
            # Transfer fees from transfer_charges table
            result = self.client.table("transfer_charges").select("fee_charged").eq("status", "completed").execute()
            if result.data:
                profits["transfer_fees"] = sum(float(row.get("fee_charged", 0)) for row in result.data)
            
            # Airtime profits
            result = self.client.table("airtime_transactions").select("profit_amount").eq("status", "success").execute()
            if result.data:
                profits["airtime_profits"] = sum(float(row.get("profit_amount", 0)) for row in result.data)
            
            # Crypto trading profits
            result = self.client.table("crypto_profits").select("profit_amount").execute()
            if result.data:
                profits["crypto_profits"] = sum(float(row.get("profit_amount", 0)) for row in result.data)
            
            # Data purchase profits
            result = self.client.table("data_transactions").select("profit_amount").eq("status", "success").execute()
            if result.data:
                profits["data_profits"] = sum(float(row.get("profit_amount", 0)) for row in result.data)
            
            # Calculate total
            profits["total_profit"] = sum([
                profits["transfer_fees"],
                profits["airtime_profits"], 
                profits["crypto_profits"],
                profits["data_profits"]
            ])
            
            return profits
            
        except Exception as e:
            logger.error(f"Error getting total profits: {e}")
            return {"error": str(e)}
    
    async def get_new_users_count(self, days: int = 30) -> Dict:
        """Get new user registrations for specified period"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get new users
            result = self.client.table("users").select("id, first_name, created_at").gte("created_at", start_date.isoformat()).execute()
            
            new_users = len(result.data) if result.data else 0
            
            # Get total users
            total_result = self.client.table("users").select("id").execute()
            total_users = len(total_result.data) if total_result.data else 0
            
            return {
                "new_users_last_30_days": new_users,
                "total_users": total_users,
                "growth_rate": (new_users / max(total_users - new_users, 1)) * 100,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting new users count: {e}")
            return {"error": str(e)}
    
    async def get_feature_revenue_breakdown(self) -> Dict:
        """Get detailed revenue breakdown by feature"""
        try:
            revenue_breakdown = {}
            
            # Transfer fees breakdown
            result = self.client.table("transfer_charges").select("fee_charged, created_at").eq("status", "completed").execute()
            if result.data:
                transfer_count = len(result.data)
                transfer_revenue = sum(float(row.get("fee_charged", 0)) for row in result.data)
                revenue_breakdown["transfers"] = {
                    "transaction_count": transfer_count,
                    "total_revenue": transfer_revenue,
                    "average_fee": transfer_revenue / max(transfer_count, 1)
                }
            
            # Airtime revenue breakdown
            result = self.client.table("airtime_transactions").select("amount, profit_amount, created_at").eq("status", "success").execute()
            if result.data:
                airtime_count = len(result.data)
                airtime_volume = sum(float(row.get("amount", 0)) for row in result.data)
                airtime_profit = sum(float(row.get("profit_amount", 0)) for row in result.data)
                revenue_breakdown["airtime"] = {
                    "transaction_count": airtime_count,
                    "total_volume": airtime_volume,
                    "total_profit": airtime_profit,
                    "profit_margin": (airtime_profit / max(airtime_volume, 1)) * 100
                }
            
            # Crypto revenue breakdown
            result = self.client.table("crypto_transactions").select("crypto_amount, ngn_amount, profit_amount, created_at").execute()
            if result.data:
                crypto_count = len(result.data)
                crypto_volume = sum(float(row.get("ngn_amount", 0)) for row in result.data)
                crypto_profit = sum(float(row.get("profit_amount", 0)) for row in result.data)
                revenue_breakdown["crypto"] = {
                    "transaction_count": crypto_count,
                    "total_volume_ngn": crypto_volume,
                    "total_profit": crypto_profit,
                    "profit_margin": (crypto_profit / max(crypto_volume, 1)) * 100
                }
            
            # Data purchase revenue breakdown
            result = self.client.table("data_transactions").select("amount, profit_amount, created_at").eq("status", "success").execute()
            if result.data:
                data_count = len(result.data)
                data_volume = sum(float(row.get("amount", 0)) for row in result.data)
                data_profit = sum(float(row.get("profit_amount", 0)) for row in result.data)
                revenue_breakdown["data"] = {
                    "transaction_count": data_count,
                    "total_volume": data_volume,
                    "total_profit": data_profit,
                    "profit_margin": (data_profit / max(data_volume, 1)) * 100
                }
            
            return revenue_breakdown
            
        except Exception as e:
            logger.error(f"Error getting feature revenue breakdown: {e}")
            return {"error": str(e)}
    
    async def get_user_engagement_stats(self) -> Dict:
        """Get user engagement and activity statistics"""
        try:
            stats = {}
            
            # Active users (users with transactions in last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            # Get active users from various transaction tables
            active_users = set()
            
            # From transfers
            result = self.client.table("bank_transactions").select("user_id").gte("created_at", thirty_days_ago).execute()
            if result.data:
                active_users.update(row["user_id"] for row in result.data if row.get("user_id"))
            
            # From airtime
            result = self.client.table("airtime_transactions").select("user_id").gte("created_at", thirty_days_ago).execute()
            if result.data:
                active_users.update(row["user_id"] for row in result.data if row.get("user_id"))
            
            # From crypto
            result = self.client.table("crypto_transactions").select("user_id").gte("created_at", thirty_days_ago).execute()
            if result.data:
                active_users.update(row["user_id"] for row in result.data if row.get("user_id"))
            
            stats["active_users_30_days"] = len(active_users)
            
            # Total users
            result = self.client.table("users").select("id").execute()
            total_users = len(result.data) if result.data else 0
            
            stats["total_users"] = total_users
            stats["engagement_rate"] = (len(active_users) / max(total_users, 1)) * 100
            
            # Average transactions per user
            result = self.client.table("bank_transactions").select("user_id").execute()
            total_transactions = len(result.data) if result.data else 0
            stats["avg_transactions_per_user"] = total_transactions / max(total_users, 1)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user engagement stats: {e}")
            return {"error": str(e)}
    
    async def get_daily_growth_metrics(self, days: int = 7) -> Dict:
        """Get daily growth metrics for the last N days"""
        try:
            daily_metrics = []
            
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                
                day_data = {
                    "date": start_of_day.strftime("%Y-%m-%d"),
                    "new_users": 0,
                    "transactions": 0,
                    "revenue": 0.0
                }
                
                # New users for this day
                result = self.client.table("users").select("id").gte("created_at", start_of_day.isoformat()).lt("created_at", end_of_day.isoformat()).execute()
                day_data["new_users"] = len(result.data) if result.data else 0
                
                # Transactions for this day
                result = self.client.table("bank_transactions").select("id").gte("created_at", start_of_day.isoformat()).lt("created_at", end_of_day.isoformat()).execute()
                day_data["transactions"] = len(result.data) if result.data else 0
                
                # Revenue for this day (transfer fees)
                result = self.client.table("transfer_charges").select("fee_charged").gte("created_at", start_of_day.isoformat()).lt("created_at", end_of_day.isoformat()).execute()
                if result.data:
                    day_data["revenue"] = sum(float(row.get("fee_charged", 0)) for row in result.data)
                
                daily_metrics.append(day_data)
            
            return {"daily_metrics": daily_metrics}
            
        except Exception as e:
            logger.error(f"Error getting daily growth metrics: {e}")
            return {"error": str(e)}
    
    async def generate_admin_report(self) -> str:
        """Generate a comprehensive admin report"""
        try:
            # Get all metrics
            profits = await self.get_total_profits()
            users = await self.get_new_users_count()
            revenue_breakdown = await self.get_feature_revenue_breakdown()
            engagement = await self.get_user_engagement_stats()
            daily_growth = await self.get_daily_growth_metrics()
            
            # Generate report
            report = f"""
🏢 SOFI AI ADMIN DASHBOARD - BUSINESS REPORT
==========================================
📅 Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

💰 TOTAL PROFITS SUMMARY
========================
💸 Transfer Fees: ₦{profits.get('transfer_fees', 0):,.2f}
📱 Airtime Profits: ₦{profits.get('airtime_profits', 0):,.2f}
₿ Crypto Profits: ₦{profits.get('crypto_profits', 0):,.2f}
📊 Data Profits: ₦{profits.get('data_profits', 0):,.2f}
🎯 TOTAL PROFIT: ₦{profits.get('total_profit', 0):,.2f}

👥 USER GROWTH METRICS
======================
📈 New Users (30 days): {users.get('new_users_last_30_days', 0)}
👤 Total Users: {users.get('total_users', 0)}
📊 Growth Rate: {users.get('growth_rate', 0):.2f}%

🚀 USER ENGAGEMENT
==================
🎯 Active Users (30 days): {engagement.get('active_users_30_days', 0)}
📊 Engagement Rate: {engagement.get('engagement_rate', 0):.2f}%
🔄 Avg Transactions/User: {engagement.get('avg_transactions_per_user', 0):.2f}

💼 FEATURE REVENUE BREAKDOWN
============================"""

            # Add feature breakdowns
            for feature, data in revenue_breakdown.items():
                if isinstance(data, dict):
                    report += f"""
📋 {feature.upper()}:
   • Transactions: {data.get('transaction_count', 0):,}
   • Revenue/Profit: ₦{data.get('total_profit', data.get('total_revenue', 0)):,.2f}
   • Volume: ₦{data.get('total_volume', data.get('total_volume_ngn', 0)):,.2f}"""
                    if 'profit_margin' in data:
                        report += f"""
   • Profit Margin: {data.get('profit_margin', 0):.2f}%"""

            report += f"""

📈 DAILY GROWTH (Last 7 Days)
============================="""
            
            for day in daily_growth.get('daily_metrics', []):
                report += f"""
📅 {day['date']}: {day['new_users']} new users, {day['transactions']} transactions, ₦{day['revenue']:,.2f} revenue"""

            report += f"""

🎯 KEY PERFORMANCE INDICATORS
=============================
• Total Revenue: ₦{profits.get('total_profit', 0):,.2f}
• Active User Rate: {engagement.get('engagement_rate', 0):.2f}%
• Growth Rate: {users.get('growth_rate', 0):.2f}%
• Daily Active Users: {engagement.get('active_users_30_days', 0) / 30:.0f}

🏆 BUSINESS HEALTH: {'🟢 EXCELLENT' if profits.get('total_profit', 0) > 100000 else '🟡 GOOD' if profits.get('total_profit', 0) > 50000 else '🔴 NEEDS ATTENTION'}
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating admin report: {e}")
            return f"❌ Error generating report: {e}"

# Create global dashboard instance
admin_dashboard = SofiAdminDashboard()

async def get_admin_business_report():
    """Get comprehensive business report for admin"""
    return await admin_dashboard.generate_admin_report()

async def get_total_profits():
    """Get total profits from all features"""
    return await admin_dashboard.get_total_profits()

async def get_new_users_count(days=30):
    """Get new user count"""
    return await admin_dashboard.get_new_users_count(days)

async def get_feature_revenue():
    """Get revenue breakdown by feature"""
    return await admin_dashboard.get_feature_revenue_breakdown()

def deploy_security_schema():
    """Deploy the security schema to Supabase"""
    try:
        print("🔐 DEPLOYING SECURITY SCHEMA TO SUPABASE...")
        print("=" * 50)
        
        # Read the security schema
        with open("secure_transaction_schema.sql", "r") as f:
            schema_sql = f.read()
        
        print("✅ Security schema loaded")
        print("📋 Schema includes:")
        print("   • pin_attempts table for account security")
        print("   • daily_transaction_limits table")
        print("   • security_audit_log table")
        print("   • balance column for virtual_accounts")
        print("   • Row Level Security policies")
        
        print(f"\n📝 SQL COMMANDS TO RUN IN SUPABASE:")
        print("-" * 40)
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run the following SQL commands:")
        print(f"\n{schema_sql}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying schema: {e}")
        return False

if __name__ == "__main__":
    async def main():
        # Deploy security schema first
        deploy_security_schema()
        
        print("\n" + "="*60)
        print("🏢 GENERATING ADMIN BUSINESS REPORT...")
        print("="*60)
        
        # Generate admin report
        report = await get_admin_business_report()
        print(report)
        
        print("\n" + "="*60)
        print("✅ ADMIN DASHBOARD READY!")
        print("Use the admin functions to monitor your business:")
        print("• await get_admin_business_report()")
        print("• await get_total_profits()")
        print("• await get_new_users_count()")
        print("• await get_feature_revenue()")
        print("="*60)
    
    # Run the admin dashboard
    asyncio.run(main())
