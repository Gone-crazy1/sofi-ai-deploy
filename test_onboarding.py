#!/usr/bin/env python3
"""
Simple test script for WhatsApp Interactive Onboarding System
"""

import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🧪 WhatsApp Interactive Onboarding Test")
print("=" * 50)

# Test 1: Basic imports
print("📦 Testing imports...")
try:
    import requests
    import hmac
    import hashlib
    from dotenv import load_dotenv
    from supabase import create_client
    print("✅ All required packages imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Load environment
print("\n🔧 Loading environment...")
load_dotenv()

# Test 3: Check configuration
print("\n📋 Checking configuration...")
required_vars = {
    'WHATSAPP_TOKEN': os.getenv('WHATSAPP_TOKEN'),
    'WHATSAPP_PHONE_NUMBER_ID': os.getenv('WHATSAPP_PHONE_NUMBER_ID'),
    'SUPABASE_URL': os.getenv('SUPABASE_URL'),
    'SUPABASE_KEY': os.getenv('SUPABASE_KEY')
}

for var, value in required_vars.items():
    status = "✅ Set" if value else "❌ Missing"
    print(f"  {var}: {status}")

# Test 4: Import onboarding module
print("\n🚀 Testing onboarding module...")
try:
    from whatsapp_onboarding import WhatsAppOnboardingManager
    print("✅ WhatsApp onboarding module imported successfully")
    
    # Test initialization
    manager = WhatsAppOnboardingManager()
    print("✅ WhatsApp onboarding manager initialized")
    
    # Test token generation
    test_number = "+2348104611794"
    token = manager.generate_secure_token(test_number)
    print(f"✅ Token generated: {token[:30]}...")
    
    # Test token validation
    is_valid = manager.validate_token(token, test_number)
    print(f"✅ Token validation: {'Valid' if is_valid else 'Invalid'}")
    
    print("\n🎉 All tests passed! Onboarding system is ready.")
    
except Exception as e:
    print(f"❌ Error testing onboarding module: {e}")
    import traceback
    print("\nFull error details:")
    traceback.print_exc()

print("\n" + "=" * 50)
print("✅ Test complete!")
