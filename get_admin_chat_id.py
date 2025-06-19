#!/usr/bin/env python3
"""
🔐 GET YOUR TELEGRAM CHAT ID

This script helps you get your Telegram chat ID to configure as admin.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔐 TELEGRAM ADMIN CHAT ID SETUP")
    print("=" * 40)
    
    print("\n📋 TO GET YOUR TELEGRAM CHAT ID:")
    print("1. Message @userinfobot on Telegram")
    print("2. Or message @getidsbot on Telegram") 
    print("3. Copy the 'Id' number they send you")
    print("4. Add it to your .env file")
    
    print(f"\n📝 CURRENT ADMIN CONFIGURATION:")
    admin_ids = os.getenv("ADMIN_CHAT_IDS", "")
    
    if admin_ids and admin_ids != "YOUR_TELEGRAM_CHAT_ID":
        print(f"✅ Admin IDs configured: {admin_ids}")
        print("🔐 Admin security is ACTIVE")
    else:
        print("❌ Admin IDs NOT configured")
        print("⚠️ Admin commands are DISABLED for security")
    
    print(f"\n🔧 TO CONFIGURE YOUR ADMIN ACCESS:")
    print("1. Get your chat ID from @userinfobot")
    print("2. Edit your .env file") 
    print("3. Replace 'YOUR_TELEGRAM_CHAT_ID' with your actual ID")
    print("4. Save the file and restart Sofi")
    
    print(f"\n📄 Example .env configuration:")
    print("ADMIN_CHAT_IDS=123456789")
    print("# For multiple admins: ADMIN_CHAT_IDS=123456789,987654321")
    
    print(f"\n🚨 SECURITY NOTE:")
    print("Only users with chat IDs in ADMIN_CHAT_IDS can:")
    print("• Check profit balances")
    print("• Withdraw profits") 
    print("• Generate admin reports")
    print("• Access sensitive business data")
    
    print(f"\n✅ Once configured, test by messaging Sofi:")
    print("'How much profit do I have?'")

if __name__ == "__main__":
    main()
