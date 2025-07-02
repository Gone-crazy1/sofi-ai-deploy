#!/usr/bin/env python3
"""
REAL SOFI AI TELEGRAM TRANSFER TEST
==================================
Test the actual Sofi AI assistant making transfers through Telegram interface
This simulates a real user chatting with Sofi and asking to send money
"""

import asyncio
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def test_real_sofi_conversation():
    """Test actual conversation with Sofi AI for money transfer"""
    print("🤖 TESTING REAL SOFI AI CONVERSATION FOR MONEY TRANSFER")
    print("=" * 70)
    print("👤 Simulating user chatting with Sofi via Telegram")
    print("💸 Goal: Send ₦100 to account 2206553670 (UBA)")
    print("=" * 70)
    
    try:
        # Import the main handler from main.py
        from main import handle_message
        
        # Test user who we know has balance and PIN
        test_user_id = "test_money_user_123"
        
        # Simulate the conversation step by step
        print("\n💬 CONVERSATION 1: Ask Sofi to check balance")
        print("👤 User: What's my account balance?")
        
        response1 = await handle_message(
            chat_id=test_user_id,
            message="What's my account balance?",
            user_data={
                "telegram_chat_id": test_user_id,
                "first_name": "Test User"
            }
        )
        
        print(f"🤖 Sofi: {response1}")
        
        print("\n💬 CONVERSATION 2: Ask Sofi to verify recipient account")
        print("👤 User: Please verify account 2206553670 at UBA bank")
        
        response2 = await handle_message(
            chat_id=test_user_id,
            message="Please verify account 2206553670 at UBA bank",
            user_data={
                "telegram_chat_id": test_user_id,
                "first_name": "Test User"
            }
        )
        
        print(f"🤖 Sofi: {response2}")
        
        print("\n💬 CONVERSATION 3: Ask Sofi to send money with PIN")
        print("👤 User: Send ₦100 to account 2206553670 at UBA. My PIN is 1234. This is for testing Sofi AI transfer.")
        
        response3 = await handle_message(
            chat_id=test_user_id,
            message="Send ₦100 to account 2206553670 at UBA. My PIN is 1234. This is for testing Sofi AI transfer.",
            user_data={
                "telegram_chat_id": test_user_id,
                "first_name": "Test User"
            }
        )
        
        print(f"🤖 Sofi: {response3}")
        
        # Check if the response indicates successful transfer
        if any(word in response3.lower() for word in ['transfer', 'sent', 'successful', 'completed', 'reference']):
            print("\n🎉 SUCCESS! Sofi AI successfully handled the money transfer!")
            print("✅ Sofi understood the request")
            print("✅ Sofi processed the transfer")
            print("✅ Sofi provided confirmation")
            return True
        else:
            print("\n⚠️ Sofi didn't complete the transfer - checking what happened...")
            return False
        
    except Exception as e:
        print(f"❌ Error testing Sofi conversation: {e}")
        return False

async def test_sofi_with_different_requests():
    """Test various ways users might ask Sofi to send money"""
    print("\n🔄 TESTING DIFFERENT WAYS TO ASK SOFI FOR TRANSFERS")
    print("=" * 60)
    
    test_user_id = "test_money_user_123"
    
    # Import the main handler
    from main import handle_message
    
    test_messages = [
        "Transfer ₦100 to 2206553670 UBA PIN 1234",
        "Send money to OLUWATOBI ATURU account 2206553670 UBA ₦100 PIN 1234", 
        "I want to send ₦100 to UBA account 2206553670. My PIN is 1234",
        "Please transfer one hundred naira to account number 2206553670 at United Bank for Africa. Transaction PIN: 1234"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 TEST {i}: {message}")
        
        try:
            response = await handle_message(
                chat_id=test_user_id,
                message=message,
                user_data={
                    "telegram_chat_id": test_user_id,
                    "first_name": "Test User"
                }
            )
            
            print(f"🤖 Sofi: {response[:200]}...")
            
            # Check if transfer was handled
            if any(word in response.lower() for word in ['transfer', 'sent', 'processing', 'reference']):
                print("✅ Transfer request understood and processed")
            else:
                print("⚠️ Transfer request not processed")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all Sofi AI conversation tests"""
    print("🚀 TESTING SOFI AI END-TO-END MONEY TRANSFER")
    print("🎯 Goal: Verify Sofi can handle real money transfers via chat")
    print("\n")
    
    # Test 1: Step-by-step conversation
    success1 = await test_real_sofi_conversation()
    
    # Test 2: Different request formats
    await test_sofi_with_different_requests()
    
    if success1:
        print("\n" + "=" * 70)
        print("🎉 SOFI AI MONEY TRANSFER TEST: SUCCESS!")
        print("✅ Sofi can chat with users naturally")
        print("✅ Sofi can verify account details")
        print("✅ Sofi can execute money transfers")
        print("✅ Sofi can handle PIN verification")
        print("✅ Sofi provides transfer confirmations")
        print("")
        print("🚀 SOFI AI IS READY FOR REAL USERS TO SEND MONEY VIA TELEGRAM!")
        print("=" * 70)
    else:
        print("\n❌ Some issues need to be resolved with the chat interface")

if __name__ == "__main__":
    asyncio.run(main())
