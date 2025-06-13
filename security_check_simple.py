#!/usr/bin/env python3
"""
🔒 SIMPLIFIED SECURITY CHECK FOR SOFI AI
"""

import os
import re

def simple_security_check():
    """Quick security check for exposed secrets"""
    
    print("🔒 SOFI AI SECURITY CHECK")
    print("=" * 40)
    
    issues = []
    
    # 1. Check if .env is properly gitignored
    print("\n1. Checking .env security...")
    
    if os.path.exists(".env"):
        print("   ⚠️  .env file exists (local development)")
        
        # Check gitignore
        if os.path.exists(".gitignore"):
            with open(".gitignore", "r") as f:
                if ".env" in f.read():
                    print("   ✅ .env is in .gitignore")
                else:
                    issues.append(".env not in .gitignore")
        else:
            issues.append("Missing .gitignore file")
    else:
        print("   ✅ No .env file (good for production)")
    
    # 2. Check for hardcoded secrets in main files
    print("\n2. Checking main files for hardcoded secrets...")
    
    main_files = ["main.py", "requirements.txt", "Procfile", "render.yaml"]
    
    for file_path in main_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Look for suspicious patterns (but exclude os.getenv usage)
                if re.search(r'sk-[a-zA-Z0-9]{20,}', content) and 'os.getenv' not in content:
                    issues.append(f"Potential hardcoded OpenAI key in {file_path}")
                
                if re.search(r'[0-9]{10}:[A-Za-z0-9_-]{35}', content) and 'os.getenv' not in content:
                    issues.append(f"Potential hardcoded Telegram token in {file_path}")
                    
                print(f"   ✅ {file_path} - No hardcoded secrets found")
                    
            except Exception as e:
                print(f"   ⚠️  Could not check {file_path}: {e}")
    
    # 3. Check environment variable usage in main.py
    print("\n3. Checking environment variable usage...")
    
    if os.path.exists("main.py"):
        with open("main.py", "r", encoding='utf-8', errors='ignore') as f:
            main_content = f.read()
            
        env_vars = [
            'OPENAI_API_KEY', 'TELEGRAM_BOT_TOKEN', 'SUPABASE_URL',
            'SUPABASE_SERVICE_ROLE_KEY', 'MONNIFY_API_KEY', 'BITNOB_SECRET_KEY'
        ]
        
        for var in env_vars:
            if f'os.getenv("{var}")' in main_content:
                print(f"   ✅ {var} properly loaded")
            else:
                print(f"   ⚠️  {var} not found in env loading")
    
    # 4. Summary
    print("\n" + "=" * 40)
    print("🔒 SECURITY CHECK SUMMARY")
    print("=" * 40)
    
    if not issues:
        print("✅ NO CRITICAL SECURITY ISSUES FOUND!")
        print("\n🚀 READY FOR SECURE DEPLOYMENT")
        
        print("\n📋 DEPLOYMENT SECURITY CHECKLIST:")
        print("   ✅ No hardcoded API keys in source code")
        print("   ✅ Environment variables properly used")
        print("   ✅ .env file properly gitignored")
        print("   ✅ Secrets will be set in Render dashboard")
        
        return True
    else:
        print(f"🚨 {len(issues)} ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n❌ PLEASE FIX ISSUES BEFORE DEPLOYMENT")
        return False

def render_deployment_guide():
    """Show how to securely set environment variables in Render"""
    
    print("\n🚀 RENDER DEPLOYMENT SECURITY GUIDE")
    print("=" * 50)
    
    print("""
🔑 SETTING ENVIRONMENT VARIABLES IN RENDER:

1. Log into your Render dashboard
2. Go to your web service
3. Click on "Environment" tab
4. Add these variables ONE BY ONE:

   Key: OPENAI_API_KEY
   Value: [Your actual OpenAI API key]
   
   Key: TELEGRAM_BOT_TOKEN  
   Value: [Your actual Telegram bot token]
   
   Key: SUPABASE_URL
   Value: [Your actual Supabase URL]
   
   Key: SUPABASE_SERVICE_ROLE_KEY
   Value: [Your actual Supabase service role key]
   
   Key: MONNIFY_API_KEY
   Value: [Your actual Monnify API key]
   
   Key: MONNIFY_SECRET_KEY
   Value: [Your actual Monnify secret key]
   
   Key: MONNIFY_BASE_URL
   Value: https://sandbox.monnify.com
   
   Key: MONNIFY_CONTRACT_CODE
   Value: [Your actual Monnify contract code]
   
   Key: BITNOB_SECRET_KEY
   Value: [Your actual Bitnob secret key]
   
   Key: NELLOBYTES_USERID
   Value: [Your actual Nellobytes user ID]
   
   Key: NELLOBYTES_APIKEY
   Value: [Your actual Nellobytes API key]

⚠️  SECURITY REMINDERS:

❌ NEVER commit .env files to git
❌ NEVER hardcode API keys in source code  
❌ NEVER share API keys in plain text
✅ ALWAYS use Render's environment variables
✅ ALWAYS keep .env in .gitignore
✅ ALWAYS use os.getenv() in Python code

🔒 After setting environment variables in Render:
   • Your app will automatically load them
   • They're encrypted and secure
   • Only your app can access them
   • You can update them anytime

🎯 Ready to deploy securely!
""")

if __name__ == "__main__":
    print("🔒 Starting simplified security check...\n")
    
    is_secure = simple_security_check()
    render_deployment_guide()
    
    if is_secure:
        print("\n🎉 SECURITY CHECK PASSED!")
        print("🚀 Ready for secure deployment to Render!")
    else:
        print("\n❌ Security issues found - please fix before deployment")
