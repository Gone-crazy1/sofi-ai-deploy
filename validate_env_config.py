#!/usr/bin/env python3
"""
Environment Configuration Validator for Sofi AI
Checks if all required environment variables are properly configured
"""

import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    print("✅ Loaded environment variables from .env file")

def check_required_variables() -> Tuple[List[str], List[str]]:
    """Check if all required environment variables are set"""
    
    required_vars = [
        # Core Application
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY',
        
        # Database
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SERVICE_ROLE_KEY',
        
        # Payment Gateway
        'MONNIFY_API_KEY',
        'MONNIFY_SECRET_KEY',
        'MONNIFY_CONTRACT_CODE',
        
        # Crypto API
        'BITNOB_SECRET_KEY',
    ]
    
    optional_vars = [
        'NELLOBYTES_USERID',
        'NELLOBYTES_APIKEY',
        'WEBHOOK_SECRET',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
    ]
    
    missing_required = []
    missing_optional = []
    
    print("\n🔍 Checking Required Variables:")
    print("=" * 50)
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_required.append(var)
            print(f"❌ {var}: Not configured")
        else:
            # Mask sensitive values
            if len(value) > 10:
                masked_value = value[:6] + "..." + value[-4:]
            else:
                masked_value = "***"
            print(f"✅ {var}: {masked_value}")
    
    print("\n🔍 Checking Optional Variables:")
    print("=" * 50)
    
    for var in optional_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_optional.append(var)
            print(f"⚠️  {var}: Not configured (optional)")
        else:
            if len(value) > 10:
                masked_value = value[:6] + "..." + value[-4:]
            else:
                masked_value = "***"
            print(f"✅ {var}: {masked_value}")
    
    return missing_required, missing_optional

def check_application_config():
    """Check application configuration settings"""
    print("\n🔍 Checking Application Configuration:")
    print("=" * 50)
    
    flask_env = os.getenv('FLASK_ENV', 'development')
    port = os.getenv('PORT', '5000')
    debug = os.getenv('DEBUG', 'true')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    print(f"🔧 FLASK_ENV: {flask_env}")
    print(f"🔧 PORT: {port}")
    print(f"🔧 DEBUG: {debug}")
    print(f"🔧 LOG_LEVEL: {log_level}")
    
    # Check if production settings are appropriate
    if flask_env == 'production':
        if debug.lower() == 'true':
            print("⚠️  WARNING: DEBUG is enabled in production!")
        
        monnify_url = os.getenv('MONNIFY_BASE_URL', '')
        if 'sandbox' in monnify_url.lower():
            print("⚠️  WARNING: Using sandbox Monnify URL in production!")
    
    return True

def check_api_key_formats():
    """Validate API key formats"""
    print("\n🔍 Checking API Key Formats:")
    print("=" * 50)
    
    # OpenAI API key should start with 'sk-'
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if openai_key and not openai_key.startswith('sk-'):
        print("❌ OpenAI API key should start with 'sk-'")
    elif openai_key:
        print("✅ OpenAI API key format looks correct")
    
    # Bitnob API key should start with 'sk.'
    bitnob_key = os.getenv('BITNOB_SECRET_KEY', '')
    if bitnob_key and not bitnob_key.startswith('sk.'):
        print("❌ Bitnob API key should start with 'sk.'")
    elif bitnob_key:
        print("✅ Bitnob API key format looks correct")
    
    # Supabase URL should contain 'supabase'
    supabase_url = os.getenv('SUPABASE_URL', '')
    if supabase_url and 'supabase' not in supabase_url.lower():
        print("❌ Supabase URL format looks incorrect")
    elif supabase_url:
        print("✅ Supabase URL format looks correct")
    
    return True

def generate_missing_vars_guide(missing_required: List[str], missing_optional: List[str]):
    """Generate a guide for missing variables"""
    if not missing_required and not missing_optional:
        return
    
    print("\n📝 Configuration Guide for Missing Variables:")
    print("=" * 50)
    
    if missing_required:
        print("\n❗ REQUIRED Variables (must be configured):")
        for var in missing_required:
            print(f"   • {var}")
    
    if missing_optional:
        print("\n⚠️  OPTIONAL Variables (recommended):")
        for var in missing_optional:
            print(f"   • {var}")
    
    print("\n📖 See ENV_CONFIGURATION_GUIDE.md for detailed setup instructions")

def main():
    """Main validation function"""
    print("🚀 Sofi AI Environment Configuration Validator")
    print("=" * 50)
    
    try:
        # Load environment
        load_environment()
        
        # Check variables
        missing_required, missing_optional = check_required_variables()
        
        # Check application config
        check_application_config()
        
        # Check API key formats
        check_api_key_formats()
        
        # Generate guide for missing variables
        generate_missing_vars_guide(missing_required, missing_optional)
        
        print("\n" + "=" * 50)
        
        if not missing_required:
            print("🎉 All required environment variables are configured!")
            print("✅ Your Sofi AI application should be ready to run")
            
            if missing_optional:
                print(f"⚠️  {len(missing_optional)} optional variables not configured")
            
            return True
        else:
            print(f"❌ {len(missing_required)} required variables are missing")
            print("🔧 Please configure the missing variables and run this script again")
            return False
            
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
