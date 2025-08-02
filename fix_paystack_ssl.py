"""
SSL Connection Fix for Paystack API
===================================
Fixes SSL connection issues with Paystack API on Windows
"""

import os
import ssl
import urllib3
import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SSLContextAdapter(HTTPAdapter):
    """Custom SSL adapter for Paystack API connections"""
    
    def init_poolmanager(self, *args, **kwargs):
        # Create a more permissive SSL context
        context = create_urllib3_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

def create_paystack_session():
    """Create a requests session with SSL fixes for Paystack"""
    session = requests.Session()
    
    # Use custom SSL adapter
    adapter = SSLContextAdapter()
    session.mount('https://', adapter)
    
    # Set timeout and other configurations
    session.timeout = 30
    
    return session

def test_paystack_connection():
    """Test Paystack API connection with SSL fixes"""
    from dotenv import load_dotenv
    load_dotenv()
    
    secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    if not secret_key:
        print("❌ PAYSTACK_SECRET_KEY not found in environment")
        return False
    
    print("🔧 Testing Paystack connection with SSL fixes...")
    
    try:
        session = create_paystack_session()
        
        headers = {
            'Authorization': f'Bearer {secret_key}',
            'Content-Type': 'application/json'
        }
        
        # Test simple API call
        response = session.get(
            'https://api.paystack.co/bank',
            headers=headers,
            verify=False  # Disable SSL verification temporarily
        )
        
        if response.status_code == 200:
            print("✅ Paystack connection successful!")
            data = response.json()
            banks = data.get('data', [])
            print(f"Found {len(banks)} banks available")
            return True
        else:
            print(f"❌ Paystack API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔐 SSL Fix Test for Paystack")
    print("=" * 30)
    test_paystack_connection()
