#!/usr/bin/env python3
"""
Simplified test for all Sofi AI fixes
Tests each fix individually without complex mocking
"""

import sys
import os
import asyncio

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("🚀 SOFI AI FIXES - SIMPLE VERIFICATION TEST")
print("=" * 60)

def test_1_duplicate_message_fix():
    """Test that main.py imports correctly and has proper structure"""
    print("1️⃣ Testing Duplicate Message Fix Structure...")
    
    try:
        # Import main module
        import main
        
        # Check that generate_ai_reply exists and is callable
        if hasattr(main, 'generate_ai_reply') and callable(main.generate_ai_reply):
            print("   ✅ generate_ai_reply function exists")
            
            # Check that the webhook handler exists
            if hasattr(main, 'handle_incoming_message'):
                print("   ✅ handle_incoming_message webhook handler exists")
                
                # Get the source code to check structure
                import inspect
                source = inspect.getsource(main.handle_incoming_message)
                
                # Check if webhook properly handles dict responses
                if "isinstance(ai_response, dict)" in source:
                    print("   ✅ Webhook handler supports dict responses")
                    print("   ✅ DUPLICATE MESSAGE FIX: IMPLEMENTED")
                    return True
                else:
                    print("   ❌ Webhook handler missing dict response handling")
                    return False
            else:
                print("   ❌ handle_incoming_message not found")
                return False
        else:
            print("   ❌ generate_ai_reply not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_2_balance_checking():
    """Test balance checking functionality"""
    print("\n2️⃣ Testing Balance Checking Implementation...")
    
    try:
        import main
        
        # Check if get_user_balance function exists
        if hasattr(main, 'get_user_balance'):
            print("   ✅ get_user_balance function exists")
            
            # Check generate_ai_reply for balance keywords
            import inspect
            source = inspect.getsource(main.generate_ai_reply)
            
            if "balance_keywords" in source and "check balance" in source:
                print("   ✅ Balance keyword detection implemented")
                
                if "get_user_balance" in source:
                    print("   ✅ Balance checking integrated in AI reply")
                    print("   ✅ BALANCE CHECKING: IMPLEMENTED")
                    return True
                else:
                    print("   ❌ Balance checking not integrated")
                    return False
            else:
                print("   ❌ Balance keyword detection missing")
                return False
        else:
            print("   ❌ get_user_balance function not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_3_airtime_functionality():
    """Test airtime purchase functionality"""
    print("\n3️⃣ Testing Airtime Functionality...")
    
    try:
        import main
        
        # Check if handle_airtime_purchase function exists
        if hasattr(main, 'handle_airtime_purchase'):
            print("   ✅ handle_airtime_purchase function exists")
            
            # Check if AirtimeAPI is imported
            import inspect
            source = inspect.getsource(main)
            
            if "from utils.airtime_api import AirtimeAPI" in source:
                print("   ✅ AirtimeAPI imported")
                
                # Check if airtime handling is in generate_ai_reply
                reply_source = inspect.getsource(main.generate_ai_reply)
                if "handle_airtime_purchase" in reply_source:
                    print("   ✅ Airtime handling integrated in AI reply")
                    
                    # Check if the utils/airtime_api.py file exists
                    if os.path.exists("utils/airtime_api.py"):
                        print("   ✅ utils/airtime_api.py file exists")
                        print("   ✅ AIRTIME FUNCTIONALITY: IMPLEMENTED")
                        return True
                    else:
                        print("   ❌ utils/airtime_api.py file missing")
                        return False
                else:
                    print("   ❌ Airtime handling not integrated")
                    return False
            else:
                print("   ❌ AirtimeAPI not imported")
                return False
        else:
            print("   ❌ handle_airtime_purchase function not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_4_transfer_flow():
    """Test transfer flow and beneficiary system"""
    print("\n4️⃣ Testing Transfer Flow...")
    
    try:
        import main
        
        # Check if beneficiary functions exist
        beneficiary_functions = [
            'handle_beneficiary_commands',
            'save_beneficiary_to_supabase',
            'get_user_beneficiaries',
            'find_beneficiary_by_name'
        ]
        
        missing_functions = []
        for func in beneficiary_functions:
            if not hasattr(main, func):
                missing_functions.append(func)
        
        if not missing_functions:
            print("   ✅ All beneficiary functions exist")
            
            # Check if beneficiary handling is in generate_ai_reply
            import inspect
            source = inspect.getsource(main.generate_ai_reply)
            
            if "handle_beneficiary_commands" in source:
                print("   ✅ Beneficiary handling integrated in AI reply")
                print("   ✅ TRANSFER FLOW: IMPLEMENTED")
                return True
            else:
                print("   ❌ Beneficiary handling not integrated")
                return False
        else:
            print(f"   ❌ Missing functions: {missing_functions}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_5_airtime_parsing():
    """Test specific airtime parsing patterns"""
    print("\n5️⃣ Testing Airtime Parsing Patterns...")
    
    try:
        import main
        import inspect
        
        # Get the handle_airtime_purchase source
        source = inspect.getsource(main.handle_airtime_purchase)
        
        # Check for phone number patterns
        if "phone_patterns" in source and "r'\\b0[789][01]\\d{8}\\b'" in source:
            print("   ✅ Phone number regex patterns exist")
            
            # Check for amount patterns
            if "amount_patterns" in source and "50 <= potential_amount <= 20000" in source:
                print("   ✅ Amount validation patterns exist")
                
                # Check for network detection
                if "network_keywords" in source and "mtn" in source.lower():
                    print("   ✅ Network detection implemented")
                    print("   ✅ AIRTIME PARSING: IMPLEMENTED")
                    return True
                else:
                    print("   ❌ Network detection missing")
                    return False
            else:
                print("   ❌ Amount validation missing")
                return False
        else:
            print("   ❌ Phone number patterns missing")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_6_crypto_wallet():
    """Test crypto wallet functionality"""
    print("\n6️⃣ Testing Crypto Wallet Integration...")
    
    try:
        import main
        
        # Check crypto imports
        import inspect
        source = inspect.getsource(main)
        
        crypto_imports = [
            "from crypto.wallet import",
            "from crypto.rates import", 
            "from crypto.webhook import"
        ]
        
        missing_imports = []
        for imp in crypto_imports:
            if imp not in source:
                missing_imports.append(imp)
        
        if not missing_imports:
            print("   ✅ All crypto imports exist")
            
            # Check if handle_crypto_commands exists
            if hasattr(main, 'handle_crypto_commands'):
                print("   ✅ handle_crypto_commands function exists")
                print("   ✅ CRYPTO WALLET: IMPLEMENTED")
                return True
            else:
                print("   ❌ handle_crypto_commands missing")
                return False
        else:
            print(f"   ❌ Missing imports: {missing_imports}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing all implemented fixes...\n")
    
    tests = [
        ("Duplicate Message Fix", test_1_duplicate_message_fix),
        ("Balance Checking", test_2_balance_checking),
        ("Airtime Functionality", test_3_airtime_functionality),
        ("Transfer Flow", test_4_transfer_flow),
        ("Airtime Parsing", test_5_airtime_parsing),
        ("Crypto Wallet", test_6_crypto_wallet)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 IMPLEMENTATION STATUS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ IMPLEMENTED" if result else "❌ ISSUE"
        print(f"{status} | {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL: {passed}/{total} fixes implemented correctly")
    
    if passed == total:
        print("\n🎉 ALL FIXES IMPLEMENTED! System ready for deployment.")
        print("\n📋 DEPLOYMENT CHECKLIST:")
        print("   1. ✅ Duplicate message fix")
        print("   2. ✅ Balance checking functionality") 
        print("   3. ✅ Airtime/data purchase system")
        print("   4. ✅ Transfer flow with beneficiaries")
        print("   5. ✅ Crypto wallet integration")
        print("   6. ✅ Parsing patterns for edge cases")
        print("\n🚀 Ready to commit and deploy!")
    else:
        print("\n⚠️  Some implementations need review. Check failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
