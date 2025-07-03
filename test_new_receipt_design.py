"""
Test the new OPay-style receipt design
"""
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.receipt_generator import SofiReceiptGenerator

async def test_new_receipt_design():
    """Test the new OPay-style receipt design"""
    print("\n🎨 Testing New Sofi AI Receipt Design")
    print("=" * 50)
    
    # Sample receipt data like the OPay example
    receipt_data = {
        'amount': 1000.00,
        'fee': 25.00,
        'total_charged': 1025.00,
        'new_balance': 2475.00,
        'recipient_name': 'MRHAW SOLOMON',
        'bank_name': 'OPay Digital Services Limited',
        'account_number': '8104965538',
        'reference': 'TRF_sofi_ai_20250703_001',
        'transaction_id': 'SOFI250702021001358973336936',
        'transaction_time': 'Jul 3rd, 2025 06:38:03',
        'narration': 'Transfer via Sofi AI'
    }
    
    try:
        receipt_generator = SofiReceiptGenerator()
        
        # Generate HTML receipt
        print("🎨 Generating new OPay-style HTML receipt...")
        html_receipt = receipt_generator.generate_html_receipt(receipt_data)
        
        if html_receipt:
            # Save HTML file
            html_filename = "sofi_receipt_new_design.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_receipt)
            
            print(f"✅ New design HTML receipt saved as: {html_filename}")
            print("📱 Open this file in your browser to see the new design!")
            
            # Also test Telegram format
            print("\n📱 Telegram receipt preview:")
            telegram_receipt = receipt_generator.generate_telegram_receipt(receipt_data)
            print("-" * 40)
            print(telegram_receipt)
            print("-" * 40)
            
            # Test PDF generation (if available)
            try:
                pdf_path = receipt_generator.generate_pdf_receipt(receipt_data, "sofi_receipt_new_design.pdf")
                if pdf_path:
                    print(f"✅ PDF receipt saved as: {pdf_path}")
                else:
                    print("⚠️ PDF generation not available (missing system libraries)")
            except Exception as pdf_error:
                print(f"⚠️ PDF generation failed: {pdf_error}")
            
            return True
        else:
            print("❌ HTML receipt generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing receipt design: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test the new receipt design"""
    print("🎨 TESTING NEW SOFI AI RECEIPT DESIGN")
    print("=" * 60)
    print("📋 Based on OPay receipt style with Sofi AI branding")
    print("=" * 60)
    
    success = await test_new_receipt_design()
    
    if success:
        print("\n🎉 NEW RECEIPT DESIGN FEATURES:")
        print("✅ Clean white background (no dark colors)")
        print("✅ Professional OPay-style layout")
        print("✅ Sofi AI branding with green accents")
        print("✅ Clear transaction amount display")
        print("✅ Organized sections for all details")
        print("✅ Professional typography")
        print("✅ Mobile-friendly responsive design")
        print("\n📁 Check the generated HTML file to see the design!")
    else:
        print("\n❌ Receipt design test failed")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n{'🎉 SUCCESS' if result else '❌ FAILED'}")
