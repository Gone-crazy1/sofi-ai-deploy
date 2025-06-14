#!/usr/bin/env python3
"""
Test Comprehensive Nigerian Bank Support in Sofi AI
Tests all major Nigerian banks and fintech platforms for Xara-style detection
"""

import asyncio
import os, sys
import re
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from utils.bank_api import BankAPI

async def test_comprehensive_bank_support():
    """Test all Nigerian banks and fintech platforms"""
    
    print("🏦 TESTING COMPREHENSIVE NIGERIAN BANK SUPPORT")
    print("=" * 70)
    
    # Test cases covering major Nigerian banks and fintech
    test_cases = [
        # Traditional Banks
        ("1234567890 access bank send 5k", "access", "044"),
        ("9876543210 gtb transfer 3k", "gtbank", "058"),
        ("1111222233 zenith send 10k", "zenith", "057"),
        ("4444555566 uba 2k transfer", "uba", "033"),
        ("7777888899 first bank pay 1500", "first bank", "011"),
        ("0000111122 fidelity send 8k", "fidelity", "070"),
        ("3333444455 fcmb transfer 6k", "fcmb", "214"),
        ("6666777788 sterling bank 4k", "sterling", "232"),
        ("9999000011 wema send 7k", "wema", "035"),
        
        # Major Fintech Banks
        ("1234567890 opay send 5k", "opay", "304"),
        ("9876543210 moniepoint transfer 3k", "moniepoint", "50515"),
        ("1111222233 kuda send 2k", "kuda", "50211"),
        ("4444555566 palmpay 1500", "palmpay", "999991"),
        ("7777888899 vfd transfer 4k", "vfd", "566"),
        ("0000111122 9psb send 6k", "9psb", "120001"),
        ("3333444455 carbon 8k", "carbon", "565"),
        
        # Alternative spellings/formats
        ("1234567890 monie point send 2k", "moniepoint", "50515"),
        ("9876543210 palm pay transfer 3k", "palmpay", "999991"),
        ("1111222233 guaranty trust 5k", "gtbank", "058"),
        ("4444555566 united bank for africa 1k", "uba", "033"),
        ("7777888899 o pay send 9k", "opay", "304"),
        ("0000111122 9 psb transfer 7k", "9psb", "120001"),
    ]
    
    bank_api = BankAPI()
    success_count = 0
    total_tests = len(test_cases)
    
    for i, (message, expected_bank, expected_code) in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i:2d}: {message}")
        print("-" * 50)
        
        # Test smart detection
        result = await test_single_message(message, bank_api)
        
        detected_bank = result.get('detected_bank')
        bank_code = result.get('bank_code')
        
        # Check if detection matches expected
        if detected_bank == expected_bank and bank_code == expected_code:
            print(f"✅ SUCCESS: {detected_bank.upper()} ({bank_code})")
            success_count += 1
        else:
            print(f"❌ FAILED: Expected {expected_bank} ({expected_code})")
            print(f"   Got: {detected_bank} ({bank_code})")
    
    print("\n" + "=" * 70)
    print(f"🎯 TEST SUMMARY: {success_count}/{total_tests} banks supported")
    print(f"📊 SUCCESS RATE: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 ALL NIGERIAN BANKS FULLY SUPPORTED!")
    else:
        print(f"⚠️  {total_tests - success_count} banks need attention")

async def test_single_message(message: str, bank_api: BankAPI) -> dict:
    """Test a single message for bank detection"""
    
    # Enhanced patterns for account detection
    account_patterns = [
        r'\b(\d{10,11})\b',  # 10-11 digit account numbers
        r'\b(\d{4}\s?\d{3}\s?\d{3,4})\b',  # Formatted account numbers
    ]
    
    # COMPREHENSIVE bank name patterns with fuzzy matching - ALL NIGERIAN BANKS & FINTECH
    bank_patterns = {
        # Traditional Banks
        'access': ['access', 'access bank'],
        'gtbank': ['gtb', 'gtbank', 'guaranty trust', 'gt bank', 'gtworld'],
        'zenith': ['zenith', 'zenith bank'],
        'uba': ['uba', 'united bank for africa'],
        'first bank': ['first bank', 'firstbank', 'fbn'],
        'fidelity': ['fidelity', 'fidelity bank'],
        'fcmb': ['fcmb', 'first city monument bank'],
        'sterling': ['sterling', 'sterling bank'],
        'wema': ['wema', 'wema bank', 'alat', 'alat by wema'],
        'union': ['union bank', 'union'],
        'polaris': ['polaris', 'polaris bank'],
        'keystone': ['keystone', 'keystone bank'],
        'eco bank': ['eco bank', 'ecobank'],
        'heritage': ['heritage', 'heritage bank'],
        'stanbic': ['stanbic', 'stanbic ibtc'],
        'standard chartered': ['standard chartered'],
        'citi bank': ['citi bank', 'citibank'],
        
        # Major Fintech Banks & Digital Banks
        'opay': ['opay', 'o pay'],
        'moniepoint': ['monie', 'moniepoint', 'monie point', 'moneypoint'],
        'kuda': ['kuda', 'kuda bank'],
        'palmpay': ['palmpay', 'palm pay'],
        'vfd': ['vfd', 'vfd microfinance bank', 'vfd bank'],
        '9psb': ['9psb', '9 psb', '9mobile psb', '9mobile'],
        'carbon': ['carbon', 'carbon microfinance bank'],
        'rubies': ['rubies', 'rubies microfinance bank'],
        'microvis': ['microvis', 'microvis microfinance bank'],
        'raven': ['raven', 'raven bank'],
        'mint': ['mint', 'mint finex'],
        'sparkle': ['sparkle', 'sparkle microfinance bank'],
        'taj': ['taj', 'taj bank'],
        'sun trust': ['sun trust', 'suntrust'],
        'titan': ['titan', 'titan trust bank'],
        'coronation': ['coronation', 'coronation merchant bank'],
        'rand': ['rand', 'rand merchant bank'],
        
        # Other Banks
        'diamond': ['diamond', 'diamond bank'],
        'providus': ['providus', 'providus bank'],
        'jaiz': ['jaiz', 'jaiz bank'],
        'lotus': ['lotus', 'lotus bank'],
    }
    
    detected_account = None
    detected_bank = None
    
    # Find account number
    for pattern in account_patterns:
        match = re.search(pattern, message)
        if match:
            detected_account = re.sub(r'\s', '', match.group(1))
            break
    
    # Find bank name with fuzzy matching
    message_lower = message.lower()
    for bank_name, variations in bank_patterns.items():
        for variation in variations:
            if variation in message_lower:
                detected_bank = bank_name
                break
        if detected_bank:
            break
    
    # Get bank code
    bank_code = None
    if detected_bank:
        bank_code = bank_api.get_bank_code(detected_bank)
    
    return {
        'detected_account': detected_account,
        'detected_bank': detected_bank,
        'bank_code': bank_code
    }

if __name__ == "__main__":
    asyncio.run(test_comprehensive_bank_support())
