"""
Check recent transaction records in Supabase database
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client

def check_transaction_records():
    """Check recent transaction records in the database"""
    
    try:
        # Create Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        print("🔍 Checking Supabase Transaction Records...")
        print("=" * 60)
        
        # Check users table
        print("\n👥 USERS TABLE:")
        users_result = supabase.table("users").select("*").limit(5).execute()
        if users_result.data:
            print(f"✅ Found {len(users_result.data)} users")
            for user in users_result.data[:3]:
                chat_id = user.get('telegram_chat_id', 'N/A')
                balance = user.get('wallet_balance', 0)
                name = user.get('first_name', 'Unknown')
                print(f"   👤 {name} (ID: {chat_id}) - Balance: ₦{balance:,.2f}")
        else:
            print("❌ No users found")
        
        # Check bank_transactions table
        print("\n💰 BANK TRANSACTIONS TABLE:")
        try:
            # Get all transactions
            all_transactions = supabase.table("bank_transactions").select("*").order("created_at", desc=True).limit(10).execute()
            
            if all_transactions.data:
                print(f"✅ Found {len(all_transactions.data)} recent transactions:")
                for i, txn in enumerate(all_transactions.data, 1):
                    amount = txn.get('amount', 0)
                    recipient = txn.get('recipient_name', 'Unknown')
                    status = txn.get('status', 'Unknown')
                    created = txn.get('created_at', 'Unknown')
                    sender_id = txn.get('sender_telegram_id', 'Unknown')
                    reference = txn.get('reference', 'N/A')
                    
                    print(f"   {i}. ₦{amount:,.2f} to {recipient[:20]}...")
                    print(f"      Status: {status} | Sender: {sender_id}")
                    print(f"      Reference: {reference}")
                    print(f"      Time: {created}")
                    print()
            else:
                print("❌ No transactions found in bank_transactions table")
                
        except Exception as e:
            print(f"❌ Error querying bank_transactions: {e}")
        
        # Check if table exists and what columns it has
        print("\n📋 CHECKING TABLE SCHEMA:")
        try:
            # Try to get table info
            schema_result = supabase.table("bank_transactions").select("*").limit(1).execute()
            if schema_result.data:
                print("✅ bank_transactions table exists")
                if schema_result.data:
                    columns = list(schema_result.data[0].keys())
                    print(f"   Columns: {', '.join(columns)}")
            else:
                print("⚠️ bank_transactions table exists but is empty")
                
        except Exception as e:
            print(f"❌ Error checking table schema: {e}")
            
        # Check recent activity (last 24 hours)
        print("\n🕐 RECENT ACTIVITY (Last 24 hours):")
        try:
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            recent_transactions = supabase.table("bank_transactions").select("*").gte("created_at", yesterday).execute()
            
            if recent_transactions.data:
                print(f"✅ Found {len(recent_transactions.data)} transactions in last 24 hours")
                for txn in recent_transactions.data:
                    amount = txn.get('amount', 0)
                    status = txn.get('status', 'Unknown')
                    created = txn.get('created_at', 'Unknown')
                    print(f"   ₦{amount:,.2f} - {status} - {created}")
            else:
                print("❌ No transactions in last 24 hours")
                
        except Exception as e:
            print(f"❌ Error checking recent activity: {e}")
            
        # Test connection with a simple query
        print("\n🔗 TESTING DATABASE CONNECTION:")
        try:
            test_result = supabase.table("users").select("count").execute()
            print("✅ Database connection working")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            
        print("\n" + "=" * 60)
        print("📊 Summary:")
        print("   - Check if transfers are actually being sent")
        print("   - Verify Supabase logging is working")
        print("   - Look for any database connection issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_transaction_records()
