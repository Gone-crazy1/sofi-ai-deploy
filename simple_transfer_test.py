#!/usr/bin/env python3
"""
Simple ₦100 Transfer Test for Sofi AI
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function from sofi_money_functions
from sofi_money_functions import sofi_send_money

async def test_100_naira_transfer():
    """Test ₦100 transfer with your Telegram ID"""
    
    # YOUR TELEGRAM ID 
    YOUR_TELEGRAM_ID = "7812930440"
    
    print("🧪 Testing ₦100 Transfer")
    print("=" * 30)
    
    # Transfer details - Using known working account
    amount = 100
    account_number = "9325047112"  # Known working account 
    bank_name = "Wema Bank"  # Valid bank name  
    
    print(f"💸 Amount: ₦{amount}")
    print(f"📱 Account: {account_number}")
    print(f"🏦 Bank: {bank_name}")
    print(f"👤 Your ID: {YOUR_TELEGRAM_ID}")
    print()
    
    try:
        print("🚀 Initiating transfer...")
        
        # Use the main sofi_send_money function
        result = await sofi_send_money(
            telegram_chat_id=YOUR_TELEGRAM_ID,
            recipient_account=account_number,
            recipient_bank=bank_name, 
            amount=amount,
            pin="1998",  # Your PIN
            reason="Test ₦100 transfer from Sofi AI"
        )
        
        print(f"📋 Result: {result}")
        
        if "TRANSFER SUCCESSFUL" in result:
            print("✅ SUCCESS! Check your Telegram for the receipt!")
        elif "requires_pin" in result.lower():
            print("🔐 PIN required - check Telegram for secure link!")
        else:
            print("⚠️ Transfer may need manual completion")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_100_naira_transfer())
