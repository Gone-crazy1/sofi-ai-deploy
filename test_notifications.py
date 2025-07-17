#!/usr/bin/env python3
"""
Test notification sending to debug webhook notifications
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_notification_sending():
    """Test if notification sending works"""
    try:
        # Import the send_reply function from main
        import sys
        sys.path.append('.')
        
        from main import send_reply
        
        print('🔍 Testing notification sending...')
        
        # Test sending a notification to the recent deposit user
        test_chat_id = "7812930440"  # The user from recent deposits
        test_message = """🎉 *Test Deposit Alert!*

Hi there! You just received ₦100.00

💸 *From:* **Test Sender**
🏦 *via* Test Bank
💰 *New Balance:* ₦1,000.00

This is a test notification to verify the alert system! 🚀"""
        
        print(f'📱 Sending test notification to chat ID: {test_chat_id}')
        
        result = send_reply(test_chat_id, test_message)
        
        if result:
            print('✅ Test notification sent successfully!')
            print(f'📱 Response: {result}')
        else:
            print('❌ Test notification failed to send')
            
        # Also test with a simple message
        simple_result = send_reply(test_chat_id, "🚨 Test: Deposit notification system check!")
        
        if simple_result:
            print('✅ Simple test notification also sent successfully!')
        else:
            print('❌ Simple test notification also failed')
            
    except Exception as e:
        print(f'❌ Error testing notification: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notification_sending()
