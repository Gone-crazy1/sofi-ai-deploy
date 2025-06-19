#!/usr/bin/env python3
"""
🔍 SIMPLE SYSTEM CHECK

Basic system health check for Sofi AI
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔍 SOFI AI SYSTEM CHECK")
    print("=" * 40)
    
    # Check Python version
    print(f"🐍 Python Version: {sys.version}")
    
    # Check environment variables
    env_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY", 
        "TELEGRAM_BOT_TOKEN",
        "MONNIFY_API_KEY",
        "MONNIFY_SECRET_KEY"
    ]
    
    print("\n🔐 Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configured")
        else:
            print(f"❌ {var}: Missing")
    
    # Check file structure
    print("\n📁 Key Files:")
    key_files = [
        "main.py",
        "admin_dashboard.py", 
        "utils/admin_command_handler.py",
        "utils/admin_profit_manager.py",
        "monnify/monnify_api.py",
        "monnify/monnify_webhook.py"
    ]
    
    for file in key_files:
        if os.path.exists(file):
            print(f"✅ {file}: Exists")
        else:
            print(f"❌ {file}: Missing")
    
    # Try basic imports
    print("\n📦 Module Imports:")
    modules = [
        ("supabase", "supabase"),
        ("dotenv", "python-dotenv"),
        ("requests", "requests"),
        ("flask", "flask")
    ]
    
    for module, package in modules:
        try:
            __import__(module)
            print(f"✅ {module}: Available")
        except ImportError:
            print(f"❌ {module}: Missing (install with: pip install {package})")
    
    print("\n✅ Basic system check complete!")

if __name__ == "__main__":
    main()
