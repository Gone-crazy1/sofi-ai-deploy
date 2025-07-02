#!/usr/bin/env python3
"""
Generate Secure Keys for Sofi AI Application
Creates cryptographically secure keys for JWT, Flask secret, and webhook secrets
"""

import secrets
import string
import uuid
from datetime import datetime

def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(length)

def generate_hex_key(length: int = 32) -> str:
    """Generate a hex-encoded secret key"""
    return secrets.token_hex(length)

def generate_password(length: int = 16) -> str:
    """Generate a secure password with mixed characters"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_uuid() -> str:
    """Generate a UUID for unique identifiers"""
    return str(uuid.uuid4())

def main():
    """Generate all necessary secure keys"""
    print("🔐 Sofi AI Secure Key Generator")
    print("=" * 50)
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Generate keys
    flask_secret = generate_secret_key(32)
    jwt_secret = generate_secret_key(32)
    webhook_secret = generate_secret_key(24)
    api_secret = generate_hex_key(16)
    session_secret = generate_secret_key(24)
    
    print("🔑 Generated Secure Keys:")
    print("-" * 30)
    print(f"SECRET_KEY={flask_secret}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"WEBHOOK_SECRET={webhook_secret}")
    print(f"API_SECRET={api_secret}")
    print(f"SESSION_SECRET={session_secret}")
    print()
    
    print("📋 Copy these values to your .env file:")
    print("-" * 40)
    print("# Security Configuration")
    print(f"SECRET_KEY={flask_secret}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"WEBHOOK_SECRET={webhook_secret}")
    print()
    
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("-" * 30)
    print("• Store these keys securely")
    print("• Never commit them to version control")
    print("• Use different keys for development and production")
    print("• Rotate keys regularly")
    print("• Keep backups of production keys in a secure location")
    print()
    
    print("🔄 Additional Security Recommendations:")
    print("-" * 40)
    print("• Use environment-specific keys")
    print("• Implement key rotation policy")
    print("• Monitor for key exposure")
    print("• Use secrets management service in production")
    
    # Save to file option
    save_to_file = input("\n💾 Save keys to 'generated_keys.txt'? (y/N): ").lower().strip()
    
    if save_to_file == 'y':
        with open('generated_keys.txt', 'w') as f:
            f.write("# Sofi AI Generated Security Keys\n")
            f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# WARNING: Keep this file secure and delete after use!\n\n")
            f.write(f"SECRET_KEY={flask_secret}\n")
            f.write(f"JWT_SECRET_KEY={jwt_secret}\n")
            f.write(f"WEBHOOK_SECRET={webhook_secret}\n")
            f.write(f"API_SECRET={api_secret}\n")
            f.write(f"SESSION_SECRET={session_secret}\n")
        
        print("✅ Keys saved to 'generated_keys.txt'")
        print("⚠️  Remember to delete this file after copying keys to .env!")

if __name__ == "__main__":
    main()
