#!/usr/bin/env python3
"""
Minimal PIN test - bypass imports
"""

def test_minimal():
    print("🔍 MINIMAL PIN SYSTEM TEST")
    print("=" * 40)
    
    try:
        # Test 1: Basic Python functionality
        print("1️⃣ Testing basic Python...")
        import uuid
        test_id = str(uuid.uuid4())[:8]
        print(f"✅ UUID generated: {test_id}")
        
        # Test 2: Check if utils directory exists
        print("\n2️⃣ Checking utils directory...")
        import os
        if os.path.exists('utils'):
            print("✅ Utils directory found")
            
            # List files in utils
            files = os.listdir('utils')
            print(f"📁 Files in utils: {len(files)}")
            for f in files:
                if 'pin' in f.lower():
                    print(f"   🔐 {f}")
        else:
            print("❌ Utils directory not found")
            return False
        
        # Test 3: Try to import without instantiation
        print("\n3️⃣ Testing class definition import...")
        import sys
        sys.path.append('.')
        
        # Import the module but not the instance
        import utils.secure_pin_verification as spv_module
        print("✅ Module imported successfully")
        
        # Test 4: Create our own instance
        print("\n4️⃣ Creating test instance...")
        spv_class = spv_module.SecurePinVerification
        test_instance = spv_class()
        print("✅ Instance created successfully")
        
        # Test 5: Test token generation
        print("\n5️⃣ Testing token generation...")
        test_data = {'amount': 1000, 'test': True}
        token = test_instance.store_pending_transaction(f"TEST{test_id}", test_data)
        
        if token and len(token) > 15:
            print(f"✅ Token generated: {token[:10]}...")
            
            # Test retrieval
            retrieved = test_instance.get_pending_transaction_by_token(token)
            if retrieved and retrieved.get('amount') == 1000:
                print("✅ Token retrieval works!")
                
                # Generate PIN URL
                pin_url = f"/verify-pin?token={token}"
                print(f"🔗 PIN URL: {pin_url[:40]}...")
                
                print("\n🎉 MINIMAL TEST PASSED!")
                print("✅ Core PIN system is working")
                return True
            else:
                print("❌ Token retrieval failed")
        else:
            print("❌ Token generation failed")
            
    except Exception as e:
        print(f"❌ Error in minimal test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal()
    if success:
        print(f"\n🚀 Your PIN system core is working!")
        print("Next: Test with Flask server")
    else:
        print(f"\n💥 Core system has issues")
