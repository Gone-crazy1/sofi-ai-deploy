"""
WhatsApp Flow Encryption - Fixed Implementation Based on Meta's Official Documentation
This implementation follows Meta's exact encryption specification:
- RSA-OAEP with SHA-256 for AES key decryption  
- AES-128-GCM (not CBC) for data encryption/decryption
- 16-byte authentication tag appended to encrypted data
- Flipped IV for response encryption
"""

import os
import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class FlowEncryptionFixed:
    """WhatsApp Flow encryption handler following Meta's official specification"""
    
    def __init__(self):
        """Initialize with private key from environment"""
        self.private_key = self._load_private_key()
    
    def _load_private_key(self):
        """Load private key from environment variable"""
        private_key_b64 = os.getenv('WHATSAPP_FLOW_PRIVATE_KEY')
        
        if not private_key_b64:
            raise ValueError("WHATSAPP_FLOW_PRIVATE_KEY not found in environment variables")
        
        try:
            # Decode base64 to get PEM string, then encode to bytes for loading
            private_key_pem_str = base64.b64decode(private_key_b64).decode('utf-8')
            private_key_pem_bytes = private_key_pem_str.encode('utf-8')
            
            private_key = serialization.load_pem_private_key(
                private_key_pem_bytes,
                password=None,
                backend=default_backend()
            )
            print("✅ Private key loaded successfully")
            return private_key
            
        except Exception as e:
            raise ValueError(f"Failed to load private key: {e}")
    
    def decrypt_request(self, encrypted_flow_data, encrypted_aes_key, initial_vector):
        """
        Decrypt WhatsApp Flow request using AES-GCM as per Meta's documentation
        
        Based on Meta's official docs:
        1. Decrypt AES key using RSA-OAEP with SHA-256
        2. Decrypt data using AES-GCM with 16-byte auth tag at end
        
        Args:
            encrypted_flow_data (str): Base64 encoded encrypted payload
            encrypted_aes_key (str): Base64 encoded encrypted AES key  
            initial_vector (str): Base64 encoded initialization vector
            
        Returns:
            tuple: (decrypted_payload, aes_key, iv) or None if decryption fails
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
            
            # Step 1: Decrypt AES key using RSA-OAEP with SHA-256 (Meta spec)
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
            
            # Step 2: Split encrypted data and authentication tag (Meta spec)
            # Per Meta docs: "128-bit authentication tag is appended to the end"
            TAG_LENGTH = 16  # 128 bits = 16 bytes
            
            if len(encrypted_data) < TAG_LENGTH:
                raise ValueError(f"Encrypted data too short: {len(encrypted_data)} bytes, minimum {TAG_LENGTH}")
            
            encrypted_flow_data_body = encrypted_data[:-TAG_LENGTH]
            encrypted_flow_data_tag = encrypted_data[-TAG_LENGTH:]
            
            print(f"📊 Body length: {len(encrypted_flow_data_body)}")
            print(f"📊 Tag length: {len(encrypted_flow_data_tag)}")
            
            # Step 3: Decrypt using AES-128-GCM (Meta spec, not CBC!)
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(iv, encrypted_flow_data_tag),  # GCM mode with auth tag
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt the data
            decrypted_data = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
            
            print(f"✅ AES-GCM decryption successful, length: {len(decrypted_data)}")
            
            # Step 4: Decode as UTF-8 and parse JSON
            try:
                plaintext = decrypted_data.decode('utf-8')
                print(f"✅ UTF-8 decode successful")
                print(f"📄 Plaintext (first 200 chars): {plaintext[:200]}...")
                
                payload = json.loads(plaintext)
                print("✅ JSON parsing successful")
                print(f"📋 Payload keys: {list(payload.keys())}")
                
                return payload, aes_key, iv
                
            except UnicodeDecodeError as decode_error:
                print(f"❌ UTF-8 decode failed: {decode_error}")
                print(f"🔍 Raw bytes (first 50): {decrypted_data[:50]}")
                raise ValueError(f"UTF-8 decode failed: {decode_error}")
                
            except json.JSONDecodeError as json_error:
                print(f"❌ JSON parsing failed: {json_error}")
                print(f"🔍 Text content: {plaintext}")
                raise ValueError(f"JSON parsing failed: {json_error}")
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None
    
    def encrypt_response(self, response_data, aes_key, original_iv):
        """
        Encrypt response using AES-GCM with flipped IV as per Meta's documentation
        
        Based on Meta's docs:
        1. Flip all bits of the original IV for response encryption
        2. Use AES-128-GCM to encrypt response
        3. Append 16-byte auth tag to encrypted data
        4. Return as base64 string
        
        Args:
            response_data (dict): Response data to encrypt
            aes_key (bytes): AES key from the request
            original_iv (bytes): Original IV from request (will be flipped)
            
        Returns:
            str: Base64 encoded encrypted response
        """
        try:
            print("🔒 Encrypting WhatsApp Flow response...")
            
            # Convert response to JSON string
            response_json = json.dumps(response_data)
            response_bytes = response_json.encode('utf-8')
            
            print(f"📄 Response JSON: {response_json}")
            print(f"📊 Response bytes length: {len(response_bytes)}")
            
            # Step 1: Flip IV bits as per Meta specification
            flipped_iv = bytearray()
            for byte in original_iv:
                flipped_iv.append(byte ^ 0xFF)  # XOR with 0xFF to flip all bits
            
            print(f"🔄 IV flipped for response encryption")
            
            # Step 2: Encrypt using AES-128-GCM
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(bytes(flipped_iv)),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt the data
            encrypted_data = encryptor.update(response_bytes) + encryptor.finalize()
            
            # Step 3: Append authentication tag (Meta spec)
            encrypted_with_tag = encrypted_data + encryptor.tag
            
            # Step 4: Return base64 encoded result
            encrypted_b64 = base64.b64encode(encrypted_with_tag).decode('utf-8')
            
            print(f"✅ Response encrypted successfully with AES-GCM")
            print(f"📊 Final encrypted length: {len(encrypted_with_tag)} bytes")
            
            return encrypted_b64
            
        except Exception as e:
            print(f"❌ Response encryption error: {e}")
            import traceback
            traceback.print_exc()
            return None
