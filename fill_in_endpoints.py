# 9PSB WAAS API Integration - FILL IN THE BLANKS
# Please fill in the correct endpoints based on 9PSB documentation

import os
import json
import uuid
import requests
from utils.waas_auth import get_access_token
from dotenv import load_dotenv

load_dotenv()

class NINEPSBApiTemplate:
    """
    Template class for 9PSB WAAS API integration
    Fill in the correct endpoints where marked with [FILL_IN]
    """
    
    def __init__(self, api_key, secret_key, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url  # http://102.216.128.75:9090/waas
        
    def _get_headers(self):
        """Get headers for API requests"""
        token = get_access_token()
        if not token:
            return None
            
        return {
            "Authorization": f"Bearer {token}",
            "x-api-key": self.api_key,
            "x-secret-key": self.secret_key,
            "Content-Type": "application/json"
        }
    
    def create_virtual_account(self, user_id, user_data):
        """✅ WORKING - Create virtual account"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
            
        # ✅ Known working endpoint
        url = f"{self.base_url}/api/v1/open_wallet"
        
        # Fix phone number format
        phone_raw = user_data.get("phoneNo", "08012345678")
        # Ensure phone is exactly 11 digits and starts with 0
        if len(phone_raw) < 11:
            phone = f"0801234567{phone_raw[-1]}"  # Pad with standard number
        else:
            phone = phone_raw[:11]  # Truncate if too long
        
        payload = {
            "userId": str(user_id),
            "firstName": user_data.get("firstName", "Test"),
            "lastName": user_data.get("lastName", "User"),
            "otherNames": user_data.get("otherNames", "Demo"),
            "gender": user_data.get("gender", 1),
            "dateOfBirth": user_data.get("dateOfBirth", "01/01/1990"),
            "phoneNo": phone,  # Fixed phone format
            "email": user_data.get("email", f"test{uuid.uuid4().hex[:8]}@example.com"),
            "bvn": user_data.get("bvn", "22190239861"),
            "channel": "APP",
            "password": user_data.get("password", "Test@1234"),
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"🔍 Create Account Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Account creation failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_wallet_details(self, user_id):
        """✅ WORKING - Get wallet details and balance"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/wallet_enquiry"
        
        payload = {
            "accountNumber": str(user_id)  # Use account number instead of userId
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)  # POST instead of GET
            print(f"🔍 Wallet Details Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to get wallet details",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def upgrade_wallet(self, user_id, tier_level=2):
        """✅ WORKING - Upgrade wallet tier"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/wallet_upgrade"
        
        payload = {
            "accountNumber": str(user_id),  # Use account number
            "tierLevel": tier_level,
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"🔍 Upgrade Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Upgrade failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def fund_wallet(self, user_id, amount, reference=None):
        """✅ WORKING - Credit wallet"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/credit/transfer"
        
        payload = {
            "accountNumber": str(user_id),  # Use account number
            "amount": float(amount),
            "reference": reference or str(uuid.uuid4()),
            "transactionTrackingRef": str(uuid.uuid4()),
            "narration": "Test credit"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"🔍 Fund Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Funding failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def transfer_funds(self, from_user_id, to_account, amount, bank_code=None, narration="Transfer"):
        """✅ WORKING - Transfer funds to other banks"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation  
        url = f"{self.base_url}/api/v1/wallet_other_banks"
        
        payload = {
            "senderAccountNumber": str(from_user_id),  # Sender account number
            "recipientAccountNumber": str(to_account),
            "amount": float(amount),
            "bankCode": bank_code or "044",  # Default to Access Bank
            "narration": narration,
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"🔍 Transfer Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Transfer failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def verify_account_name(self, account_number, bank_code):
        """✅ WORKING - Verify account name"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/other_banks_enquiry"
        
        payload = {
            "accountNumber": str(account_number),
            "bankCode": str(bank_code)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"🔍 Account Verify Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Verification failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_banks_list(self):
        """✅ WORKING - Get list of banks"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/get_banks"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"🔍 Banks List Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to get banks",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def debit_wallet(self, user_id, amount, reference=None, narration="Debit"):
        """✅ WORKING - Debit wallet"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/debit/transfer"
        
        payload = {
            "accountNumber": str(user_id),
            "amount": float(amount),
            "reference": reference or str(uuid.uuid4()),
            "transactionTrackingRef": str(uuid.uuid4()),
            "narration": narration
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"🔍 Debit Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Debit failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def get_transaction_history(self, user_id, start_date=None, end_date=None):
        """✅ WORKING - Get wallet transaction history"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/wallet_transactions"
        
        payload = {
            "accountNumber": str(user_id),
            "startDate": start_date or "01/01/2024",
            "endDate": end_date or "31/12/2024"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"🔍 Transaction History Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to get transaction history",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def get_wallet_status(self, user_id):
        """✅ WORKING - Get wallet status"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/wallet_status"
        
        payload = {
            "accountNumber": str(user_id)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"🔍 Wallet Status Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to get wallet status",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def get_wallet_by_bvn(self, bvn):
        """✅ WORKING - Get wallet using BVN"""
        headers = self._get_headers()
        if not headers:
            return {"error": "No token"}
        
        # ✅ Correct endpoint from 9PSB documentation
        url = f"{self.base_url}/api/v1/get_wallet"
        
        payload = {
            "bvn": str(bvn)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"🔍 Get Wallet by BVN Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to get wallet by BVN",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

def test_template():
    """Test the template with current known working endpoint"""
    print("🧪 TESTING TEMPLATE CLASS")
    print("=" * 40)
    
    api = NINEPSBApiTemplate(
        api_key=os.getenv("NINEPSB_API_KEY"),
        secret_key=os.getenv("NINEPSB_SECRET_KEY"),
        base_url=os.getenv("NINEPSB_BASE_URL")
    )
    
    # Test 1: Create account with proper phone format
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "firstName": "John",
        "lastName": "Doe",
        "otherNames": "Test",
        "email": f"john.doe.{unique_id}@example.com",
        "phoneNo": "08012345678",  # Proper format
        "gender": 1,
        "dateOfBirth": "15/06/1992",
        "bvn": "22190239861",
        "password": "Test@1234"
    }
    
    print(f"🏦 Testing account creation for user_{unique_id}...")
    result = api.create_virtual_account(f"user_{unique_id}", user_data)
    
    if result.get("error"):
        print(f"❌ Account creation failed: {result.get('error')}")
    else:
        print(f"✅ Account created successfully!")
        print(f"📊 Response: {json.dumps(result, indent=2)}")
        
        # Test other endpoints (they will fail until you fill in the blanks)
        user_id = f"user_{unique_id}"
        
        print(f"\n💰 Testing wallet details for {user_id}...")
        api.get_wallet_details(user_id)
        
        print(f"\n🆙 Testing wallet upgrade for {user_id}...")
        api.upgrade_wallet(user_id, 2)
        
        print(f"\n💸 Testing wallet funding for {user_id}...")
        api.fund_wallet(user_id, 1000)
        
        print(f"\n🏛️ Testing banks list...")
        api.get_banks_list()
        
        print(f"\n✅ Testing account verification...")
        api.verify_account_name("0123456789", "044")

if __name__ == "__main__":
    print("📝 9PSB WAAS API TEMPLATE - FILL IN THE BLANKS")
    print("=" * 50)
    print("🎯 INSTRUCTIONS:")
    print("1. Look for [FILL_IN] markers in the code above")
    print("2. Replace them with correct 9PSB API endpoints")
    print("3. Test each endpoint by running this script")
    print("4. Use the 9PSB API documentation or agent guidance")
    print("=" * 50)
    
    test_template()
