#!/usr/bin/env python3
"""
Quick test for account creation
"""

def quick_test():
    print("🧪 QUICK ACCOUNT CREATION TEST")
    print("=" * 40)
    
    # Test 1: Import test
    try:
        from main import create_virtual_account
        print("✅ Function imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test 2: Environment check
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['MONNIFY_API_KEY', 'MONNIFY_SECRET_KEY', 'MONNIFY_BASE_URL', 'MONNIFY_CONTRACT_CODE']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        print("🔧 Add these to your .env file:")
        for var in missing:
            print(f"   {var}=your_value_here")
        return
    else:
        print("✅ Environment variables present")
    
    # Test 3: Basic validation
    test_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'bvn': '12345678901',
        'chat_id': 'test123'
    }
    
    print(f"✅ Test data prepared: {test_data['first_name']} {test_data['last_name']}")
    
    # Test 4: Function call (this will test Monnify API)
    print("\n🚀 Testing account creation...")
    try:
        result = create_virtual_account(
            test_data['first_name'],
            test_data['last_name'], 
            test_data['bvn'],
            test_data['chat_id']
        )
        
        if result:
            if result.get('status') == 'success':
                print("✅ ACCOUNT CREATION SUCCESSFUL!")
                data = result.get('data', {})
                print(f"   Account: {data.get('accountNumber', 'N/A')}")
                print(f"   Bank: {data.get('bankName', 'N/A')}")
            else:
                print(f"❌ ACCOUNT CREATION FAILED: {result.get('message', 'Unknown error')}")
        else:
            print("❌ No result returned")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n🏁 Test complete")

if __name__ == "__main__":
    quick_test()
