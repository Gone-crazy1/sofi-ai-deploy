#!/usr/bin/env python3
"""
Test Moniepoint bank name variations and ensure they all work
"""

import os

print("🏦 TESTING MONIEPOINT BANK NAME VARIATIONS")
print("=" * 50)

# Common variations users might type
moniepoint_variations = [
    "moniepoint",
    "Moniepoint", 
    "MONIEPOINT",
    "moniepoint mfb",
    "Moniepoint MFB",
    "MONIEPOINT MFB",
    "Moniepoint Microfinance Bank",
    "moniepoint microfinance bank",
    "monie point",
    "MoniePoint",
    "moniepont",  # common typo
    "moniepiont", # common typo
]

print("\\n1️⃣ CHECKING SUPPORTED VARIATIONS:")

# Check bank_api.py
try:
    with open("utils/bank_api.py", "r", encoding="utf-8") as f:
        bank_api_content = f.read()
    
    print("\\n📁 utils/bank_api.py:")
    supported_in_bank_api = []
    
    for variation in moniepoint_variations:
        if f'"{variation.lower()}"' in bank_api_content.lower():
            supported_in_bank_api.append(variation)
            print(f"  ✅ {variation}")
        else:
            print(f"  ❌ {variation}")
            
except Exception as e:
    print(f"❌ Error reading bank_api.py: {e}")

print("\\n2️⃣ ADDING MISSING VARIATIONS:")

missing_variations = [
    "monie point",  # with space
    "moniepoint microfinance bank",
    "moniepoint bank"
]

print("\\nThese variations should be added:")
for variation in missing_variations:
    print(f"• '{variation}': '50515'")

print("\\n3️⃣ COMMON USER ISSUES:")
print("• Users type 'Monie Point' (with space)")
print("• Users type full name 'Moniepoint Microfinance Bank'")
print("• Users make typos like 'moniepont'")
print("• Case sensitivity shouldn't matter (already handled)")

print("\\n4️⃣ SOLUTION:")
print("• Add more variations to bank code mappings")
print("• Include common typos and misspellings")
print("• Include full official bank name")
print("• Include variations with/without spaces")

print("\\n💡 RECOMMENDATION:")
print("Add these to the bank mapping:")
print('  "monie point": "50515",')
print('  "moniepoint bank": "50515",')
print('  "moniepoint microfinance bank": "50515",')
print('  "moniepont": "50515",  # common typo')
print('  "moniepiont": "50515",  # common typo')

print("\\n🔧 This will make Moniepoint work for ALL user inputs!")
