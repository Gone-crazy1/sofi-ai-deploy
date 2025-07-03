#!/usr/bin/env python3
"""
Make a real ₦100 transfer to OPay account to test receipt system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from functions.balance_functions import get_balance
from functions.transfer_functions import send_money
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def make_real_transfer_to_opay():
    """Make a real ₦100 transfer to OPay account"""
    print("🎯 REAL TRANSFER TO OPAY - RECEIPT TEST")
    print("=" * 50)
    
    # Check current balance first
    try:
        current_balance = await get_balance()
        print(f"💰 Current Balance: ₦{current_balance:,.2f}")
        
        if current_balance < 150:  # Need at least ₦150 for ₦100 transfer + fees
            print("❌ Insufficient balance for ₦100 transfer (need ~₦150 with fees)")
            return
            
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return
    
    # Transfer details for OPay
    print("\n🏦 TRANSFER DETAILS:")
    print("=" * 30)
    print("💰 Amount: ₦100")
    print("🏦 Bank: OPay Digital Services Limited")
    print("📱 Account: [Your OPay Account Number]")
    print("👤 Recipient: [Your Name]")
    print("💬 Narration: Testing Sofi AI receipt system")
    print("📧 Chat ID: 5495194750 (Your Telegram)")
    
    # Confirm transfer
    confirm = input("\n⚠️  This is a REAL transfer of ₦100! Continue? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("❌ Transfer cancelled")
        return
    
    print("\n⏳ Processing real transfer...")
    
    try:
        # Make the actual transfer
        # Note: You'll need to provide your actual OPay account details
        result = await send_money(
            chat_id="5495194750",  # Your Telegram ID
            amount=100.0,  # ₦100 transfer
            narration="Testing Sofi AI receipt system - Real transfer",
            # You'll need to add recipient details here - 
            # either through the bot interface or provide them directly
        )
        
        print("\n📋 TRANSFER RESULT:")
        print("=" * 30)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('status') == 'success':
            print("✅ Transfer completed successfully!")
            print("🧾 Check your Telegram for the beautiful receipt!")
            print("📊 Transaction should be logged in Supabase")
            print("💳 You should receive the money in your OPay account")
        else:
            print("❌ Transfer failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Transfer error: {e}")
        print("💡 Note: You may need to provide recipient details through the bot interface")

if __name__ == "__main__":
    print("🚨 WARNING: This will make a REAL money transfer!")
    print("🔔 Make sure you have your OPay account details ready")
    print()
    
    asyncio.run(make_real_transfer_to_opay())
