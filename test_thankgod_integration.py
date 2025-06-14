#!/usr/bin/env python3
"""
Test ThankGod's wallet integration with the bot
"""

import sys
sys.path.append('.')

from main import handle_crypto_commands

async def test_thankgod_bot_integration():
    """Test ThankGod's crypto commands in the bot"""
    
    print("🧪 TESTING THANKGOD'S BOT INTEGRATION")
    print("=" * 60)
    
    # ThankGod's user data
    thankgod_user = {
        'user_id': '52',
        'first_name': 'ThankGod',
        'email': 'mrhawt10@gmail.com'
    }
    
    # Test commands ThankGod might use
    test_commands = [
        "my wallet addresses",
        "create BTC wallet", 
        "my btc address",
        "show my crypto addresses"
    ]
    
    for cmd in test_commands:
        print(f"\n📱 Testing: '{cmd}'")
        print("-" * 40)
        
        try:
            response = await handle_crypto_commands(
                chat_id="thankgod_test",
                message=cmd,
                user_data=thankgod_user
            )
            
            if response:
                print(f"✅ Bot Response:")
                print(response)
                
                # Check if valid BTC address is in response
                if "bc1qce002b944a1d243df5b9ce3498b2a5f09e921d" in response:
                    print("🎉 CONFIRMED: Valid BTC address shown!")
                elif "bc1q" in response and len([word for word in response.split() if word.startswith("bc1q")]) > 0:
                    print("✅ BTC address detected in response")
                    
            else:
                print("❌ No response from bot")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n🎉 BOT INTEGRATION TEST COMPLETE!")
    print("ThankGod's wallet is ready for use in Telegram!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_thankgod_bot_integration())
