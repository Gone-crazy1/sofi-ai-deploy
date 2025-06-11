#!/usr/bin/env python3
"""
Comprehensive test suite for Sofi AI virtual account and phone field integration
This script runs all critical tests to ensure the system is working correctly.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test(test_name, test_command):
    """Run a test and return the result"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(test_command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"✅ {test_name} - PASSED")
            return True
        else:
            print(f"❌ {test_name} - FAILED")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {test_name} - ERROR: {e}")
        return False

def main():
    """Run all comprehensive tests"""
    print("🚀 SOFI AI - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # List of critical tests
    tests = [
        ("Phone Field Integration", "python test_phone_field_fixed.py"),
        ("Virtual Account Creation", "python test_virtual_account_complete_fixed.py"),
        ("RLS Security Setup", "python test_rls_setup.py"),
        ("Supabase Schema Validation", "python test_supabase_schema.py"),
    ]
    
    results = []
    passed_tests = 0
    total_tests = len(tests)
    
    # Run each test
    for test_name, test_command in tests:
        success = run_test(test_name, test_command)
        results.append((test_name, success))
        if success:
            passed_tests += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 System is ready for production deployment!")
        print("\n✅ Key Features Working:")
        print("   📞 Phone field integration")
        print("   💳 Virtual account creation")
        print("   🔒 Row Level Security (RLS)")
        print("   💾 Supabase database operations")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} tests failed!")
        print("🔧 Please fix the failing tests before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
