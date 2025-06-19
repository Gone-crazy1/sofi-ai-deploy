#!/usr/bin/env python3
"""
🔒 ADMIN SECURITY TEST

Test the admin authentication system
"""

import os
import asyncio
from dotenv import load_dotenv
from utils.admin_command_handler import admin_handler

load_dotenv()

async def test_admin_security():
    print("🔒 TESTING ADMIN SECURITY SYSTEM")
    print("=" * 40)
    
    # Check current admin configuration
    admin_ids = os.getenv("ADMIN_CHAT_IDS", "")
    print(f"🔐 Configured Admin IDs: {admin_ids if admin_ids else 'NONE'}")
    
    if not admin_ids or admin_ids == "YOUR_TELEGRAM_CHAT_ID":
        print("❌ No valid admin IDs configured")
        print("⚠️ Admin commands will be BLOCKED for all users")
        print("\n📋 To fix:")
        print("1. Get your chat ID from @userinfobot on Telegram")
        print("2. Update .env: ADMIN_CHAT_IDS=your_chat_id_here")
        print("3. Restart Sofi")
        return
    
    # Test admin detection
    print(f"\n🧪 TESTING ADMIN ACCESS:")
    
    # Test authorized admin
    test_admin_id = admin_ids.split(",")[0].strip()
    is_admin = admin_handler.is_admin(test_admin_id)
    print(f"✅ Authorized admin ({test_admin_id}): {'GRANTED' if is_admin else 'DENIED'}")
    
    # Test unauthorized user
    fake_admin_id = "999999999"
    is_fake_admin = admin_handler.is_admin(fake_admin_id)
    print(f"🚨 Unauthorized user ({fake_admin_id}): {'GRANTED' if is_fake_admin else 'DENIED'}")
    
    # Test admin command detection
    print(f"\n🔍 TESTING COMMAND DETECTION:")
    
    test_commands = [
        "How much profit do I have?",
        "I want to withdraw ₦10000 profit",
        "Generate profit report"
    ]
    
    for cmd in test_commands:
        # Test with authorized admin
        command_type = await admin_handler.detect_admin_command(cmd, test_admin_id)
        print(f"✅ Admin command '{cmd}': {'DETECTED' if command_type else 'NOT DETECTED'}")
        
        # Test with unauthorized user
        command_type_fake = await admin_handler.detect_admin_command(cmd, fake_admin_id)
        print(f"🚨 Fake admin '{cmd}': {'DETECTED' if command_type_fake else 'BLOCKED'}")
    
    print(f"\n🏆 SECURITY STATUS:")
    if is_admin and not is_fake_admin:
        print("✅ SECURITY WORKING PERFECTLY!")
        print("• Authorized admins: GRANTED access")
        print("• Unauthorized users: DENIED access")
        print("• Your Sofi is SECURE from impersonation")
    else:
        print("❌ SECURITY ISSUE DETECTED!")
        print("• Check your admin configuration")
        print("• Review .env file settings")

if __name__ == "__main__":
    asyncio.run(test_admin_security())
