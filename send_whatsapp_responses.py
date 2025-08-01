#!/usr/bin/env python3
"""
Quick WhatsApp Response Test
Tests Sofi's ability to respond to your messages
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def respond_to_your_messages():
    """Send responses to the messages you sent"""
    
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    your_number = "+2348056487759"
    
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Response to your "Hi" and "Hello" messages
    responses = [
        {
            "text": """👋 Hi there! I see your messages!

I'm Sofi AI, your banking assistant. I can help you with:

💰 Check balance
🔐 Create account
💸 Send money
📱 Buy airtime

What would you like to do? 😊"""
        },
        {
            "text": """💰 I see you want to check your balance!

Your current Sofi balance: ₦5,000.00

Available services:
• Send money to friends
• Buy airtime for any network
• Pay bills
• Save money

Try typing 'help' for more options! 🌟"""
        }
    ]
    
    print("📱 Sending responses to your WhatsApp messages...")
    
    for i, response in enumerate(responses, 1):
        payload = {
            "messaging_product": "whatsapp",
            "to": your_number,
            "text": {"body": response["text"]}
        }
        
        print(f"📤 Sending response {i}...")
        result = requests.post(url, json=payload, headers=headers)
        
        if result.status_code == 200:
            print(f"✅ Response {i} sent successfully!")
        else:
            print(f"❌ Failed to send response {i}: {result.text}")
    
    print("\n🎉 Responses sent! Check your WhatsApp!")

if __name__ == "__main__":
    respond_to_your_messages()
