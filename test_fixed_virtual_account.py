#!/usr/bin/env python3
"""
Quick test of the fixed virtual account creation
"""
import requests
import json

def test_fixed_virtual_account():
    """Test the fixed virtual account creation"""
    url = "http://localhost:5000/api/create_virtual_account"
    
    # Test data with proper field names
    test_data = {
        "first_name": "John",
        "last_name": "Doe",
        "bvn": "12345678901",
        "chat_id": "test_user_123"
    }
    
    print("🧪 Testing Fixed Virtual Account Creation")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Data: {test_data}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Content: {response.text}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                if response_json.get("status") == "success":
                    data = response_json.get("data", {})
                    print("\n🎉 SUCCESS! Virtual account created:")
                    print(f"   💳 Account Number: {data.get('accountNumber')}")
                    print(f"   🏦 Bank Name: {data.get('bankName')}")
                    print(f"   👤 Account Name: {data.get('accountName')}")
                    return True
                else:
                    print(f"\n❌ API returned error: {response_json.get('message')}")
            except json.JSONDecodeError:
                print("\n⚠️ Response is not valid JSON")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Is Flask server running?")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_fixed_virtual_account()
    if success:
        print("\n✅ Virtual account creation is working!")
    else:
        print("\n🔧 Virtual account creation needs more fixes")
