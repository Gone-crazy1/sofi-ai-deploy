"""
🚀 SOFI AI PRODUCTION DEPLOYMENT CHECKLIST
==========================================

Pre-deployment verification and deployment guide
"""

import os
import sys
from pathlib import Path

def check_deployment_readiness():
    """Check if Sofi AI is ready for deployment"""
    print("🔍 SOFI AI DEPLOYMENT READINESS CHECK")
    print("=" * 50)
    
    checks = []
    
    # 1. Check main.py loads
    try:
        import main
        print("✅ main.py loads successfully")
        checks.append(True)
    except Exception as e:
        print(f"❌ main.py failed to load: {e}")
        checks.append(False)
    
    # 2. Check requirements.txt exists
    if Path("requirements.txt").exists():
        print("✅ requirements.txt found")
        checks.append(True)
    else:
        print("❌ requirements.txt missing")
        checks.append(False)
    
    # 3. Check .env.example exists
    if Path(".env.example").exists():
        print("✅ .env.example found")
        checks.append(True)
    else:
        print("❌ .env.example missing")
        checks.append(False)
    
    # 4. Check Nigerian banks database
    try:
        from utils.nigerian_banks import NIGERIAN_BANKS
        bank_count = len(NIGERIAN_BANKS)
        if bank_count >= 50:
            print(f"✅ Nigerian banks database ready ({bank_count} banks)")
            checks.append(True)
        else:
            print(f"❌ Not enough banks ({bank_count} < 50)")
            checks.append(False)
    except Exception as e:
        print(f"❌ Banks database error: {e}")
        checks.append(False)
    
    # 5. Check Monnify integration
    try:
        from utils.real_monnify_transfer import MonnifyTransferAPI
        print("✅ Monnify API integration ready")
        checks.append(True)
    except Exception as e:
        print(f"❌ Monnify integration error: {e}")
        checks.append(False)
    
    # 6. Check Flask app
    try:
        from main import app
        print("✅ Flask app configured")
        checks.append(True)
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        checks.append(False)
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n📊 READINESS SCORE: {passed}/{total}")
    
    if passed == total:
        print("🚀 ✅ SOFI AI IS READY FOR DEPLOYMENT!")
        return True
    else:
        print("⚠️ Some issues need to be resolved first")
        return False

def create_deployment_files():
    """Create necessary deployment files"""
    print("\n📦 Creating deployment files...")
    
    # Create Procfile for Heroku/Render
    procfile_content = "web: gunicorn main:app --bind 0.0.0.0:$PORT"
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    print("✅ Procfile created")
    
    # Create runtime.txt for Python version
    runtime_content = "python-3.11.0"
    with open("runtime.txt", "w") as f:
        f.write(runtime_content)
    print("✅ runtime.txt created")
    
    # Create deployment instructions
    deploy_instructions = """
🚀 SOFI AI DEPLOYMENT INSTRUCTIONS
==================================

## Option 1: Deploy to Render.com (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy Sofi AI - Production Ready"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com
   - Connect your GitHub repository
   - Create new "Web Service"
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn main:app --bind 0.0.0.0:$PORT`
   - Add environment variables from .env

3. **Set Environment Variables:**
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   OPENAI_API_KEY=your_openai_api_key
   MONNIFY_API_KEY=your_monnify_api_key
   MONNIFY_SECRET_KEY=your_monnify_secret_key
   MONNIFY_CONTRACT_CODE=your_monnify_contract_code
   ADMIN_CHAT_IDS=your_admin_telegram_ids
   ```

## Option 2: Deploy to Heroku

1. **Install Heroku CLI**
2. **Login and create app:**
   ```bash
   heroku login
   heroku create sofi-ai-banking-bot
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set SUPABASE_URL=your_url
   # ... add all other env vars
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

## Option 3: Deploy to Railway

1. **Connect GitHub to Railway**
2. **Set environment variables**
3. **Deploy automatically from main branch**

## Post-Deployment Steps:

1. **Set Telegram Webhook:**
   ```bash
   curl -F "url=https://your-app-url.com/webhook" \
   https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook
   ```

2. **Test the deployment:**
   - Send message to your Telegram bot
   - Check logs for any errors
   - Test transfer flow: "Send 1000 to GTBank 0123456789"

3. **Monitor:**
   - Check application logs
   - Monitor Supabase database
   - Watch Monnify API responses

## Security Notes:
- ✅ All sensitive data in environment variables
- ✅ Admin access properly configured  
- ✅ PIN verification for transfers
- ✅ Rate limiting built-in
- ✅ Error handling implemented

## Features Ready:
🏦 Real money transfers via Monnify API
💳 58+ Nigerian banks (including all fintechs)
🧠 Enhanced NLP for natural language
🔐 Admin security and user authentication
📱 Nigerian expressions and user-friendly UI
🤖 ChatGPT-4o-latest with custom prompt
"""
    
    with open("DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(deploy_instructions)
    print("✅ DEPLOYMENT_GUIDE.md created")

def main():
    """Run deployment preparation"""
    # Check readiness
    if check_deployment_readiness():
        # Create deployment files
        create_deployment_files()
        
        print("\n🚀 DEPLOYMENT PREPARATION COMPLETE!")
        print("=" * 50)
        print("📋 Next Steps:")
        print("1. Review DEPLOYMENT_GUIDE.md")
        print("2. Commit and push to GitHub")
        print("3. Deploy to your chosen platform")
        print("4. Set environment variables")
        print("5. Configure Telegram webhook")
        print("6. Test with real users!")
        print("\n💰 Sofi AI is ready to handle real Nigerian banking! 🇳🇬")
    else:
        print("\n⚠️ Fix the issues above before deployment")

if __name__ == "__main__":
    main()
