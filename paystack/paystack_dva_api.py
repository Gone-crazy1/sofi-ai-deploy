"""
Paystack Dedicated Virtual Account API Integration
Based on official Paystack documentation
"""

import os
import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class PaystackDVAAPI:
    """Paystack Dedicated Virtual Account API integration"""
    
    def __init__(self):
        """Initialize Paystack API with secret key"""
        self.secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        self.base_url = "https://api.paystack.co"
        
        if not self.secret_key:
            raise ValueError("PAYSTACK_SECRET_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        logger.info("✅ Paystack API initialized")
    
    def create_customer_with_dva(self, user_data: Dict) -> Dict[str, Any]:
        """
        Create customer and DVA with proper async handling
        1. Create customer
        2. Create DVA (may be async)
        3. Fetch DVA details via GET (the correct way!)
        """
        try:
            # Step 1: Create customer
            customer_result = self.create_customer(user_data)
            
            if not customer_result.get("success"):
                return customer_result
            
            # Extract customer data properly
            customer_data = customer_result.get("data", {})
            customer_code = customer_data.get("customer_code")
            customer_id = customer_data.get("id")
            
            if not customer_code:
                logger.error(f"❌ No customer_code in response: {customer_result}")
                return {
                    "success": False,
                    "error": "Customer creation succeeded but no customer_code returned",
                    "debug_data": customer_result
                }
            
            logger.info(f"✅ Customer created: {customer_code} (ID: {customer_id})")
            
            # Step 2: Create DVA for customer (may return "in progress")
            dva_create_result = self.create_dva_for_existing_customer(
                customer_code, 
                user_data.get("preferred_bank", "wema-bank")
            )
            
            logger.info(f"DVA creation initiated: {dva_create_result.get('message', 'Unknown status')}")
            
            # Step 3: Fetch actual DVA details via GET (the correct way!)
            dva_details = self.fetch_dva_by_customer(customer_code)
            
            if dva_details.get("success"):
                logger.info(f"✅ DVA details retrieved successfully!")
                
                return {
                    "success": True,
                    "data": {
                        "customer": customer_data,
                        "dedicated_account": dva_details.get("data")
                    },
                    "customer_code": customer_code,
                    "customer_id": customer_id,
                    "account_number": dva_details.get("account_number"),
                    "account_name": dva_details.get("account_name"),
                    "bank_name": dva_details.get("bank_name"),
                    "bank_code": dva_details.get("bank_code"),
                    "dva_id": dva_details.get("dva_id"),
                    "message": "Customer and DVA created successfully with full details"
                }
            else:
                # DVA creation might still be in progress
                logger.warning(f"⚠️ DVA details not ready yet: {dva_details.get('error')}")
                
                return {
                    "success": True,
                    "pending_dva": True,
                    "customer_code": customer_code,
                    "customer_id": customer_id,
                    "message": "Customer created, DVA assignment in progress",
                    "data": {"customer": customer_data},
                    "retry_instructions": f"Use fetch_dva_by_customer('{customer_code}') to get DVA details"
                }
                
        except Exception as e:
            logger.error(f"❌ Error in customer+DVA creation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_dva_for_existing_customer(self, customer_code: str, preferred_bank: str = "wema-bank") -> Dict[str, Any]:
        """
        Create dedicated virtual account for existing customer
        Based on: POST /dedicated_account
        """
        try:
            url = f"{self.base_url}/dedicated_account"
            
            payload = {
                "customer": customer_code,
                "preferred_bank": preferred_bank
            }
            
            logger.info(f"🔄 Creating DVA for existing customer: {customer_code}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status"):
                data = result.get("data", {})
                logger.info(f"✅ DVA created: {data.get('account_number')} - {data.get('bank', {}).get('name')}")
                return {
                    "success": True,
                    "data": data,
                    "account_number": data.get("account_number"),
                    "account_name": data.get("account_name"),
                    "bank_name": data.get("bank", {}).get("name"),
                    "bank_slug": data.get("bank", {}).get("slug")
                }
            else:
                logger.error(f"❌ DVA creation failed: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating DVA: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_dedicated_accounts(self, active: bool = True, currency: str = "NGN") -> Dict[str, Any]:
        """
        List all dedicated virtual accounts
        Based on: GET /dedicated_account
        """
        try:
            url = f"{self.base_url}/dedicated_account"
            params = {
                "active": str(active).lower(),
                "currency": currency
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status"):
                accounts = result.get("data", [])
                logger.info(f"✅ Retrieved {len(accounts)} dedicated accounts")
                return {
                    "success": True,
                    "data": accounts,
                    "meta": result.get("meta", {})
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Failed to retrieve accounts")
                }
                
        except Exception as e:
            logger.error(f"❌ Error listing DVAs: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def fetch_dedicated_account(self, account_id: int) -> Dict[str, Any]:
        """
        Get details of specific dedicated virtual account
        Based on: GET /dedicated_account/:dedicated_account_id
        """
        try:
            url = f"{self.base_url}/dedicated_account/{account_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status"):
                data = result.get("data", {})
                return {
                    "success": True,
                    "data": data,
                    "account_number": data.get("account_number"),
                    "account_name": data.get("account_name"),
                    "bank_name": data.get("bank", {}).get("name"),
                    "customer": data.get("customer", {})
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Account not found")
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching DVA {account_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def requery_dedicated_account(self, account_number: str, provider_slug: str = "wema-bank", date: str = None) -> Dict[str, Any]:
        """
        Requery dedicated virtual account for new transactions
        Based on: GET /dedicated_account/requery
        """
        try:
            url = f"{self.base_url}/dedicated_account/requery"
            params = {
                "account_number": account_number,
                "provider_slug": provider_slug
            }
            
            if date:
                params["date"] = date
            
            logger.info(f"🔄 Requerying DVA: {account_number}")
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status"):
                logger.info(f"✅ DVA requery successful: {account_number}")
                return {
                    "success": True,
                    "message": result.get("message", "Requery successful")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Requery failed")
                }
                
        except Exception as e:
            logger.error(f"❌ Error requerying DVA {account_number}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_banks(self) -> Dict[str, Any]:
        """
        Get list of supported banks for DVA
        Based on: GET /bank (or dedicated account providers)
        """
        try:
            # This endpoint might be /bank or /dedicated_account/available_providers
            # Using /bank as it's more commonly documented
            url = f"{self.base_url}/bank"
            params = {
                "country": "nigeria",
                "use_cursor": "false"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status"):
                banks = result.get("data", [])
                # Filter for banks that support DVA (usually includes slug field)
                dva_banks = [bank for bank in banks if bank.get("slug")]
                
                logger.info(f"✅ Retrieved {len(dva_banks)} DVA-supported banks")
                return {
                    "success": True,
                    "data": dva_banks
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Failed to retrieve banks")
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting supported banks: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_customer(self, user_data: Dict) -> Dict[str, Any]:
        """
        Create a customer (without DVA)
        Based on: POST /customer
        """
        try:
            url = f"{self.base_url}/customer"
            
            payload = {
                "email": user_data.get("email"),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "phone": user_data.get("phone", "")
            }
            
            # Add middle name if available
            if user_data.get("middle_name"):
                payload["middle_name"] = user_data["middle_name"]
            
            logger.info(f"🔄 Creating Paystack customer: {payload['email']}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status"):
                logger.info(f"✅ Customer created: {result['data']['customer_code']}")
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "message": result.get("message", "Customer created successfully")
                }
            else:
                logger.error(f"❌ Customer creation failed: {result}")
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Paystack API request failed: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error in customer creation: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def fetch_dva_by_customer(self, customer_code: str) -> Dict[str, Any]:
        """
        Fetch DVA details using customer code (the correct way!)
        GET /dedicated_account?customer=CUS_abc123
        """
        try:
            url = f"{self.base_url}/dedicated_account"
            params = {"customer": customer_code}
            
            logger.info(f"🔍 Fetching DVA for customer: {customer_code}")
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status") and result.get("data"):
                # Get the first (and usually only) DVA for this customer
                dva_list = result.get("data", [])
                if dva_list:
                    dva = dva_list[0]  # Take the first DVA
                    
                    logger.info(f"✅ DVA found: {dva.get('account_number')} - {dva.get('bank', {}).get('name')}")
                    
                    return {
                        "success": True,
                        "data": dva,
                        "account_number": dva.get("account_number"),
                        "account_name": dva.get("account_name"),
                        "bank_name": dva.get("bank", {}).get("name"),
                        "bank_code": dva.get("bank", {}).get("code"),
                        "dva_id": dva.get("id"),
                        "currency": dva.get("currency"),
                        "active": dva.get("active"),
                        "message": f"DVA retrieved: {dva.get('account_number')}"
                    }
                else:
                    return {
                        "success": False,
                        "error": "No DVA found for this customer"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch DVA: {result.get('message', 'Unknown error')}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching DVA: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Create global instance
paystack_dva_api = PaystackDVAAPI()


def get_paystack_dva_api() -> PaystackDVAAPI:
    """Get the global Paystack DVA API instance"""
    return paystack_dva_api
