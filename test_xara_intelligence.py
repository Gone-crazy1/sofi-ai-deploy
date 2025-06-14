#!/usr/bin/env python3
"""
Test Xara-style Account Lookup Intelligence
This script tests the smart account detection functionality that automatically
resolves recipient names from account numbers and bank names, just like Xara.
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

async def test_smart_account_detection(message: str) -> dict:
    """Test the smart account detection function - Xara-style intelligence"""
    
    # Enhanced patterns for account detection
    account_patterns = [
        r'\b(\d{10,11})\b',  # 10-11 digit account numbers
        r'\b(\d{4}\s?\d{3}\s?\d{3,4})\b',  # Formatted account numbers
    ]
    
    # Enhanced bank name patterns with fuzzy matching
    bank_patterns = {
        'moniepoint': ['monie', 'moniepoint', 'monie point', 'moneypoint'],
        'access': ['access', 'access bank'],
        'gtbank': ['gtb', 'gtbank', 'guaranty trust', 'gt bank'],
        'zenith': ['zenith', 'zenith bank'],
        'uba': ['uba', 'united bank for africa'],
        'first bank': ['first bank', 'firstbank', 'fbn'],
        'wema': ['wema', 'wema bank'],
        'sterling': ['sterling', 'sterling bank'],
        'fcmb': ['fcmb', 'first city monument bank'],
        'fidelity': ['fidelity', 'fidelity bank'],
        'polaris': ['polaris', 'polaris bank'],
        'keystone': ['keystone', 'keystone bank'],
        'union': ['union bank', 'union'],
        'kuda': ['kuda', 'kuda bank']
    }
    
    detected_account = None
    detected_bank = None
    
    # Find account number
    for pattern in account_patterns:
        match = re.search(pattern, message)
        if match:
            detected_account = re.sub(r'\s', '', match.group(1))  # Remove spaces
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
    
    print(f"🔍 DETECTION RESULTS:")
    print(f"   Account: {detected_account}")
    print(f"   Bank: {detected_bank}")
    
    # Auto-verify if both found
    if detected_account and detected_bank:
        print(f"🎯 XARA-STYLE DETECTION: {detected_account} at {detected_bank}")
        
        try:
            bank_api = BankAPI()
            bank_code = bank_api.get_bank_code(detected_bank)
            
            if bank_code:
                print(f"✅ Bank code found: {bank_code}")
                verification = await bank_api.verify_account(detected_account, bank_code)
                
                if verification:
                    account_name = verification.get('account_name', 'Unknown')
                    print(f"🎉 ACCOUNT VERIFIED: {account_name.upper()}")
                    
                    return {
                        'account_found': True,
                        'account_number': detected_account,
                        'bank_name': detected_bank,
                        'account_name': account_name,
                        'auto_verified': True
                    }
                else:
                    print("❌ Account verification failed")
            else:
                print(f"❌ Bank code not found for {detected_bank}")
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")
    
    return {
        'account_found': False,
        'detected_account': detected_account,
        'detected_bank': detected_bank
    }

async def test_amount_extraction(message: str) -> float:
    """Test amount extraction from natural language"""
    # Extract amount from message - avoid account numbers
    # Look for amounts with 'k' suffix or standalone amounts not part of account numbers
    amount_patterns = [
        r'\b(\d+)k\b',  # Numbers followed by 'k' (like 2k, 10k)
        r'\bsend\s+(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # send 5000
        r'\btransfer\s+(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # transfer 1500
        r'\bpay\s+(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # pay 7500
        r'₦(\d+(?:,?\d{3})*(?:\.\d{2})?)\b',  # ₦5000
    ]
    
    amount = None
    
    for pattern in amount_patterns:
        match = re.search(pattern, message.lower())
        if match:
            amount_str = match.group(1).replace(',', '')
            
            # Handle 'k' for thousands
            if 'k' in pattern:
                amount = float(amount_str) * 1000
            else:
                amount = float(amount_str)
            
            print(f"💰 AMOUNT DETECTED: ₦{amount:,.2f}")
            break
    
    if not amount:
        print("❌ No amount detected")
    
    return amount

async def main():
    """Test various Xara-style input formats"""
    
    print("🧠 TESTING XARA-STYLE ACCOUNT LOOKUP INTELLIGENCE")
    print("=" * 60)
    
    test_messages = [
        "9048887846 Monie point send 2k",  # Exact Xara example
        "0123456789 access bank transfer 5000",
        "1234567890 gtb send 1500",
        "Send 3000 to 2468135790 zenith bank",
        "0987654321 uba 10k transfer",
        "Pay 7500 to account 1357924680 first bank",
        "2468135790 moniepoint 5k",  # Another Moniepoint test
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🧪 TEST {i}: {message}")
        print("-" * 40)
        
        # Test smart detection
        result = await test_smart_account_detection(message)
        
        # Test amount extraction
        amount = await test_amount_extraction(message)
        
        if result.get('account_found'):
            # Simulate Xara-style response
            account_name = result.get('account_name', 'UNKNOWN')
            account_number = result.get('account_number')
            bank_name = result.get('bank_name', '').title()
            
            xara_response = f"""🎯 **Transfer Details Detected:**

**Click the Verify Transaction button below to complete transfer of ₦{amount:,.2f} to {account_name.upper()} ({account_number}) at {bank_name}**

💳 **Account Verified:**
• Name: {account_name.upper()}
• Account: {account_number}
• Bank: {bank_name}
• Amount: ₦{amount:,.2f}

Proceed with this transfer? Type 'yes' to confirm or 'no' to cancel."""
            
            print("✅ XARA-STYLE RESPONSE:")
            print(xara_response)
        else:
            print("❌ Account detection failed - would use regular flow")
            
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
