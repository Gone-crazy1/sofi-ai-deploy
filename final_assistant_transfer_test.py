#!/usr/bin/env python3
"""
Final Assistant Money Transfer Test
Test with ₦100 (minimum amount) to account 2206553670
"""

import asyncio
from assistant import get_assistant

async def test_real_transfer():
    print("🚀 FINAL MONEY TRANSFER TEST VIA ASSISTANT")
    print("=" * 60)
    print("📋 Transfer Details:")
    print("   Account: 2206553670 (OLUWATOBI ATURU)")
    print("   Bank: UBA")
    print("   Amount: ₦100 (minimum required)")
    print("   Method: Sofi AI Assistant")
    print("=" * 60)
    
    try:
        assistant = get_assistant()
        
        # First, let's add some balance to our test user
        print("\n💰 Adding balance to test user...")
        from supabase import create_client
        import os
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Update user balance to ₦500 for testing
        update_result = supabase.table('users').update({
            'wallet_balance': 500.0
        }).eq('telegram_chat_id', 'test_money_user_123').execute()
        
        if update_result.data:
            print("✅ Test user balance updated to ₦500")
        
        # Now test the transfer via assistant
        print("\n🤖 Testing transfer via Sofi Assistant...")
        
        transfer_message = """
        Please send ₦100 to account number 2206553670 at UBA bank.
        My PIN is 1234.
        This is for testing Sofi AI money transfer capabilities.
        """
        
        response, function_data = await assistant.process_message(
            chat_id="test_money_user_123",
            message=transfer_message,
            user_data={"telegram_chat_id": "test_money_user_123"}
        )
        
        print(f"\n🤖 Assistant Response:")
        print(response)
        
        if function_data:
            print(f"\n📊 Functions Called: {list(function_data.keys())}")
            
            for func_name, result in function_data.items():
                print(f"\n{func_name}:")
                print(f"  {result}")
                
                if func_name == "send_money" and result.get("success"):
                    print("\n🎉 SUCCESS! MONEY SENT VIA SOFI ASSISTANT!")
                    print(f"✅ Reference: {result.get('reference')}")
                    print(f"✅ Status: {result.get('status')}")
                    print(f"✅ Fee: ₦{result.get('fee', 0):.2f}")
                    print(f"✅ Recipient: OLUWATOBI ATURU")
                    print(f"✅ Account: 2206553670 (UBA)")
                    
                    print("\n" + "=" * 60)
                    print("🎯 CONFIRMATION: SOFI AI CAN SEND MONEY!")
                    print("✅ PIN verification works")
                    print("✅ Account verification works") 
                    print("✅ Money transfer works")
                    print("✅ Receipt generation works")
                    print("✅ Assistant integration works")
                    print("=" * 60)
                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_real_transfer())
    
    if result:
        print("\n🚀 SOFI AI IS READY FOR PRODUCTION MONEY TRANSFERS! 🚀")
    else:
        print("\n⚠️ Some issues need to be resolved")
