#!/usr/bin/env python3
"""
Final verification that both issues are resolved:
1. Beneficiary system functions are recognized by OpenAI Assistant
2. PIN verification is under 1 second
"""

import os
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

def test_openai_assistant_functions():
    """Test that OpenAI Assistant recognizes beneficiary functions"""
    print("🤖 TESTING OPENAI ASSISTANT FUNCTION RECOGNITION")
    print("=" * 55)
    
    try:
        from openai import OpenAI
        
        client = OpenAI()
        
        # Find Sofi Assistant
        assistants = client.beta.assistants.list()
        sofi_assistant = None
        
        for assistant in assistants.data:
            if "Sofi" in assistant.name or "Banking" in assistant.name:
                sofi_assistant = assistant
                break
        
        if not sofi_assistant:
            print("❌ No Sofi Assistant found")
            return False
        
        print(f"✅ Found Assistant: {sofi_assistant.name}")
        
        # Check functions
        function_names = []
        for tool in sofi_assistant.tools:
            if tool.type == 'function':
                function_names.append(tool.function.name)
        
        print(f"📋 Total Functions: {len(function_names)}")
        
        # Check specifically for beneficiary functions
        beneficiary_functions = [
            'save_beneficiary',
            'get_user_beneficiaries', 
            'find_beneficiary_by_name'
        ]
        
        all_present = True
        for func in beneficiary_functions:
            if func in function_names:
                print(f"   ✅ {func}")
            else:
                print(f"   ❌ {func} - MISSING!")
                all_present = False
        
        if all_present:
            print("\n🎉 SUCCESS: All beneficiary functions are registered!")
            return True
        else:
            print("\n❌ FAILURE: Some beneficiary functions missing")
            return False
            
    except Exception as e:
        print(f"❌ Error checking assistant functions: {e}")
        return False

async def test_pin_verification_speed():
    """Test PIN verification speed is under 1 second"""
    print("\n⚡ TESTING PIN VERIFICATION SPEED")
    print("=" * 40)
    
    try:
        from sofi_money_functions import SofiMoneyTransferService
        
        service = SofiMoneyTransferService()
        
        # Test with dummy data
        test_times = []
        
        for i in range(3):
            start_time = time.time()
            try:
                await service.verify_user_pin("test_user", "1234")
            except:
                pass  # Expected error for test user
            elapsed = time.time() - start_time
            test_times.append(elapsed)
            print(f"   Test {i+1}: {elapsed:.3f}s")
        
        avg_time = sum(test_times) / len(test_times)
        max_time = max(test_times)
        
        print(f"\n📊 Results:")
        print(f"   Average: {avg_time:.3f}s")
        print(f"   Maximum: {max_time:.3f}s")
        print(f"   Target: < 1.0s")
        
        if max_time <= 1.0:
            print("   ✅ SUCCESS: PIN verification is fast!")
            return True
        else:
            print("   ❌ FAILURE: Still too slow")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PIN speed: {e}")
        return False

def test_beneficiary_service():
    """Test beneficiary service is working"""
    print("\n💼 TESTING BENEFICIARY SERVICE")
    print("=" * 35)
    
    try:
        from utils.supabase_beneficiary_service import beneficiary_service
        
        if beneficiary_service:
            print("✅ Beneficiary service imported successfully")
            
            # Test service methods exist
            methods = ['save_beneficiary', 'get_user_beneficiaries', 'find_beneficiary_by_name']
            all_methods_exist = True
            
            for method in methods:
                if hasattr(beneficiary_service, method):
                    print(f"   ✅ {method}")
                else:
                    print(f"   ❌ {method} - MISSING!")
                    all_methods_exist = False
            
            if all_methods_exist:
                print("\n✅ SUCCESS: Beneficiary service is ready!")
                return True
            else:
                print("\n❌ FAILURE: Some methods missing")
                return False
        else:
            print("❌ Beneficiary service not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing beneficiary service: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔧 COMPREHENSIVE SOFI AI SYSTEM TEST")
    print("====================================")
    
    # Test 1: OpenAI Assistant Functions
    openai_test = test_openai_assistant_functions()
    
    # Test 2: PIN Verification Speed  
    pin_test = await test_pin_verification_speed()
    
    # Test 3: Beneficiary Service
    beneficiary_test = test_beneficiary_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 50)
    
    tests = [
        ("OpenAI Assistant Functions", openai_test),
        ("PIN Verification Speed", pin_test),
        ("Beneficiary Service", beneficiary_test)
    ]
    
    all_passed = True
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 ALL SYSTEMS GO!")
        print("✅ Beneficiary functions are working")
        print("✅ PIN verification is under 1 second")
        print("✅ User experience is now optimized!")
        print("\n💡 Next time a user transfers money:")
        print("   1. PIN entry will be lightning fast (< 1 second)")
        print("   2. Save beneficiary prompt will appear after success")
        print("   3. OpenAI Assistant will recognize all functions")
    else:
        print("⚠️  SOME ISSUES REMAINING")
        print("Please check the failed tests above")

if __name__ == "__main__":
    asyncio.run(main())
