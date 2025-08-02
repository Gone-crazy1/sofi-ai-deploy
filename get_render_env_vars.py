#!/usr/bin/env python3
"""
Environment Variables for Render.com Deployment
Extract WhatsApp Flow encryption keys for deployment
"""

import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    print("🔑 WhatsApp Flow Environment Variables for Render.com")
    print("=" * 60)
    
    # Get the encryption keys
    private_key = os.getenv('WHATSAPP_FLOW_PRIVATE_KEY')
    public_key = os.getenv('WHATSAPP_FLOW_PUBLIC_KEY')
    
    if private_key and public_key:
        print("\n✅ Encryption keys found in .env file")
        print("\n📋 Add these to Render.com Environment Variables:")
        print("-" * 50)
        
        print("\nVariable Name: WHATSAPP_FLOW_PRIVATE_KEY")
        print(f"Value: {private_key}")
        
        print("\nVariable Name: WHATSAPP_FLOW_PUBLIC_KEY")
        print(f"Value: {public_key}")
        
        print("\n🚀 Instructions:")
        print("1. Go to Render.com dashboard")
        print("2. Select your sofi-ai-deploy service")
        print("3. Go to Environment tab")
        print("4. Add the two variables above")
        print("5. Deploy will restart automatically")
        
        print("\n✅ After adding these, your WhatsApp Flow encryption will work!")
        
    else:
        print("❌ Encryption keys not found in .env file")
        print("Run: python generate_flow_keys.py")

if __name__ == "__main__":
    main()
