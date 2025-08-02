#!/usr/bin/env python3
"""
WhatsApp Flow Key Verification Utility
Helps diagnose key and encryption issues
"""

import os
import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

def verify_key_configuration():
    """Verify WhatsApp Flow key configuration"""
    
    print("🔍 WhatsApp Flow Key Verification")
    print("=" * 50)
    
    # Check environment variables
    private_key_b64 = os.getenv('WHATSAPP_FLOW_PRIVATE_KEY')
    public_key_b64 = os.getenv('WHATSAPP_FLOW_PUBLIC_KEY')
    
    print(f"Private Key Environment: {'✅ Found' if private_key_b64 else '❌ Missing'}")
    print(f"Public Key Environment: {'✅ Found' if public_key_b64 else '❌ Missing'}")
    
    if not private_key_b64:
        print("❌ WHATSAPP_FLOW_PRIVATE_KEY not found in environment")
        return False
        
    if not public_key_b64:
        print("❌ WHATSAPP_FLOW_PUBLIC_KEY not found in environment")
        return False
    
    try:
        # Load private key
        private_key_pem = base64.b64decode(private_key_b64)
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Load public key
        public_key_pem = base64.b64decode(public_key_b64)
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        print("✅ Both keys loaded successfully")
        
        # Verify key pair match
        test_data = b"test_message_for_verification"
        
        # Encrypt with public key
        encrypted = public_key.encrypt(
            test_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt with private key
        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        if decrypted == test_data:
            print("✅ Key pair verification successful")
            
            # Get key details
            private_size = private_key.key_size
            public_size = public_key.key_size
            
            print(f"🔑 Private key size: {private_size} bits")
            print(f"🔑 Public key size: {public_size} bits")
            
            if private_size == public_size == 2048:
                print("✅ Key size is correct (2048 bits)")
            else:
                print(f"⚠️  Unexpected key size: {private_size}/{public_size} (expected 2048)")
            
            return True
        else:
            print("❌ Key pair verification failed - keys don't match!")
            return False
            
    except Exception as e:
        print(f"❌ Key verification error: {e}")
        return False

def suggest_solutions():
    """Suggest solutions for the encryption issue"""
    
    print("\n🔧 TROUBLESHOOTING SUGGESTIONS")
    print("=" * 50)
    
    print("1. 📋 **Re-check Meta Business Manager setup:**")
    print("   - Ensure the EXACT public key from your environment is uploaded")
    print("   - No manual copying/reformatting - use raw PEM content")
    print("   - Verify the Flow is properly published and active")
    
    print("\n2. 🔄 **Regenerate key pair if needed:**")
    print("   - Run: python generate_flow_keys.py")
    print("   - Upload the NEW public key to Meta")
    print("   - Update environment variables with new keys")
    
    print("\n3. 📊 **Check Meta's encryption format:**")
    print("   - Data length 49 bytes suggests possible format issue")
    print("   - Meta might be using different padding or encoding")
    print("   - Consider reaching out to Meta support")
    
    print("\n4. 🧪 **Test with Meta's tools:**")
    print("   - Use Meta's Flow testing tools in Business Manager")
    print("   - Verify the endpoint receives the expected format")
    print("   - Check if health checks pass before testing flows")

if __name__ == "__main__":
    print("🧪 Running WhatsApp Flow diagnostics...\n")
    
    success = verify_key_configuration()
    
    if not success:
        suggest_solutions()
    else:
        print("\n✅ Key configuration appears correct")
        print("💡 The issue might be with Meta's encryption format or Flow setup")
        suggest_solutions()
