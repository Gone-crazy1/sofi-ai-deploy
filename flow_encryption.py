"""
WhatsApp Flow Encryption/Decryption Handler
Handles encryption and decryption of WhatsApp Flow data exchanges
"""

import os
import base64
import json
import secrets
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class FlowEncryption:
    """Handles WhatsApp Flow encryption and decryption"""
    
    def __init__(self):
        """Initialize with private key from environment"""
        self.private_key = self._load_private_key()
    
    def _load_private_key(self):
        """Load private key from environment variable"""
        private_key_b64 = os.getenv('WHATSAPP_FLOW_PRIVATE_KEY')
        
        if not private_key_b64:
            raise ValueError("WHATSAPP_FLOW_PRIVATE_KEY not found in environment variables")
        
        try:
            # Decode base64 and load PEM key
            private_key_pem = base64.b64decode(private_key_b64)
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=default_backend()
            )
            print("✅ Private key loaded successfully")
            return private_key
            
        except Exception as e:
            raise ValueError(f"Failed to load private key: {e}")
    
    def decrypt_request(self, encrypted_flow_data, encrypted_aes_key, initial_vector):
        """
        Decrypt incoming WhatsApp Flow request
        
        Args:
            encrypted_flow_data (str): Base64 encoded encrypted payload
            encrypted_aes_key (str): Base64 encoded encrypted AES key
            initial_vector (str): Base64 encoded initialization vector
            
        Returns:
            dict: Decrypted JSON payload or None if decryption fails
        """
        try:
            print("🔓 Decrypting WhatsApp Flow request...")
            
            # Decode base64 data
            encrypted_data = base64.b64decode(encrypted_flow_data)
            encrypted_key = base64.b64decode(encrypted_aes_key)
            iv = base64.b64decode(initial_vector)
            
            print(f"Data length: {len(encrypted_data)}")
            print(f"Key length: {len(encrypted_key)}")
            print(f"IV length: {len(iv)}")
            
            # Decrypt AES key using RSA private key
            aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            print(f"AES key decrypted, length: {len(aes_key)}")
            
            # Check if data length is valid for AES CBC
            if len(encrypted_data) % 16 != 0:
                print(f"⚠️  Data length {len(encrypted_data)} not multiple of 16, attempting to fix...")
                # Pad the data to make it a multiple of 16
                padding_needed = 16 - (len(encrypted_data) % 16)
                encrypted_data += b'\x00' * padding_needed
                print(f"Padded data length: {len(encrypted_data)}")
            
            # Decrypt data using AES key
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            try:
                decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
                
                # Remove PKCS7 padding
                if len(decrypted_padded) > 0:
                    padding_length = decrypted_padded[-1]
                    if padding_length <= 16 and padding_length > 0:
                        decrypted_data = decrypted_padded[:-padding_length]
                    else:
                        # Invalid padding, try without padding removal
                        decrypted_data = decrypted_padded.rstrip(b'\x00')
                else:
                    decrypted_data = decrypted_padded
                    
            except ValueError as ve:
                print(f"❌ AES decryption failed: {ve}")
                # Try alternative: maybe it's not properly base64 encoded
                print("🔄 Trying alternative decryption method...")
                return None
            
            # Parse JSON
            payload = json.loads(decrypted_data.decode('utf-8'))
            
            print("✅ Request decrypted successfully")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            return payload
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def encrypt_response(self, response_data, aes_key):
        """
        Encrypt response data using AES key
        
        Args:
            response_data (dict): Response data to encrypt
            aes_key (bytes): AES key from the request
            
        Returns:
            str: Base64 encoded encrypted response or None if encryption fails
        """
        try:
            print("🔒 Encrypting WhatsApp Flow response...")
            
            # Convert response to JSON string
            response_json = json.dumps(response_data)
            response_bytes = response_json.encode('utf-8')
            
            print(f"Response JSON: {response_json}")
            
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
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            print("✅ Response encrypted successfully")
            print(f"Encrypted length: {len(encrypted_data)}")
            
            return encrypted_b64
            
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def decrypt_aes_key(self, encrypted_aes_key):
        """
        Decrypt AES key for response encryption
        
        Args:
            encrypted_aes_key (str): Base64 encoded encrypted AES key
            
        Returns:
            bytes: Decrypted AES key or None if decryption fails
        """
        try:
            encrypted_key_bytes = base64.b64decode(encrypted_aes_key)
            
            aes_key = self.private_key.decrypt(
                encrypted_key_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return aes_key
            
        except Exception as e:
            print(f"❌ AES key decryption error: {e}")
            return None

# Global instance
flow_encryption = None

def get_flow_encryption():
    """Get or create flow encryption instance"""
    global flow_encryption
    
    if flow_encryption is None:
        try:
            flow_encryption = FlowEncryption()
        except Exception as e:
            print(f"❌ Failed to initialize flow encryption: {e}")
            return None
    
    return flow_encryption

def test_encryption_setup():
    """Test if encryption setup is working"""
    try:
        encryption = get_flow_encryption()
        if encryption:
            print("✅ Flow encryption setup is working")
            return True
        else:
            print("❌ Flow encryption setup failed")
            return False
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

if __name__ == "__main__":
    # Test encryption setup
    print("🧪 Testing WhatsApp Flow encryption setup...")
    test_encryption_setup()
