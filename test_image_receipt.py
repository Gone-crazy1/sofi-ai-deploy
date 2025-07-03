"""
Test script to send an image receipt to Telegram
"""

import sys
import os
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the receipt generator and sending functions
from utils.receipt_generator import SofiReceiptGenerator
from main import send_photo, send_reply, TELEGRAM_BOT_TOKEN

def test_image_receipt():
    """Test image receipt generation and sending"""
    
    # Your Telegram chat ID
    MY_TELEGRAM_ID = "5495194750"
    
    # Sample transaction data
    receipt_data = {
        'amount': 15000,
        'fee': 50,
        'total_charged': 15050,
        'new_balance': 25000,
        'recipient_name': 'John Doe',
        'bank_name': 'First Bank Nigeria (FBN)',
        'account_number': '1234567890',
        'reference': 'TXN' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'transaction_id': 'SOFI' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'transaction_time': datetime.now().strftime('%d/%m/%Y %I:%M %p'),
        'narration': 'Transfer to John Doe'
    }
    
    print("🧾 Testing Sofi AI Image Receipt Generation...")
    print("=" * 50)
    
    # Test receipt generator
    generator = SofiReceiptGenerator()
    
    # Generate image receipt
    print("📸 Generating image receipt...")
    image_path = "test_receipt_image.png"
    
    try:
        result = generator.generate_image_receipt(receipt_data, image_path)
        if result and os.path.exists(result):
            print(f"✅ Image receipt generated: {result}")
            
            # Send to Telegram
            print("📤 Sending image receipt to Telegram...")
            success = send_photo(MY_TELEGRAM_ID, result, f"🧾 Test Receipt for ₦{receipt_data['amount']:,.0f}")
            
            if success:
                print("✅ Image receipt sent successfully!")
            else:
                print("❌ Failed to send image receipt")
            
            # Clean up
            try:
                os.remove(result)
                print("🗑️ Cleaned up temporary image file")
            except:
                pass
                
        else:
            print("❌ Failed to generate image receipt")
            
            # Fallback: try HTML receipt
            print("📄 Trying HTML receipt as fallback...")
            html_content = generator.generate_html_receipt(receipt_data)
            if html_content:
                with open("test_receipt.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("✅ HTML receipt saved as test_receipt.html")
                print("🌐 You can open this file in your browser to preview")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔔 Check your Telegram for the receipt!")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    test_image_receipt()
