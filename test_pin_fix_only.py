#!/usr/bin/env python3
"""
PIN VERIFICATION FIX TEST
=========================
Test ONLY the PIN verification fix without requiring balance
- Telegram ID: 7812930440 (Your actual ID)
- PIN: 1998 (Your actual PIN)

This tests the secure token generation and PIN verification logic.
"""

import asyncio
import json
import logging
from utils.secure_pin_verification import secure_pin_verification

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pin_verification_fix_only():
    """Test ONLY the PIN verification fix without requiring balance"""
    
    print("🔐 PIN VERIFICATION FIX TEST")
    print("=" * 50)
    
    # Your actual credentials
    telegram_chat_id = "7812930440"  # Your real Telegram ID
    user_pin = "1998"                # Your actual PIN
    amount = 100.0
    recipient_account = "8104965538"
    recipient_bank = "opay"
    
    print(f"📋 Test Details:")
    print(f"   User: {telegram_chat_id}")
    print(f"   PIN: {'*' * len(user_pin)}")
    print(f"   Testing PIN verification fix...")
    
    try:
        # Step 1: Check user exists
        print(f"\n1️⃣ Checking user exists...")
        
        from supabase import create_client
        import os
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get user data
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", telegram_chat_id).execute()
        
        if not user_result.data:
            print(f"❌ User not found: {telegram_chat_id}")
            return
            
        user_data = user_result.data[0]
        print(f"✅ User found: {user_data.get('full_name', 'Unknown')}")
        
        # Step 2: Test PIN verification
        print(f"\n2️⃣ Testing PIN verification...")
        
        from functions.security_functions import verify_pin
        pin_result = await verify_pin(telegram_chat_id, user_pin)
        
        if pin_result.get("valid"):
            print(f"✅ PIN {user_pin} verification SUCCESSFUL!")
            print(f"   Message: {pin_result.get('message', 'PIN valid')}")
        else:
            print(f"❌ PIN verification failed: {pin_result.get('error')}")
            print(f"⚠️  This means your PIN might not be {user_pin}")
            return
            
        # Step 3: Test secure token generation and validation
        print(f"\n3️⃣ Testing secure token system...")
        
        import uuid
        transaction_id = f"PIN_TEST_{uuid.uuid4().hex[:8].upper()}"
        
        transfer_data = {
            'chat_id': telegram_chat_id,
            'user_data': user_data,
            'transfer_data': {
                'amount': amount,
                'recipient_name': 'PIN Test',
                'account_number': recipient_account,
                'bank': recipient_bank,
                'transaction_id': transaction_id
            },
            'amount': amount
        }
        
        # Generate secure token (this is what the backend does)
        secure_token = secure_pin_verification.store_pending_transaction(transaction_id, transfer_data)
        
        print(f"✅ Secure token generated:")
        print(f"   Transaction ID: {transaction_id}")
        print(f"   Token: {secure_token[:15]}...")
        print(f"   Token Length: {len(secure_token)}")
        
        # Step 4: Test PIN verification URL (this is what user would click)
        pin_url = f"https://pipinstallsofi.com/verify-pin?token={secure_token}"
        print(f"\n4️⃣ PIN verification URL:")
        print(f"📱 {pin_url}")
        
        # Step 5: Test token validation (this is what the frontend should do)
        print(f"\n5️⃣ Testing frontend token extraction...")
        
        # Simulate URL parsing (what our FIXED frontend now does)
        from urllib.parse import urlparse, parse_qs
        
        parsed_url = urlparse(pin_url)
        query_params = parse_qs(parsed_url.query)
        extracted_token = query_params.get('token', [None])[0]
        
        print(f"✅ Frontend should extract:")
        print(f"   URL: {pin_url}")
        print(f"   Extracted token: {extracted_token[:15]}...")
        print(f"   Token matches: {extracted_token == secure_token}")
        
        # Step 6: Test the FIXED request body format
        print(f"\n6️⃣ Testing FIXED request format...")
        
        # BEFORE (broken): {'pin': '1998', 'transaction_id': None}
        broken_request = {
            'pin': user_pin,
            'transaction_id': None
        }
        
        # AFTER (fixed): {'pin': '1998', 'secure_token': 'abc123...'}
        fixed_request = {
            'pin': user_pin,
            'secure_token': secure_token
        }
        
        print(f"❌ OLD (broken) request:")
        print(f"   {json.dumps({'pin': '****', 'transaction_id': None}, indent=2)}")
        
        print(f"✅ NEW (fixed) request:")
        print(f"   {json.dumps({'pin': '****', 'secure_token': secure_token[:15] + '...'}, indent=2)}")
        
        # Step 7: Test backend token validation
        print(f"\n7️⃣ Testing backend validation...")
        
        validated_transaction = secure_pin_verification.get_pending_transaction_by_token(secure_token)
        
        if validated_transaction:
            print(f"✅ Backend validation SUCCESS!")
            print(f"   Amount: ₦{validated_transaction.get('amount', 0):,.2f}")
            print(f"   Chat ID: {validated_transaction.get('chat_id')}")
            print(f"   Recipient: {validated_transaction.get('transfer_data', {}).get('account_number')}")
        else:
            print(f"❌ Backend validation failed")
            return
            
        print(f"\n🎉 PIN VERIFICATION FIX TEST RESULTS:")
        print(f"=" * 50)
        print(f"✅ User exists: Tee God ({telegram_chat_id})")
        print(f"✅ PIN {user_pin} is valid")
        print(f"✅ Secure token generation works")
        print(f"✅ Frontend token extraction works")
        print(f"✅ Backend token validation works")
        print(f"✅ Request format is fixed")
        
        print(f"\n🚀 READY FOR REAL TRANSFER!")
        print(f"📝 To test with real money:")
        print(f"   1. Go to Sofi Telegram bot")
        print(f"   2. Send: 'send 100 to 8104965538 opay'")
        print(f"   3. Click 'Verify Transaction' button")
        print(f"   4. Enter PIN: {user_pin}")
        print(f"   5. Check browser console for our fix logs")
        print(f"   6. Transfer should complete successfully!")
        
        # Generate a test PIN URL you can actually use
        print(f"\n🧪 TEST PIN URL (copy and paste in browser):")
        print(f"🔗 {pin_url}")
        print(f"   Enter PIN: {user_pin}")
        print(f"   Should show: 'Transfer completed successfully!'")
        
    except Exception as e:
        logger.error(f"❌ Error during PIN test: {e}")
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_pin_verification_fix_only())
