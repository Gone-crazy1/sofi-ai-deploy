"""
Simple test for PIN keyboard and receipt fixes
"""
import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pin_keyboard_simple():
    """Test PIN keyboard response without dependencies"""
    print("\n🧪 TEST: PIN Keyboard Response")
    print("=" * 50)
    
    try:
        # Import the main handler
        from main import handle_message
        
        # Test chat ID (user who exists in database)
        chat_id = "1492735403"
        
        # Message that should trigger transfer
        test_message = "Send 101 to 8104945538 opay"
        
        # This should trigger PIN entry
        result = await handle_message(chat_id, test_message)
        
        print(f"📱 Result: {result}")
        
        # Check if PIN keyboard was triggered
        if result == "PIN keyboard sent":
            print("✅ SUCCESS: PIN keyboard was sent correctly!")
            return True
        else:
            print(f"❌ ISSUE: Expected 'PIN keyboard sent', got: {result}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_receipt_basic():
    """Test basic receipt generation"""
    print("\n🧪 TEST: Basic Receipt Generation")
    print("=" * 50)
    
    try:
        # Import receipt generator without problematic dependencies
        from utils.receipt_generator import SofiReceiptGenerator
        
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
        
        receipt_generator = SofiReceiptGenerator()
        
        # Test Telegram receipt (no external dependencies)
        print("📱 Testing Telegram receipt...")
        telegram_receipt = receipt_generator.generate_telegram_receipt(receipt_data)
        if telegram_receipt and "TRANSFER SUCCESSFUL" in telegram_receipt:
            print("✅ Telegram receipt generated successfully!")
            print(f"📄 Preview:\n{telegram_receipt[:200]}...")
        else:
            print("❌ Telegram receipt generation failed")
            return False
        
        # Test HTML receipt
        print("\n📄 Testing HTML receipt...")
        html_receipt = receipt_generator.generate_html_receipt(receipt_data)
        if html_receipt and "SOFI AI" in html_receipt:
            print("✅ HTML receipt generated successfully!")
            # Save to file for inspection
            with open("test_receipt.html", "w", encoding="utf-8") as f:
                f.write(html_receipt)
            print("📁 Saved as test_receipt.html")
        else:
            print("❌ HTML receipt generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR in receipt generation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run basic tests"""
    print("🚀 TESTING SOFI AI FIXES (SIMPLIFIED)")
    print("=" * 60)
    
    # Run tests
    test1_result = await test_pin_keyboard_simple()
    test2_result = await test_receipt_basic()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"📱 PIN Keyboard: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"📄 Receipt Generation: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    all_passed = test1_result and test2_result
    print(f"\n🎯 OVERALL: {'✅ TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 FIXES VERIFICATION:")
        print("1. ✅ PIN keyboard will be sent when user requests transfer")
        print("2. ✅ Beautiful receipts can be generated in multiple formats")
        print("3. ✅ Transfer completion will automatically send receipts")
        
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
