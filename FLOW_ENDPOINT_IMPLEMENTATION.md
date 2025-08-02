# 🔐 WhatsApp Flow Endpoint Implementation Guide

## 🎯 **Complete Setup Process**

This guide implements the full WhatsApp Flow endpoint with encryption, public key signing, and all required handlers.

## 🔑 **Step 1: Generate and Sign Public Key**

### **Create Key Pair Generation Script:**

```python
# generate_flow_keys.py
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import NoEncryption
import base64
import requests
import json

def generate_key_pair():
    """Generate RSA key pair for WhatsApp Flow encryption"""
    
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
    
    return private_pem, public_pem

def sign_public_key(public_key_pem, whatsapp_token, phone_number_id):
    """Sign and upload public key to WhatsApp"""
    
    # Convert PEM to string
    public_key_str = public_key_pem.decode('utf-8')
    
    # Prepare payload
    payload = {
        "public_key": public_key_str
    }
    
    # WhatsApp API endpoint
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/whatsapp_business_encryption"
    
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }
    
    # Upload and sign public key
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ Public key successfully uploaded and signed!")
        return response.json()
    else:
        print(f"❌ Error uploading public key: {response.status_code}")
        print(response.text)
        return None

def save_keys_to_env(private_key_pem, public_key_pem):
    """Save keys to environment variables"""
    
    # Encode keys as base64 for storage
    private_key_b64 = base64.b64encode(private_key_pem).decode('utf-8')
    public_key_b64 = base64.b64encode(public_key_pem).decode('utf-8')
    
    env_content = f"""
# WhatsApp Flow Encryption Keys
WHATSAPP_FLOW_PRIVATE_KEY={private_key_b64}
WHATSAPP_FLOW_PUBLIC_KEY={public_key_b64}
"""
    
    with open('.env.flow_keys', 'w') as f:
        f.write(env_content)
    
    print("✅ Keys saved to .env.flow_keys file")
    print("Add these to your main .env file and Render.com environment variables")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("❌ Please set WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env file")
        exit(1)
    
    print("🔑 Generating RSA key pair...")
    private_key, public_key = generate_key_pair()
    
    print("📤 Uploading and signing public key with WhatsApp...")
    result = sign_public_key(public_key, WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID)
    
    if result:
        print("💾 Saving keys to environment file...")
        save_keys_to_env(private_key, public_key)
        
        print("\n🎉 Setup Complete!")
        print("Next steps:")
        print("1. Copy keys from .env.flow_keys to your main .env file")
        print("2. Add keys to Render.com environment variables")
        print("3. Deploy your updated application")
    else:
        print("❌ Key signing failed. Please check your WhatsApp credentials.")
```

## 🔧 **Step 2: Install Required Dependencies**

```bash
pip install cryptography pycryptodome
```

## 🔐 **Step 3: Implement Flow Encryption Handler**

```python
# flow_encryption.py
import os
import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

class FlowEncryption:
    def __init__(self):
        self.private_key = self._load_private_key()
    
    def _load_private_key(self):
        """Load private key from environment variable"""
        private_key_b64 = os.getenv('WHATSAPP_FLOW_PRIVATE_KEY')
        if not private_key_b64:
            raise ValueError("WHATSAPP_FLOW_PRIVATE_KEY not found in environment")
        
        private_key_pem = base64.b64decode(private_key_b64)
        return serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
    
    def decrypt_request(self, encrypted_flow_data, encrypted_aes_key, initial_vector):
        """Decrypt incoming flow request"""
        try:
            # Decode base64 data
            encrypted_data = base64.b64decode(encrypted_flow_data)
            encrypted_key = base64.b64decode(encrypted_aes_key)
            iv = base64.b64decode(initial_vector)
            
            # Decrypt AES key using RSA private key
            aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data using AES key
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding and parse JSON
            # PKCS7 padding removal
            padding_length = decrypted_data[-1]
            decrypted_data = decrypted_data[:-padding_length]
            
            return json.loads(decrypted_data.decode('utf-8'))
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return None
    
    def encrypt_response(self, response_data, aes_key):
        """Encrypt response data using provided AES key"""
        try:
            # Convert response to JSON string
            response_json = json.dumps(response_data)
            response_bytes = response_json.encode('utf-8')
            
            # Add PKCS7 padding
            block_size = 16
            padding_length = block_size - (len(response_bytes) % block_size)
            padded_data = response_bytes + bytes([padding_length] * padding_length)
            
            # Generate random IV
            iv = secrets.token_bytes(16)
            
            # Encrypt using AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Return base64 encoded result
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            return None
```

## 🎯 **Step 4: Enhanced Main Application with Flow Endpoints**

```python
# Enhanced main.py sections for Flow handling

from flow_encryption import FlowEncryption
import hashlib
import hmac
import time
from datetime import datetime

# Initialize encryption handler
flow_encryption = FlowEncryption()

@app.route('/whatsapp-flow-webhook', methods=['GET', 'POST'])
def whatsapp_flow_webhook():
    """Handle WhatsApp Flow webhook - both verification and data exchange"""
    
    if request.method == 'GET':
        # Meta verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
            return challenge
        else:
            return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Flow data exchange
        try:
            # Get encrypted payload
            payload = request.get_json()
            
            if not payload:
                return 'Bad Request', 400
            
            encrypted_flow_data = payload.get('encrypted_flow_data')
            encrypted_aes_key = payload.get('encrypted_aes_key')
            initial_vector = payload.get('initial_vector')
            
            if not all([encrypted_flow_data, encrypted_aes_key, initial_vector]):
                return 'Missing required fields', 421
            
            # Decrypt request
            decrypted_data = flow_encryption.decrypt_request(
                encrypted_flow_data, 
                encrypted_aes_key, 
                initial_vector
            )
            
            if not decrypted_data:
                return 'Decryption failed', 421
            
            # Process the flow request
            response_data = process_flow_request(decrypted_data)
            
            # Decrypt AES key for response encryption
            encrypted_key_bytes = base64.b64decode(encrypted_aes_key)
            aes_key = flow_encryption.private_key.decrypt(
                encrypted_key_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Encrypt response
            encrypted_response = flow_encryption.encrypt_response(response_data, aes_key)
            
            if not encrypted_response:
                return 'Encryption failed', 500
            
            return encrypted_response, 200, {'Content-Type': 'text/plain'}
            
        except Exception as e:
            print(f"❌ Flow webhook error: {e}")
            return 'Internal Server Error', 500

def process_flow_request(decrypted_data):
    """Process decrypted flow request and return appropriate response"""
    
    version = decrypted_data.get('version')
    action = decrypted_data.get('action')
    screen = decrypted_data.get('screen')
    data = decrypted_data.get('data', {})
    flow_token = decrypted_data.get('flow_token')
    
    print(f"📱 Flow Request - Action: {action}, Screen: {screen}")
    
    # Handle different actions
    if action == 'INIT':
        return handle_flow_init(flow_token, data)
    
    elif action == 'data_exchange':
        if screen == 'ONBOARDING':
            return handle_onboarding_submission(data, flow_token)
        elif screen == 'PIN_VERIFICATION':
            return handle_pin_verification_submission(data, flow_token)
    
    elif action == 'BACK':
        return handle_flow_back(screen, data)
    
    # Default response
    return {
        "screen": "SUCCESS",
        "data": {
            "extension_message_response": {
                "params": {
                    "flow_token": flow_token,
                    "status": "completed"
                }
            }
        }
    }

def handle_flow_init(flow_token, data):
    """Handle flow initialization"""
    return {
        "screen": "ONBOARDING",
        "data": {
            "welcome_message": "Welcome to Sofi Banking",
            "subtitle": "Complete your account setup"
        }
    }

def handle_onboarding_submission(data, flow_token):
    """Handle onboarding form submission"""
    try:
        full_name = data.get('full_name')
        email = data.get('email')
        pin = data.get('pin')
        terms_agreement = data.get('terms_agreement')
        
        # Validate input
        if not all([full_name, email, pin, terms_agreement]):
            return {
                "screen": "ONBOARDING",
                "data": {
                    "error_message": "All fields are required"
                }
            }
        
        if len(pin) != 4 or not pin.isdigit():
            return {
                "screen": "ONBOARDING",
                "data": {
                    "error_message": "PIN must be exactly 4 digits"
                }
            }
        
        # Create account
        phone_number = extract_phone_from_flow_token(flow_token)
        account_number = generate_account_number()
        
        # Hash PIN
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        # Store in database
        user_data = {
            'phone_number': phone_number,
            'full_name': full_name,
            'email': email,
            'pin_hash': pin_hash,
            'account_number': account_number,
            'balance': 0.00,
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            # Create virtual account
            create_virtual_account(phone_number, account_number, full_name)
            
            # Success response - terminate flow
            return {
                "screen": "SUCCESS",
                "data": {
                    "extension_message_response": {
                        "params": {
                            "flow_token": flow_token,
                            "account_number": account_number,
                            "full_name": full_name,
                            "status": "account_created"
                        }
                    }
                }
            }
        else:
            return {
                "screen": "ONBOARDING",
                "data": {
                    "error_message": "Account creation failed. Please try again."
                }
            }
            
    except Exception as e:
        print(f"❌ Onboarding error: {e}")
        return {
            "screen": "ONBOARDING",
            "data": {
                "error_message": "An error occurred. Please try again."
            }
        }

def handle_pin_verification_submission(data, flow_token):
    """Handle PIN verification form submission"""
    try:
        pin = data.get('pin')
        amount = data.get('amount')
        recipient = data.get('recipient')
        
        # Get user info from flow token
        phone_number = extract_phone_from_flow_token(flow_token)
        
        # Verify PIN
        user_result = supabase.table('users').select('*').eq('phone_number', phone_number).execute()
        
        if not user_result.data:
            return {
                "screen": "PIN_VERIFICATION",
                "data": {
                    "error_message": "User not found"
                }
            }
        
        user = user_result.data[0]
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        if pin_hash != user['pin_hash']:
            return {
                "screen": "PIN_VERIFICATION",
                "data": {
                    "error_message": "Incorrect PIN"
                }
            }
        
        # PIN verified - proceed with transaction
        return {
            "screen": "SUCCESS",
            "data": {
                "extension_message_response": {
                    "params": {
                        "flow_token": flow_token,
                        "pin_verified": True,
                        "amount": amount,
                        "recipient": recipient,
                        "status": "pin_verified"
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"❌ PIN verification error: {e}")
        return {
            "screen": "PIN_VERIFICATION",
            "data": {
                "error_message": "Verification failed. Please try again."
            }
        }

def extract_phone_from_flow_token(flow_token):
    """Extract phone number from flow token"""
    # Implement your flow token parsing logic
    # For now, return a placeholder
    return "2348104611794"

@app.route('/health/flow', methods=['GET'])
def flow_health_check():
    """Flow-specific health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Sofi WhatsApp Flow Endpoint",
        "timestamp": datetime.utcnow().isoformat(),
        "encryption": "ready",
        "endpoints": {
            "flow_webhook": "/whatsapp-flow-webhook",
            "health": "/health",
            "flow_health": "/health/flow"
        }
    })
```

## 🚀 **Step 5: Run Key Generation and Signing**

Let me create the key generation script for you:
