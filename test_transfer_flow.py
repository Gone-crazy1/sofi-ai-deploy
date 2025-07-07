#!/usr/bin/env python3
"""
Test Real Transfer Flow
======================
Test the complete transfer flow with PIN verification
"""

import asyncio
import requests
import json
from sofi_money_functions import SofiMoneyTransferService

async def test_real_transfer_flow():
    """Test a real transfer to 8104965538 opay"""
    
    print("💸 Testing Real Transfer Flow...")
    
    try:
        service = SofiMoneyTransferService()
        chat_id = "5495194750"  # Your chat ID
        
        print("\n📋 Transfer Details:")
        print("   Amount: ₦100")
        print("   Account: 8104965538")
        print("   Bank: Opay")
        print("   PIN: 1998")
        
        # Step 1: Initiate transfer (this should trigger PIN flow)
        print("\n1️⃣ Initiating transfer...")
        result = await service.send_money(
            telegram_chat_id=chat_id,
            account_number="8104965538",
            bank_name="opay", 
            amount=100,
            narration="Test transfer via Sofi AI"
            # No PIN - this should trigger web PIN entry
        )
        
        print(f"Transfer initiation result: {result}")
        
        if result.get("requires_pin") and result.get("show_web_pin"):
            pin_url = result.get("pin_url")
            print(f"\n🔐 PIN verification required!")
            print(f"PIN URL: {pin_url}")
            
            # Extract transaction ID from URL
            if "txn_id=" in pin_url:
                txn_id = pin_url.split("txn_id=")[1].split("&")[0]
                print(f"Transaction ID: {txn_id}")
                
                # Test the PIN entry page
                print(f"\n🌐 Testing PIN entry page...")
                response = requests.get(pin_url)
                if response.status_code == 200:
                    print("✅ PIN entry page loads successfully")
                    print("💡 You can now open this URL and enter PIN 1998")
                else:
                    print(f"❌ PIN entry page failed: {response.status_code}")
                
                # Now simulate PIN submission
                print(f"\n🔐 Simulating PIN submission...")
                pin_response = requests.post(
                    "https://pipinstallsofi.com/api/verify-pin",
                    json={
                        "pin": "1998",
                        "transaction_id": txn_id
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"PIN submission result: {pin_response.status_code}")
                if pin_response.status_code == 200:
                    print("✅ Transfer should be processing!")
                    print(f"Response: {pin_response.json()}")
                else:
                    print(f"❌ PIN submission failed: {pin_response.text}")
        
        else:
            print("❌ Transfer did not trigger PIN flow as expected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_transfer_flow())
