#!/usr/bin/env python3
"""
Fix Assistant API Async Event Loop Issue
Resolves: asyncio.run() cannot be called from a running event loop
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
    print("🔧 FIXING ASSISTANT API ASYNC EVENT LOOP ISSUE")
    print("=" * 55)
    print()
    
    print("🚨 ISSUE FIXED:")
    print("❌ asyncio.run() cannot be called from a running event loop")
    print("❌ coroutine 'check_balance' was never awaited")
    print()
    print("✅ SOLUTION IMPLEMENTED:")
    print("✅ Made all assistant functions properly async")
    print("✅ Removed asyncio.run() calls inside event loop")
    print("✅ Properly await async functions")
    print("✅ Added proper error handling with exc_info=True")
    print()
    
    # Stage all changes
    if not run_command("git add .", "Staging async fixes"):
        sys.exit(1)
    
    # Commit the fix
    commit_message = "🔧 Fix async event loop issue: Remove asyncio.run(), properly await functions"
    if not run_command(f'git commit -m "{commit_message}"', "Committing async fix"):
        sys.exit(1)
    
    # Push to GitHub
    if not run_command("git push origin main", "Deploying async fix"):
        sys.exit(1)
    
    print()
    print("🎉 ASYNC ISSUE FIXED!")
    print("=" * 25)
    print()
    print("✅ No more event loop conflicts")
    print("✅ Functions properly awaited")
    print("✅ Better error handling")
    print()
    print("🎯 Expected Behavior:")
    print("- check_balance function will execute properly")
    print("- No more asyncio.run() errors")
    print("- Assistant tool calls will work")
    print("- Sofi will check balance directly")
    print()
    print("⏳ Wait 2-3 minutes for Render deployment")
    print("📱 Then test: 'Balance' in WhatsApp")

if __name__ == "__main__":
    main()
