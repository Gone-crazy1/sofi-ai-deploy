# 9PSB WAAS API Integration - Complete Implementation

from utils.waas_auth import get_access_token
import requests
import os
import uuid
import json
from datetime import datetime

class NINEPSBApi:
    def __init__(self, api_key, secret_key, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        # Ensure base URL points to WAAS root
        if 'authenticate' in base_url:
            self.base_url = base_url.replace('/bank9ja/api/v2/k1/authenticate', '/waas')
        else:
            self.base_url = base_url
        
    def _get_headers(self):
        """Get common headers for API requests"""
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
        """Create a virtual account using correct 9PSB endpoint"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        # Use the correct endpoint provided by 9PSB agent
        url = "http://102.216.128.75:9090/waas/api/v1/open_wallet"
        
        # Prepare payload with required fields for 9PSB wallet creation
        dob = user_data.get("dateOfBirth") or "05/05/1988"
        if "-" in dob and "/" not in dob:
            dob = dob.replace("-", "/")
        
        gender_raw = user_data.get("gender", "M")
        gender_map = {"M": 1, "F": 2, "male": 1, "female": 2, 1: 1, 2: 2}
        gender = gender_map.get(str(gender_raw).strip().lower().capitalize(), 1)
        
        phone = user_data.get("phoneNo") or user_data.get("phone") or "08055006199"
        other_names = user_data.get("otherNames") or user_data.get("middleName") or "N/A"
        
        payload = {
            "userId": str(user_id),
            "firstName": user_data.get("firstName") or user_data.get("first_name") or "Test",
            "lastName": user_data.get("lastName") or user_data.get("last_name") or "User",
            "otherNames": other_names,
            "gender": gender,
            "dateOfBirth": dob,
            "phoneNo": phone,
            "email": user_data.get("email") or "test@example.com",
            "bvn": user_data.get("bvn") or "22190239861",
            "channel": "APP",
            "password": user_data.get("password") or "Sofi@1234",
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            print(f"🔍 Creating wallet at: {url}")
            print(f"🔍 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"🔍 Response Status: {response.status_code}")
            print(f"🔍 Response: {response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Wallet creation failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def upgrade_wallet(self, user_id, tier_level=2):
        """Upgrade wallet to higher tier (Tier 1, 2, or 3)"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/upgrade_wallet"
        
        payload = {
            "userId": str(user_id),
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
                    "error": "Wallet upgrade failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Upgrade request failed: {str(e)}"}
    
    def get_wallet_details(self, user_id):
        """Get wallet details and balance"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/wallet_details/{user_id}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
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
    
    def fund_wallet(self, user_id, amount, reference=None):
        """Fund wallet (for testing purposes)"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/fund_wallet"
        
        payload = {
            "userId": str(user_id),
            "amount": float(amount),
            "reference": reference or str(uuid.uuid4()),
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Wallet funding failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Funding request failed: {str(e)}"}
    
    def transfer_funds(self, from_user_id, to_account, amount, bank_code=None, narration="Transfer"):
        """Transfer funds from wallet to another account"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/transfer"
        
        payload = {
            "fromUserId": str(from_user_id),
            "toAccount": str(to_account),
            "amount": float(amount),
            "bankCode": bank_code,
            "narration": narration,
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Transfer failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Transfer request failed: {str(e)}"}
    
    def get_transaction_history(self, user_id, start_date=None, end_date=None, limit=50):
        """Get transaction history for a wallet"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/transaction_history/{user_id}"
        
        params = {"limit": limit}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
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
    
    def lookup_existing_wallet(self, bvn=None, phone=None):
        """Lookup existing wallet by BVN or phone number"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
        
        if bvn:
            url = f"{self.base_url}/api/v1/wallet/lookup/bvn/{bvn}"
        elif phone:
            url = f"{self.base_url}/api/v1/wallet/lookup/phone/{phone}"
        else:
            return {"error": "BVN or phone number required"}
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Lookup failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Lookup request failed: {str(e)}"}
    
    def verify_bvn(self, bvn, first_name=None, last_name=None, date_of_birth=None):
        """Verify BVN details"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/verify_bvn"
        
        payload = {
            "bvn": str(bvn),
            "firstName": first_name,
            "lastName": last_name,
            "dateOfBirth": date_of_birth
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "BVN verification failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"BVN verification request failed: {str(e)}"}
            
    def get_banks_list(self):
        """Get list of supported banks"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/banks"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to get banks list",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
            
    def verify_account_name(self, account_number, bank_code):
        """Verify account name with bank"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/name_enquiry"
        
        payload = {
            "accountNumber": str(account_number),
            "bankCode": str(bank_code)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Account verification failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Account verification request failed: {str(e)}"}
            
    # VAS Services (Airtime, Data, Bills)
    def buy_airtime(self, user_id, phone_number, amount, network):
        """Buy airtime using wallet balance"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/buy_airtime"
        
        payload = {
            "userId": str(user_id),
            "phoneNumber": str(phone_number),
            "amount": float(amount),
            "network": str(network).upper(),
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Airtime purchase failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Airtime purchase request failed: {str(e)}"}
            
    def buy_data(self, user_id, phone_number, data_plan_code, network):
        """Buy data bundle using wallet balance"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/buy_data"
        
        payload = {
            "userId": str(user_id),
            "phoneNumber": str(phone_number),
            "dataPlanCode": str(data_plan_code),
            "network": str(network).upper(),
            "transactionTrackingRef": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": "Data purchase failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Data purchase request failed: {str(e)}"}
            
    def get_data_plans(self, network):
        """Get available data plans for a network"""
        headers = self._get_headers()
        if not headers:
            return {"error": "Failed to get access token"}
            
        url = f"{self.base_url}/api/v1/data_plans/{network.upper()}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to get data plans",
                    "status_code": response.status_code,
                    "response": response.text
                }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
