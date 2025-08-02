#!/usr/bin/env python3
"""
Generate a fresh RSA key pair to compare with our problematic key
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

def generate_fresh_keys():
    """Generate a fresh RSA key pair for comparison"""
    
    print("🔑 Generating fresh RSA key pair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key to PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key to PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    print(f"✅ Generated private key ({len(private_pem)} bytes)")
    print(f"✅ Generated public key ({len(public_pem)} bytes)")
    
    # Test loading them back
    try:
        test_private = serialization.load_pem_private_key(private_pem, password=None)
        test_public = serialization.load_pem_public_key(public_pem)
        print("✅ Fresh keys load successfully")
    except Exception as e:
        print(f"❌ Fresh keys failed to load: {e}")
        return
    
    # Compare structure with our problematic key
    print("\n" + "="*50)
    print("🔍 Comparing with our problematic key...")
    
    # Our problematic key
    our_key_b64 = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2QUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktZd2dnU2lBZ0VBQW9JQkFRRFd6ZnVFc0RXQWNvaUgKV1Z3d0luRGd4Sy9yeTJmTktURktVRTB5RGYvZDY4dDd2VU5KNy9GT3o0d3g2UkY2Sk15cmJxUmFyOWJaeE4yQwpJcXpzNlJ4MWgyQ0NOZUdEZjJvcEJBZEJqZVVvRkJHQlVJTWtNWjRpakxHa0VweW9Xdm5VdTlxb1Q5aXM5bDRyCmJ4U2s0L3NhaXNCaWtGOXhzQ0JtUUFKdmVHUlBWZkZyeTB2c2owRTVFVnE0ZnlSSkUxdkd1Zm9lcmJSMHVtdlAKcWZucWNhMHBEdEpjSkVLUjVVWU03bGJvVHQxbXdnVzFtR3B1QzNPNSsxZkhRQ0N1MmRCUVVEWlhTcjRYNjg3OApZc28xMjM1QkpUSmdTaHhGdEsxdTZ2LzFqbzRMQ0VBREkyRUNlMGhJdUpXUExzM2lCN3NyRU40aEI3R3BLZERkCnZRWHpMVzdmQWdNQkFBRUNnZ0VBSUIwdmkwamsxczFJeUNOOSt0eExUKzlYOWNLMVJDRHljNC9KMnIvcER2NmYKcjJJK1d5RjZURFFQVzY3aXBBWTRhekRoZFlWd2M2SlJFNUdubE12TksyMFA2cWV2alg5UkdjeTJZUUNiMEFBZwpGZHM1b0FHakNMdE1HNkdFdGs3VHB4Qm13bDhkbjg0OWlmVFRlMHR5VVNlSlY3TUo4ZTlKQ01CdEhNazlCZmNuCkYwYzFUL3JhbnF6UGVxNmdsWFF0eExpL0RkNEU5Y2tZbG1FOVRQZjV0YWZqUjErVk5GckZoalZGd2FGemViYnUKSFdwWDZxcjdtTHNsbGVsOGp1Z0Y5dlBhL3JXZDN1NFh6Z3liRzFLOXRENVB6c1RtODZyT3dVb1BOSUtuaXFqMApPQU95aEp3ejRTYzBuNDZlZjRJQllQMFhjejhub29DZlRZOG9qdHRIOFFLQmdRRDYrUkVhb0tlNXRmTHIwZ0t0CmdmVkFRS2Y2TUtodE5zcUZmTWR3TWd4TVpKU2JUWmlhYVl0aGttWnBMWUNRNTdLRStKWlMzMmorMkdXTUFiWWwKTWFUcCs4R1FvZlRoSTBycStjZlJsNW9Md3dSU29jWTNlblMwakFKa1hRNjRadFVJU1d6UEtXeHNDU1ZGckV5UWorRFJTSDFKM0w3UlpXVzJYWjRwY2U1eVhvd0tCZ1FEYkczUGt0Z2YyNFk4L3VoRHc4djRLL01nUVg4NGdocElrCnV3am00dk54Y2xlWTgyY0N0OWgxYVBQSStHK1ZOS05Xbkg1RXlMZ2l2akJPc2tmclI1UEY2QWJ3NDZ1TURMZ2cKREZCc3JmMFI4M0VWdjRxeHViTEVRekhBcnFqTk1hU1cyNFpTN0pVeVZJQm13UmdhcXhzaVVYQzlKOC96a2xxNApmWUJxU2lqdmxRS0JnQzN5TngxbTJBMzVyM1ZZeDBDNGtBdXBTcGRWSFNDUmJWWXUxOXhFYlZmMitmWE1xT2xyCjlTWnh4T253ZUo4T3EvSUlDSTAzZFdOaWZvUzVNMzF2cno5ZTVicnl5NEFFRkEwY21XWlhtTTRhYjhvbzc3N3MKWGoxSGZKQ2ZNTGkxcXI2UG9xbnliWFVCMzU3M3dqVU4xNVpKUWJHc1BCbzNjd2JLMzl1NmpacDlBb0dBT0ZFMQpGNnRHSHNuWk5Rc1JRYTFqYU5XU1lzc05RMFR6bVdkTm9YTGlHZDNHOERSWDNOWCtXQ2RTeWV3NVdnTituRXQ3CkZSajJZMCs1UVBFSUZVeC9paFhhZXQ0NkFMUmdPelNQRTNBaEpSVUtrd2w1ajdib1lSUFlYT3RIemY0ZGpQejkKNktDUXRMQU5sTnU2NDFmcGtJZVlUN1pFK0JrOUlrQjMybG9YYllVQ2dZQitqYnczOEFiVEpmRSthM1czTDZGcwpETzB1SHplMlBEaEVXWXB2SCt1dFpJZVBRTEowMkhWWlczVW92OFFnSDBKY2VUOHlXZHhJZEQvelJVbTFBQklkCjBKbTFqUkEzRk9CUkFoUUtKVlE1TWNERndNbnpMbU9saC9GTXozRENCT0psTUMvM29Cek1DUmNJRWlrQ08zdFEKY2txZjgvMjhwemtyV3dVL1JuZVNhdz09Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K"
    
    our_key_pem = base64.b64decode(our_key_b64).decode('utf-8')
    
    print(f"📏 Our key length: {len(our_key_pem)} chars")
    print(f"📏 Fresh key length: {len(private_pem)} bytes")
    
    # Compare structure
    our_lines = our_key_pem.strip().split('\n')
    fresh_lines = private_pem.decode('utf-8').strip().split('\n')
    
    print(f"📋 Our key lines: {len(our_lines)}")
    print(f"📋 Fresh key lines: {len(fresh_lines)}")
    
    print(f"🔍 Our first line: '{our_lines[0]}'")
    print(f"🔍 Fresh first line: '{fresh_lines[0]}'")
    
    print(f"🔍 Our last line: '{our_lines[-1]}'")
    print(f"🔍 Fresh last line: '{fresh_lines[-1]}'")
    
    # Check the Base64 content structure
    our_b64_content = '\n'.join(our_lines[1:-1])  # Remove header/footer
    fresh_b64_content = '\n'.join(fresh_lines[1:-1])
    
    print(f"📋 Our Base64 content lines: {len(our_b64_content.split())}")
    print(f"📋 Fresh Base64 content lines: {len(fresh_b64_content.split())}")
    
    # Try to decode just the Base64 part
    try:
        our_decoded = base64.b64decode(''.join(our_b64_content.split()))
        print(f"✅ Our Base64 content decodes to {len(our_decoded)} bytes")
    except Exception as e:
        print(f"❌ Our Base64 content decode failed: {e}")
    
    # Generate new keys and save them properly
    print("\n" + "="*50)
    print("🔑 Creating new Base64 encoded keys...")
    
    # Encode our fresh keys to Base64
    fresh_private_b64 = base64.b64encode(private_pem).decode('utf-8')
    fresh_public_b64 = base64.b64encode(public_pem).decode('utf-8')
    
    print(f"✅ Fresh private key Base64: {len(fresh_private_b64)} chars")
    print(f"✅ Fresh public key Base64: {len(fresh_public_b64)} chars")
    
    # Save to file for use
    with open('FRESH_KEYS.txt', 'w') as f:
        f.write(f"# Fresh RSA Keys (Generated {__import__('datetime').datetime.now()})\n\n")
        f.write(f"WHATSAPP_FLOW_PRIVATE_KEY={fresh_private_b64}\n\n")
        f.write(f"WHATSAPP_FLOW_PUBLIC_KEY={fresh_public_b64}\n\n")
        f.write("# Raw PEM format:\n\n")
        f.write("PRIVATE_KEY:\n")
        f.write(private_pem.decode('utf-8'))
        f.write("\n\nPUBLIC_KEY:\n")
        f.write(public_pem.decode('utf-8'))
    
    print("📄 Fresh keys saved to FRESH_KEYS.txt")
    
    # Test the fresh Base64 keys
    print("\n🧪 Testing fresh Base64 keys...")
    try:
        test_private_pem = base64.b64decode(fresh_private_b64).decode('utf-8')
        test_private_key = serialization.load_pem_private_key(
            test_private_pem.encode('utf-8'),
            password=None
        )
        print("✅ Fresh Base64 private key loads successfully!")
        
        test_public_pem = base64.b64decode(fresh_public_b64).decode('utf-8')
        test_public_key = serialization.load_pem_public_key(
            test_public_pem.encode('utf-8')
        )
        print("✅ Fresh Base64 public key loads successfully!")
        
        return fresh_private_b64, fresh_public_b64
        
    except Exception as e:
        print(f"❌ Fresh Base64 keys failed: {e}")
        return None, None

if __name__ == "__main__":
    generate_fresh_keys()
