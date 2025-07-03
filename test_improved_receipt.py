#!/usr/bin/env python3
"""
Test the improved receipt format with better styling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.receipt_generator import SofiReceiptGenerator
import asyncio
from main import send_beautiful_receipt

# Test data
test_transaction = {
    'amount': 5000.00,
    'fee': 50.00,
    'total_charged': 5050.00,
    'new_balance': 4950.00,
    'recipient_name': 'John Doe',
    'bank_name': 'Access Bank (Diamond Bank)',
    'account_number': '1234567890',
    'reference': 'TXN123456789',
    'transaction_id': 'SOFI_TXN_001',
    'transaction_time': '20/12/2024 02:30 PM'
}

async def test_improved_receipt():
    """Test the improved receipt format"""
    print("🧪 Testing Improved Receipt Format")
    print("=" * 50)
    
    # Generate telegram receipt
    generator = SofiReceiptGenerator()
    telegram_receipt = generator.generate_telegram_receipt(test_transaction)
    
    print("📱 TELEGRAM RECEIPT:")
    print(telegram_receipt)
    print("\n" + "=" * 50)
    
    # Send to Telegram
    try:
        await send_beautiful_receipt(
            chat_id="5495194750",  # Your Telegram ID as string
            receipt_data=test_transaction,
            transfer_result={'status': 'success', 'message': 'Transfer completed successfully'}
        )
        print("✅ Receipt sent to Telegram successfully!")
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(test_improved_receipt())
