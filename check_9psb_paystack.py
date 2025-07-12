"""
🔍 VERIFY 9PSB BANK CODE

Check if 9PSB bank code is correct with Paystack
"""

import asyncio
import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def check_9psb_with_paystack():
    """Check if 9PSB is supported by Paystack"""
    
    paystack_secret = os.getenv("PAYSTACK_SECRET_KEY")
    if not paystack_secret:
        print("❌ PAYSTACK_SECRET_KEY not found")
        return
    
    # Get list of banks from Paystack
    headers = {
        "Authorization": f"Bearer {paystack_secret}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Fetching banks from Paystack...")
        response = requests.get("https://api.paystack.co/bank", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            banks = data.get("data", [])
            
            # Search for 9PSB or 9mobile related banks
            psb_banks = []
            for bank in banks:
                name = bank.get("name", "").lower()
                code = bank.get("code", "")
                
                if "9" in name or "psb" in name or "9mobile" in name or "payment service" in name:
                    psb_banks.append({
                        "name": bank.get("name"),
                        "code": code,
                        "currency": bank.get("currency"),
                        "country": bank.get("country")
                    })
            
            print(f"📋 Found {len(psb_banks)} potential 9PSB/PSB banks:")
            for bank in psb_banks:
                print(f"   {bank['code']} - {bank['name']} ({bank.get('country', 'Unknown')})")
            
            # Specifically check for code 120001
            code_120001 = next((bank for bank in banks if bank.get("code") == "120001"), None)
            if code_120001:
                print(f"\n✅ Code 120001 found: {code_120001['name']}")
            else:
                print(f"\n❌ Code 120001 not found in Paystack banks")
                
                # Look for other 9mobile related codes
                mobile_banks = [bank for bank in banks if "9mobile" in bank.get("name", "").lower()]
                if mobile_banks:
                    print("🔍 Found other 9mobile banks:")
                    for bank in mobile_banks:
                        print(f"   {bank['code']} - {bank['name']}")
        else:
            print(f"❌ Failed to fetch banks: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking Paystack banks: {e}")

if __name__ == "__main__":
    asyncio.run(check_9psb_with_paystack())
