"""
Test actual Telegram receipt sending
"""
import sys
import os
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import send_beautiful_receipt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_telegram_receipt_sending():
    """Test that receipts are actually sent to Telegram"""
    print("\n📱 Testing Telegram Receipt Sending")
    print("=" * 50)
    
    # Test chat ID
    chat_id = "1492735403"
    
    # Sample receipt data
    receipt_data = {
        'amount': 101.0,
        'fee': 25.0,
        'total_charged': 126.0,
        'new_balance': 874.0,
        'recipient_name': 'THANKGOD OLUWASEUN NDIDI',
        'bank_name': 'OPay Digital Services Limited',
        'account_number': '8104965538',
        'reference': 'TRF_kd5hj6pwjasba52l',
        'transaction_id': 'TXN_test_' + str(int(datetime.now().timestamp())),
        'transaction_time': 'Jul 3rd, 2025 06:40:03',
        'narration': 'Test transfer'
    }
    
    # Mock transfer result
    transfer_result = {
        'success': True,
        'message': 'Transfer completed successfully'
    }
    
    try:
        print(f"📤 Attempting to send receipt to chat {chat_id}...")
        
        # This should send the receipt to Telegram
        result = await send_beautiful_receipt(chat_id, receipt_data, transfer_result)
        
        if result:
            print("✅ Receipt sending function completed successfully!")
            print("📱 Check your Telegram chat to see if the receipt was received")
            return True
        else:
            print("❌ Receipt sending function failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing receipt sending: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test receipt sending"""
    print("📱 TESTING TELEGRAM RECEIPT DELIVERY")
    print("=" * 60)
    
    success = await test_telegram_receipt_sending()
    
    if success:
        print("\n✅ RECEIPT SENDING TEST COMPLETED")
        print("📱 Check your Telegram chat to confirm receipt delivery")
    else:
        print("\n❌ RECEIPT SENDING TEST FAILED")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
