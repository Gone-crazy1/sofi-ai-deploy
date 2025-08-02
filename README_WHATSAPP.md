# Sofi AI - WhatsApp Banking Assistant

🚀 **Complete WhatsApp-only banking assistant with AI-powered conversations**

## 🌟 Features

- **💬 WhatsApp Cloud API Integration** - Native WhatsApp messaging
- **🤖 AI Assistant** - OpenAI GPT-powered conversations with banking functions
- **💰 Banking Services** - Balance checks, transfers, virtual accounts
- **📱 Airtime/Data** - Mobile recharge services
- **🔒 Security** - Enterprise-grade security and monitoring
- **⚡ Real-time** - Instant responses and background processing

## 🏗️ Architecture

```
WhatsApp Cloud API → Flask Webhook → AI Assistant → Banking APIs
                                   ↓
                           Supabase Database
```

## ⚙️ Quick Setup

### 1. Environment Configuration

Copy the template and update with your credentials:

```bash
cp .env.whatsapp-template .env
```

Update your `.env` file with:

```env
# WhatsApp Cloud API
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# AI
OPENAI_API_KEY=your_openai_key

# Banking
PAYSTACK_SECRET_KEY=your_paystack_key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Service

```bash
python start_whatsapp_sofi.py
```

### 4. Configure WhatsApp Webhook

Set your WhatsApp webhook URL to:
```
https://yourdomain.com/webhook
```

## 📱 WhatsApp Commands

### Account Management
- `balance` - Check wallet balance
- `signup` - Create new account
- `my account` - Get account details

### Transfers
- `send 5000 to John` - Send money (requires full account details)
- `transfer 2000` - Initiate transfer

### Airtime/Data
- `airtime 1000` - Buy airtime
- `data` - Purchase data

### General
- `help` - Get assistance
- Any question - AI-powered responses

## 🔧 Core Components

### Main Application (`main.py`)
- Flask web server
- WhatsApp webhook handler
- Security middleware
- API endpoints

### AI Assistant (`assistant.py`)
- OpenAI GPT integration
- Banking function execution
- Background task processing
- WhatsApp message handling

### Banking Functions
- **Balance**: Real-time balance checking
- **Transfers**: Secure money transfers with PIN verification
- **Accounts**: Virtual account management
- **Airtime**: Mobile recharge services

### Security (`utils/security.py`)
- Rate limiting
- IP blocking
- Request validation
- Security monitoring

## 🔐 Security Features

- **Request Validation** - All WhatsApp webhooks validated
- **Rate Limiting** - Prevents abuse and spam
- **Encryption** - Sensitive data encrypted at rest
- **Audit Logs** - Complete transaction history
- **IP Blocking** - Automatic threat detection

## 📊 Database Schema

The application uses Supabase with the following main tables:

```sql
-- Users table
users (
  id UUID PRIMARY KEY,
  whatsapp_number TEXT UNIQUE,
  first_name TEXT,
  last_name TEXT,
  email TEXT,
  balance DECIMAL,
  pin_hash TEXT,
  created_at TIMESTAMP
)

-- Transactions table
transactions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  type TEXT,
  amount DECIMAL,
  status TEXT,
  created_at TIMESTAMP
)
```

## 🚀 Deployment

### Render.com (Recommended)

1. Connect your GitHub repository
2. Add environment variables
3. Deploy with auto-build
4. Configure WhatsApp webhook URL

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export WHATSAPP_ACCESS_TOKEN="your_token"
export SUPABASE_URL="your_url"
# ... other variables

# Start the application
python start_whatsapp_sofi.py
```

## 🔍 Monitoring & Logs

### Security Events
```bash
curl -H "X-API-Key: your_admin_key" https://yourdomain.com/security/events
```

### Performance Stats
```bash
curl https://yourdomain.com/performance/status
```

### Health Check
```bash
curl https://yourdomain.com/
```

## 🛠️ Development

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Set up local environment
cp .env.whatsapp-template .env.local
# Update .env.local with test credentials

# Run in development mode
python start_whatsapp_sofi.py
```

### Testing WhatsApp Integration

Use WhatsApp Business API testing tools or ngrok for local testing:

```bash
# Install ngrok
ngrok http 5000

# Use the ngrok URL as your webhook
# Example: https://abc123.ngrok.io/webhook
```

## 📚 API Documentation

### Webhook Endpoint

**POST** `/webhook`
- Handles WhatsApp Cloud API webhooks
- Processes all message types (text, media, interactive)
- Returns immediate acknowledgment

**GET** `/webhook`
- WhatsApp webhook verification
- Validates verify token

### Banking APIs

**POST** `/api/create_virtual_account`
- Creates new virtual bank account
- Requires user authentication

**POST** `/api/verify-pin`
- Verifies user transaction PIN
- Returns success/failure status

## 🔧 Configuration

### WhatsApp Cloud API Setup

1. Create Facebook Developer Account
2. Create WhatsApp Business App
3. Get permanent access token
4. Configure webhook URL
5. Add phone number ID

### Database Setup

1. Create Supabase project
2. Run SQL schema from `schema.sql`
3. Configure RLS policies
4. Get connection credentials

### Banking Integration

1. Register with Paystack
2. Get API keys
3. Configure webhook endpoints
4. Test payment flows

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

Copyright © 2024 Sofi AI. All rights reserved.

## 🆘 Support

For technical support or questions:
- Create an issue in this repository
- Contact: support@sofi.ai
- Documentation: [docs.sofi.ai](https://docs.sofi.ai)

---

## 🚀 Ready to Deploy?

1. ✅ Update `.env` with your credentials
2. ✅ Run `python start_whatsapp_sofi.py`
3. ✅ Configure WhatsApp webhook
4. ✅ Test with WhatsApp messages
5. ✅ Monitor logs and performance

**Your AI banking assistant is ready to serve users on WhatsApp! 🎉**
