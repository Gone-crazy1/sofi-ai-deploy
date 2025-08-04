# 🚨 WhatsApp Flow Webhook Troubleshooting Guide

## 🔍 **Your Webhook Configuration:**

### **WhatsApp Flow Webhook (Form Submissions)**
- **URL:** `https://www.pipinstallsofi.com/whatsapp-flow-webhook`
- **Purpose:** Receives form data when users submit WhatsApp Flows
- **Used for:** Account creation, onboarding forms

### **WhatsApp Cloud API Webhook (Messages)**
- **URL:** `https://pipinstallsofi.com/whatsapp-webhook`
- **Purpose:** Receives regular WhatsApp messages and status updates
- **Used for:** Chat messages, message delivery status

## Quick Diagnosis Steps:

### 1. **Test Both Webhook URLs**
```bash
# Test Flow webhook (with www)
curl https://www.pipinstallsofi.com/health
curl https://www.pipinstallsofi.com/whatsapp-flow-webhook

# Test Messages webhook (without www)
curl https://pipinstallsofi.com/health
curl https://pipinstallsofi.com/whatsapp-webhook

# Test Flow webhook verification
curl "https://www.pipinstallsofi.com/whatsapp-flow-webhook?hub.mode=subscribe&hub.verify_token=sofi_ai_webhook_verify_2024&hub.challenge=test123"

# Test Messages webhook verification
curl "https://pipinstallsofi.com/whatsapp-webhook?hub.mode=subscribe&hub.verify_token=sofi_ai_webhook_verify_2024&hub.challenge=test123"
```

### 2. **Check Environment Variables**
Make sure these are set in your deployment:
```bash
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id_here  
WHATSAPP_FLOW_ID=your_flow_id_here
WHATSAPP_VERIFY_TOKEN=sofi_ai_webhook_verify_2024
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 3. **Meta Business Manager Configuration**

**⚠️ IMPORTANT: You have TWO different webhook configurations needed:**

#### **For WhatsApp Flows (Form Submissions):**
- **Webhook URL:** `https://www.pipinstallsofi.com/whatsapp-flow-webhook`
- **Verify token:** `sofi_ai_webhook_verify_2024`
- **Configure in:** Meta Business Manager → WhatsApp Business Account → Flows

#### **For WhatsApp Messages (Chat):**
- **Webhook URL:** `https://pipinstallsofi.com/whatsapp-webhook`
- **Verify token:** `sofi_ai_webhook_verify_2024`
- **Configure in:** Meta Business Manager → WhatsApp Business Account → Configuration
- **Subscribe to:** `messages`, `message_deliveries`

**🚨 Domain Issue:** Notice one uses `www.` and the other doesn't. This might cause issues!

### 4. **Test Flow Data Reception**

Send a test POST request to your actual Flow webhook:
```bash
curl -X POST https://www.pipinstallsofi.com/whatsapp-flow-webhook \
  -H "Content-Type: application/json" \
  -H "User-Agent: Meta-Test" \
  -d '{
    "action": "data_exchange",
    "screen": "screen_oxjvpn",
    "flow_token": "flows-builder-45407699",
    "data": {
      "screen_0_First_Name__0": "Test",
      "screen_0_Last_Name__1": "User",
      "screen_0_Email__2": "test@example.com",
      "screen_0_Phone__3": "08055611794",
      "screen_0_BVN__4": "12345678901",
      "screen_0_Address__5": "Test Address",
      "screen_0_PIN__6": "1234"
    }
  }'
```

### 5. **Check Your Logs**

Look for these log messages:
- `🚨 FLOW WEBHOOK POST REQUEST RECEIVED 🚨` (webhook received data)
- `🎯 PROCESSING FLOW COMPLETION - ACCOUNT CREATION` (processing started)
- `✅ User created successfully` (account creation worked)
- `❌` (any error messages)

### 6. **Common Issues & Solutions**

#### Issue: "Webhook not receiving data"
**Solution:** Check your Meta Business Manager webhook configuration:
1. Go to Meta Business Manager → WhatsApp → Configuration
2. Set webhook URL to: `https://your-domain.com/whatsapp-flow-webhook`
3. Set verify token to: `sofi_ai_webhook_verify_2024`
4. Subscribe to `messages` events

#### Issue: "Flow not triggering webhook"
**Solution:** Verify your Flow configuration:
1. Flow ID in environment matches Meta Business Manager
2. Flow endpoint URL is correct
3. Flow is published (not in draft mode)

#### Issue: "Data not being processed"
**Solution:** Check field name mapping:
```python
# Your code expects these field names:
first_name = data.get('screen_0_First_Name__0')
last_name = data.get('screen_0_Last_Name__1') 
bvn = data.get('screen_0_BVN__2')
# etc.
```

#### Issue: "Logs not updating"
**Solution:**
1. Check if your application is running
2. Verify logging configuration
3. Check if webhook URL is accessible from outside

### 7. **Test Script Usage**

Run the test script:
```bash
cd /path/to/your/project
python test_webhook.py
```

Enter your domain when prompted and check all test results.

### 8. **Flow Configuration Checklist**

In Meta Business Manager, verify:
- [ ] Flow is published (not draft)
- [ ] Webhook URL is set correctly
- [ ] Verify token matches your environment variable
- [ ] Flow ID matches your `WHATSAPP_FLOW_ID`
- [ ] Form field names match your code expectations

### 9. **Debug Endpoints Available**

Your app has these debug endpoints:
- `/health` - Basic health check
- `/health/flow` - Flow-specific health with environment status
- `/debug/flow` - Flow webhook testing
- `/monitor/webhooks` - Webhook activity monitoring

### 10. **If Still Not Working**

1. **Check server logs** for any startup errors
2. **Test with curl** to ensure basic connectivity
3. **Verify Meta Business Manager settings** one by one
4. **Check if Flow is published** (not in draft mode)
5. **Ensure webhook URL is publicly accessible** (not localhost)

## 🔧 Quick Fixes to Try:

1. **Restart your application**
2. **Republish your WhatsApp Flow** in Meta Business Manager
3. **Update webhook URL** in Meta Business Manager
4. **Check firewall/security groups** if using cloud hosting
5. **Verify SSL certificate** is valid for HTTPS

## 📞 Need Help?

If the issue persists:
1. Check the logs from `/debug/flow` endpoint
2. Verify your Flow is published in Meta Business Manager
3. Test basic webhook connectivity with curl
4. Make sure your domain has a valid SSL certificate
