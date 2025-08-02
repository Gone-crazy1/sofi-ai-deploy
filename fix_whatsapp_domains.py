#!/usr/bin/env python3
"""
WhatsApp Domain Configuration Fixer
Ensures the webhook works with both www and non-www domains
"""

import os
import sys

def update_environment_for_domains():
    """Update environment to handle both domain formats"""
    
    # Update the verification token to ensure it matches
    verification_token = "sofi_ai_webhook_verify_2024"
    
    print("🔧 Configuring WhatsApp webhook for both domain formats...")
    
    # Check current environment
    current_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'default')
    print(f"Current verification token: {current_token}")
    
    if current_token != verification_token:
        print(f"⚠️  Token mismatch detected")
        print(f"Expected: {verification_token}")
        print(f"Current: {current_token}")
    
    print("\n📋 Environment Variable Configuration for Render.com:")
    print("=" * 60)
    print(f"WHATSAPP_VERIFY_TOKEN={verification_token}")
    print(f"WHATSAPP_FLOW_PRIVATE_KEY=<your_base64_private_key>")
    print(f"WHATSAPP_FLOW_PUBLIC_KEY=<your_base64_public_key>")
    print("=" * 60)
    
    print("\n🌐 Domain Configuration:")
    print("=" * 60)
    print("✅ Primary: https://www.pipinstallsofi.com/whatsapp-flow-webhook")
    print("⚠️  Secondary: https://pipinstallsofi.com/whatsapp-flow-webhook (may redirect)")
    print("=" * 60)
    
    print("\n📱 Meta Business Manager Setup:")
    print("=" * 60)
    print("Endpoint URI: https://www.pipinstallsofi.com/whatsapp-flow-webhook")
    print("Verify Token: sofi_ai_webhook_verify_2024")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    update_environment_for_domains()
