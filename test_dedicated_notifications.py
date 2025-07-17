#!/usr/bin/env python3
"""
Test the dedicated notification service
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_dedicated_notification():
    """Test the dedicated notification service"""
    try:
        from utils.telegram_notifications import send_telegram_notification
        
        print('🔍 Testing dedicated notification service...')
        
        # Test sending a notification to the recent deposit user
        test_chat_id = "7812930440"  # The user from recent deposits
        test_message = """🎉 *Deposit Alert Test!*

Hi Tee! You just received ₦100.00

💸 *From:* **Test Sender**
🏦 *via* Test Bank
💰 *New Balance:* ₦1,000.00

This is a test of the fixed notification system! 🚀"""
        
        print(f'📱 Sending test notification to chat ID: {test_chat_id}')
        
        success = send_telegram_notification(test_chat_id, test_message)
        
        if success:
            print('✅ Test notification sent successfully!')
        else:
            print('❌ Test notification failed to send')
            
        # Also test with a simple message
        simple_success = send_telegram_notification(test_chat_id, "🚨 Test: Fixed deposit notification system!")
        
        if simple_success:
            print('✅ Simple test notification also sent successfully!')
        else:
            print('❌ Simple test notification also failed')
            
    except Exception as e:
        print(f'❌ Error testing notification: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dedicated_notification()
