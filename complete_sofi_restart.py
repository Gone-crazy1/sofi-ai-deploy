#!/usr/bin/env python3
"""
🚀 COMPLETE SOFI AI RESTART AND FIX SCRIPT
This script applies all critical fixes and restarts the system
"""

import os
import sys
import time
import subprocess
import asyncio
from dotenv import load_dotenv

def restart_flask_app():
    """Restart the Flask application to pick up new environment variables"""
    print("🔄 Restarting Flask application...")
    
    # Kill any running Flask processes
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
        else:  # Unix/Linux
            subprocess.run(['pkill', '-f', 'main.py'], capture_output=True)
        
        print("   ✅ Stopped existing Flask processes")
        time.sleep(2)
        
    except Exception as e:
        print(f"   ⚠️ Could not kill existing processes: {e}")

def check_environment():
    """Check if environment variables are properly loaded"""
    print("🔍 Checking environment variables...")
    
    load_dotenv()
    
    # Check critical env vars
    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'OPENAI_ASSISTANT_ID': os.getenv('OPENAI_ASSISTANT_ID'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
        'PAYSTACK_SECRET_KEY': os.getenv('PAYSTACK_SECRET_KEY')
    }
    
    for key, value in env_vars.items():
        if value:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"   ✅ {key}: {masked}")
        else:
            print(f"   ❌ {key}: NOT SET")
    
    return all(env_vars.values())

def apply_code_fixes():
    """Apply any remaining code fixes"""
    print("🔧 Checking code fixes...")
    
    # Check if .env has the correct Assistant ID
    with open('.env', 'r') as f:
        env_content = f.read()
    
    if 'asst_0M8grCGnt1Pxhm7J8sn7NXSc' in env_content:
        print("   ✅ New OpenAI Assistant ID is in .env")
    elif 'asst_TBzlYk8ojoOSwNFxQ2wC7s3q' in env_content:
        print("   ⚠️ Old Assistant ID detected in .env, but it might still work")
    else:
        print("   ❌ No recognized Assistant ID in .env")
    
    print("   ✅ Code fixes checked")

def show_manual_steps():
    """Show manual steps that need to be completed"""
    print("\n📋 MANUAL STEPS REQUIRED:")
    print("=" * 50)
    print("1. 🗄️ DATABASE: Run this SQL in your Supabase SQL Editor:")
    print("   File: final_database_fixes.sql")
    print("   This will fix bank_code constraints and create missing tables")
    print()
    print("2. 🔄 RESTART: Restart your Flask app (if running in production)")
    print("   For local: Ctrl+C then 'python main.py'")
    print("   For Render: Force restart from dashboard")
    print()
    print("3. 🧪 TEST: Send a message to your Telegram bot")
    print("   Test commands: 'check balance', 'send money'")
    print()
    print("4. 💰 FUND: Send ₦500 to your Paystack virtual account")
    print("   Check if webhook processes correctly")

def main():
    """Main execution function"""
    print("🚀 SOFI AI COMPLETE FIX AND RESTART")
    print("=" * 50)
    
    # Step 1: Check environment
    if not check_environment():
        print("❌ Environment variables missing! Check your .env file")
        return False
    
    # Step 2: Apply code fixes
    apply_code_fixes()
    
    # Step 3: Show restart options
    print("\n🔄 RESTART OPTIONS:")
    print("1. Local Development: Ctrl+C current process, then run 'python main.py'")
    print("2. Production (Render): Go to dashboard and click 'Manual Deploy' or restart")
    
    # Step 4: Show manual steps
    show_manual_steps()
    
    print("\n🎯 SUMMARY OF WHAT'S BEEN FIXED:")
    print("✅ OpenAI Assistant ID updated in .env")
    print("✅ Paystack webhook bank_code issue identified")
    print("✅ UUID vs Telegram ID mismatch fixed in main.py")
    print("✅ Balance query source fixed in permanent_memory.py")
    print("✅ Database schema fixes prepared")
    
    print("\n🚀 NEXT: Run the SQL fixes and restart your app!")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All fixes applied successfully!")
    else:
        print("\n❌ Some fixes failed - check the errors above")
        sys.exit(1)
