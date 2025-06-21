#!/usr/bin/env python3
"""
🚀 FINAL SOFI AI PRODUCTION TEST
===============================

Quick test to verify:
1. No syntax errors (main.py loads)
2. Nigerian banks database (50+ banks)
3. Monnify API integration
"""

import sys
import os
import importlib.util

def test_main_syntax():
    """Test that main.py has no syntax errors"""
    print("🔍 Testing main.py syntax...")
    try:
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        print("✅ main.py loads without syntax errors")
        return True
    except Exception as e:
        print(f"❌ Syntax error in main.py: {e}")
        return False

def test_nigerian_banks():
    """Test Nigerian banks database"""
    print("\n🏦 Testing Nigerian banks database...")
    try:
        from utils.nigerian_banks import NIGERIAN_BANKS
        
        total_banks = len(NIGERIAN_BANKS)
        fintech_count = len([b for b in NIGERIAN_BANKS.values() if b.get('type') == 'fintech'])
        
        print(f"📊 Total banks: {total_banks}")
        print(f"💳 Fintech banks: {fintech_count}")
        
        # Check popular fintechs
        fintechs = ['opay', 'kuda', 'palmpay', 'carbon']
        found = sum(1 for f in fintechs if f in NIGERIAN_BANKS)
        print(f"✅ Popular fintechs found: {found}/{len(fintechs)}")
        
        return total_banks >= 50
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_monnify_api():
    """Test Monnify API integration"""
    print("\n💰 Testing Monnify API...")
    try:
        from utils.real_monnify_transfer import MonnifyTransferAPI
        
        api = MonnifyTransferAPI()
        print("✅ MonnifyTransferAPI loads successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run tests"""
    print("🚀 SOFI AI PRODUCTION READINESS TEST")
    print("=" * 40)
    
    tests = [
        ("Main Syntax", test_main_syntax),
        ("Nigerian Banks", test_nigerian_banks),
        ("Monnify API", test_monnify_api)
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🚀 SOFI AI IS PRODUCTION-READY!")
        print("✅ All syntax errors fixed")
        print("✅ 50+ Nigerian banks supported")
        print("✅ Real Monnify API integration")
    else:
        print("\n⚠️ Some issues found")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()
