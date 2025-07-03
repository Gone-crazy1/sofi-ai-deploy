#!/usr/bin/env python3
"""
Test Xara-style command integration with running bot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xara_style_transfer import XaraStyleTransfer

def test_xara_integration():
    """Test the Xara-style integration"""
    print("🧪 TESTING XARA-STYLE INTEGRATION")
    print("=" * 45)
    
    handler = XaraStyleTransfer()
    
    # Test commands
    test_commands = [
        "6115491450 Opay send 100",
        "9067927398 Opay send 5300",
        "1234567890 Access Bank send 1000",
        "invalid command",
        "0123456789 gtb send 500"
    ]
    
    print("✅ Testing command parser:")
    for cmd in test_commands:
        result = handler.parse_xara_command(cmd)
        if result:
            print(f"  ✅ '{cmd}' → {result}")
            
            # Test bank normalization
            normalized = handler.normalize_bank_name(result['bank'])
            print(f"     📦 Bank normalized: '{result['bank']}' → '{normalized}'")
        else:
            print(f"  ❌ '{cmd}' → Not a valid Xara command")
    
    print("\n" + "=" * 45)
    print("📱 HOW TO TEST WITH THE RUNNING BOT:")
    print("=" * 45)
    print("1. Bot is running at: http://127.0.0.1:5000")
    print("2. Open Telegram and find your Sofi AI bot")
    print("3. Try this command:")
    print("   📝 6115491450 Opay send 100")
    print("4. The bot should:")
    print("   ✅ Detect it as Xara-style command")
    print("   ✅ Verify the account automatically")
    print("   ✅ Show 'Verify Transaction' button")
    print("   ✅ Request PIN when clicked")
    print("   ✅ Process transfer and send receipt")
    print()
    print("🚨 REMEMBER: This will transfer REAL money!")
    print("   Make sure 6115491450 is your actual OPay account")

if __name__ == "__main__":
    test_xara_integration()
