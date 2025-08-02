#!/usr/bin/env python3
"""
WhatsApp Flow Public Key Generator and Signer
Generates RSA key pair and uploads/signs public key with WhatsApp
"""

import os
import sys
import base64
import requests
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import NoEncryption

def generate_key_pair():
    """Generate RSA key pair for WhatsApp Flow encryption"""
    print("🔑 Generating RSA 2048-bit key pair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    print("✅ Key pair generated successfully!")
    return private_pem, public_pem

def sign_public_key(public_key_pem, whatsapp_token, phone_number_id):
    """Sign and upload public key to WhatsApp"""
    print("📤 Uploading and signing public key with WhatsApp...")
    
    # Convert PEM to string
    public_key_str = public_key_pem.decode('utf-8')
    
    # Prepare payload
    payload = {
        "business_public_key": public_key_str
    }
    
    # WhatsApp API endpoint
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/whatsapp_business_encryption"
    
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }
    
    print(f"Endpoint: {url}")
    print(f"Phone Number ID: {phone_number_id}")
    
    # Upload and sign public key
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("✅ Public key successfully uploaded and signed!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Error uploading public key: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return None

def save_keys_to_env(private_key_pem, public_key_pem):
    """Save keys to environment file"""
    print("💾 Saving keys to environment file...")
    
    # Encode keys as base64 for storage
    private_key_b64 = base64.b64encode(private_key_pem).decode('utf-8')
    public_key_b64 = base64.b64encode(public_key_pem).decode('utf-8')
    
    env_content = f"""
# WhatsApp Flow Encryption Keys (Generated: {__import__('datetime').datetime.now()})
WHATSAPP_FLOW_PRIVATE_KEY={private_key_b64}
WHATSAPP_FLOW_PUBLIC_KEY={public_key_b64}

# Add these to your main .env file and Render.com environment variables
"""
    
    try:
        with open('.env.flow_keys', 'w') as f:
            f.write(env_content)
        
        print("✅ Keys saved to .env.flow_keys file")
        print("\n📋 Next Steps:")
        print("1. Copy the keys above to your main .env file")
        print("2. Add them to Render.com environment variables")
        print("3. Deploy your updated application")
        
        return True
    except Exception as e:
        print(f"❌ Error saving keys: {e}")
        return False

def load_environment():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env file")
    except ImportError:
        print("⚠️  python-dotenv not installed. Please set environment variables manually.")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")

def main():
    """Main execution function"""
    print("🚀 WhatsApp Flow Key Generator and Signer")
    print("=" * 50)
    
    # Load environment
    load_environment()
    
    # Get required environment variables
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN') or os.getenv('WHATSAPP_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    # Validate environment
    if not WHATSAPP_TOKEN:
        print("❌ WHATSAPP_ACCESS_TOKEN or WHATSAPP_TOKEN not found in environment variables")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    if not WHATSAPP_PHONE_NUMBER_ID:
        print("❌ WHATSAPP_PHONE_NUMBER_ID not found in environment variables")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    print(f"📱 Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")
    print(f"🔑 Token: {WHATSAPP_TOKEN[:20]}...")
    
    # Generate key pair
    try:
        private_key, public_key = generate_key_pair()
    except Exception as e:
        print(f"❌ Key generation failed: {e}")
        sys.exit(1)
    
    # Upload and sign public key
    result = sign_public_key(public_key, WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID)
    
    if result:
        # Save keys to file
        if save_keys_to_env(private_key, public_key):
            print("\n🎉 Setup Complete!")
            print("\n📝 Summary:")
            print("✅ RSA key pair generated")
            print("✅ Public key uploaded to WhatsApp")
            print("✅ Public key signed by WhatsApp")
            print("✅ Keys saved to .env.flow_keys")
            
            print("\n🔧 Next Steps:")
            print("1. Copy keys from .env.flow_keys to your main .env file")
            print("2. Add keys to Render.com environment variables:")
            print("   - WHATSAPP_FLOW_PRIVATE_KEY")
            print("   - WHATSAPP_FLOW_PUBLIC_KEY")
            print("3. Deploy your application")
            print("4. Test your WhatsApp Flow endpoints")
            
        else:
            print("❌ Failed to save keys")
            sys.exit(1)
    else:
        print("❌ Public key signing failed")
        print("\n🔧 Troubleshooting:")
        print("1. Check your WHATSAPP_TOKEN is valid")
        print("2. Verify WHATSAPP_PHONE_NUMBER_ID is correct")
        print("3. Ensure your WhatsApp Business Account has proper permissions")
        print("4. Try again in a few minutes")
        sys.exit(1)

if __name__ == "__main__":
    main()
