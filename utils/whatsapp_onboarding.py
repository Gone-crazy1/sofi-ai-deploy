#!/usr/bin/env python3
"""
WhatsApp Onboarding System with Smart Reply Buttons
Handles account creation and onboarding via WhatsApp with interactive buttons
"""

import os
import json
import requests
from datetime import datetime

def send_whatsapp_onboarding_link(phone_number, user_name=None):
    """
    Send WhatsApp message with onboarding link and interactive buttons
    """
    try:
        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        domain = os.getenv("DOMAIN", "pipinstallsofi.com")
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Create onboarding link
        onboarding_link = f"https://{domain}/onboard"
        
        # Personalized greeting
        greeting = f"Hi {user_name}!" if user_name else "Hi there!"
        
        # Interactive message with buttons
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"""🎉 {greeting} Welcome to Sofi AI!

I'm your personal financial assistant. To get started, I need to create your secure account.

Choose how you'd like to proceed:"""
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "quick_signup",
                                "title": "📱 Quick Setup"
                            }
                        },
                        {
                            "type": "reply", 
                            "reply": {
                                "id": "full_onboard",
                                "title": "🌐 Full Setup"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "learn_more",
                                "title": "ℹ️ Learn More"
                            }
                        }
                    ]
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Onboarding message sent to {phone_number}")
            return True
        else:
            print(f"❌ Failed to send onboarding message: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ WhatsApp onboarding error: {e}")
        return False

def handle_whatsapp_onboarding_response(sender, button_id):
    """
    Handle user responses to onboarding buttons
    """
    domain = os.getenv("DOMAIN", "pipinstallsofi.com")
    onboarding_link = f"https://{domain}/onboard"
    
    if button_id == "quick_signup":
        return send_whatsapp_quick_signup(sender)
    
    elif button_id == "full_onboard":
        message = f"""🌐 **Complete Setup**

For the full Sofi experience with all features, please complete your setup on our secure website:

🔗 {onboarding_link}

This includes:
✅ Bank account creation
✅ Identity verification  
✅ PIN setup
✅ Security features
✅ Transaction history

The link will be hidden after you complete setup for security."""
        
        return send_whatsapp_message(sender, message)
    
    elif button_id == "learn_more":
        message = """ℹ️ **About Sofi AI**

Sofi is your intelligent financial assistant that helps you:

💰 **Send & Receive Money**
- Instant transfers to any bank
- Virtual account for receiving funds
- Transaction receipts

📱 **Mobile Services**
- Buy airtime & data
- Pay bills instantly
- Check account balance

🔒 **Secure & Safe**
- Bank-level security
- PIN protection
- Real-time notifications

🤖 **AI-Powered**
- Natural language commands
- Smart suggestions
- 24/7 availability

Ready to get started? Type 'signup' or 'create account'"""
        
        return send_whatsapp_message(sender, message)
    
    else:
        return "Please choose one of the options above to continue."

def send_whatsapp_quick_signup(sender):
    """
    Handle quick signup via WhatsApp
    """
    message = f"""📱 **Quick Setup Started**

I'll help you create your account right here in WhatsApp!

Please provide the following information:

1️⃣ **Full Name**: What's your full name?
   Example: "My name is John Doe"

Type your full name to continue..."""
    
    # Store user state for quick signup
    store_user_onboarding_state(sender, "awaiting_name")
    
    return send_whatsapp_message(sender, message)

def store_user_onboarding_state(phone, state, data=None):
    """
    Store user's onboarding state in memory/database
    """
    # For now, store in memory. In production, use database
    if not hasattr(store_user_onboarding_state, 'states'):
        store_user_onboarding_state.states = {}
    
    store_user_onboarding_state.states[phone] = {
        'state': state,
        'data': data or {},
        'timestamp': datetime.now().isoformat()
    }

def get_user_onboarding_state(phone):
    """
    Get user's current onboarding state
    """
    if hasattr(store_user_onboarding_state, 'states'):
        return store_user_onboarding_state.states.get(phone)
    return None

def process_whatsapp_onboarding_step(sender, text):
    """
    Process user input during onboarding steps
    """
    state_info = get_user_onboarding_state(sender)
    
    if not state_info:
        return None  # No active onboarding
    
    state = state_info['state']
    data = state_info['data']
    
    if state == "awaiting_name":
        # Extract name from message
        name = extract_name_from_text(text)
        if name:
            data['full_name'] = name
            store_user_onboarding_state(sender, "awaiting_email", data)
            
            return f"""✅ Great! Hi {name}!

2️⃣ **Email Address**: What's your email?
   Example: "john.doe@gmail.com"

Please provide a valid email address..."""
        else:
            return "Please provide your full name. Example: 'My name is John Doe'"
    
    elif state == "awaiting_email":
        # Extract email from message
        email = extract_email_from_text(text)
        if email:
            data['email'] = email
            store_user_onboarding_state(sender, "creating_account", data)
            
            # Create the account
            return create_whatsapp_virtual_account(sender, data)
        else:
            return "Please provide a valid email address. Example: 'john.doe@gmail.com'"
    
    return None

def extract_name_from_text(text):
    """
    Extract name from user's message
    """
    text = text.lower().strip()
    
    # Common patterns for name input
    patterns = [
        "my name is ",
        "i am ",
        "i'm ",
        "name: ",
        "full name: "
    ]
    
    for pattern in patterns:
        if pattern in text:
            name = text.split(pattern, 1)[1].strip()
            # Clean up and capitalize
            name = ' '.join(word.capitalize() for word in name.split())
            if len(name) > 2:
                return name
    
    # If no pattern, assume the whole message is the name
    words = text.split()
    if len(words) >= 2 and len(text) < 50:  # Reasonable name length
        name = ' '.join(word.capitalize() for word in words)
        return name
    
    return None

def extract_email_from_text(text):
    """
    Extract email from user's message
    """
    import re
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    
    if matches:
        return matches[0].lower()
    
    return None

def create_whatsapp_virtual_account(sender, user_data):
    """
    Create virtual account for WhatsApp user
    """
    try:
        from utils.ninepsb_api import NINEPSBApi
        import uuid
        import random
        
        # Generate unique user ID
        user_id = f"whatsapp_{uuid.uuid4().hex[:8]}"
        
        # Get 9PSB credentials
        api_key = os.getenv("NINEPSB_API_KEY")
        secret_key = os.getenv("NINEPSB_SECRET_KEY")
        base_url = os.getenv("NINEPSB_BASE_URL")
        
        psb = NINEPSBApi(api_key, secret_key, base_url)
        
        # Prepare user data for 9PSB
        name_parts = user_data['full_name'].split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else name_parts[0]
        
        # Generate Nigerian phone if sender is international
        if not sender.startswith('234'):
            # Generate random Nigerian phone
            phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            phone = f"080{phone_suffix}"
        else:
            phone = sender
        
        ninepsb_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": user_data['email'],
            "phone": phone,
            "whatsapp_phone": sender
        }
        
        # Create virtual account
        result = psb.create_virtual_account(user_id, ninepsb_data)
        
        if result and result.get('status') == 'SUCCESS':
            account_data = result.get('data', {})
            account_number = account_data.get('accountNumber')
            account_name = account_data.get('fullName')
            
            # Store in Supabase
            store_whatsapp_user_in_database(sender, user_data, account_number, account_name)
            
            # Clear onboarding state
            if hasattr(store_user_onboarding_state, 'states'):
                store_user_onboarding_state.states.pop(sender, None)
            
            return f"""🎉 **Account Created Successfully!**

✅ **Your Virtual Account:**
🏦 Account Number: `{account_number}`
👤 Account Name: {account_name}
📱 WhatsApp: Connected

💡 **You can now:**
• Send money: "Send 5000 to John"
• Check balance: "Balance"
• Buy airtime: "Airtime 1000"
• Get help: "Help"

🔒 Your account is secure and ready to use!

Want to set up a PIN for extra security? Reply 'setup pin'"""
        else:
            error_msg = result.get('message', 'Unknown error') if result else 'Connection error'
            return f"""❌ **Account creation failed**

Error: {error_msg}

Please try again later or contact support.
You can also complete setup at: https://{os.getenv('DOMAIN', 'pipinstallsofi.com')}/onboard"""
            
    except Exception as e:
        print(f"❌ WhatsApp account creation error: {e}")
        return """❌ **Account creation failed**

Please try again later or complete setup on our website:
https://pipinstallsofi.com/onboard"""

def store_whatsapp_user_in_database(whatsapp_phone, user_data, account_number, account_name):
    """
    Store WhatsApp user in Supabase database
    """
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        user_record = {
            "full_name": user_data['full_name'],
            "email": user_data['email'],
            "whatsapp_phone": whatsapp_phone,
            "account_number": account_number,
            "account_name": account_name,
            "platform": "whatsapp",
            "balance": 0,
            "created_at": datetime.utcnow().isoformat(),
            "is_verified": True,
            "onboarding_completed": True
        }
        
        result = supabase.table("users").insert(user_record).execute()
        print(f"✅ WhatsApp user stored in database: {whatsapp_phone}")
        return True
        
    except Exception as e:
        print(f"❌ Database storage error: {e}")
        return False

def send_whatsapp_message(phone_number, message):
    """
    Send simple WhatsApp text message
    """
    try:
        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ WhatsApp message error: {e}")
        return False

# Test function
def test_whatsapp_onboarding():
    """
    Test WhatsApp onboarding system
    """
    print("🧪 Testing WhatsApp Onboarding System...")
    
    test_phone = os.getenv("WHATSAPP_TEST_NUMBER", "+15551825466")
    
    # Test onboarding link
    success = send_whatsapp_onboarding_link(test_phone, "John")
    print(f"Onboarding link sent: {success}")
    
    # Test button response
    response = handle_whatsapp_onboarding_response(test_phone, "learn_more")
    print(f"Button response: {response}")

if __name__ == "__main__":
    test_whatsapp_onboarding()
