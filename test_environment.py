#!/usr/bin/env python3
"""
Simple environment and import test for Sofi AI
"""
import os
import sys
from dotenv import load_dotenv

print("🧪 Sofi AI Environment Test")
print("=" * 40)

# Load environment
load_dotenv()

# Check critical environment variables
required_vars = [
    "TELEGRAM_BOT_TOKEN",
    "SUPABASE_URL", 
    "SUPABASE_KEY",
    "OPENAI_API_KEY",
    "PAYSTACK_SECRET_KEY"
]

missing_vars = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * min(len(value), 20)}")
    else:
        print(f"❌ {var}: MISSING")
        missing_vars.append(var)

if missing_vars:
    print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
    print("Make sure your .env file is properly configured.")
else:
    print("\n✅ All required environment variables are set")

# Test key imports
try:
    print("\n🔄 Testing imports...")
    import flask
    print("✅ Flask imported")
    
    import supabase
    print("✅ Supabase imported")
    
    import openai
    print("✅ OpenAI imported")
    
    from paystack import get_paystack_service
    print("✅ Paystack service imported")
    
    from utils.bank_api import BankAPI
    print("✅ Bank API imported")
    
    print("\n🎉 All core imports successful!")
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)

print("\n✨ Environment test completed successfully!")
