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
from cryptography.hazmat.primitives.padding import PKCS7
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
        Decrypt incoming WhatsApp Flow request using proper crypto primitives
        
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
            
            print(f"📊 Data length: {len(encrypted_data)}")
            print(f"📊 RSA key length: {len(encrypted_key)}")
            print(f"📊 IV length: {len(iv)}")
            
            # Step 1: Decrypt AES key using RSA-OAEP with SHA-256
            aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            print(f"✅ AES key decrypted, length: {len(aes_key)} bytes")
            
            # Validate AES key length (should be 16 bytes for AES-128)
            if len(aes_key) != 16:
                raise ValueError(f"Unexpected AES key length: {len(aes_key)}, expected 16")
            
            # Debug: Check if data length is valid for AES block cipher
            if len(encrypted_data) % 16 != 0:
                print(f"⚠️  CRITICAL: Data length {len(encrypted_data)} is not multiple of 16!")
                print(f"🔍 This suggests encryption/decryption key mismatch")
                print(f"🔍 Raw encrypted data (hex): {encrypted_data.hex()}")
                
                # Log the issue but try to understand the problem
                print(f"❌ Cannot proceed with AES decryption - invalid block length")
                print(f"💡 Possible causes:")
                print(f"   1. Public/private key mismatch")
                print(f"   2. Different encryption algorithm used by Meta")
                print(f"   3. Data corruption during transmission")
                
                # Don't try to "fix" the data - this indicates a fundamental issue
                raise ValueError(f"Invalid block length: {len(encrypted_data)} (not multiple of 16)")
            
            # Step 2: Decrypt data using AES-128-CBC
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
            
            print(f"📊 Decrypted padded length: {len(decrypted_padded)}")
            print(f"🔍 First 32 bytes (hex): {decrypted_padded[:32].hex()}")
            print(f"🔍 Last 16 bytes (hex): {decrypted_padded[-16:].hex()}")
            
            # Step 3: Remove PKCS7 padding using proper unpadding
            unpadder = PKCS7(128).unpadder()  # 128-bit block size for AES
            try:
                decrypted_data = unpadder.update(decrypted_padded)
                decrypted_data += unpadder.finalize()
                print(f"✅ PKCS7 unpadding successful, final length: {len(decrypted_data)}")
            except ValueError as pad_error:
                print(f"❌ PKCS7 unpadding failed: {pad_error}")
                # Log more details for debugging
                padding_byte = decrypted_padded[-1]
                print(f"🔍 Last byte (padding indicator): {padding_byte}")
                print(f"🔍 Last 16 bytes: {[hex(b) for b in decrypted_padded[-16:]]}")
                raise ValueError(f"PKCS7 unpadding failed: {pad_error}")
            
            # Step 4: Decode as UTF-8 and parse JSON
            try:
                plaintext = decrypted_data.decode('utf-8')
                print(f"✅ UTF-8 decode successful")
                print(f"📄 Plaintext (first 200 chars): {plaintext[:200]}...")
                
                payload = json.loads(plaintext)
                print("✅ JSON parsing successful")
                print(f"📋 Payload keys: {list(payload.keys())}")
                
                return payload
                
            except UnicodeDecodeError as decode_error:
                print(f"❌ UTF-8 decode failed: {decode_error}")
                print(f"� Raw bytes (first 50): {decrypted_data[:50]}")
                raise ValueError(f"UTF-8 decode failed: {decode_error}")
                
            except json.JSONDecodeError as json_error:
                print(f"❌ JSON parsing failed: {json_error}")
                print(f"🔍 Text content: {plaintext}")
                raise ValueError(f"JSON parsing failed: {json_error}")
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def encrypt_response(self, response_data, aes_key):
        """
        Encrypt response data using AES key with proper PKCS7 padding
        
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
            
            print(f"📄 Response JSON: {response_json}")
            print(f"📊 Response bytes length: {len(response_bytes)}")
            
            # Add PKCS7 padding using proper library
            padder = PKCS7(128).padder()  # 128-bit block size for AES
            padded_data = padder.update(response_bytes)
            padded_data += padder.finalize()
            
            print(f"📊 Padded data length: {len(padded_data)}")
            
            # Generate random IV
            iv = secrets.token_bytes(16)
            
            # Encrypt using AES-128-CBC
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
            print(f"📊 Encrypted length: {len(encrypted_data)}")
            
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
