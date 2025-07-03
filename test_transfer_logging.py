"""
Test real transfer with database logging verification
"""

import os
import sys
import asyncio
from datetime import datetime
from supabase import create_client

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from functions.transfer_functions import send_money

async def test_transfer_and_logging():
    """Test a real transfer and verify database logging"""
    
    try:
        # Create Supabase client to check before/after
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        print("🧪 Testing Transfer and Database Logging")
        print("=" * 60)
        
        # Check user balance before
        print("\n📊 BEFORE TRANSFER:")
        chat_id = "5495194750"  # Your Telegram ID
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", chat_id).execute()
        
        if user_result.data:
            user_data = user_result.data[0]
            current_balance = user_data.get("wallet_balance", 0)
            print(f"   👤 User found: {user_data.get('first_name', 'Unknown')}")
            print(f"   💰 Current balance: ₦{current_balance:,.2f}")
        else:
            print("   ❌ User not found in database")
            return False
        
        # Check transaction count before
        before_count = len(supabase.table("bank_transactions").select("*").execute().data)
        print(f"   📋 Transactions in DB before: {before_count}")
        
        # Test transfer data
        transfer_data = {
            "chat_id": chat_id,
            "amount": 100.0,  # Small amount for testing
            "account_number": "8104965538",
            "bank_name": "opay",  # Use valid bank code format
            "narration": "Test transfer for database logging",
            "pin": "1234"  # Test PIN
        }
        
        print(f"\n💸 EXECUTING TRANSFER:")
        print(f"   Amount: ₦{transfer_data['amount']:,.2f}")
        print(f"   To: {transfer_data['account_number']} ({transfer_data['bank_name']})")
        print(f"   From: {chat_id}")
        
        # Execute transfer
        result = await send_money(**transfer_data)
        
        print(f"\n📤 TRANSFER RESULT:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
        
        # Check database after transfer
        print(f"\n📊 AFTER TRANSFER:")
        
        # Check user balance after
        user_result_after = supabase.table("users").select("*").eq("telegram_chat_id", chat_id).execute()
        if user_result_after.data:
            new_balance = user_result_after.data[0].get("wallet_balance", 0)
            print(f"   💰 New balance: ₦{new_balance:,.2f}")
            print(f"   📉 Balance change: ₦{new_balance - current_balance:,.2f}")
        
        # Check transaction count after
        after_count = len(supabase.table("bank_transactions").select("*").execute().data)
        print(f"   📋 Transactions in DB after: {after_count}")
        
        if after_count > before_count:
            print("   ✅ Transaction logged to database!")
            
            # Get the latest transaction
            latest_txn = supabase.table("bank_transactions").select("*").order("created_at", desc=True).limit(1).execute()
            if latest_txn.data:
                txn = latest_txn.data[0]
                print(f"   📄 Latest transaction:")
                print(f"      ID: {txn.get('id', 'N/A')}")
                print(f"      Amount: ₦{txn.get('amount', 0):,.2f}")
                print(f"      Status: {txn.get('status', 'Unknown')}")
                print(f"      Reference: {txn.get('reference', 'N/A')}")
                print(f"      Created: {txn.get('created_at', 'N/A')}")
        else:
            print("   ❌ Transaction NOT logged to database!")
            print("   🔧 Need to investigate database logging issue")
        
        print("\n" + "=" * 60)
        
        if result.get('success'):
            print("✅ Transfer executed successfully")
            if after_count > before_count:
                print("✅ Database logging working")
            else:
                print("❌ Database logging FAILED")
        else:
            print("❌ Transfer failed")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_transfer_and_logging())
