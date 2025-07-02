"""
Test send_money function directly to verify it works
"""
import asyncio
from functions.transfer_functions import send_money

async def test_send_money_function():
    """Test send_money function with all required arguments"""
    
    print("🧪 Testing send_money function directly")
    print("=" * 40)
    
    # Test with all required arguments
    test_args = {
        "chat_id": "5495194750",  # Your telegram ID
        "recipient_account": "1234567890",
        "recipient_bank": "OPay",
        "amount": 100.0,
        "pin": "1234",
        "narration": "Test transfer"
    }
    
    print("Test arguments:")
    for key, value in test_args.items():
        print(f"  {key}: {value}")
    
    try:
        result = await send_money(**test_args)
        print(f"\n📊 Result: {result}")
        
        if result.get("success"):
            print("✅ Function call successful")
        else:
            print(f"❌ Function call failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error calling function: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_send_money_function())
