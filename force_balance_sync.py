"""
🔧 BALANCE SYNC FIX

This script fixes the balance sync issue where users have funds but Sofi shows 0.00
"""

import asyncio
import logging
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.permanent_memory import get_user_balance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def force_balance_sync():
    """Force sync all user balances across tables"""
    try:
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        print("🔄 Starting balance sync...")
        
        # Get all users
        users_result = client.table("users").select("id, telegram_chat_id, wallet_balance").execute()
        
        total_synced = 0
        for user in users_result.data:
            user_id = user["id"]
            telegram_chat_id = user.get("telegram_chat_id")
            current_wallet_balance = user.get("wallet_balance", 0)
            
            # Get real balance using secure method
            balance_info = await get_user_balance(user_id)
            
            if balance_info["success"]:
                real_balance = balance_info["balance"]
                
                if abs(real_balance - current_wallet_balance) > 0.01:  # More than 1 kobo difference
                    # Update wallet_balance in users table
                    client.table("users").update({
                        "wallet_balance": real_balance
                    }).eq("id", user_id).execute()
                    
                    # Also update virtual_accounts table if exists
                    va_result = client.table("virtual_accounts").select("id").eq("user_id", user_id).execute()
                    if va_result.data:
                        client.table("virtual_accounts").update({
                            "balance": real_balance
                        }).eq("user_id", user_id).execute()
                    
                    print(f"✅ Synced user {telegram_chat_id}: {current_wallet_balance} → {real_balance}")
                    total_synced += 1
                else:
                    print(f"✓ User {telegram_chat_id}: Already synced ({real_balance})")
            else:
                print(f"❌ Failed to get balance for user {telegram_chat_id}: {balance_info.get('error')}")
        
        print(f"\n🎉 Balance sync complete! Synced {total_synced} users")
        
    except Exception as e:
        logger.error(f"Error in force_balance_sync: {e}")

if __name__ == "__main__":
    asyncio.run(force_balance_sync())
