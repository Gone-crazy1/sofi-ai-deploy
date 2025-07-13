#!/usr/bin/env python3
"""
Test environment setup for PIN verification testing
Sets up minimal environment variables to avoid import errors
"""

import os
from datetime import datetime

def setup_test_environment():
    """Setup minimal environment variables for testing"""
    
    print("🔧 Setting up test environment...")
    
    # Set minimal required environment variables
    os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
    os.environ['SUPABASE_KEY'] = 'test_key'
    os.environ['PAYSTACK_SECRET_KEY'] = 'sk_test_dummy_key_for_testing'
    os.environ['PAYSTACK_PUBLIC_KEY'] = 'pk_test_dummy_key_for_testing'
    os.environ['TELEGRAM_TOKEN'] = 'dummy_telegram_token'
    os.environ['OPENAI_API_KEY'] = 'dummy_openai_key'
    
    # Optional environment variables
    os.environ.setdefault('ENVIRONMENT', 'testing')
    os.environ.setdefault('DEBUG', 'true')
    
    print("✅ Test environment configured")
    
    # Display what we've set
    test_vars = [
        'SUPABASE_URL', 'SUPABASE_KEY', 'PAYSTACK_SECRET_KEY', 
        'PAYSTACK_PUBLIC_KEY', 'TELEGRAM_TOKEN', 'OPENAI_API_KEY'
    ]
    
    print("\n📋 Environment variables set:")
    for var in test_vars:
        value = os.environ.get(var, 'NOT SET')
        # Mask sensitive values
        if 'KEY' in var or 'TOKEN' in var:
            display_value = value[:10] + '...' if len(value) > 10 else value
        else:
            display_value = value
        print(f"   {var}: {display_value}")

if __name__ == "__main__":
    setup_test_environment()
    print(f"\n🕐 Environment ready at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
