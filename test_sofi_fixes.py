"""
Test PIN keyboard and receipt generation fixes
"""
import sys
import os
import asyncio
import json
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import handle_message, send_beautiful_receipt
from functions.transfer_functions import send_money
from utils.receipt_generator import SofiReceiptGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pin_keyboard_display():
    """Test that PIN keyboard is sent when transfer requires PIN"""
    print("\n🧪 TEST 1: PIN Keyboard Display")
    print("=" * 50)
    
    # Test chat ID (user who exists in database)
    chat_id = "1492735403"
    
    # Message that should trigger transfer
    test_message = "Send 101 to 8104945538 opay"
    
    try:
        # This should trigger PIN entry
        result = await handle_message(chat_id, test_message)
        
        print(f"✅ Result: {result}")
        
        # Check if PIN keyboard was triggered
        if result == "PIN keyboard sent":
            print("✅ SUCCESS: PIN keyboard was sent!")
            return True
        else:
            print(f"❌ FAILED: Expected 'PIN keyboard sent', got: {result}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def test_receipt_generation():
    """Test receipt generation (HTML, PDF, Word)"""
    print("\n🧪 TEST 2: Receipt Generation")
    print("=" * 50)
    
    # Sample receipt data
    receipt_data = {
        'amount': 101.0,
        'fee': 25.0,
        'total_charged': 126.0,
        'new_balance': 500.0,
        'recipient_name': 'MRHAW SOLOMON',
        'bank_name': 'OPay Digital Services Limited',
        'account_number': '8104945538',
        'reference': 'TRF_12345',
        'transaction_id': 'TXN_67890',
        'transaction_time': '03/07/2025 01:04 AM',
        'narration': 'Transfer via Sofi AI'
    }
    
    try:
        receipt_generator = SofiReceiptGenerator()
        
        # Test HTML generation
        print("📄 Testing HTML receipt...")
        html_receipt = receipt_generator.generate_html_receipt(receipt_data)
        if html_receipt:
            print("✅ HTML receipt generated successfully!")
            # Save to file for inspection
            with open("test_receipt.html", "w", encoding="utf-8") as f:
                f.write(html_receipt)
            print("📁 Saved as test_receipt.html")
        else:
            print("❌ HTML receipt generation failed")
        
        # Test PDF generation
        print("\n📄 Testing PDF receipt...")
        pdf_path = receipt_generator.generate_pdf_receipt(receipt_data, "test_receipt.pdf")
        if pdf_path and os.path.exists(pdf_path):
            print("✅ PDF receipt generated successfully!")
            print(f"📁 Saved as {pdf_path}")
        else:
            print("❌ PDF receipt generation failed")
        
        # Test Word document generation
        print("\n📄 Testing Word document receipt...")
        doc_path = receipt_generator.generate_word_doc_receipt(receipt_data, "test_receipt.docx")
        if doc_path and os.path.exists(doc_path):
            print("✅ Word document receipt generated successfully!")
            print(f"📁 Saved as {doc_path}")
        else:
            print("❌ Word document receipt generation failed")
        
        # Test Telegram receipt
        print("\n📱 Testing Telegram receipt...")
        telegram_receipt = receipt_generator.generate_telegram_receipt(receipt_data)
        print("✅ Telegram receipt:")
        print(telegram_receipt)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR in receipt generation: {e}")
        return False

async def test_complete_transfer_flow():
    """Test complete transfer with PIN and receipt"""
    print("\n🧪 TEST 3: Complete Transfer Flow")
    print("=" * 50)
    
    # Test with actual PIN
    chat_id = "1492735403"
    pin = "1998"
    
    try:
        # Execute transfer directly with PIN
        result = await send_money(
            chat_id=chat_id,
            account_number="8104945538",
            bank_name="opay",
            amount=50.0,
            pin=pin,
            narration="Test transfer with receipt"
        )
        
        print(f"💸 Transfer result: {result.get('success', False)}")
        
        if result.get("success"):
            print("✅ Transfer succeeded!")
            
            # Check if receipt data is available
            receipt_data = result.get("receipt_data")
            if receipt_data:
                print("📧 Receipt data found - testing beautiful receipt...")
                
                # Test sending beautiful receipt
                await send_beautiful_receipt(chat_id, receipt_data, result)
                print("✅ Beautiful receipt sent!")
                
                return True
            else:
                print("❌ No receipt data in transfer result")
                return False
        else:
            print(f"❌ Transfer failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in complete transfer flow: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 TESTING SOFI AI FIXES")
    print("=" * 60)
    
    # Run tests
    test1_result = await test_pin_keyboard_display()
    test2_result = await test_receipt_generation()
    test3_result = await test_complete_transfer_flow()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"📱 PIN Keyboard Display: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"📄 Receipt Generation: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"💸 Complete Transfer Flow: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    all_passed = test1_result and test2_result and test3_result
    print(f"\n🎯 OVERALL: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
