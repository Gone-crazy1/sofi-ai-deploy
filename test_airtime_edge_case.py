#!/usr/bin/env python3
"""
Test the specific airtime parsing edge case
Test: "Buy MTN airtime for 08012345678" should NOT extract "5678" as amount
"""

import re

def test_airtime_parsing_edge_case():
    """Test the problematic parsing case"""
    test_message = "Buy MTN airtime for 08012345678"
    
    print(f"🔍 Testing message: '{test_message}'")
    
    # These are the amount patterns from main.py
    amount_patterns = [
        r'₦\s*(\d+(?:,\d{3})*)',  # ₦100, ₦1,000
        r'\b(\d+(?:,\d{3})*)\s*naira\b',  # 100 naira
        r'\b(\d+(?:,\d{3})*)\s*(?:ngn|₦)\b',  # 100 NGN
        r'(?:buy|purchase|get|recharge).*?₦(\d{3,4})\b',  # Buy ₦500 (with currency symbol)
        r'\bwith\s*₦(\d{3,4})\b',  # with ₦500 (with currency symbol)
        r'(?:buy|purchase|get|recharge)\s+(\d{3,4})\s+(?:naira|ngn)',  # Buy 500 naira
    ]
    
    amount = None
    found_matches = []
    
    for i, pattern in enumerate(amount_patterns):
        match = re.search(pattern, test_message, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            found_matches.append((i, pattern, amount_str))
            
            # Additional validation to avoid phone numbers
            try:
                potential_amount = float(amount_str)
                if 50 <= potential_amount <= 20000:  # Reasonable airtime range
                    amount = potential_amount
                    print(f"❌ PROBLEM: Pattern {i} extracted amount: {amount}")
                    break
                else:
                    print(f"✅ Pattern {i} rejected amount {potential_amount} (out of range)")
            except ValueError:
                print(f"✅ Pattern {i} rejected non-numeric: {amount_str}")
    
    if found_matches:
        print(f"📝 Found potential matches: {found_matches}")
    else:
        print("✅ No amount patterns matched (correct behavior)")
    
    if amount is None:
        print("✅ CORRECT: No valid amount extracted from phone number")
        return True
    else:
        print(f"❌ INCORRECT: Extracted amount {amount} from phone number")
        return False

def test_valid_airtime_messages():
    """Test that valid messages still work"""
    valid_messages = [
        "Buy ₦500 MTN airtime for 08012345678",
        "Buy 1000 naira airtime for 08012345678",
        "Recharge 08012345678 with ₦200"
    ]
    
    amount_patterns = [
        r'₦\s*(\d+(?:,\d{3})*)',  # ₦100, ₦1,000
        r'\b(\d+(?:,\d{3})*)\s*naira\b',  # 100 naira
        r'\b(\d+(?:,\d{3})*)\s*(?:ngn|₦)\b',  # 100 NGN
        r'(?:buy|purchase|get|recharge).*?₦(\d{3,4})\b',  # Buy ₦500 (with currency symbol)
        r'\bwith\s*₦(\d{3,4})\b',  # with ₦500 (with currency symbol)
        r'(?:buy|purchase|get|recharge)\s+(\d{3,4})\s+(?:naira|ngn)',  # Buy 500 naira
    ]
    
    all_valid = True
    
    for message in valid_messages:
        print(f"\n🧪 Testing: '{message}'")
        amount = None
        
        for pattern in amount_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    potential_amount = float(amount_str)
                    if 50 <= potential_amount <= 20000:
                        amount = potential_amount
                        print(f"   ✅ Extracted amount: {amount}")
                        break
                except ValueError:
                    continue
        
        if amount is None:
            print(f"   ❌ Failed to extract amount from valid message")
            all_valid = False
    
    return all_valid

def main():
    print("🔧 AIRTIME PARSING EDGE CASE TEST")
    print("=" * 50)
    
    # Test the specific problematic case
    print("\n1️⃣ Testing problematic case...")
    edge_case_ok = test_airtime_parsing_edge_case()
    
    # Test that valid cases still work
    print("\n2️⃣ Testing valid cases...")
    valid_cases_ok = test_valid_airtime_messages()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    
    if edge_case_ok and valid_cases_ok:
        print("✅ ALL TESTS PASSED!")
        print("✅ Edge case handled correctly")
        print("✅ Valid cases still work")
        print("\n🎉 Airtime parsing is working perfectly!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        if not edge_case_ok:
            print("❌ Edge case not handled properly")
        if not valid_cases_ok:
            print("❌ Some valid cases broken")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
