"""
Test webhook balance updating for future deposits
"""
import asyncio
import os
from dotenv import load_dotenv
from paystack.paystack_webhook import PaystackWebhookHandler

load_dotenv()

async def test_webhook_balance_update():
    """Test that webhook properly updates both users and virtual_accounts tables"""
    
    # Simulate a webhook payload
    webhook_payload = {
        "event": "charge.success",
        "data": {
            "amount": 50000,  # ₦500 in kobo
            "reference": "test_payment_12345",
            "customer": {
                "customer_code": "CUS_test123"  # You might not have this
            },
            "authorization": {
                "receiver_bank_account_number": "9325047112"  # Your account
            },
            "created_at": "2025-07-02T16:30:00.000Z"
        }
    }
    
    print("🧪 Testing webhook balance update")
    print("=" * 40)
    
    # Initialize webhook handler
    handler = PaystackWebhookHandler()
    
    # Process the webhook
    result = await handler.handle_webhook(webhook_payload)
    
    print("Webhook result:", result)
    
    if result.get("success"):
        print("✅ Webhook processed successfully")
        
        # Check updated balances
        from utils.balance_helper import get_user_balance, check_virtual_account
        
        telegram_id = "5495194750"
        new_balance = await get_user_balance(telegram_id)
        va_details = await check_virtual_account(telegram_id)
        
        print(f"📊 New balance in users table: ₦{new_balance:,.2f}")
        print(f"📊 New balance in virtual_accounts table: ₦{va_details['balance']:,.2f}")
        
        if new_balance == va_details['balance']:
            print("✅ Both tables are in sync!")
        else:
            print("❌ Tables are out of sync")
    else:
        print("❌ Webhook processing failed:", result.get("error"))

if __name__ == "__main__":
    asyncio.run(test_webhook_balance_update())
