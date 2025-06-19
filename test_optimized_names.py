"""
Test the optimized account name function
"""

from monnify.monnify_api import MonnifyAPI
import time

def test_optimized_names():
    """Test the new optimized account name function"""
    
    print("🔧 TESTING OPTIMIZED ACCOUNT NAME FUNCTION")
    print("=" * 50)
    
    monnify_api = MonnifyAPI()
    
    # Test cases to verify our optimization strategy
    test_cases = [
        {"first_name": "John", "last_name": "Doe", "description": "Normal names"},
        {"first_name": "Christopher", "last_name": "Williams", "description": "Long names"},
        {"first_name": "A", "last_name": "B", "description": "Single letters"},
        {"first_name": "Jo", "last_name": "Smith", "description": "Short first name"},
        {"first_name": "Ali", "last_name": "", "description": "No last name"},
        {"first_name": "Sam", "last_name": "Lee", "description": "Short names"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['description']}")
        print("-" * 30)
        
        # Test our optimization function
        optimized_name = monnify_api._optimize_account_name(
            test_case['first_name'], 
            test_case['last_name']
        )
        
        print(f"Input: '{test_case['first_name']}' + '{test_case['last_name']}'")
        print(f"Optimized: '{optimized_name}' (Length: {len(optimized_name)})")
        
        # Test with actual API
        customer_data = {
            'first_name': test_case['first_name'],
            'last_name': test_case['last_name'],
            'email': f'optimized_test_{int(time.time())}_{i}@sofi-ai.com',
            'phone': '+2348012345678',
            'user_id': f'opt_user_{i}'
        }
        
        try:
            result = monnify_api.create_virtual_account(customer_data)
            
            if result.get('success'):
                accounts = result.get('accounts', [])
                print(f"✅ Success! Created {len(accounts)} accounts:")
                
                for account in accounts:
                    actual_name = account.get('account_name')
                    print(f"   {account['bank_name']}: '{actual_name}'")
                    
                    if actual_name == optimized_name:
                        print(f"   ✅ Perfect! Optimization worked")
                    else:
                        print(f"   ⚠️ Monnify changed: '{optimized_name}' → '{actual_name}'")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📋 SUMMARY:")
    print("Testing our account name optimization against Monnify's 3-character limit")

if __name__ == "__main__":
    test_optimized_names()
