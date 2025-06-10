#!/usr/bin/env python3
"""Debug script to check which Supabase key is being used"""

import os
import jwt
from dotenv import load_dotenv

load_dotenv()

def decode_jwt_payload(token):
    """Decode JWT token payload without verification"""
    try:
        # Split the token and decode the payload
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Add padding if needed
        payload = parts[1]
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        import base64
        import json
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

# Check environment variables
supabase_url = os.getenv("SUPABASE_URL")
anon_key = os.getenv("SUPABASE_KEY")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("=== Supabase Configuration Debug ===")
print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_KEY exists: {bool(anon_key)}")
print(f"SUPABASE_SERVICE_ROLE_KEY exists: {bool(service_key)}")

if anon_key:
    anon_payload = decode_jwt_payload(anon_key)
    if anon_payload:
        print(f"Anon key role: {anon_payload.get('role', 'unknown')}")

if service_key:
    service_payload = decode_jwt_payload(service_key)
    if service_payload:
        print(f"Service key role: {service_payload.get('role', 'unknown')}")

# Check which key will be used by memory.py
selected_key = service_key or anon_key
selected_payload = decode_jwt_payload(selected_key)
print(f"\nKey being used by memory.py:")
print(f"Role: {selected_payload.get('role', 'unknown') if selected_payload else 'Could not decode'}")
print(f"Key starts with: {selected_key[:50]}..." if selected_key else "No key found")
