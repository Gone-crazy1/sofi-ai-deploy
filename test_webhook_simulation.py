#!/usr/bin/env python3
"""
Test the full webhook flow simulation including PIN entry
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main functions
from main import handle_message
from utils.pin_entry_system import pin_manager, create_pin_entry_keyboard

async def test_webhook_simulation():
    """Test the webhook simulation with PIN entry"""
    print("🧪 Testing Webhook Simulation with PIN Entry...")
    
    test_chat_id = "TEST_WEBHOOK_USER"
    
    try:
        # Mock user data (simulating existing user)
        mock_user_data = {
            "telegram_id": test_chat_id,
            "first_name": "Test User",
            "wallet_balance": 5000.0
        }
        
        # Mock virtual account
        mock_virtual_account = {
            "account_number": "9876543210",
            "bank_name": "Test Bank",
            "balance": 5000.0
        }
        
        # Test message that should trigger transfer
        test_message = "Please send 1000 naira to account 1234567890 at Access Bank"
        
        print(f"\n📱 User message: {test_message}")
        
        # Call handle_message (this is what webhook calls)
        response = await handle_message(test_chat_id, test_message, mock_user_data, mock_virtual_account)
        
        print(f"\n🤖 Handle message response type: {type(response)}")
        print(f"📝 Response content: {response}")
        
        # Check if response indicates PIN entry is needed
        if isinstance(response, dict) and response.get("requires_pin"):
            print(f"\n✅ PIN entry flow triggered!")
            print(f"💬 PIN message: {response.get('message')}")
            
            # This is what would happen in the webhook
            print(f"\n⌨️ PIN keyboard would be sent to user")
            keyboard = create_pin_entry_keyboard()
            print(f"   Keyboard has {len(keyboard['inline_keyboard'])} rows")
            
            # Check if PIN session was created
            session = pin_manager.get_session(test_chat_id)
            if session:
                print(f"✅ PIN session created successfully")
                print(f"   Transfer amount: ₦{session['transfer_data']['amount']}")
                print(f"   Recipient: {session['transfer_data']['recipient_account']}")
                
                # Simulate PIN entry (what happens when user clicks buttons)
                print(f"\n🔢 Simulating user entering PIN via keyboard...")
                for i, digit in enumerate("1234", 1):
                    result = pin_manager.add_pin_digit(test_chat_id, digit)
                    print(f"   Button press {i}: digit={digit}, display={result.get('display', 'N/A')}")
                
                print(f"✅ PIN entry simulation completed")
                
                # Clear session
                pin_manager.clear_session(test_chat_id)
                print(f"🧹 Session cleared")
            else:
                print(f"❌ No PIN session found - this is an issue")
        else:
            print(f"\n❌ PIN entry flow was NOT triggered")
            print(f"   Response type: {type(response)}")
            if isinstance(response, str):
                print(f"   Response preview: {response[:200]}...")
                
    except Exception as e:
        print(f"\n❌ Error in webhook simulation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_webhook_simulation())
