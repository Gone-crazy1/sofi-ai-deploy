#!/usr/bin/env python3
"""
🔍 9PSB API ENDPOINT DISCOVERY TOOL
Quickly test any endpoint path you want to try
"""

import os
import json
import uuid
import requests
from utils.waas_auth import get_access_token
from dotenv import load_dotenv

load_dotenv()

class EndpointTester:
    def __init__(self):
        self.base_url = os.getenv("NINEPSB_BASE_URL", "http://102.216.128.75:9090/waas")
        self.api_key = os.getenv("NINEPSB_API_KEY")
        self.secret_key = os.getenv("NINEPSB_SECRET_KEY")
        
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
    
    def test_endpoint(self, endpoint_path, method="GET", payload=None, user_id=None):
        """
        Test any endpoint path
        
        Args:
            endpoint_path: The API path (e.g., "api/v1/banks" or "api/v1/wallet/123")
            method: HTTP method (GET, POST, PUT, DELETE)
            payload: JSON payload for POST/PUT requests
            user_id: User ID to substitute in path if needed
        """
        headers = self._get_headers()
        if not headers:
            return {"error": "No token available"}
        
        # Build full URL
        if endpoint_path.startswith('/'):
            endpoint_path = endpoint_path[1:]  # Remove leading slash
        
        # Substitute user_id if {user_id} placeholder exists
        if user_id and '{user_id}' in endpoint_path:
            endpoint_path = endpoint_path.replace('{user_id}', str(user_id))
        
        url = f"{self.base_url}/{endpoint_path}"
        
        print(f"🔍 Testing: {method} {url}")
        if payload:
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=15)
            elif method.upper() == "POST":
                response = requests.post(url, json=payload, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=payload, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=15)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            print(f"📊 Response: {response.status_code}")
            print(f"📄 Content: {response.text}")
            
            result = {
                "status_code": response.status_code,
                "url": url,
                "method": method,
                "success": response.status_code in [200, 201],
                "raw_response": response.text
            }
            
            # Try to parse JSON
            try:
                result["json_response"] = response.json()
            except:
                result["json_response"] = None
            
            return result
            
        except Exception as e:
            return {
                "error": f"Request failed: {str(e)}",
                "url": url,
                "method": method
            }

def interactive_test():
    """Interactive endpoint testing"""
    tester = EndpointTester()
    
    print("🔍 9PSB ENDPOINT DISCOVERY TOOL")
    print("=" * 40)
    print("Enter endpoint paths to test. Type 'quit' to exit.")
    print("Examples:")
    print("  api/v1/banks")
    print("  api/v1/wallet/{user_id}")
    print("  api/v1/wallet/balance/user123")
    print()
    
    while True:
        try:
            endpoint = input("🎯 Enter endpoint path: ").strip()
            
            if endpoint.lower() in ['quit', 'exit', 'q']:
                break
            
            if not endpoint:
                continue
            
            method = input("📡 HTTP method (GET/POST) [GET]: ").strip().upper() or "GET"
            
            payload = None
            user_id = None
            
            if method == "POST":
                use_payload = input("📦 Add JSON payload? (y/n) [n]: ").strip().lower()
                if use_payload == 'y':
                    print("Enter JSON payload (paste and press Enter twice):")
                    payload_lines = []
                    while True:
                        line = input()
                        if line == "":
                            break
                        payload_lines.append(line)
                    
                    if payload_lines:
                        try:
                            payload = json.loads('\n'.join(payload_lines))
                        except:
                            print("❌ Invalid JSON, using empty payload")
                            payload = {}
            
            if '{user_id}' in endpoint:
                user_id = input("👤 Enter user ID: ").strip() or "test_user_123"
            
            print("\n" + "="*50)
            result = tester.test_endpoint(endpoint, method, payload, user_id)
            
            if result.get("success"):
                print("✅ SUCCESS!")
            elif result.get("error"):
                print(f"❌ ERROR: {result['error']}")
            else:
                print(f"⚠️  Status: {result.get('status_code')}")
            
            print("="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def quick_tests():
    """Run some quick common endpoint tests"""
    tester = EndpointTester()
    
    print("🚀 QUICK ENDPOINT TESTS")
    print("=" * 30)
    
    # Common endpoint patterns to test
    endpoints_to_test = [
        # Banks
        ("api/v1/banks", "GET"),
        ("api/v1/bank/list", "GET"),
        ("api/v1/supported_banks", "GET"),
        
        # Wallet operations
        ("api/v1/wallet/user123", "GET"),
        ("api/v1/wallet_details/user123", "GET"),
        ("api/v1/balance/user123", "GET"),
        
        # Transactions
        ("api/v1/transactions/user123", "GET"),
        ("api/v1/transaction_history/user123", "GET"),
        
        # Verification
        ("api/v1/name_enquiry", "POST"),
        ("api/v1/verify_account", "POST"),
    ]
    
    for endpoint, method in endpoints_to_test:
        print(f"\n🧪 Testing {endpoint}...")
        result = tester.test_endpoint(endpoint, method)
        
        if result.get("success"):
            print(f"✅ {endpoint} - SUCCESS")
        elif result.get("status_code") == 404:
            print(f"❌ {endpoint} - NOT FOUND")
        elif result.get("status_code") == 400:
            print(f"⚠️  {endpoint} - BAD REQUEST (might need payload)")
        else:
            print(f"❓ {endpoint} - Status: {result.get('status_code', 'ERROR')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_tests()
    else:
        interactive_test()
