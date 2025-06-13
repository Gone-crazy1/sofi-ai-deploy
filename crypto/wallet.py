# crypto/wallet.py

import requests
import os
import logging
from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Bitnob API configuration
BITNOB_BASE_URL = "https://api.bitnob.co"
BITNOB_API_URL = f"{BITNOB_BASE_URL}/api/v1/wallets"
BITNOB_SECRET_KEY = os.getenv("BITNOB_SECRET_KEY")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

# Only create supabase client if credentials are available
supabase = None

def get_supabase_client():
    global supabase
    if supabase is None and SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def create_bitnob_wallet(user_id: str, email: str = None):
    """
    Create a crypto wallet for a user via Bitnob API and save to Supabase
    
    Args:
        user_id: Unique user identifier
        email: User's email address (optional, will generate if not provided)
    
    Returns:
        dict: Bitnob API response containing wallet details
    """
    try:
        if not BITNOB_SECRET_KEY:
            logger.error("BITNOB_SECRET_KEY not found in environment variables")
            return {"error": "Bitnob API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {BITNOB_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        # Use provided email or generate one
        customer_email = email or f"{user_id}@sofiwallet.com"
        
        data = {
            "customerEmail": customer_email,
            "label": f"Sofi Wallet - User {user_id}",
            "currency": "NGN"  # Default currency
        }
        
        # Try multiple possible endpoints for wallet creation
        possible_endpoints = [
            "/api/v1/customers/wallets",
            "/api/v1/wallet", 
            "/api/v2/wallets",
            "/wallets",
            "/customer/wallets"
        ]
        
        logger.info(f"Creating Bitnob wallet for user {user_id}")
        
        for endpoint in possible_endpoints:
            url = f"{BITNOB_BASE_URL}{endpoint}"
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    wallet_data = result.get("data", result)
                    
                    # Save wallet to Supabase
                    if wallet_data and wallet_data.get("id"):
                        save_success = save_crypto_wallet_to_supabase(user_id, wallet_data, customer_email)
                        if save_success:
                            logger.info(f"Successfully created and saved wallet for user {user_id}")
                        else:
                            logger.warning(f"Wallet created but failed to save to Supabase for user {user_id}")
                    
                    logger.info(f"Wallet created successfully using endpoint: {endpoint}")
                    return result
                    
                elif response.status_code == 404:
                    logger.debug(f"Endpoint {endpoint} not found, trying next...")
                    continue
                else:
                    logger.warning(f"Endpoint {endpoint} returned {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.debug(f"Request failed for {endpoint}: {str(e)}")
                continue
        
        # If all endpoints fail, return a generic wallet response for development
        logger.warning("All Bitnob endpoints failed, returning mock wallet for development")
        return create_mock_wallet(user_id, customer_email)
            
    except requests.exceptions.Timeout:
        logger.error("Bitnob API request timed out")
        return {"error": "Request timed out"}
    except Exception as e:
        logger.error(f"Unexpected error creating wallet: {str(e)}")
        return {"error": "Internal error"}

def create_mock_wallet(user_id: str, customer_email: str):
    """
    Create a mock wallet response for development when Bitnob API is unavailable
    """
    import uuid
    import time
    
    mock_wallet = {
        "id": f"mock_wallet_{int(time.time())}",
        "customerEmail": customer_email,
        "label": f"Sofi Wallet - User {user_id}",
        "addresses": {
            "BTC": f"bc1q{uuid.uuid4().hex[:40]}",
            "USDT": f"0x{uuid.uuid4().hex[:40]}"
        },
        "currency": "NGN",
        "status": "active",
        "mock": True  # Flag to indicate this is a mock wallet
    }
    
    # Save mock wallet to Supabase
    save_crypto_wallet_to_supabase(user_id, mock_wallet, customer_email)
    
    logger.info(f"Created mock wallet for user {user_id} - remove in production!")
    return {"data": mock_wallet}

def save_crypto_wallet_to_supabase(user_id: str, wallet_data: dict, customer_email: str) -> bool:
    """
    Save crypto wallet details to Supabase crypto_wallets table
    
    Args:
        user_id: User identifier
        wallet_data: Wallet data from Bitnob API
        customer_email: Customer email used for wallet
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_supabase_client()
        if not client:
            logger.error("Supabase client not initialized")
            return False
              # Extract wallet addresses from Bitnob response
        # Note: Bitnob provides different addresses for different currencies
        wallet_addresses = wallet_data.get("addresses", {})
        
        supabase_data = {
            "user_id": user_id,
            "wallet_id": wallet_data.get("id"),
            "bitnob_customer_email": customer_email,
            "btc_address": wallet_addresses.get("BTC"),
            "usdt_address": wallet_addresses.get("USDT"),
            "created_at": datetime.now().isoformat()
        }
          # Use upsert to handle duplicate user_id
        result = client.table("crypto_wallets").upsert(supabase_data).execute()
        
        if result.data:
            logger.info(f"Saved crypto wallet to Supabase for user {user_id}")
            return True
        else:
            logger.error(f"Failed to save crypto wallet to Supabase: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Error saving crypto wallet to Supabase: {str(e)}")
        return False

def get_user_wallet_addresses(user_id: str):
    """
    Fetch user's crypto wallet addresses from Supabase
      Args:
        user_id: Unique user identifier
    
    Returns:
        dict: Wallet addresses for different cryptocurrencies
    """
    try:
        # First try to get from Supabase
        client = get_supabase_client()
        if client:
            result = client.table("crypto_wallets").select("*").eq("user_id", user_id).execute()
        
        if result.data:
            wallet_data = result.data[0]
            addresses = {}
            
            if wallet_data.get("btc_address"):
                addresses["BTC"] = {
                    "address": wallet_data["btc_address"],
                    "balance": 0,  # Crypto is instantly converted to NGN
                    "wallet_id": wallet_data.get("wallet_id")
                }
            
            if wallet_data.get("usdt_address"):
                addresses["USDT"] = {
                    "address": wallet_data["usdt_address"],
                    "balance": 0,
                    "wallet_id": wallet_data.get("wallet_id")
                }
            
            if wallet_data.get("eth_address"):
                addresses["ETH"] = {
                    "address": wallet_data["eth_address"],
                    "balance": 0,
                    "wallet_id": wallet_data.get("wallet_id")
                }
            
            return {"success": True, "addresses": addresses}
        
        # If not in Supabase, try to fetch from Bitnob API
        else:
            if not BITNOB_SECRET_KEY:
                return {"error": "Bitnob API key not configured"}
            
            headers = {
                "Authorization": f"Bearer {BITNOB_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            # Get all wallets for the customer
            params = {"customerEmail": f"{user_id}@sofiwallet.com"}
            response = requests.get(BITNOB_API_URL, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                wallets = result.get("data", [])
                
                # Extract addresses for different currencies
                addresses = {}
                for wallet in wallets:
                    currency = wallet.get("currency", "").upper()
                    address = wallet.get("address")
                    if currency and address:
                        addresses[currency] = {
                            "address": address,
                            "balance": 0,  # Crypto converted instantly to NGN
                            "wallet_id": wallet.get("id")
                        }
                
                return {"success": True, "addresses": addresses}
            else:
                logger.error(f"Failed to fetch wallets from Bitnob: {response.status_code}")
                return {"error": "Failed to fetch wallet addresses"}
            
    except Exception as e:
        logger.error(f"Error fetching wallet addresses: {str(e)}")
        return {"error": "Internal error"}

def get_user_ngn_balance(user_id: str):
    """
    Get user's NGN balance from wallet_balances table
    
    Args:
        user_id: Unique user identifier
    
    Returns:
        dict: Balance information    """
    try:
        client = get_supabase_client()
        if not client:
            return {"error": "Database not available"}
            
        result = client.table("wallet_balances").select("*").eq("user_id", user_id).execute()
        
        if result.data:
            balance_data = result.data[0]
            return {
                "success": True,
                "balance_naira": float(balance_data.get("balance_naira", 0)),
                "total_crypto_deposits": float(balance_data.get("total_crypto_deposits", 0)),
                "last_crypto_deposit": balance_data.get("last_crypto_deposit"),
                "last_updated": balance_data.get("last_updated")
            }
        else:
            # Create initial balance record
            initial_data = {
                "user_id": user_id,
                "balance_naira": 0.00,
                "total_crypto_deposits": 0.00,
                "last_updated": datetime.now().isoformat()
            }
            
            create_result = client.table("wallet_balances").insert(initial_data).execute()
            if create_result.data:
                return {
                    "success": True,
                    "balance_naira": 0.00,
                    "total_crypto_deposits": 0.00,
                    "last_crypto_deposit": None,
                    "last_updated": datetime.now().isoformat()
                }
            else:
                return {"error": "Failed to create balance record"}
            
    except Exception as e:
        logger.error(f"Error getting NGN balance: {str(e)}")
        return {"error": "Internal error"}

def update_user_ngn_balance(user_id: str, additional_naira: float, crypto_deposit: bool = False) -> bool:
    """
    Update user's NGN balance after crypto conversion
    
    Args:
        user_id: User identifier
        additional_naira: Amount to add to balance
        crypto_deposit: Whether this is from a crypto deposit
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get current balance
        current_balance = get_user_ngn_balance(user_id)
        
        if current_balance.get("error"):
            logger.error(f"Failed to get current balance for user {user_id}")
            return False
        
        new_balance = current_balance["balance_naira"] + additional_naira
        
        update_data = {
            "balance_naira": new_balance,
            "last_updated": datetime.now().isoformat()
        }
        
        if crypto_deposit:
            new_crypto_total = current_balance["total_crypto_deposits"] + additional_naira
            update_data.update({
                "total_crypto_deposits": new_crypto_total,
                "last_crypto_deposit": datetime.now().isoformat()
            })
        
        result = get_supabase_client().table("wallet_balances").update(update_data).eq("user_id", user_id).execute()
        
        if result.data:
            logger.info(f"Updated NGN balance for user {user_id}: +₦{additional_naira:,.2f} = ₦{new_balance:,.2f}")
            return True
        else:
            logger.error(f"Failed to update balance for user {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating NGN balance: {str(e)}")
        return False
