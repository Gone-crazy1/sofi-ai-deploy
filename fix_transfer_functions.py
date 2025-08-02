#!/usr/bin/env python3
"""
Fix Send Money and Verify Account Functions
Resolves missing chat_id parameter and import errors
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
    print("💸 FIXING SEND MONEY & VERIFY ACCOUNT FUNCTIONS")
    print("=" * 55)
    print()
    
    print("🚨 ISSUES FIXED:")
    print("❌ send_money() missing 1 required positional argument: 'chat_id'")
    print("❌ cannot import name 'verify_account_name' from 'functions.transfer_functions'")
    print()
    print("✅ SOLUTIONS IMPLEMENTED:")
    print("✅ Fixed send_money parameter mapping")
    print("✅ Added phone number context to function calls")
    print("✅ Import verify_account_name from main.py")
    print("✅ Proper parameter passing for all functions")
    print()
    
    # Stage all changes
    if not run_command("git add .", "Staging function fixes"):
        sys.exit(1)
    
    # Commit the fix
    commit_message = "💸 Fix send_money and verify_account_name: proper parameters and imports"
    if not run_command(f'git commit -m "{commit_message}"', "Committing function fixes"):
        sys.exit(1)
    
    # Push to GitHub
    if not run_command("git push origin main", "Deploying function fixes"):
        sys.exit(1)
    
    print()
    print("🎉 TRANSFER FUNCTIONS FIXED!")
    print("=" * 35)
    print()
    print("✅ send_money now has proper chat_id parameter")
    print("✅ verify_account_name properly imported")
    print("✅ Phone number context passed correctly")
    print()
    print("🎯 Expected Behavior:")
    print("- 'Send 200 to 8104611794 Opay' → Works properly")
    print("- Account verification before transfer")
    print("- Proper transfer processing")
    print("- No missing parameter errors")
    print()
    print("⏳ Wait 2-3 minutes for Render deployment")
    print("📱 Then test: 'Send 100 to [account] [bank]' in WhatsApp")

if __name__ == "__main__":
    main()
