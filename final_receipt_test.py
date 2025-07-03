"""
Final test for the improved receipt system
"""

import sys
import os
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import send_beautiful_receipt

async def final_test():
    """Final test with the exact style of OPay receipt"""
    
    # Your Telegram chat ID
    MY_TELEGRAM_ID = "5495194750"
    
    # Receipt data matching the OPay style you showed
    receipt_data = {
        'amount': 101,
        'fee': 25,
        'total_charged': 126,
        'new_balance': 874,
        'recipient_name': 'THANKGOD OLUWASEUN NDIDI',
        'bank_name': 'OPay Digital Services Limited (OPay)',
        'account_number': '8104965538',
        'reference': 'TRF_kd5hj6pwjasba52l',
        'transaction_id': 'TXN_67890',
        'transaction_time': '03/07/2025 02:30 PM',
        'narration': 'Payment to Thankgod'
    }
    
    transfer_result = {
        'status': 'success',
        'message': 'Transfer completed successfully',
        'reference': receipt_data['reference']
    }
    
    print("🎯 Final Test: OPay-Style Receipt")
    print("=" * 50)
    print(f"💰 Amount: ₦{receipt_data['amount']:,}")
    print(f"💸 Fee: ₦{receipt_data['fee']:,}")
    print(f"💵 Total: ₦{receipt_data['total_charged']:,}")
    print(f"💳 New Balance: ₦{receipt_data['new_balance']:,}")
    print(f"👤 Recipient: {receipt_data['recipient_name']}")
    print(f"🏦 Bank: {receipt_data['bank_name']}")
    print(f"📱 Account: {receipt_data['account_number']}")
    print(f"🧾 Reference: {receipt_data['reference']}")
    print(f"🆔 Transaction ID: {receipt_data['transaction_id']}")
    print(f"🕐 Time: {receipt_data['transaction_time']}")
    print("=" * 50)
    
    try:
        await send_beautiful_receipt(MY_TELEGRAM_ID, receipt_data, transfer_result)
        
        print("✅ SUCCESS! Receipt sent with new features:")
        print("   📱 Short text receipt (immediate)")
        print("   📸 Visual image receipt (OPay-style)")
        print("   💦 Sofi AI watermark")
        print("   🎨 Clean, professional design")
        print("   📲 Displays directly in chat (no clicking files!)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Check your Telegram! You should see:")
    print("   1. A short, clean text receipt")
    print("   2. A beautiful image receipt that displays immediately")
    print("   3. No need to click files - it shows directly!")

if __name__ == "__main__":
    asyncio.run(final_test())
