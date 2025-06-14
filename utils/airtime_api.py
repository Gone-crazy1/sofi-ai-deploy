# utils/airtime_api.py

import requests
import os
import logging
import socket
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Clubkonnect (Nellobytes) API configuration
NELLOBYTES_USERID = os.getenv("NELLOBYTES_USERID")
NELLOBYTES_APIKEY = os.getenv("NELLOBYTES_APIKEY")
NELLOBYTES_BASE_URL = "https://clubkonnect.com"  # Updated to correct domain

# Alternative endpoints for testing
ALTERNATIVE_ENDPOINTS = [
    "https://clubkonnect.com",
    "https://www.clubkonnect.com",  
    "http://clubkonnect.com",  # HTTP fallback
    "http://www.clubkonnect.com",
]

class AirtimeAPI:
    """Handle airtime and data purchases via Nellobytes API"""
    
    def __init__(self):
        self.user_id = NELLOBYTES_USERID
        self.api_key = NELLOBYTES_APIKEY
        self.base_url = NELLOBYTES_BASE_URL
        
        if not self.user_id or not self.api_key:
            logger.warning("Nellobytes API credentials not configured")
    
    def test_dns_resolution(self, domain: str) -> bool:
        """Test DNS resolution for a domain"""
        try:
            socket.gethostbyname(domain.replace('https://', '').replace('http://', ''))
            return True
        except socket.gaierror:
            logger.warning(f"DNS resolution failed for {domain}")
            return False
    
    def test_connection(self, url: str) -> bool:
        """Test basic connectivity to an endpoint"""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code < 500
        except Exception as e:
            logger.warning(f"Connection test failed for {url}: {str(e)}")
            return False
    
    def get_working_endpoint(self) -> Optional[str]:
        """Find a working endpoint from available alternatives"""
        
        # Use the corrected ALTERNATIVE_ENDPOINTS from the top of the file
        # which now correctly point to clubkonnect.com
        for endpoint in ALTERNATIVE_ENDPOINTS:
            domain = endpoint.replace('https://', '').replace('http://', '')
            
            # Test DNS resolution first
            if not self.test_dns_resolution(domain):
                logger.debug(f"DNS resolution failed for {domain}")
                continue
                
            # Test basic connectivity
            if self.test_connection(endpoint):
                logger.info(f"Using working endpoint: {endpoint}")
                return endpoint
        
        # If no endpoints work, log comprehensive error
        logger.error("All Clubkonnect endpoints failed - service appears to be down")
        logger.error("This indicates either:")
        logger.error("1. Clubkonnect API is experiencing issues")
        logger.error("2. Network connectivity problems")
        logger.error("3. DNS server problems")
        logger.error("4. API endpoint path may be incorrect")
        
        return None

    def get_network_code(self, network_name: str) -> Optional[str]:
        """Get network code for Nellobytes API"""
        network_codes = {
            "mtn": "MTN",
            "airtel": "AIRTEL", 
            "glo": "GLO",
            "9mobile": "9MOBILE",
            "etisalat": "9MOBILE"  # Fallback for old name
        }
        return network_codes.get(network_name.lower())

    def buy_airtime(self, amount: float, phone_number: str, network: str) -> Dict:
        """
        Purchase airtime via Nellobytes API with enhanced error handling
        
        Args:
            amount: Amount in NGN
            phone_number: Recipient phone number
            network: Network name (MTN, Airtel, Glo, 9mobile)
            
        Returns:
            Dict: API response with success status
        """
        try:
            if not self.user_id or not self.api_key:
                return {
                    "success": False, 
                    "message": "Nellobytes API credentials not configured. Please contact support.",
                    "error_code": "CONFIG_ERROR"
                }
            
            network_code = self.get_network_code(network)
            if not network_code:
                return {
                    "success": False, 
                    "message": f"Unsupported network: {network}",
                    "error_code": "INVALID_NETWORK"
                }
            
            # Find working endpoint
            working_endpoint = self.get_working_endpoint()
            if not working_endpoint:
                return {
                    "success": False,
                    "message": "Airtime service is temporarily unavailable. Please try again later.",
                    "error_code": "SERVICE_UNAVAILABLE"
                }
            
            # Ensure phone number is in correct format (remove +234, add 0)
            if phone_number.startswith("+234"):
                phone_number = "0" + phone_number[4:]
            elif phone_number.startswith("234"):
                phone_number = "0" + phone_number[3:]
            
            url = f"{working_endpoint}/airtime_api.php"
            
            params = {
                "userid": self.user_id,
                "pass": self.api_key,
                "amount": int(amount),  # Nellobytes expects integer
                "network": network_code,
                "phone": phone_number,
                "ref": f"SOFI{int(os.urandom(4).hex(), 16)}"  # Random reference
            }
            
            logger.info(f"Purchasing ₦{amount} {network_code} airtime for {phone_number} via {working_endpoint}")
            
            # Make request with enhanced error handling
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Nellobytes returns plain text response
                response_text = response.text.strip()
                
                # Check for success indicators
                if "successful" in response_text.lower() or "success" in response_text.lower():
                    return {
                        "success": True,
                        "message": response_text,
                        "amount": amount,
                        "network": network_code,
                        "phone": phone_number,
                        "reference": params["ref"]
                    }
                else:
                    return {
                        "success": False,
                        "message": response_text or "Airtime purchase failed - please check your balance and try again",
                        "error_code": "PURCHASE_FAILED"
                    }
            else:
                logger.error(f"Nellobytes API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "message": f"Service temporarily unavailable (Error {response.status_code}). Please try again later.",
                    "error_code": "API_ERROR"
                }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error purchasing airtime: {str(e)}")
            return {
                "success": False,
                "message": "Unable to connect to airtime service. Please check your internet connection and try again.",
                "error_code": "CONNECTION_ERROR"
            }
        except requests.exceptions.Timeout:
            logger.error("Nellobytes API timeout")
            return {
                "success": False,
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }
        except requests.exceptions.DNSError as e:
            logger.error(f"DNS error purchasing airtime: {str(e)}")
            return {
                "success": False,
                "message": "Airtime service is temporarily unreachable. Please try again later.",
                "error_code": "DNS_ERROR"
            }
        except Exception as e:
            logger.error(f"Error purchasing airtime: {str(e)}")
            return {
                "success": False,
                "message": "An unexpected error occurred. Please try again later or contact support.",
                "error_code": "INTERNAL_ERROR"
            }

    def buy_data(self, data_plan: str, phone_number: str, network: str) -> Dict:
        """
        Purchase data via Nellobytes API with enhanced error handling
        
        Args:
            data_plan: Data plan ID/code
            phone_number: Recipient phone number  
            network: Network name (MTN, Airtel, Glo, 9mobile)
            
        Returns:
            Dict: API response with success status
        """
        try:
            if not self.user_id or not self.api_key:
                return {
                    "success": False, 
                    "message": "Nellobytes API credentials not configured. Please contact support.",
                    "error_code": "CONFIG_ERROR"
                }
            
            network_code = self.get_network_code(network)
            if not network_code:
                return {
                    "success": False, 
                    "message": f"Unsupported network: {network}",
                    "error_code": "INVALID_NETWORK"
                }
            
            # Find working endpoint
            working_endpoint = self.get_working_endpoint()
            if not working_endpoint:
                return {
                    "success": False,
                    "message": "Data service is temporarily unavailable. Please try again later.",
                    "error_code": "SERVICE_UNAVAILABLE"
                }
            
            # Ensure phone number is in correct format
            if phone_number.startswith("+234"):
                phone_number = "0" + phone_number[4:]
            elif phone_number.startswith("234"):
                phone_number = "0" + phone_number[3:]
            
            url = f"{working_endpoint}/data_api.php"
            
            params = {
                "userid": self.user_id,
                "pass": self.api_key,
                "dataplan": data_plan,
                "network": network_code,
                "phone": phone_number,
                "ref": f"SOFI{int(os.urandom(4).hex(), 16)}"
            }
            
            logger.info(f"Purchasing {data_plan} data for {phone_number} on {network_code} via {working_endpoint}")
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                if "successful" in response_text.lower() or "success" in response_text.lower():
                    return {
                        "success": True,
                        "message": response_text,
                        "plan": data_plan,
                        "network": network_code,
                        "phone": phone_number,
                        "reference": params["ref"]
                    }
                else:
                    return {
                        "success": False,
                        "message": response_text or "Data purchase failed - please check your balance and try again",
                        "error_code": "PURCHASE_FAILED"
                    }
            else:
                logger.error(f"Nellobytes data API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "message": f"Service temporarily unavailable (Error {response.status_code}). Please try again later.",
                    "error_code": "API_ERROR"
                }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error purchasing data: {str(e)}")
            return {
                "success": False,
                "message": "Unable to connect to data service. Please check your internet connection and try again.",
                "error_code": "CONNECTION_ERROR"
            }
        except requests.exceptions.Timeout:
            logger.error("Nellobytes data API timeout")
            return {
                "success": False,
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }
        except requests.exceptions.DNSError as e:
            logger.error(f"DNS error purchasing data: {str(e)}")
            return {
                "success": False,
                "message": "Data service is temporarily unreachable. Please try again later.",
                "error_code": "DNS_ERROR"
            }
        except Exception as e:
            logger.error(f"Error purchasing data: {str(e)}")
            return {
                "success": False,
                "message": "An unexpected error occurred. Please try again later or contact support.",
                "error_code": "INTERNAL_ERROR"
            }
    
    def get_data_plans(self, network: str) -> Dict:
        """
        Get available data plans for a network
        
        Args:
            network: Network name (MTN, Airtel, Glo, 9mobile)
            
        Returns:
            Dict: Available data plans
        """
        # Common data plans for Nigerian networks
        data_plans = {
            "MTN": {
                "1": {"name": "500MB - 30 Days", "amount": 250, "validity": "30 days"},
                "2": {"name": "1GB - 30 Days", "amount": 350, "validity": "30 days"},
                "3": {"name": "2GB - 30 Days", "amount": 700, "validity": "30 days"},
                "4": {"name": "3GB - 30 Days", "amount": 1000, "validity": "30 days"},
                "5": {"name": "5GB - 30 Days", "amount": 1500, "validity": "30 days"},
                "6": {"name": "10GB - 30 Days", "amount": 2800, "validity": "30 days"}
            },
            "AIRTEL": {
                "1": {"name": "500MB - 30 Days", "amount": 250, "validity": "30 days"},
                "2": {"name": "1GB - 30 Days", "amount": 350, "validity": "30 days"},
                "3": {"name": "2GB - 30 Days", "amount": 700, "validity": "30 days"},
                "4": {"name": "5GB - 30 Days", "amount": 1500, "validity": "30 days"},
                "5": {"name": "10GB - 30 Days", "amount": 2800, "validity": "30 days"}
            },
            "GLO": {
                "1": {"name": "1GB - 30 Days", "amount": 350, "validity": "30 days"},
                "2": {"name": "2.9GB - 30 Days", "amount": 1000, "validity": "30 days"},
                "3": {"name": "5.8GB - 30 Days", "amount": 1500, "validity": "30 days"},
                "4": {"name": "10GB - 30 Days", "amount": 2500, "validity": "30 days"}
            },
            "9MOBILE": {
                "1": {"name": "500MB - 30 Days", "amount": 300, "validity": "30 days"},
                "2": {"name": "1.5GB - 30 Days", "amount": 500, "validity": "30 days"},
                "3": {"name": "4.5GB - 30 Days", "amount": 1500, "validity": "30 days"},
                "4": {"name": "11GB - 30 Days", "amount": 3000, "validity": "30 days"}
            }
        }
        
        network_code = self.get_network_code(network)
        if network_code and network_code in data_plans:
            return {"success": True, "plans": data_plans[network_code]}
        else:
            return {"success": False, "message": f"No data plans found for {network}"}

# Convenience function for easy importing
def get_airtime_api():
    """Get AirtimeAPI instance"""
    return AirtimeAPI()
