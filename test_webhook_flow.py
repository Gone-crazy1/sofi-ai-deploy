#!/usr/bin/env python3
"""
Test the full webhook notification flow
"""

import json
from datetime import datetime

def test_webhook_notification():
    """Test the complete webhook notification flow"""
    try:
        from paystack.paystack_webhook import handle_paystack_webhook
        
        print('🔍 Testing complete webhook notification flow...')
        
        # Create a realistic webhook payload like Paystack would send
        webhook_payload = {
            "event": "charge.success",
            "data": {
                "id": 2900000000,
                "domain": "live",
                "status": "success",
                "reference": "test_ref_" + str(int(datetime.now().timestamp())),
                "amount": 10000,  # 100 NGN in kobo
                "message": None,
                "gateway_response": "Successful",
                "paid_at": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "channel": "dedicated_nuban",
                "currency": "NGN",
                "customer": {
                    "id": 123456,
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@example.com",
                    "customer_code": "CUS_test123",
                    "phone": "+2348000000000",
                    "metadata": {},
                    "risk_action": "default"
                },
                "authorization": {
                    "authorization_code": "AUTH_test123",
                    "bin": "408408",
                    "last4": "4081",
                    "exp_month": "12",
                    "exp_year": "2030",
                    "channel": "bank",
                    "card_type": "visa",
                    "bank": "TEST BANK",
                    "country_code": "NG",
                    "brand": "visa",
                    "reusable": True,
                    "signature": "SIG_test123",
                    "account_name": "Test Sender Name",
                    "receiver_bank_account_number": "9325313442",  # This should match virtual account
                    "sender_name": "REAL TEST SENDER"
                },
                "metadata": {
                    "sender_name": "REAL TEST SENDER", 
                    "sender_bank": "GTBank"
                },
                "fees_breakdown": [],
                "log": {
                    "start_time": 1,
                    "time_spent": 1,
                    "attempts": 1,
                    "errors": 0,
                    "success": True,
                    "mobile": False,
                    "input": [],
                    "history": []
                }
            }
        }
        
        print(f'📱 Testing with account number: 9325313442')
        print(f'💰 Testing with amount: ₦100.00')
        
        # Call webhook handler
        result = handle_paystack_webhook(webhook_payload)
        
        print(f'📊 Webhook result: {result}')
        
        if result.get('success'):
            print('✅ Webhook processed successfully!')
            print('📱 Check Telegram chat 7812930440 for notification')
        else:
            print('❌ Webhook processing failed')
            print(f'Error: {result.get("error")}')
            
    except Exception as e:
        print(f'❌ Error testing webhook: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_webhook_notification()
