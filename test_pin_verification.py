#!/usr/bin/env python3
"""
Test script for PIN verification endpoint
Tests the immediate receipt page functionality
"""

import requests
import json
import time
from datetime import datetime

def test_pin_verification():
    """Test the /api/verify-pin endpoint with immediate response"""
    
    # Base URL - adjust if needed
    base_url = "http://localhost:5000"
    
    print("🧪 Testing PIN Verification - Immediate Receipt Page")
    print("=" * 60)
    
    # Test 1: Create a mock transaction in temp storage
    print("\n1️⃣ Testing with mock transaction data...")
    
    # Mock transaction data (simulating what would be in app.temp_transfers)
    test_transaction_id = "test_tx_12345678"
    
    # Test payload
    test_payload = {
        "transaction_id": test_transaction_id,
        "pin": "1234"  # Test PIN
    }
    
    print(f"   📋 Transaction ID: {test_transaction_id}")
    print(f"   🔐 PIN: {test_payload['pin']}")
    
    # Measure response time
    start_time = time.time()
    
    try:
        # Make request to PIN verification endpoint
        response = requests.post(
            f"{base_url}/api/verify-pin",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10  # Should respond much faster than this
        )
        
        response_time = time.time() - start_time
        
        print(f"\n   ⏱️  Response time: {response_time:.3f} seconds")
        print(f"   📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Response: {json.dumps(result, indent=2)}")
            
            # Check if redirect_url is present (immediate response)
            if 'redirect_url' in result:
                print(f"   🚀 SUCCESS: Immediate redirect URL provided!")
                print(f"   🔗 Redirect: {result['redirect_url']}")
                
                # Test the success page
                success_url = f"{base_url}{result['redirect_url']}"
                print(f"\n2️⃣ Testing success page access...")
                print(f"   🌐 URL: {success_url}")
                
                success_response = requests.get(success_url)
                if success_response.status_code == 200:
                    print(f"   ✅ Success page loads correctly!")
                    print(f"   📄 Content length: {len(success_response.text)} bytes")
                else:
                    print(f"   ❌ Success page failed: {success_response.status_code}")
            else:
                print(f"   ⚠️  No redirect_url in response")
        else:
            print(f"   ❌ Request failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT: Response took longer than 10 seconds")
    except requests.exceptions.ConnectionError:
        print(f"   🔌 CONNECTION ERROR: Cannot connect to {base_url}")
        print(f"   💡 Make sure the Flask app is running with: python main.py")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    
    # Test timing expectations
    if 'response_time' in locals() and response_time > 2.0:
        print(f"⚠️  WARNING: Response time ({response_time:.3f}s) is slower than expected")
        print(f"   Expected: < 2.0 seconds for immediate response")
    elif 'response_time' in locals():
        print(f"✅ EXCELLENT: Fast response time ({response_time:.3f}s)")

def test_success_page():
    """Test the success page with sample data"""
    
    print("\n🧪 Testing Success Page Directly")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Sample success page parameters
    sample_params = {
        'amount': 5000.00,
        'recipient_name': 'John Doe',
        'bank': 'GTBank',
        'account_number': '0123456789',
        'reference': 'TX12345678',
        'fee': 20.00,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Build URL with parameters
    params_str = '&'.join([f"{k}={v}" for k, v in sample_params.items()])
    success_url = f"{base_url}/success?{params_str}"
    
    print(f"🌐 Testing URL: {success_url}")
    
    try:
        response = requests.get(success_url)
        
        if response.status_code == 200:
            print(f"✅ Success page loads correctly!")
            print(f"📄 Content length: {len(response.text)} bytes")
            
            # Check for key elements in the response
            content = response.text.lower()
            checks = [
                ('amount display', str(sample_params['amount']) in content),
                ('recipient name', sample_params['recipient_name'].lower() in content),
                ('bank name', sample_params['bank'].lower() in content),
                ('reference', sample_params['reference'].lower() in content)
            ]
            
            print("\n📋 Content checks:")
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}: {'FOUND' if result else 'NOT FOUND'}")
                
        else:
            print(f"❌ Success page failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR testing success page: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Sofi AI PIN Verification Tests")
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test the success page first (doesn't require transaction setup)
    test_success_page()
    
    # Test PIN verification (requires running Flask app)
    test_pin_verification()
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
