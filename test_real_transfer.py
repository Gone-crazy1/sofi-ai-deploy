#!/usr/bin/env python3
"""
Test real account verification and transfer
Testing with: 9325047112 (Wema Bank) - ₦100 transfer
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_account_verification():
    """Test account verification for 9325047112 at Wema Bank"""
    try:
        # Import the verification function
        from functions.verification_functions import verify_account_name
        
        account_number = "9325047112"
        bank_name = "Wema Bank"
        
        logger.info(f"🔍 Testing account verification...")
        logger.info(f"Account: {account_number}")
        logger.info(f"Bank: {bank_name}")
        
        # Test verification
        result = await verify_account_name(account_number, bank_name)
        
        logger.info(f"📋 Verification Result:")
        logger.info(f"✅ Verified: {result.get('verified')}")
        
        if result.get('verified'):
            logger.info(f"👤 Account Name: {result.get('account_name')}")
            logger.info(f"🏦 Bank: {result.get('bank_name')}")
            logger.info(f"🔢 Bank Code: {result.get('bank_code')}")
            logger.info(f"📱 Account Number: {result.get('account_number')}")
        else:
            logger.error(f"❌ Error: {result.get('error')}")
            logger.error(f"💬 Message: {result.get('message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return {"verified": False, "error": str(e)}

async def test_assistant_transfer():
    """Test transfer via OpenAI Assistant"""
    try:
        # Import the assistant
        from assistant import get_assistant
        
        # Test chat ID (use admin chat ID from env)
        test_chat_id = os.getenv("ADMIN_CHAT_IDS", "123456789").split(",")[0]
        
        logger.info(f"🤖 Testing transfer via OpenAI Assistant...")
        logger.info(f"Chat ID: {test_chat_id}")
        
        assistant = get_assistant()
        
        # Test message for transfer
        test_message = "Send ₦100 to account 9325047112 at Wema Bank"
        
        logger.info(f"💬 Test Message: {test_message}")
        
        # Process message with assistant
        response, function_data = await assistant.process_message(
            test_chat_id, 
            test_message, 
            {"full_name": "Test User", "phone": "+2348000000000"}
        )
        
        logger.info(f"🤖 Assistant Response: {response}")
        
        if function_data:
            logger.info(f"🔧 Function Calls:")
            for func_name, func_result in function_data.items():
                logger.info(f"  - {func_name}: {func_result}")
        else:
            logger.info("🔧 No function calls made")
        
        return {"response": response, "function_data": function_data}
        
    except Exception as e:
        logger.error(f"❌ Assistant test failed: {str(e)}")
        return {"error": str(e)}

async def test_direct_transfer():
    """Test direct transfer function call"""
    try:
        # Import transfer function
        from functions.transfer_functions import send_money
        
        logger.info(f"💸 Testing direct transfer function...")
        
        # Test parameters
        test_chat_id = os.getenv("ADMIN_CHAT_IDS", "123456789").split(",")[0]
        account_number = "9325047112"
        bank_name = "Wema Bank"
        amount = 100.0
        pin = "1234"  # Default test PIN
        
        logger.info(f"Parameters:")
        logger.info(f"  - Chat ID: {test_chat_id}")
        logger.info(f"  - Account: {account_number}")
        logger.info(f"  - Bank: {bank_name}")
        logger.info(f"  - Amount: ₦{amount}")
        
        # Call transfer function
        result = await send_money(
            chat_id=test_chat_id,
            account_number=account_number,
            bank_name=bank_name,
            amount=amount,
            pin=pin,
            narration="Test transfer via Sofi AI"
        )
        
        logger.info(f"💸 Transfer Result:")
        logger.info(f"✅ Success: {result.get('success')}")
        
        if result.get('success'):
            logger.info(f"💰 Message: {result.get('message')}")
            logger.info(f"🧾 Receipt: {result.get('receipt')}")
        else:
            logger.error(f"❌ Error: {result.get('error')}")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Direct transfer test failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test function"""
    logger.info("🚀 Starting comprehensive transfer test...")
    logger.info("=" * 60)
    
    # Test 1: Account Verification
    logger.info("📋 TEST 1: Account Verification")
    logger.info("-" * 30)
    verification_result = await test_account_verification()
    logger.info("")
    
    if not verification_result.get('verified'):
        logger.error("❌ Account verification failed - stopping tests")
        return
    
    # Test 2: Assistant Transfer
    logger.info("🤖 TEST 2: Assistant Transfer")
    logger.info("-" * 30)
    assistant_result = await test_assistant_transfer()
    logger.info("")
    
    # Test 3: Direct Transfer (only if we have a verified account)
    logger.info("💸 TEST 3: Direct Transfer Function")
    logger.info("-" * 30)
    transfer_result = await test_direct_transfer()
    logger.info("")
    
    # Summary
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Account Verified: {verification_result.get('verified')}")
    if verification_result.get('verified'):
        logger.info(f"👤 Account Name: {verification_result.get('account_name')}")
    
    logger.info(f"🤖 Assistant Response: {'✅' if assistant_result.get('response') else '❌'}")
    logger.info(f"💸 Transfer Success: {'✅' if transfer_result.get('success') else '❌'}")
    
    if transfer_result.get('success'):
        logger.info("🎉 REAL MONEY TRANSFER COMPLETED!")
    else:
        logger.info("⚠️ Transfer test failed - check logs above")

if __name__ == "__main__":
    asyncio.run(main())
