#!/usr/bin/env python3
"""
Test Environment Variable Loading
Check if admin IDs are loading correctly
"""

import os
from dotenv import load_dotenv

print("🔍 Testing Environment Variable Loading")
print("=" * 50)

# Test 1: Load .env file
print("📁 Loading .env file...")
load_dotenv()

# Test 2: Check all admin-related environment variables
admin_vars = {
    "ADMIN_CHAT_IDS": os.getenv("ADMIN_CHAT_IDS"),
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN")[:20] + "..." if os.getenv("TELEGRAM_BOT_TOKEN") else None,
}

print("\n🔑 Environment Variables:")
for key, value in admin_vars.items():
    if value:
        print(f"✅ {key}: {value}")
    else:
        print(f"❌ {key}: NOT FOUND")

# Test 3: Test AdminCommandHandler
print("\n🧪 Testing AdminCommandHandler...")
try:
    from utils.admin_command_handler import AdminCommandHandler
    admin_handler = AdminCommandHandler()
    
    print(f"📋 Admin IDs loaded: {admin_handler.admin_chat_ids}")
    
    # Test admin check
    test_id = "5495194750"
    is_admin = admin_handler.is_admin(test_id)
    print(f"🔐 Is {test_id} admin? {is_admin}")
    
except Exception as e:
    print(f"❌ Error testing AdminCommandHandler: {e}")

print("\n" + "=" * 50)
print("🎯 Test completed!")
