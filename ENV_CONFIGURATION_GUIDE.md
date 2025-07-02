# Environment Variables Configuration Guide

## 📋 Required Environment Variables

Your Sofi AI project requires the following environment variables to be configured in the `.env` file:

### 🤖 Telegram Bot Configuration
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```
**How to get it:**
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Copy the token provided

### 🧠 OpenAI Configuration
```bash
OPENAI_API_KEY=your_openai_api_key_here
```
**How to get it:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

### 🗄️ Supabase Database Configuration
```bash
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```
**How to get it:**
1. Go to your Supabase project dashboard
2. Navigate to Settings > API
3. Copy the Project URL and API Keys

### 🏦 Monnify Payment Gateway (Primary)
```bash
MONNIFY_API_KEY=your_monnify_api_key_here
MONNIFY_SECRET_KEY=your_monnify_secret_key_here
MONNIFY_CONTRACT_CODE=your_monnify_contract_code_here
MONNIFY_BASE_URL=https://sandbox.monnify.com
```
**How to get it:**
1. Sign up at https://monnify.com
2. Complete verification process
3. Get credentials from your dashboard
4. Use sandbox URL for testing, production URL for live

### ₿ Bitnob Crypto Configuration
```bash
BITNOB_SECRET_KEY=your_bitnob_secret_key_here
BITNOB_BASE_URL=https://api.bitnob.co
```
**How to get it:**
1. Sign up at https://bitnob.com
2. Complete KYC verification
3. Generate API keys from dashboard

### 📱 NelloByte SMS (Optional)
```bash
NELLOBYTES_USERID=your_nellobytes_userid_here
NELLOBYTES_APIKEY=your_nellobytes_api_key_here
```
**How to get it:**
1. Sign up at NelloByte SMS service
2. Get credentials from dashboard

## 🔧 Application Configuration

### Development Settings
```bash
FLASK_ENV=development
DEBUG=true
PORT=5000
LOG_LEVEL=INFO
```

### Production Settings
```bash
FLASK_ENV=production
DEBUG=false
PORT=5000
LOG_LEVEL=WARNING
MONNIFY_BASE_URL=https://api.monnify.com
```

## 🛡️ Security Configuration
```bash
SECRET_KEY=your_flask_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
WEBHOOK_SECRET=your_webhook_secret_here
```

**Generate secure keys:**
```python
import secrets
print(secrets.token_urlsafe(32))  # Generate a secure key
```

## 🚦 Rate Limiting
```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## ✅ Configuration Checklist

- [ ] Telegram bot token configured
- [ ] OpenAI API key configured
- [ ] Supabase database configured
- [ ] Monnify payment gateway configured
- [ ] Bitnob crypto API configured
- [ ] Security keys generated
- [ ] Environment set to development/production
- [ ] Logging configured
- [ ] Rate limits set

## 🔍 Testing Configuration

Run this command to test your environment configuration:
```bash
python comprehensive_pre_deployment_test.py
```

## 🚨 Security Notes

1. **Never commit `.env` file to version control**
2. **Use strong, unique secret keys**
3. **Use sandbox URLs for testing**
4. **Rotate API keys regularly**
5. **Set proper rate limits**

## 📝 Environment File Template

A complete `.env` template has been created with all required variables. Fill in your actual values before running the application.

## 🆘 Troubleshooting

### Common Issues:
1. **Missing environment variables**: Check if all required variables are set
2. **Invalid API keys**: Verify keys are correct and active
3. **Database connection**: Ensure Supabase URL and keys are valid
4. **Payment gateway**: Verify Monnify credentials and base URL
5. **Crypto API**: Check Bitnob API key and account status

### Debug Commands:
```bash
# Check environment variables
python -c "import os; print([k for k in os.environ.keys() if 'SUPABASE' in k])"

# Test database connection
python check_supabase_data.py

# Test API connections
python comprehensive_system_audit.py
```
