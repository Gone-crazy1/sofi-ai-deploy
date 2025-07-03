#!/usr/bin/env python3
"""
Test the new OPay-style receipt design
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from utils.receipt_generator import SofiReceiptGenerator

def test_opay_style_receipt():
    """Test the new OPay-style receipt design"""
    print("🧪 Testing new OPay-style receipt design...")
    
    # Sample transaction data
    transaction_data = {
        'amount': 5000.00,
        'fee': 25.00,
        'total_charged': 5025.00,
        'new_balance': 45000.00,
        'recipient_name': 'JOHN DOE ADEBAYO',
        'bank_name': 'GTBank',
        'account_number': '0123456789',
        'reference': 'TXN_20241201_123456',
        'transaction_id': 'SF_2024_001_456789',
        'transaction_time': datetime.now().strftime("%d/%m/%Y %I:%M %p"),
        'narration': 'Transfer to John Doe'
    }
    
    # Initialize receipt generator
    receipt_gen = SofiReceiptGenerator()
    
    # Generate HTML receipt
    html_receipt = receipt_gen.generate_html_receipt(transaction_data)
    
    if html_receipt:
        # Save HTML receipt
        receipt_file = "test_opay_style_receipt.html"
        with open(receipt_file, 'w', encoding='utf-8') as f:
            f.write(html_receipt)
        
        print(f"✅ HTML receipt generated: {receipt_file}")
        
        # Generate Telegram-formatted receipt
        telegram_receipt = receipt_gen.generate_telegram_receipt(transaction_data)
        
        if telegram_receipt:
            print("✅ Telegram receipt generated successfully")
            print("\n📱 Telegram Receipt Preview:")
            print("=" * 50)
            print(telegram_receipt)
            print("=" * 50)
        else:
            print("❌ Failed to generate Telegram receipt")
        
        # Try to generate PDF if possible
        try:
            pdf_file = receipt_gen.generate_pdf_receipt(transaction_data, "test_opay_style_receipt.pdf")
            if pdf_file:
                print(f"✅ PDF receipt generated: {pdf_file}")
            else:
                print("⚠️ PDF generation not available")
        except Exception as e:
            print(f"⚠️ PDF generation failed: {e}")
        
        return True
    else:
        print("❌ Failed to generate HTML receipt")
        return False

if __name__ == "__main__":
    success = test_opay_style_receipt()
    
    if success:
        print("\n🎉 New OPay-style receipt design test completed successfully!")
        print("📄 Check the generated HTML file to see the clean, professional design")
        print("🎨 The receipt now has a white background similar to OPay but with Sofi branding")
    else:
        print("\n❌ Receipt test failed!")
        
    input("\nPress Enter to exit...")
