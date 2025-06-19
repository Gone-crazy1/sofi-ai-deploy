"""
Test to debug account name issue with Monnify
"""

from monnify.monnify_api import MonnifyAPI
import time

def test_account_name_issue():
    """Test account name creation with different lengths"""
    
    print("🔍 DEBUGGING MONNIFY ACCOUNT NAME ISSUE")
    print("=" * 50)
    
    monnify_api = MonnifyAPI()
    
    # Test cases with different name lengths
    test_cases = [
        {"first_name": "John", "last_name": "Doe", "description": "Short names"},
        {"first_name": "Christopher", "last_name": "Smith", "description": "Medium names"},
        {"first_name": "Alexander", "last_name": "Johnson-Williams", "description": "Long names"},
        {"first_name": "Clean", "last_name": "Test", "description": "Test case"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['description']}")
        print("-" * 30)
        
        full_name = f"{test_case['first_name']} {test_case['last_name']}"
        print(f"Input Name: '{full_name}' (Length: {len(full_name)})")
        
        customer_data = {
            'first_name': test_case['first_name'],
            'last_name': test_case['last_name'],
            'email': f'test_{int(time.time())}_{i}@sofi-ai.com',
            'phone': '+2348012345678',
            'user_id': f'test_user_{i}'
        }
        
        try:
            result = monnify_api.create_virtual_account(customer_data)
            
            if result.get('success'):
                accounts = result.get('accounts', [])
                print(f"✅ Success! Created {len(accounts)} accounts:")
                
                for j, account in enumerate(accounts, 1):
                    actual_name = account.get('account_name')
                    print(f"   Account {j}: {account['bank_name']}")
                    print(f"   Expected: '{full_name}'")
                    print(f"   Actual:   '{actual_name}' (Length: {len(actual_name) if actual_name else 0})")
                    print(f"   Truncated: {'Yes' if actual_name != full_name else 'No'}")
                    print()
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n📋 ANALYSIS:")
    print("If names are being truncated, we need to optimize the account name format")
    print("Possible solutions:")
    print("1. Use initials for long names (e.g., 'John D' instead of 'John Doe')")
    print("2. Truncate at word boundaries")
    print("3. Use a different naming convention")

if __name__ == "__main__":
    test_account_name_issue()
