#!/usr/bin/env python3
"""
Test a small real transfer to verify the improved receipt format works in practice
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from functions.transfer_functions import send_money
from functions.balance_functions import get_balance
import asyncio

async def test_real_transfer_with_improved_receipt():
    """Test a small real transfer to see the improved receipt"""
    print("🧪 Testing Real Transfer with Improved Receipt")
    print("=" * 60)
    
    # Check current balance first
    current_balance = await get_balance()
    print(f"💰 Current Balance: ₦{current_balance:,.2f}")
    
    if current_balance < 100:
        print("❌ Insufficient balance for test transfer")
        return
    
    # Test transfer data
    transfer_data = {
        'amount': 50,  # Small test amount
        'account_number': '0690000031',  # Test account 
        'bank_code': '044',  # Access Bank
        'recipient_name': 'FORREST GUMP',  # Test name
        'narration': 'Test improved receipt format',
        'user_id': '5495194750'  # Your Telegram ID
    }
    
    print(f"🎯 Testing transfer of ₦{transfer_data['amount']} to {transfer_data['recipient_name']}")
    print(f"🏦 Bank: Access Bank | Account: {transfer_data['account_number']}")
    print("\n⏳ Processing transfer...")
    
    try:
        # Make the transfer
        result = await send_money(
            chat_id=transfer_data['user_id'],
            amount=transfer_data['amount'],
            narration=transfer_data['narration']
        )
        
        print("\n📋 TRANSFER RESULT:")
        print("=" * 40)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('status') == 'success':
            print("✅ Transfer completed successfully!")
            print("🧾 Check your Telegram for the improved receipt!")
        else:
            print("❌ Transfer failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Transfer error: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_transfer_with_improved_receipt())
