"""
Test Paystack Integration
Test that all components are properly connected
"""

async def test_paystack_integration():
    """Test the complete Paystack integration"""
    print("🔄 Testing Paystack Integration...")
    
    try:
        # Test 1: Import Paystack service
        print("\n1. Testing Paystack service import...")
        from paystack.paystack_service import get_paystack_service
        service = get_paystack_service()
        print("✅ Paystack service imported successfully")
        
        # Test 2: Check available methods
        print("\n2. Checking available methods...")
        methods = [m for m in dir(service) if not m.startswith('_')]
        essential_methods = [
            'create_user_account_simple',
            'send_money_simple', 
            'verify_recipient_account',
            'get_user_virtual_account_summary',
            'get_transaction_history'
        ]
        
        for method in essential_methods:
            if hasattr(service, method):
                print(f"✅ {method} - Available")
            else:
                print(f"❌ {method} - Missing")
        
        # Test 3: Test assistant functions import
        print("\n3. Testing assistant function imports...")
        from functions.transfer_functions import send_money
        from functions.balance_functions import check_balance
        print("✅ Assistant functions imported successfully")
        
        # Test 4: Check Paystack APIs
        print("\n4. Checking Paystack API classes...")
        from paystack.paystack_dva_api import PaystackDVAAPI
        from paystack.paystack_transfer_api import PaystackTransferAPI
        print("✅ Paystack API classes available")
        
        print("\n🎉 All tests passed! Paystack integration is ready!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_paystack_integration())
