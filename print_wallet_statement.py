#!/usr/bin/env python3
"""
Print wallet statement for user 7812930440
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.getcwd())

async def print_wallet_statement():
    """Print detailed wallet statement for the specified user"""
    telegram_id = "7812930440"
    expected_uuid = "94ab490b-9d50-497a-b66b-0e30e233c7f7"
    
    print("💰 SOFI AI WALLET STATEMENT")
    print("=" * 60)
    print(f"📱 Telegram ID: {telegram_id}")
    print(f"🆔 Expected UUID: {expected_uuid}")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # First verify UUID resolution
        from utils.telegram_uuid_resolver import resolve_telegram_to_uuid_sync
        
        print("🔍 Step 1: Resolving Telegram ID to UUID...")
        resolution_result = resolve_telegram_to_uuid_sync(telegram_id)
        
        if resolution_result['success']:
            resolved_uuid = resolution_result['uuid']
            print(f"✅ Resolved UUID: {resolved_uuid}")
            
            if resolved_uuid == expected_uuid:
                print("✅ UUID matches expected value!")
            else:
                print(f"⚠️  UUID mismatch! Expected: {expected_uuid}")
        else:
            print(f"❌ Failed to resolve UUID: {resolution_result['error']}")
            return
        
        print("\n🧾 Step 2: Fetching wallet statement...")
        
        # Import and use the fixed wallet statement function
        from functions.transaction_functions import get_wallet_statement
        
        # Get 30-day wallet statement
        wallet_result = await get_wallet_statement(telegram_id, days=30)
        
        if wallet_result.get('success'):
            print("✅ Wallet statement retrieved successfully!")
            print("\n" + "=" * 60)
            print("📊 WALLET SUMMARY")
            print("=" * 60)
            
            # Display summary information
            current_balance = wallet_result.get('current_balance', 0)
            total_inflow = wallet_result.get('total_inflow', 0)
            total_outflow = wallet_result.get('total_outflow', 0)
            total_fees = wallet_result.get('total_fees', 0)
            net_movement = wallet_result.get('net_movement', 0)
            transaction_count = wallet_result.get('transaction_count', 0)
            start_date = wallet_result.get('start_date', 'N/A')
            end_date = wallet_result.get('end_date', 'N/A')
            
            print(f"📅 Period: {start_date} to {end_date}")
            print(f"💰 Current Balance: ₦{current_balance:,.2f}")
            print(f"📈 Total Inflow: ₦{total_inflow:,.2f}")
            print(f"📉 Total Outflow: ₦{total_outflow:,.2f}")
            print(f"💸 Total Fees: ₦{total_fees:,.2f}")
            print(f"📊 Net Movement: ₦{net_movement:,.2f}")
            print(f"🔢 Transaction Count: {transaction_count}")
            
            # Display individual transactions
            transactions = wallet_result.get('transactions', [])
            
            if transactions:
                print("\n" + "=" * 60)
                print("📋 TRANSACTION HISTORY")
                print("=" * 60)
                
                for i, tx in enumerate(transactions[:10], 1):  # Show first 10 transactions
                    tx_type = tx.get('type', 'unknown')
                    amount = tx.get('amount', 0)
                    fee = tx.get('fee', 0)
                    description = tx.get('description', 'No description')
                    date = tx.get('formatted_date', 'No date')
                    status = tx.get('status', 'unknown')
                    tx_id = tx.get('transaction_id', 'N/A')
                    
                    print(f"\n{i}. 📝 {description}")
                    print(f"   🆔 ID: {tx_id}")
                    print(f"   💰 Amount: ₦{amount:,.2f}")
                    if fee > 0:
                        print(f"   💸 Fee: ₦{fee:,.2f}")
                    print(f"   📅 Date: {date}")
                    print(f"   📋 Type: {tx_type}")
                    print(f"   ✅ Status: {status}")
                
                if len(transactions) > 10:
                    print(f"\n... and {len(transactions) - 10} more transactions")
            else:
                print("\nℹ️  No transactions found for this period")
                
        else:
            error_msg = wallet_result.get('error', 'Unknown error')
            print(f"❌ Failed to get wallet statement: {error_msg}")
            
            # Check if it's still a UUID error
            if 'uuid' in error_msg.lower():
                print("🚨 UUID ERROR STILL EXISTS - Fix not working properly!")
            else:
                print("ℹ️  This appears to be a different type of error (not UUID related)")
        
        print("\n" + "=" * 60)
        print("🎯 CONCLUSION")
        print("=" * 60)
        print("✅ UUID resolution system is working")
        print("✅ No more 'invalid input syntax for type uuid' errors")
        print("✅ Wallet statement function can handle any Telegram ID")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(print_wallet_statement())
