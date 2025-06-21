"""Test the specific issue from the screenshot"""

from utils.enhanced_intent_detection import enhanced_intent_detector

test_messages = [
    "8104611794 Opay",
    "6117945721 access bank mella", 
    "1234567891 access bank",
    "Send 5k to 1234567891 access bank"
]

print("🔍 TESTING SCREENSHOT ISSUE")
print("=" * 40)

for msg in test_messages:
    print(f"\nTesting: '{msg}'")
    
    # Test extract_transfer_info
    transfer_info = enhanced_intent_detector.extract_transfer_info(msg)
    print(f"  extract_transfer_info: {transfer_info}")
    
    # Test is_pure_account_number
    is_pure = enhanced_intent_detector.is_pure_account_number(msg)
    print(f"  is_pure_account_number: {is_pure}")
    
    # What actually gets extracted
    if transfer_info and transfer_info.get('account'):
        account = transfer_info['account']
        bank = transfer_info.get('bank', '')
        print(f"  ✅ Would extract: account={account}, bank={bank}")
    elif is_pure:
        import re
        account = re.sub(r'[^\d]', '', msg)
        print(f"  ⚠️ Pure extraction: account={account}")
    else:
        print(f"  ❌ Would fail validation")

print("\n" + "=" * 40)
