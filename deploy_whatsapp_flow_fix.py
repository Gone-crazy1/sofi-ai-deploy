#!/usr/bin/env python3
"""
Deploy WhatsApp Flow Integration Fix
Fix Sofi to use proper WhatsApp Flow (like Telegram Web App) instead of raw links
"""

import subprocess
import sys
import os

def deploy_whatsapp_flow_fix():
    """Deploy the WhatsApp Flow fix that makes it work like Telegram"""
    print("🌊 DEPLOYING WHATSAPP FLOW INTEGRATION FIX")
    print("=" * 50)
    print()
    
    print("🎯 WHAT THIS FIXES:")
    print("❌ OLD: Sofi sends raw links to everyone (even existing users)")  
    print("✅ NEW: Sofi uses WhatsApp Flow ID 1912417042942213 (like Telegram Web App)")
    print("✅ NEW: Smooth inline registration experience")
    print("✅ NEW: Proper user detection and onboarding flow")
    print()
    
    print("🔧 CHANGES DEPLOYED:")
    print("✅ Updated auto-onboarding to use WhatsApp Flow ID: 1912417042942213")
    print("✅ Added send_flow_message method to WhatsApp API")
    print("✅ Fixed flow data structure to match Meta's API requirements")
    print("✅ Smooth registration experience like Telegram")
    print()
    
    try:
        # Git operations
        print("📤 Committing changes...")
        subprocess.run(["git", "add", "."], check=True, cwd=os.getcwd())
        subprocess.run([
            "git", "commit", "-m", 
            "🌊 Fix WhatsApp Flow: Use Flow ID 1912417042942213 instead of raw links"
        ], check=True, cwd=os.getcwd())
        
        print("🚀 Pushing to production...")
        subprocess.run(["git", "push", "origin", "main"], check=True, cwd=os.getcwd())
        
        print()
        print("✅ WHATSAPP FLOW FIX DEPLOYED SUCCESSFULLY!")
        print()
        print("📱 TESTING INSTRUCTIONS:")
        print("1. Wait 2-3 minutes for Render deployment")
        print("2. Send a message from a NEW WhatsApp number")
        print("3. Verify Sofi shows WhatsApp Flow (not raw link)")
        print("4. Complete registration in the Flow")
        print("5. Check that account details are sent back in chat")
        print()
        print("🎯 EXPECTED BEHAVIOR:")
        print("• New users get WhatsApp Flow (inline registration)")
        print("• Existing users get normal AI responses")
        print("• No more raw links sent to anyone")
        print("• Smooth experience like Telegram")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy_whatsapp_flow_fix()
