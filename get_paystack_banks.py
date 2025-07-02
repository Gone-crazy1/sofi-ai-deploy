"""
Get current bank list from Paystack API to update our bank codes
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_paystack_banks():
    """Get current bank list from Paystack"""
    
    secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    if not secret_key:
        print("❌ PAYSTACK_SECRET_KEY not found")
        return
    
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Fetching current bank list from Paystack...")
        response = requests.get("https://api.paystack.co/bank", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            banks = data.get("data", [])
            
            print(f"✅ Found {len(banks)} banks")
            print("\n📋 Current Paystack Bank Codes:")
            print("=" * 60)
            
            # Sort by name for better readability
            sorted_banks = sorted(banks, key=lambda x: x.get("name", ""))
            
            for bank in sorted_banks[:50]:  # Show first 50
                name = bank.get("name", "Unknown")
                code = bank.get("code", "N/A")
                active = "✅" if bank.get("active") else "❌"
                
                print(f"{active} {name:<35} → {code}")
            
            # Create a mapping for our code
            print(f"\n🔧 Python Dictionary Format:")
            print("-" * 40)
            
            active_banks = [b for b in sorted_banks if b.get("active")]
            
            for bank in active_banks[:20]:  # First 20 active banks
                name = bank.get("name", "").lower()
                code = bank.get("code", "")
                print(f'"{name}": "{code}",')
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_paystack_banks()
