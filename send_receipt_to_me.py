"""
Test sending receipt to the correct Telegram ID (5495194750)
"""
import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.receipt_generator import SofiReceiptGenerator
from main import send_beautiful_receipt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_receipt_to_correct_telegram():
    """Send receipt to the correct Telegram ID: 5495194750"""
    print("\n📱 Sending Receipt to Your Telegram")
    print("=" * 50)
    
    try:
        # Your actual Telegram ID
        your_chat_id = "5495194750"
        
        # Sample receipt data with the correct account number
        receipt_data = {
            'amount': 101.0,
            'fee': 25.0,
            'total_charged': 126.0,
            'new_balance': 874.0,
            'recipient_name': 'THANKGOD OLUWASEUN NDIDI',
            'bank_name': 'OPay Digital Services Limited (OPay)',
            'account_number': '8104965538',  # Correct account number
            'reference': 'TRF_kd5hj6pwjasba52l',
            'transaction_id': 'TXN_67890',
            'transaction_time': '03/07/2025 02:30 PM',
            'narration': 'Test transfer via Sofi AI'
        }
        
        print(f"📧 Sending receipt to Telegram ID: {your_chat_id}")
        print(f"💰 Amount: ₦{receipt_data['amount']:,.2f}")
        print(f"👤 Recipient: {receipt_data['recipient_name']}")
        print(f"📱 Account: {receipt_data['account_number']}")
        
        # Create a mock transfer result
        transfer_result = {
            "success": True,
            "message": "Transfer completed successfully!",
            "receipt_data": receipt_data
        }
        
        # Send the beautiful receipt to your Telegram
        await send_beautiful_receipt(your_chat_id, receipt_data, transfer_result)
        
        print("✅ Receipt sent to your Telegram!")
        print(f"📱 Check your Telegram chat ID: {your_chat_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending receipt: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_receipt_generation_and_display():
    """Generate and display the receipt format"""
    print("\n🧾 Generating Receipt Preview")
    print("=" * 50)
    
    try:
        # Sample receipt data
        receipt_data = {
            'amount': 101.0,
            'fee': 25.0,
            'total_charged': 126.0,
            'new_balance': 874.0,
            'recipient_name': 'THANKGOD OLUWASEUN NDIDI',
            'bank_name': 'OPay Digital Services Limited (OPay)',
            'account_number': '8104965538',
            'reference': 'TRF_kd5hj6pwjasba52l',
            'transaction_id': 'TXN_67890',
            'transaction_time': '03/07/2025 02:30 PM',
            'narration': 'Test transfer via Sofi AI'
        }
        
        receipt_generator = SofiReceiptGenerator()
        
        # Test Telegram receipt
        print("📱 Telegram Receipt Preview:")
        print("-" * 60)
        telegram_receipt = receipt_generator.generate_telegram_receipt(receipt_data)
        print(telegram_receipt)
        print("-" * 60)
        
        # Test HTML receipt
        print("\n📄 Generating HTML receipt...")
        html_receipt = receipt_generator.generate_html_receipt(receipt_data)
        if html_receipt:
            # Save to file for inspection
            with open("your_receipt_preview.html", "w", encoding="utf-8") as f:
                f.write(html_receipt)
            print("✅ HTML receipt saved as 'your_receipt_preview.html'")
            print("📁 Open this file in your browser to see the clean, professional design!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating receipt: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Send receipt to correct Telegram ID and show preview"""
    print("🚀 SENDING RECEIPT TO CORRECT TELEGRAM ID")
    print("=" * 60)
    print(f"📱 Target Telegram ID: 5495194750")
    print("=" * 60)
    
    # Generate and show receipt preview
    preview_result = await test_receipt_generation_and_display()
    
    # Send to your Telegram
    send_result = await send_receipt_to_correct_telegram()
    
    # Summary
    print("\n📊 RESULTS")
    print("=" * 60)
    print(f"📄 Receipt Generation: {'✅ SUCCESS' if preview_result else '❌ FAILED'}")
    print(f"📱 Telegram Sending: {'✅ SUCCESS' if send_result else '❌ FAILED'}")
    
    if send_result:
        print("\n🎉 SUCCESS!")
        print("📱 Check your Telegram (ID: 5495194750) for the receipt!")
        print("🧾 You should see a beautiful, clean receipt like OPay's style")
        print("✅ The receipt includes all transaction details with professional formatting")
    
    return preview_result and send_result

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
