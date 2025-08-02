#!/usr/bin/env python3
"""
Deploy Balance System & Auto-Onboarding Fixes
Fixes balance queries and implements automatic user onboarding
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    print("🏦 DEPLOYING BALANCE SYSTEM & AUTO-ONBOARDING FIXES")
    print("=" * 60)
    print()
    
    print("🐛 CRITICAL ISSUES FIXED:")
    print("❌ virtual_accounts.chat_id column doesn't exist")
    print("❌ Balance queries using wrong field names")
    print("❌ New WhatsApp users not getting onboarding links")
    print("❌ No user channel detection (WhatsApp vs Telegram)")
    print()
    print("✅ SOLUTIONS IMPLEMENTED:")
    print("✅ Fixed balance queries to use whatsapp_number and user_id")
    print("✅ Added channel detection (WhatsApp vs Telegram)")
    print("✅ Automatic onboarding for new WhatsApp users")
    print("✅ User resolution system with proper field mapping")
    print("✅ Balance sync from transaction history when needed")
    print("✅ Comprehensive error handling and fallbacks")
    print()
    
    # Stage all changes
    if not run_command("git add .", "Staging balance system fixes"):
        sys.exit(1)
    
    # Commit the fix
    commit_message = "🏦 Fix balance system: proper field mapping + auto-onboarding for WhatsApp users"
    if not run_command(f'git commit -m "{commit_message}"', "Committing balance fixes"):
        sys.exit(1)
    
    # Push to GitHub
    if not run_command("git push origin main", "Deploying balance system fixes"):
        sys.exit(1)
    
    print()
    print("🎉 BALANCE SYSTEM & AUTO-ONBOARDING DEPLOYED!")
    print("=" * 50)
    print()
    print("✅ Balance queries now use correct fields:")
    print("   - WhatsApp: users.whatsapp_number → virtual_accounts.user_id")
    print("   - Telegram: users.telegram_chat_id → virtual_accounts.user_id")
    print()
    print("✅ Auto-onboarding for new users:")
    print("   - New WhatsApp users automatically get onboarding link")
    print("   - Existing users proceed to Assistant API")
    print("   - Channel detection (WhatsApp vs Telegram)")
    print()
    print("🎯 Expected Behavior:")
    print("👤 New user messages Sofi → Auto onboarding link sent")
    print("👤 Existing user → 'Check balance' works properly")
    print("👤 No more 'virtual_accounts.chat_id' errors")
    print("👤 Balance sync from transactions if needed")
    print()
    print("⏳ Wait 2-3 minutes for Render deployment")
    print("📱 Test with new WhatsApp number to verify auto-onboarding")

if __name__ == "__main__":
    main()
