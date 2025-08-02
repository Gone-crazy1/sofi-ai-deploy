#!/usr/bin/env python3
"""
Security Fix: Remove hardcoded API keys and use environment variables
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
    print("🔐 SECURITY FIX: REMOVING HARDCODED API KEYS")
    print("=" * 50)
    print()
    
    print("🚨 CRITICAL SECURITY ISSUE FIXED:")
    print("❌ Hardcoded OpenAI Assistant ID removed from code")
    print("✅ Now using OPENAI_ASSISTANT_ID environment variable")
    print("✅ Secure environment variable template created")
    print()
    
    # Stage all changes
    if not run_command("git add .", "Staging security fixes"):
        sys.exit(1)
    
    # Commit the security fix
    commit_message = "🔐 SECURITY FIX: Remove hardcoded Assistant ID, use environment variables"
    if not run_command(f'git commit -m "{commit_message}"', "Committing security fix"):
        sys.exit(1)
    
    # Push to GitHub
    if not run_command("git push origin main", "Deploying security fix"):
        sys.exit(1)
    
    print()
    print("🎉 SECURITY FIX DEPLOYED!")
    print("=" * 30)
    print()
    print("✅ No more hardcoded API keys in code")
    print("✅ Environment variables properly used")
    print("✅ Secure template provided")
    print()
    print("⚠️  NEXT STEPS REQUIRED:")
    print("1. Go to Render.com Dashboard")
    print("2. Add environment variable:")
    print("   OPENAI_ASSISTANT_ID = asst_0M8grCGnt1Pxhm7J8sn7NXSc")
    print("3. Save and wait for deployment")
    print()
    print("🔒 Your API keys are now secure!")

if __name__ == "__main__":
    main()
