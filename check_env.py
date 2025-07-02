#!/usr/bin/env python3
"""
Environment Variable Checker
Check if all required environment variables are properly loaded
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Environment Variable Check")
print("=" * 40)

# Check all required variables
required_vars = [
    'SUPABASE_URL',
    'SUPABASE_SERVICE_ROLE_KEY', 
    'SUPABASE_KEY',
    'PAYSTACK_SECRET_KEY',
    'PAYSTACK_PUBLIC_KEY'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show first 10 and last 4 characters for security
        if len(value) > 14:
            masked = value[:10] + '...' + value[-4:]
        else:
            masked = value[:4] + '...' if len(value) > 4 else value
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: Not set")

print("\n📄 .env file check:")
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ {env_file} exists")
    with open(env_file, 'r') as f:
        lines = f.readlines()
    print(f"📝 Contains {len(lines)} lines")
    
    # Check for key patterns (without showing values)
    for line in lines[:10]:  # Show first 10 lines only
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            print(f"   - {key}")
else:
    print(f"❌ {env_file} not found")

print("\n🔧 Next steps:")
print("1. Make sure your .env file exists in the project root")
print("2. Check that SUPABASE_SERVICE_ROLE_KEY is the correct service role key")
print("3. Verify PAYSTACK_SECRET_KEY starts with 'sk_test_' or 'sk_live_'")
