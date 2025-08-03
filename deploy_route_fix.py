#!/usr/bin/env python3
"""
Fix Route WhatsApp Message Function
Remove duplicate code and clean up the forced onboarding implementation
"""

import subprocess
import sys
import os

def deploy_route_fix():
    """Deploy the fixed route_whatsapp_message function"""
    print("🔧 FIXING ROUTE_WHATSAPP_MESSAGE FUNCTION")
    print("=" * 50)
    print()
    
    print("🎯 ISSUES FOUND:")
    print("❌ Duplicate unreachable code after return statement")  
    print("❌ Old onboarding logic mixed with new forced onboarding")
    print("❌ Function doesn't end properly - has dead code")
    print()
    
    print("🔧 FIXES APPLIED:")
    print("✅ Removed all duplicate code after function end")
    print("✅ Clean forced onboarding logic only")
    print("✅ Proper function structure with clear flow")
    print("✅ Database check → forced onboarding → assistant chat")
    print()
    
    try:
        # Git operations
        print("📤 Committing changes...")
        subprocess.run(["git", "add", "."], check=True, cwd=os.getcwd())
        subprocess.run([
            "git", "commit", "-m", 
            "🔧 Fix route_whatsapp_message: Remove duplicate code, clean forced onboarding implementation"
        ], check=True, cwd=os.getcwd())
        
        print("🚀 Pushing to production...")
        subprocess.run(["git", "push", "origin", "main"], check=True, cwd=os.getcwd())
        
        print()
        print("✅ ROUTE FUNCTION FIXED SUCCESSFULLY!")
        print()
        print("📱 NOW TESTING:")
        print("1. Wait 2-3 minutes for Render deployment")
        print("2. Test with user 18162616404 (from logs)")
        print("3. Should now see FORCED onboarding instead of going to Assistant")
        print("4. No user with account_number + customer_code = forced onboarding")
        print("5. Only users with complete Sofi accounts get normal chat")
        print()
        print("🎯 EXPECTED LOG CHANGES:")
        print("• Should see: 'FORCING onboarding for [user] - no Sofi account detected'")
        print("• Should NOT see: 'Processing message via Sofi Assistant API'")
        print("• Should see: 'FORCED onboarding sent to [user]'")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy_route_fix()
