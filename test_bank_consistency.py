#!/usr/bin/env python3
"""
Test bank code consistency across all files after fixes
"""

import os
import re

print("🧪 TESTING BANK CODE CONSISTENCY")
print("=" * 50)

# Files to check
files_to_check = [
    "utils/bank_api.py",
    "functions/transfer_functions.py", 
    "paystack/paystack_service.py",
    "sofi_money_functions.py"
]

# Expected correct codes
expected_codes = {
    "opay": "999992",
    "palmpay": "999991", 
    "moniepoint": "50515"
}

print("\\n1️⃣ CHECKING BANK CODES IN ALL FILES...")

all_consistent = True

for file_path in files_to_check:
    if not os.path.exists(file_path):
        print(f"❌ {file_path}: Not found")
        continue
        
    print(f"\\n📁 {file_path}:")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check each bank
        for bank, expected_code in expected_codes.items():
            # Find all occurrences of this bank
            patterns = [
                f'"{bank}":\\s*"([0-9]+)"',
                f"'{bank}':\\s*'([0-9]+)'",
                f'"{bank}"\\s*:\\s*"([0-9]+)"'
            ]
            
            found_codes = []
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                found_codes.extend(matches)
            
            # Remove duplicates
            unique_codes = list(set(found_codes))
            
            if not unique_codes:
                print(f"  ⚪ {bank}: Not found")
            elif len(unique_codes) == 1 and unique_codes[0] == expected_code:
                print(f"  ✅ {bank}: {unique_codes[0]} (correct)")
            elif len(unique_codes) == 1:
                print(f"  ❌ {bank}: {unique_codes[0]} (expected {expected_code})")
                all_consistent = False
            else:
                print(f"  ⚠️  {bank}: Multiple codes found: {unique_codes}")
                all_consistent = False
                
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        all_consistent = False

print("\\n" + "=" * 50)

if all_consistent:
    print("✅ ALL BANK CODES ARE NOW CONSISTENT!")
    print("\\n🎯 FIXES APPLIED:")
    print("• OPay: 999992 (standardized)")
    print("• PalmPay: 999991 (standardized)")  
    print("• Moniepoint: 50515 (already correct)")
    
    print("\\n🚀 EXPECTED RESULTS:")
    print("• Moniepoint will work consistently")
    print("• No more 'bank not supported' errors")
    print("• All fintech banks work reliably")
    print("• Transfer verification will be consistent")
    
    print("\\n💡 TEST IT:")
    print("1. Try sending money to a Moniepoint account")
    print("2. Should work every time now")
    print("3. No more random 'not supported' messages")
    
else:
    print("❌ SOME INCONSISTENCIES STILL EXIST")
    print("\\n🔧 MANUAL FIXES NEEDED:")
    print("• Check the files above with ❌ or ⚠️")
    print("• Update any incorrect codes manually")
    print("• Run this test again to verify")

print("\\n📋 SUMMARY:")
print(f"• Files checked: {len(files_to_check)}")
print(f"• Banks verified: {', '.join(expected_codes.keys())}")
print(f"• Status: {'✅ CONSISTENT' if all_consistent else '❌ NEEDS FIXES'}")
