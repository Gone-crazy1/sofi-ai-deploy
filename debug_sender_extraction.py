#!/usr/bin/env python3
"""
Debug Paystack Webhook Sender Information
==========================================
Helper script to test and debug sender name extraction from webhook payloads.
Use this to verify what sender information is being extracted from real webhook data.
"""

import json
import os
import sys
from typing import Dict

# Add parent directory to path to import our webhook handler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paystack.paystack_webhook import PaystackWebhookHandler

def test_sender_extraction(webhook_payload: Dict):
    """Test sender name and bank extraction from a webhook payload"""
    print("🧪 Testing Sender Information Extraction")
    print("=" * 50)
    
    # Create webhook handler
    handler = PaystackWebhookHandler()
    
    # Extract information
    customer = webhook_payload.get("customer", {})
    sender_name = handler._extract_sender_name(webhook_payload, customer)
    sender_bank = handler._extract_sender_bank(webhook_payload)
    
    print(f"📊 Webhook Payload Analysis:")
    print(f"   📋 Main keys: {list(webhook_payload.keys())}")
    
    if webhook_payload.get("authorization"):
        print(f"   🔐 Authorization keys: {list(webhook_payload.get('authorization', {}).keys())}")
    
    if webhook_payload.get("metadata"):
        print(f"   📝 Metadata keys: {list(webhook_payload.get('metadata', {}).keys())}")
    
    if webhook_payload.get("customer"):
        print(f"   👤 Customer keys: {list(webhook_payload.get('customer', {}).keys())}")
    
    if webhook_payload.get("gateway_response"):
        print(f"   🌐 Gateway Response keys: {list(webhook_payload.get('gateway_response', {}).keys())}")
    
    print(f"\n✅ Extraction Results:")
    print(f"   👤 Sender Name: '{sender_name}'")
    print(f"   🏦 Sender Bank: '{sender_bank}'")
    
    # Check some common fields that might contain sender info
    common_fields_to_check = [
        "payer_name", "sender_name", "account_name", "originator_name",
        "authorization.account_name", "authorization.sender_name", 
        "customer.name", "metadata.sender_name", "gateway_response.sender_name"
    ]
    
    print(f"\n🔍 Field Analysis:")
    for field in common_fields_to_check:
        if "." in field:
            # Nested field
            parts = field.split(".")
            value = webhook_payload.get(parts[0], {}).get(parts[1]) if isinstance(webhook_payload.get(parts[0]), dict) else None
        else:
            # Top-level field
            value = webhook_payload.get(field)
        
        if value:
            print(f"   ✅ {field}: '{value}'")
        else:
            print(f"   ❌ {field}: Not found")
    
    return sender_name, sender_bank

def sample_webhook_test():
    """Test with a sample webhook payload"""
    print("🧪 Testing with Sample Webhook Payload")
    print("=" * 40)
    
    # Sample webhook payload (you can replace this with actual webhook data)
    sample_payload = {
        "id": 123456789,
        "domain": "test",
        "status": "success",
        "reference": "ref_123456789",
        "amount": 500000,  # 5000 in kobo
        "message": "Approved",
        "gateway_response": "Successful",
        "paid_at": "2024-01-01T10:00:00.000Z",
        "created_at": "2024-01-01T10:00:00.000Z",
        "channel": "dedicated_nuban",
        "currency": "NGN",
        "customer": {
            "id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "customer_code": "CUS_test123",
            "phone": "+2348000000000",
            "metadata": {},
            "risk_action": "default"
        },
        "authorization": {
            "authorization_code": "AUTH_test123",
            "bin": "408408",
            "last4": "4081",
            "exp_month": "12",
            "exp_year": "2025",
            "channel": "card",
            "card_type": "visa",
            "bank": "Test Bank",
            "country_code": "NG",
            "brand": "visa",
            "reusable": True,
            "signature": "SIG_test123",
            "account_name": "NDIDI THANKGOD"  # This would be the real sender
        },
        "metadata": {}
    }
    
    sender_name, sender_bank = test_sender_extraction(sample_payload)
    
    print(f"\n📝 Sample Test Results:")
    print(f"   Expected Sender: 'NDIDI THANKGOD'")
    print(f"   Extracted Sender: '{sender_name}'")
    print(f"   Match: {'✅ YES' if 'NDIDI THANKGOD' in sender_name.upper() else '❌ NO'}")

def test_with_real_webhook():
    """Instructions for testing with real webhook data"""
    print("\n🌐 Testing with Real Webhook Data")
    print("=" * 40)
    print("To test with real webhook data:")
    print("1. Copy a real webhook payload from your logs")
    print("2. Save it as 'test_webhook.json' in this directory")
    print("3. Run this script again")
    
    # Try to load real webhook data
    webhook_file = "test_webhook.json"
    if os.path.exists(webhook_file):
        try:
            with open(webhook_file, 'r') as f:
                real_payload = json.load(f)
            
            print(f"✅ Found {webhook_file}, testing with real data...")
            sender_name, sender_bank = test_sender_extraction(real_payload)
            
        except Exception as e:
            print(f"❌ Error loading {webhook_file}: {e}")
    else:
        print(f"❌ {webhook_file} not found. Create it with real webhook data to test.")

if __name__ == "__main__":
    print("🔍 Paystack Webhook Sender Information Debug Tool")
    print(f"🕐 Started at: {os.popen('date').read().strip()}")
    
    # Test with sample data
    sample_webhook_test()
    
    # Test with real webhook data if available
    test_with_real_webhook()
    
    print(f"\n💡 Tips for debugging:")
    print(f"   • Check the logs for '🔍 DEBUG:' messages when a real deposit comes in")
    print(f"   • Look for '💾 SAVING TO DB:' to see what's actually being saved")
    print(f"   • The sender name should appear in your Telegram notifications")
    print(f"   • If sender_name is 'Bank Transfer', the real name wasn't found in the webhook")
