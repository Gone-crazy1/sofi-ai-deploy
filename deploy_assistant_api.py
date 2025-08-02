#!/usr/bin/env python3
"""
Deploy Sofi Assistant API Integration
This fixes Sofi to use OpenAI Assistant API like Telegram instead of basic GPT
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    print("🚀 DEPLOYING SOFI ASSISTANT API INTEGRATION")
    print("=" * 50)
    print()
    
    print("📋 What this fixes:")
    print("✅ Replaces basic GPT with OpenAI Assistant API")
    print("✅ Creates threads for each WhatsApp user")
    print("✅ Enables intelligent function calling like Telegram")
    print("✅ Uses secure environment variables (no hardcoded keys)")
    print()
    print("⚠️  IMPORTANT: Update Render environment variables:")
    print("   Add OPENAI_ASSISTANT_ID to your Render environment")
    print()
    
    # Stage all changes
    if not run_command("git add .", "Staging all changes"):
        sys.exit(1)
    
    # Commit the changes
    commit_message = "🤖 Implement OpenAI Assistant API for WhatsApp - Fix Sofi intelligence like Telegram"
    if not run_command(f'git commit -m "{commit_message}"', "Committing Assistant API integration"):
        sys.exit(1)
    
    # Push to GitHub (triggers Render deployment)
    if not run_command("git push origin main", "Deploying to Render via GitHub"):
        sys.exit(1)
    
    print()
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 30)
    print()
    print("✅ Sofi now uses OpenAI Assistant API")
    print("✅ Each user gets their own thread")
    print("✅ Intelligent function calling enabled")
    print("✅ Should work exactly like Telegram version")
    print()
    print("🎯 Expected Results:")
    print("- 'Balance' → Sofi checks balance directly")
    print("- 'Send money' → Sofi processes transfer")
    print("- No more generic 'log into app' responses")
    print("- Smart intent detection and function execution")
    print()
    print("⏳ Wait 2-3 minutes for Render deployment to complete")
    print("📱 Then test Sofi in WhatsApp!")

if __name__ == "__main__":
    main()
