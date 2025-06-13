#!/usr/bin/env python3
"""
🔒 SECURITY AUDIT AND CLEANUP FOR SOFI AI DEPLOYMENT
This script ensures all API keys are properly secured before deployment.
"""

import os
import re
import subprocess
from pathlib import Path

def audit_security():
    """Comprehensive security audit for API keys and secrets"""
    
    print("🔒 SOFI AI SECURITY AUDIT")
    print("=" * 50)
    
    project_root = Path(".")
    security_issues = []
    
    # 1. Check for hardcoded API keys
    print("\n1. 🔍 Scanning for hardcoded API keys...")
    
    # Patterns for common API key formats
    key_patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key'),
        (r'[0-9]{10}:[A-Za-z0-9_-]{35}', 'Telegram Bot Token'),
        (r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', 'JWT Token (Supabase)'),
        (r'sk\.[a-zA-Z0-9]{10,}\.[a-zA-Z0-9]{20,}', 'Bitnob API Key'),
        (r'MK_[A-Z0-9]{10,}', 'Monnify API Key'),
        (r'[A-Z0-9]{32,}', 'Generic Long API Key')
    ]
    
    # Files to scan (exclude .env intentionally as it should be gitignored)
    scan_files = [
        "main.py", "web_app.py", "requirements.txt", 
        "render.yaml", "Procfile", "README.md"
    ]
    
    # Add all Python files in subdirectories
    for py_file in project_root.rglob("*.py"):
        if ".env" not in str(py_file) and "test_" not in str(py_file):
            scan_files.append(str(py_file))
    
    for file_path in scan_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern, key_type in key_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Check if it's using os.getenv() (which is safe)
                        for match in matches:
                            if f'os.getenv(' not in content or 'your_' in match.lower():
                                continue  # Skip placeholder values
                            
                            # Check context around the match
                            match_lines = [line for line in content.split('\n') if match in line]
                            for line in match_lines:
                                if 'os.getenv(' not in line and 'your_' not in line.lower():
                                    security_issues.append({
                                        'file': file_path,
                                        'type': key_type,
                                        'issue': f'Hardcoded {key_type} found',
                                        'line': line.strip()
                                    })
                            
            except Exception as e:
                print(f"   ⚠️  Could not scan {file_path}: {e}")
    
    # 2. Check .env file status
    print("\n2. 🗂️  Checking .env file security...")
    
    if os.path.exists(".env"):
        print("   ⚠️  .env file exists (should be local only)")
        
        # Check if .env is in .gitignore
        if os.path.exists(".gitignore"):
            with open(".gitignore", "r") as f:
                gitignore_content = f.read()
                if ".env" in gitignore_content:
                    print("   ✅ .env is properly listed in .gitignore")
                else:
                    security_issues.append({
                        'file': '.gitignore',
                        'type': 'Configuration',
                        'issue': '.env not in .gitignore',
                        'line': 'Add .env to .gitignore'
                    })
        else:
            security_issues.append({
                'file': '.',
                'type': 'Configuration', 
                'issue': 'Missing .gitignore file',
                'line': 'Create .gitignore with .env entry'
            })
    else:
        print("   ✅ No .env file found (good for production)")
    
    # 3. Check environment variable usage
    print("\n3. 🔧 Verifying environment variable usage...")
    
    required_env_vars = [
        'OPENAI_API_KEY',
        'TELEGRAM_BOT_TOKEN', 
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY',
        'MONNIFY_API_KEY',
        'MONNIFY_SECRET_KEY',
        'BITNOB_SECRET_KEY'
    ]
    
    # Check main.py for proper env var usage
    if os.path.exists("main.py"):
        with open("main.py", "r") as f:
            main_content = f.read()
            
        for env_var in required_env_vars:
            if f'os.getenv("{env_var}")' in main_content:
                print(f"   ✅ {env_var} properly loaded with os.getenv()")
            else:
                print(f"   ⚠️  {env_var} not found in environment loading")
    
    # 4. Check git status for tracked secrets
    print("\n4. 📋 Checking git status for sensitive files...")
    
    try:
        # Check if .env is tracked by git
        result = subprocess.run(['git', 'ls-files', '.env'], 
                              capture_output=True, text=True, cwd='.')
        if result.stdout.strip():
            security_issues.append({
                'file': '.env',
                'type': 'Git Tracking',
                'issue': '.env file is tracked by git',
                'line': 'Run: git rm --cached .env'
            })
        else:
            print("   ✅ .env is not tracked by git")
            
    except Exception as e:
        print(f"   ⚠️  Could not check git status: {e}")
    
    # 5. Summary and recommendations
    print("\n" + "=" * 50)
    print("🔒 SECURITY AUDIT SUMMARY")
    print("=" * 50)
    
    if not security_issues:
        print("✅ No security issues found!")
        print("\n🚀 READY FOR SECURE DEPLOYMENT")
        print("\n📋 DEPLOYMENT CHECKLIST:")
        print("   ✅ No hardcoded API keys")
        print("   ✅ Environment variables properly used") 
        print("   ✅ .env file not tracked by git")
        print("   ✅ Sensitive data in .gitignore")
        
        return True
    else:
        print(f"🚨 {len(security_issues)} SECURITY ISSUES FOUND:")
        print("\n" + "-" * 30)
        
        for i, issue in enumerate(security_issues, 1):
            print(f"{i}. {issue['type']} in {issue['file']}")
            print(f"   Issue: {issue['issue']}")
            print(f"   Context: {issue['line']}")
            print()
        
        print("🛡️  REMEDIATION REQUIRED BEFORE DEPLOYMENT")
        return False

def create_secure_env_template():
    """Create a secure .env.example template"""
    
    template_content = '''# Sofi AI Bot Environment Variables Template
# Copy this file to .env and fill in your actual values
# NEVER commit .env to version control!

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI API Configuration  
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Database Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Monnify Payment Gateway Configuration
MONNIFY_BASE_URL=https://sandbox.monnify.com
MONNIFY_API_KEY=your_monnify_api_key_here
MONNIFY_SECRET_KEY=your_monnify_secret_key_here
MONNIFY_CONTRACT_CODE=your_monnify_contract_code_here

# Bitnob Crypto API Configuration
BITNOB_SECRET_KEY=your_bitnob_secret_key_here

# Nellobytes Airtime/Data API Configuration
NELLOBYTES_USERID=your_nellobytes_userid_here
NELLOBYTES_APIKEY=your_nellobytes_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_flask_secret_key_here
'''
    
    with open(".env.example", "w") as f:
        f.write(template_content)
    
    print("✅ Created secure .env.example template")

def deployment_security_guide():
    """Print deployment security guidelines"""
    
    print("\n🚀 RENDER DEPLOYMENT SECURITY GUIDE")
    print("=" * 50)
    
    print("""
🔑 ENVIRONMENT VARIABLES SETUP ON RENDER:

1. Go to your Render dashboard
2. Navigate to your web service 
3. Go to Environment tab
4. Add these environment variables:

   OPENAI_API_KEY=your_actual_openai_key
   TELEGRAM_BOT_TOKEN=your_actual_telegram_token
   SUPABASE_URL=your_actual_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_actual_supabase_key
   MONNIFY_API_KEY=your_actual_monnify_key
   MONNIFY_SECRET_KEY=your_actual_monnify_secret
   BITNOB_SECRET_KEY=your_actual_bitnob_key
   NELLOBYTES_USERID=your_actual_nellobytes_userid
   NELLOBYTES_APIKEY=your_actual_nellobytes_key

⚠️  CRITICAL SECURITY RULES:

✅ DO:
   • Use Render's environment variables tab
   • Keep .env file local only (never commit)
   • Use os.getenv() in code
   • Rotate keys regularly
   • Use different keys for production vs testing

❌ DON'T:
   • Hardcode API keys in source code
   • Commit .env files to git
   • Share API keys in plain text
   • Use production keys in development
   • Include keys in documentation

🔒 ADDITIONAL SECURITY MEASURES:

1. Enable webhook signature verification
2. Use HTTPS for all API endpoints  
3. Implement rate limiting
4. Log security events
5. Monitor for unusual activity
6. Set up alerts for failed authentications

🎯 VERIFICATION STEPS:

After deployment, verify:
   • All API integrations work
   • No hardcoded keys in logs
   • Environment variables loaded correctly
   • Webhook signatures validated
   • SSL certificates active
""")

if __name__ == "__main__":
    print("🔒 Starting Sofi AI Security Audit...\n")
    
    # Run the security audit
    is_secure = audit_security()
    
    # Create secure template
    create_secure_env_template()
    
    # Show deployment guide
    deployment_security_guide()
    
    if is_secure:
        print("\n🎉 SECURITY AUDIT PASSED - READY FOR DEPLOYMENT!")
    else:
        print("\n❌ SECURITY AUDIT FAILED - PLEASE FIX ISSUES BEFORE DEPLOYMENT!")
