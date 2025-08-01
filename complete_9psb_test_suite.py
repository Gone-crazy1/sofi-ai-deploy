#!/usr/bin/env python3
"""
🧪 COMPLETE 9PSB WAAS API TEST SUITE
Based on your test documentation with all 17 endpoints
"""

import os
import json
import uuid
import requests
from datetime import datetime
from fill_in_endpoints import NINEPSBApiTemplate
from dotenv import load_dotenv

load_dotenv()

def run_comprehensive_tests():
    """Run all 17 test cases from your documentation"""
    
    print("🚀 COMPLETE 9PSB WAAS API TEST SUITE")
    print("=" * 60)
    
    # Initialize API
    api = NINEPSBApiTemplate(
        api_key=os.getenv("NINEPSB_API_KEY"),
        secret_key=os.getenv("NINEPSB_SECRET_KEY"),
        base_url=os.getenv("NINEPSB_BASE_URL")
    )
    
    test_results = []
    
    # Test 1: Wallet Opening
    print("\n1️⃣ WALLET OPENING TEST")
    print("=" * 40)
    
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "firstName": "Test",
        "lastName": "User",
        "otherNames": "Demo",
        "email": f"test.user.{unique_id}@example.com",
        "phoneNo": "08123456789",  # Valid format
        "gender": 1,
        "dateOfBirth": "01/01/1990",
        "bvn": "22190239861",
        "password": "Test@1234"
    }
    
    print("🏦 Testing wallet creation...")
    result = api.create_virtual_account(f"user_{unique_id}", user_data)
    
    if result.get("error"):
        print(f"❌ Test 1 FAILED: {result.get('error')}")
        test_results.append(("Wallet Opening", "FAILED", result.get('error')))
        account_number = None
    else:
        print(f"✅ Test 1 PASSED: Wallet created successfully!")
        # Extract account number from response
        account_number = result.get('accountNumber') or result.get('data', {}).get('accountNumber')
        test_results.append(("Wallet Opening", "PASSED", f"Account: {account_number}"))
    
    # Test 2: Generate Token (already tested in auth)
    print("\n2️⃣ GENERATE TOKEN TEST")
    print("=" * 40)
    from utils.waas_auth import get_access_token
    token = get_access_token()
    if token:
        print("✅ Test 2 PASSED: Token generated successfully!")
        test_results.append(("Generate Token", "PASSED", f"Token: {token[:20]}..."))
    else:
        print("❌ Test 2 FAILED: Could not generate token")
        test_results.append(("Generate Token", "FAILED", "No token received"))
    
    # For remaining tests, use account number if we have one, otherwise use test account
    test_account = account_number or "1100059377"  # Use created account or fallback
    
    # Test 3: Wallet Enquiry
    print("\n3️⃣ WALLET ENQUIRY TEST")
    print("=" * 40)
    print(f"🔍 Testing wallet enquiry for account: {test_account}")
    result = api.get_wallet_details(test_account)
    
    if result.get("error"):
        print(f"❌ Test 3 FAILED: {result.get('error')}")
        test_results.append(("Wallet Enquiry", "FAILED", result.get('error')))
    else:
        print("✅ Test 3 PASSED: Wallet details retrieved!")
        test_results.append(("Wallet Enquiry", "PASSED", "Details retrieved"))
    
    # Test 4: Debit Wallet
    print("\n4️⃣ DEBIT WALLET TEST")
    print("=" * 40)
    result = api.debit_wallet(test_account, 100, narration="Test debit")
    
    if result.get("error"):
        print(f"❌ Test 4 FAILED: {result.get('error')}")
        test_results.append(("Debit Wallet", "FAILED", result.get('error')))
    else:
        print("✅ Test 4 PASSED: Wallet debited successfully!")
        test_results.append(("Debit Wallet", "PASSED", "100 NGN debited"))
    
    # Test 5: Credit Wallet
    print("\n5️⃣ CREDIT WALLET TEST")
    print("=" * 40)
    result = api.fund_wallet(test_account, 500, reference=f"CREDIT_{unique_id}")
    
    if result.get("error"):
        print(f"❌ Test 5 FAILED: {result.get('error')}")
        test_results.append(("Credit Wallet", "FAILED", result.get('error')))
    else:
        print("✅ Test 5 PASSED: Wallet credited successfully!")
        test_results.append(("Credit Wallet", "PASSED", "500 NGN credited"))
    
    # Test 6: Other Banks Account Enquiry
    print("\n6️⃣ OTHER BANKS ENQUIRY TEST")
    print("=" * 40)
    result = api.verify_account_name("0123456789", "044")  # Access Bank
    
    if result.get("error"):
        print(f"❌ Test 6 FAILED: {result.get('error')}")
        test_results.append(("Other Banks Enquiry", "FAILED", result.get('error')))
    else:
        print("✅ Test 6 PASSED: Account verification successful!")
        test_results.append(("Other Banks Enquiry", "PASSED", "Account verified"))
    
    # Test 7: Other Banks Transfer
    print("\n7️⃣ OTHER BANKS TRANSFER TEST")
    print("=" * 40)
    result = api.transfer_funds(test_account, "0123456789", 100, "044", "Test transfer")
    
    if result.get("error"):
        print(f"❌ Test 7 FAILED: {result.get('error')}")
        test_results.append(("Other Banks Transfer", "FAILED", result.get('error')))
    else:
        print("✅ Test 7 PASSED: Transfer initiated successfully!")
        test_results.append(("Other Banks Transfer", "PASSED", "100 NGN transferred"))
    
    # Test 8: Wallet Transaction History
    print("\n8️⃣ TRANSACTION HISTORY TEST")
    print("=" * 40)
    result = api.get_transaction_history(test_account, "01/01/2024", "31/12/2024")
    
    if result.get("error"):
        print(f"❌ Test 8 FAILED: {result.get('error')}")
        test_results.append(("Transaction History", "FAILED", result.get('error')))
    else:
        print("✅ Test 8 PASSED: Transaction history retrieved!")
        test_results.append(("Transaction History", "PASSED", "History retrieved"))
    
    # Test 9: Wallet Status
    print("\n9️⃣ WALLET STATUS TEST")
    print("=" * 40)
    result = api.get_wallet_status(test_account)
    
    if result.get("error"):
        print(f"❌ Test 9 FAILED: {result.get('error')}")
        test_results.append(("Wallet Status", "FAILED", result.get('error')))
    else:
        print("✅ Test 9 PASSED: Wallet status retrieved!")
        test_results.append(("Wallet Status", "PASSED", "Status retrieved"))
    
    # Test 10: Change Wallet Status (skipped - might affect real account)
    print("\n🔟 CHANGE WALLET STATUS TEST")
    print("=" * 40)
    print("⚠️  SKIPPED: Change wallet status test (might affect real account)")
    test_results.append(("Change Wallet Status", "SKIPPED", "Safety measure"))
    
    # Test 11: Wallet Transaction Requery
    print("\n1️⃣1️⃣ TRANSACTION REQUERY TEST")
    print("=" * 40)
    test_txn_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
    result = api.transaction_requery(test_txn_id)
    
    if result.get("error"):
        print(f"❌ Test 11 FAILED: {result.get('error')}")
        test_results.append(("Transaction Requery", "FAILED", result.get('error')))
    else:
        print("✅ Test 11 PASSED: Transaction requery successful!")
        test_results.append(("Transaction Requery", "PASSED", "Requery successful"))
    
    # Test 12: Wallet Upgrade
    print("\n1️⃣2️⃣ WALLET UPGRADE TEST")
    print("=" * 40)
    result = api.upgrade_wallet(test_account, 2)
    
    if result.get("error"):
        print(f"❌ Test 12 FAILED: {result.get('error')}")
        test_results.append(("Wallet Upgrade", "FAILED", result.get('error')))
    else:
        print("✅ Test 12 PASSED: Wallet upgrade initiated!")
        test_results.append(("Wallet Upgrade", "PASSED", "Upgrade to Tier 2"))
    
    # Test 13: Upgrade Status
    print("\n1️⃣3️⃣ UPGRADE STATUS TEST")
    print("=" * 40)
    result = api.get_upgrade_status(test_account)
    
    if result.get("error"):
        print(f"❌ Test 13 FAILED: {result.get('error')}")
        test_results.append(("Upgrade Status", "FAILED", result.get('error')))
    else:
        print("✅ Test 13 PASSED: Upgrade status retrieved!")
        test_results.append(("Upgrade Status", "PASSED", "Status retrieved"))
    
    # Test 14: Get Banks
    print("\n1️⃣4️⃣ GET BANKS TEST")
    print("=" * 40)
    result = api.get_banks_list()
    
    if result.get("error"):
        print(f"❌ Test 14 FAILED: {result.get('error')}")
        test_results.append(("Get Banks", "FAILED", result.get('error')))
    else:
        print("✅ Test 14 PASSED: Banks list retrieved!")
        banks_count = len(result.get('data', [])) if isinstance(result.get('data'), list) else 0
        test_results.append(("Get Banks", "PASSED", f"{banks_count} banks"))
    
    # Test 15: Notification Requery
    print("\n1️⃣5️⃣ NOTIFICATION REQUERY TEST")
    print("=" * 40)
    result = api.notification_requery(test_account)
    
    if result.get("error"):
        print(f"❌ Test 15 FAILED: {result.get('error')}")
        test_results.append(("Notification Requery", "FAILED", result.get('error')))
    else:
        print("✅ Test 15 PASSED: Notification requery successful!")
        test_results.append(("Notification Requery", "PASSED", "Requery successful"))
    
    # Test 16: Get Wallet by BVN
    print("\n1️⃣6️⃣ GET WALLET BY BVN TEST")
    print("=" * 40)
    result = api.get_wallet_by_bvn("22190239861")
    
    if result.get("error"):
        print(f"❌ Test 16 FAILED: {result.get('error')}")
        test_results.append(("Get Wallet by BVN", "FAILED", result.get('error')))
    else:
        print("✅ Test 16 PASSED: Wallet retrieved by BVN!")
        test_results.append(("Get Wallet by BVN", "PASSED", "Wallet found"))
    
    # Test 17: Wallet Upgrade File Upload (skipped - requires file)
    print("\n1️⃣7️⃣ WALLET UPGRADE FILE UPLOAD TEST")
    print("=" * 40)
    print("⚠️  SKIPPED: File upload test requires multipart form data")
    test_results.append(("Wallet Upgrade File Upload", "SKIPPED", "Requires file upload"))
    
    # Print Final Results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, status, details in test_results:
        status_icon = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
        print(f"{status_icon} {test_name:<30} {status:<10} {details}")
        
        if status == "PASSED":
            passed += 1
        elif status == "FAILED":
            failed += 1
        else:
            skipped += 1
    
    total = len(test_results)
    print("\n" + "=" * 80)
    print(f"📈 FINAL SCORE: {passed}/{total} PASSED | {failed} FAILED | {skipped} SKIPPED")
    
    if passed >= 10:  # At least 10 tests should pass
        print("🎉 INTEGRATION IS WORKING WELL!")
    else:
        print("🔧 INTEGRATION NEEDS MORE WORK")
    
    print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_tests()
