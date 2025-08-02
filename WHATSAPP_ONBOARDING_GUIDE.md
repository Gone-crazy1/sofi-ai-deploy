# 🚀 WhatsApp Interactive Onboarding System

## Overview
The WhatsApp Interactive Onboarding System sends beautiful interactive URL buttons that open inside WhatsApp's built-in webview, providing a seamless Xara-style onboarding experience.

## Features
- ✅ **Interactive URL Buttons** - Tap to open onboarding inside WhatsApp
- ✅ **Secure Token System** - Time-limited, signed tokens prevent abuse
- ✅ **Smart User Detection** - Automatically detects new vs returning users
- ✅ **Personalized Messages** - Welcome back existing users with their names
- ✅ **24-Hour Session Window** - Works within WhatsApp's messaging window
- ✅ **Mobile-Optimized** - Perfect webview experience on mobile devices
- ✅ **Comprehensive Error Handling** - Fallback messages and logging
- ✅ **Database Integration** - Tracks onboarding status and user creation

## How It Works

### 1. **New User Flow**
When a new user messages Sofi with greetings like "hi", "hello", "start":

```
User: hi
Sofi: 👋 Welcome to Sofi - your smart banking assistant! 
      Tap the button below to securely complete your onboarding 
      and start banking smarter.
      
      [Start Banking 🚀] <- Interactive URL Button
```

### 2. **Returning User Flow**
When an existing user messages Sofi:

```
User: hello
Sofi: Welcome back, John! 👋
      Your Sofi banking dashboard is ready. 
      Tap below to access your account securely.
      
      [Open Dashboard 📊] <- Interactive URL Button
```

## Configuration

### Environment Variables
Add these to your `.env` file and production environment:

```env
# Onboarding Configuration
ONBOARD_DOMAIN=https://sofi-ai-deploy.onrender.com
ONBOARD_TOKEN_SECRET=your-super-secret-onboarding-key-change-this

# WhatsApp Cloud API (already configured)
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Database (already configured)  
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Production Setup (Render.com)
1. Go to your Render.com dashboard
2. Select your service
3. Navigate to "Environment"
4. Add the new environment variables:
   - `ONBOARD_DOMAIN` = `https://sofi-ai-deploy.onrender.com`
   - `ONBOARD_TOKEN_SECRET` = `[generate a strong secret key]`

## Security Features

### Token-Based Security
- **HMAC Signatures**: Tokens are cryptographically signed
- **Time Expiration**: Tokens expire after 24 hours
- **User Binding**: Tokens are tied to specific WhatsApp numbers
- **Nonce Protection**: Unique random values prevent replay attacks

### Token Format
```
whatsapp_number:expires_at:nonce:hmac_signature
+2348104611794:1691234567:uuid-string:sha256-signature
```

## API Endpoints

### Core Onboarding
- `GET /onboard?token=<secure_token>` - Secure onboarding page
- `POST /whatsapp-webhook` - Handles incoming WhatsApp messages

### Testing Endpoints
- `GET /test/onboarding/<whatsapp_number>` - Test onboarding for specific number
- `GET /test/token/<whatsapp_number>` - Generate and validate test tokens
- `GET /test/onboarding-config` - Check configuration status

## Usage Examples

### Manual Testing
Test the onboarding system by visiting:
```
https://sofi-ai-deploy.onrender.com/test/onboarding/2348104611794
```

### Check Configuration
Verify all environment variables are set:
```
https://sofi-ai-deploy.onrender.com/test/onboarding-config
```

### Generate Test Token
Create a test token for development:
```
https://sofi-ai-deploy.onrender.com/test/token/2348104611794
```

## Integration

### In Your Code
```python
from whatsapp_onboarding import WhatsAppOnboardingManager

# Initialize manager
onboarding = WhatsAppOnboardingManager()

# Send onboarding to new user
result = onboarding.send_onboarding_message("+2348104611794", "John Doe")

# Send welcome back to existing user  
result = onboarding.send_welcome_back_message("+2348104611794", "John Doe")

# Validate token
is_valid = onboarding.validate_token(token, "+2348104611794")
```

### Quick Functions
```python
from whatsapp_onboarding import send_onboarding_message, validate_onboarding_token

# Send onboarding message
result = send_onboarding_message("+2348104611794", "John Doe")

# Validate token
is_valid = validate_onboarding_token(token, "+2348104611794")
```

## Message Triggers

### New User Onboarding Triggers
These words/phrases trigger onboarding for new users:
- `hi`, `hello`, `hey`
- `start`, `begin`
- `signup`, `sign up`
- `create account`, `register`
- `join`, `onboard`
- `help`

### Returning User Triggers
These trigger dashboard access for existing users:
- `hi`, `hello`, `hey`
- `start`, `dashboard`
- `account`

## Error Handling

### Fallback Messages
If the interactive system fails, users receive fallback messages:

```
👋 Welcome to Sofi! Please visit our website to create your account: 
https://sofi-ai-deploy.onrender.com/onboard
```

### Token Validation Errors
Invalid or expired tokens show:
```
❌ Invalid or expired onboarding link. Please request a new one from Sofi.
```

## Database Integration

### User Tracking
The system automatically:
- Creates user records for new WhatsApp users
- Logs onboarding tokens and URLs
- Tracks onboarding status and timestamps
- Updates existing users with onboarding data

### Database Fields
```sql
-- New columns added to users table
whatsapp_number VARCHAR(20)
onboarding_token TEXT
onboarding_url TEXT  
onboarding_sent_at TIMESTAMP
onboarding_status VARCHAR(50)
```

## Monitoring

### Logs
The system provides comprehensive logging:
```
✅ Generated secure token for +2348104611794
📤 Sending onboarding message to 2348104611794
✅ Onboarding message sent successfully to 2348104611794
✅ Created new user onboarding record for +2348104611794
```

### Error Tracking
Failed operations are logged with details:
```
❌ Failed to send onboarding message: 400 - Invalid phone number
❌ Token validation error: Invalid signature
❌ Onboarding system error: Network timeout
```

## Best Practices

### Security
1. **Strong Secret Keys**: Use cryptographically strong `ONBOARD_TOKEN_SECRET`
2. **HTTPS Only**: Ensure all URLs use HTTPS
3. **Token Expiration**: Keep 24-hour expiration for security
4. **Input Validation**: Validate all WhatsApp numbers and tokens

### User Experience
1. **Fast Response**: System responds within seconds
2. **Clear Messaging**: Simple, friendly onboarding messages
3. **Mobile First**: Optimized for WhatsApp's webview
4. **Fallback Support**: Always provide alternative options

### Performance
1. **Efficient Lookups**: Database queries are optimized
2. **Caching**: User states cached for faster responses
3. **Background Processing**: Non-blocking message sending
4. **Error Recovery**: Automatic fallback mechanisms

## Troubleshooting

### Common Issues

**1. Onboarding not triggered**
- Check if user exists in database
- Verify WhatsApp number format
- Ensure trigger words are used

**2. Token validation fails**
- Check `ONBOARD_TOKEN_SECRET` is set
- Verify token hasn't expired
- Ensure WhatsApp number matches

**3. Interactive buttons don't work**
- Verify `WHATSAPP_TOKEN` is valid
- Check `WHATSAPP_PHONE_NUMBER_ID` is correct
- Ensure 24-hour session window

**4. Messages not sending**
- Check network connectivity
- Verify WhatsApp API limits
- Review error logs for details

### Debug Commands
```bash
# Test configuration
curl https://sofi-ai-deploy.onrender.com/test/onboarding-config

# Test specific number
curl https://sofi-ai-deploy.onrender.com/test/onboarding/2348104611794

# Check logs
heroku logs --tail  # or check Render.com logs
```

## Migration Guide

If upgrading from basic onboarding:

1. **Add Environment Variables**
   ```env
   ONBOARD_DOMAIN=https://sofi-ai-deploy.onrender.com
   ONBOARD_TOKEN_SECRET=your-secret-key
   ```

2. **Update Database**
   ```sql
   ALTER TABLE users ADD COLUMN whatsapp_number VARCHAR(20);
   CREATE INDEX idx_users_whatsapp_number ON users(whatsapp_number);
   ```

3. **Deploy Changes**
   - Commit code changes
   - Update environment variables
   - Deploy to production

4. **Test System**
   - Visit test endpoints
   - Send test WhatsApp messages
   - Verify interactive buttons work

## Support

For issues or questions:
1. Check the test endpoints first
2. Review error logs
3. Verify configuration
4. Test with different WhatsApp numbers
5. Ensure 24-hour session window compliance

---

## 🎉 Success!

Your WhatsApp Interactive Onboarding System is now ready to provide a seamless, secure, and beautiful onboarding experience just like Xara! 🚀
