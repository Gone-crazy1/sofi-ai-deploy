# 🚀 RENDER DEPLOYMENT COMMANDS

## Step 1: Final Git Commit
```powershell
# Commit all current changes
git add .
git commit -m "🚀 Production Ready: Core Sofi AI with Sharp AI disabled for stability"
git push origin main
```

## Step 2: Environment Variables for Render
Copy these environment variables to your Render dashboard:

```
SUPABASE_URL=https://kjvfksgpihftzujffmvz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
OPENAI_API_KEY=your_openai_key_here
TELEGRAM_BOT_TOKEN=your_telegram_token_here
MONNIFY_API_KEY=your_monnify_api_key_here
MONNIFY_SECRET_KEY=your_monnify_secret_key_here
BITNOB_API_KEY=your_bitnob_api_key_here
PORT=5000
```

## Step 3: Render Configuration
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Python Version**: 3.9 or higher

## Step 4: Post-Deployment Webhook Setup

### Telegram Webhook:
```powershell
# Replace YOUR_BOT_TOKEN and YOUR_RENDER_URL
$botToken = "YOUR_BOT_TOKEN"
$renderUrl = "https://your-app-name.onrender.com"
Invoke-WebRequest -Uri "https://api.telegram.org/bot$botToken/setWebhook?url=$renderUrl/webhook" -Method POST
```

### Monnify Webhook:
- Log into Monnify dashboard
- Set webhook URL to: `https://your-app-name.onrender.com/monnify_webhook`
- Enable events: Transaction Successful, Transaction Failed

## Step 5: Production Testing
```powershell
# Test health endpoint
Invoke-WebRequest -Uri "https://your-app-name.onrender.com/health" -Method GET

# Test Telegram bot with a message
# Send "Hello" to your bot via Telegram
```

## 🎯 YOUR SOFI AI IS PRODUCTION READY! 🚀
