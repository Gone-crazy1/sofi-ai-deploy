"""
Test Monnify with very short account names to see if the 3-character limit is absolute
"""

from monnify.monnify_api import MonnifyAPI
import time

def test_short_names():
    """Test with very short names to see Monnify's actual limit"""
    
    print("🔍 TESTING MONNIFY WITH SHORT NAMES")
    print("=" * 40)
    
    monnify_api = MonnifyAPI()
    
    # Test with progressively shorter names
    test_cases = [
        {"first_name": "A", "last_name": "B", "expected": "A B"},
        {"first_name": "Jo", "last_name": "Do", "expected": "Jo Do"},
        {"first_name": "Max", "last_name": "Joy", "expected": "Max Joy"},
        {"first_name": "Ali", "last_name": "", "expected": "Ali"},
        {"first_name": "Sam", "last_name": "Lee", "expected": "Sam Lee"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: '{test_case['expected']}'")
        print("-" * 20)
        
        customer_data = {
            'first_name': test_case['first_name'],
            'last_name': test_case['last_name'],
            'email': f'short_test_{int(time.time())}_{i}@sofi-ai.com',
            'phone': '+2348012345678',
            'user_id': f'short_user_{i}'
        }
        
        try:
            result = monnify_api.create_virtual_account(customer_data)
            
            if result.get('success'):
                accounts = result.get('accounts', [])
                print(f"✅ Success! Created {len(accounts)} accounts:")
                
                for account in accounts:
                    actual_name = account.get('account_name')
                    print(f"   {account['bank_name']}: '{actual_name}'")
                    
                    if actual_name == test_case['expected']:
                        print(f"   ✅ Perfect match!")
                    else:
                        print(f"   ❌ Expected: '{test_case['expected']}', Got: '{actual_name}'")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📋 CONCLUSION:")
    print("Testing to find Monnify's actual character limit for account names")

if __name__ == "__main__":
    test_short_names()
