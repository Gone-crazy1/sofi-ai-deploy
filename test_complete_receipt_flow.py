"""
Complete end-to-end test with image receipt
"""

import sys
import os
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main sending function
from main import send_beautiful_receipt

async def test_complete_receipt_flow():
    """Test complete receipt flow with image generation"""
    
    # Your Telegram chat ID
    MY_TELEGRAM_ID = "5495194750"
    
    # Sample receipt data (similar to what would be generated from a real transfer)
    receipt_data = {
        'amount': 25000,
        'fee': 75,
        'total_charged': 25075,
        'new_balance': 45000,
        'recipient_name': 'Jane Smith',
        'bank_name': 'Zenith Bank (ZEN)',
        'account_number': '9876543210',
        'reference': 'SOFI' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'transaction_id': 'TXN' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'transaction_time': datetime.now().strftime('%d/%m/%Y %I:%M %p'),
        'narration': 'Payment to Jane Smith'
    }
    
    # Sample transfer result (would come from the actual transfer function)
    transfer_result = {
        'status': 'success',
        'message': 'Transfer completed successfully',
        'reference': receipt_data['reference']
    }
    
    print("🚀 Testing Complete Sofi AI Receipt Flow...")
    print("=" * 60)
    print(f"💰 Amount: ₦{receipt_data['amount']:,.0f}")
    print(f"👤 Recipient: {receipt_data['recipient_name']}")
    print(f"🏦 Bank: {receipt_data['bank_name']}")
    print(f"📱 Account: {receipt_data['account_number']}")
    print("=" * 60)
    
    try:
        # This is the same function called during real transfers
        await send_beautiful_receipt(MY_TELEGRAM_ID, receipt_data, transfer_result)
        
        print("✅ Complete receipt flow executed successfully!")
        print("📱 Check your Telegram for:")
        print("   1. Text receipt (immediate)")
        print("   2. Image receipt (visual, OPay-style)")
        print("   3. Fallback documents (if needed)")
        
    except Exception as e:
        print(f"❌ Error in receipt flow: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test completed! Check your Telegram messages.")

if __name__ == "__main__":
    asyncio.run(test_complete_receipt_flow())
