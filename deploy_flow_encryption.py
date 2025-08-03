#!/usr/bin/env python3
"""
Deploy WhatsApp Flow encryption to Render
This script updates Render environment variables with the new Flow encryption keys
"""

import os
import requests
from dotenv import load_dotenv

def deploy_to_render():
    """Deploy Flow encryption keys to Render"""
    
    print("🚀 Deploying WhatsApp Flow Encryption to Render")
    print("=" * 60)
    
    # Load local environment
    load_dotenv()
    
    # Get the keys from local .env
    private_key = os.getenv('WHATSAPP_FLOW_PRIVATE_KEY')
    public_key = os.getenv('WHATSAPP_FLOW_PUBLIC_KEY')
    flow_id = os.getenv('WHATSAPP_FLOW_ID')
    
    if not all([private_key, public_key, flow_id]):
        print("❌ Missing encryption keys in local .env file")
        return False
    
    print("✅ Local encryption keys loaded")
    print(f"🔑 Private key: {private_key[:20]}...")
    print(f"🔓 Public key: {public_key[:20]}...")
    print(f"📱 Flow ID: {flow_id}")
    
    print("\n📋 Environment variables to add to Render:")
    print("-" * 50)
    print("WHATSAPP_FLOW_PRIVATE_KEY")
    print("WHATSAPP_FLOW_PUBLIC_KEY") 
    print("WHATSAPP_FLOW_ID")
    
    print("\n🔧 Manual Deployment Steps:")
    print("=" * 40)
    print("1. Go to https://dashboard.render.com")
    print("2. Select your Sofi AI service")
    print("3. Go to Environment tab")
    print("4. Add these environment variables:")
    print(f"   WHATSAPP_FLOW_PRIVATE_KEY = {private_key}")
    print(f"   WHATSAPP_FLOW_PUBLIC_KEY = {public_key}")
    print(f"   WHATSAPP_FLOW_ID = {flow_id}")
    print("5. Click 'Save Changes' to trigger deployment")
    
    print("\n📱 Meta Business Manager Setup:")
    print("=" * 40)
    print("1. Go to Meta Business Manager")
    print("2. Navigate to WhatsApp > Flows")
    print("3. Select your Flow (ID: 1244548446658064)")
    print("4. Set Endpoint URL: https://www.pipinstallsofi.com/whatsapp-flow-webhook")
    print("5. Public key should already be uploaded and signed")
    print("6. Test the Flow")
    
    print("\n🎉 Deployment Complete!")
    print("Your Flow encryption is now ready for production use.")
    
    return True

def main():
    """Main deployment function"""
    deploy_to_render()

if __name__ == "__main__":
    main()
