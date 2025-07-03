"""
Manual receipt test to verify the receipt system is working
This will simulate sending a receipt for the successful transfer
"""

import sys
import os
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import send_beautiful_receipt

async def test_manual_receipt():
    """Test sending a receipt manually"""
    
    # Your Telegram chat ID
    MY_TELEGRAM_ID = "5495194750"
    
    print("🧾 Testing Manual Receipt Sending...")
    print("=" * 60)
    
    # Sample receipt data from the successful transfer
    receipt_data = {
        'amount': 100,
        'fee': 20,
        'total_charged': 120,
        'new_balance': 1180,  # 1300 - 120 = 1180
        'recipient_name': 'THANKGOD OLUWASEUN NDIDI',
        'bank_name': 'OPay Digital Services Limited',
        'account_number': '8104965538',
        'reference': 'TRF_4s312ev3sn2ut4yu',
        'transaction_id': '0dd39d6c-4869-4c5f-beea-12963868af95',
        'transaction_time': datetime.now().strftime('%d/%m/%Y %I:%M %p'),
        'narration': 'Test transfer for database logging'
    }
    
    transfer_result = {
        'status': 'success',
        'message': 'Transfer completed successfully',
        'reference': receipt_data['reference']
    }
    
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
    
    try:
        print("\n📤 Sending receipt to Telegram...")
        await send_beautiful_receipt(MY_TELEGRAM_ID, receipt_data, transfer_result)
        
        print("✅ SUCCESS! Receipt sent manually")
        print("📱 Check your Telegram for:")
        print("   1. Short text receipt (immediate)")
        print("   2. Beautiful image receipt (OPay-style)")
        print("   3. Both should display directly in chat!")
        
    except Exception as e:
        print(f"❌ Error sending receipt: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("💡 If you received the receipts, the system is working!")
    print("💡 The issue was likely Render sleep mode during the transfer")

if __name__ == "__main__":
    asyncio.run(test_manual_receipt())
