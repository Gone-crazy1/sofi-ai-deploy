# crypto/rates.py

import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Cryptocurrency mapping for CoinGecko API
CRYPTO_MAPPING = {
    "BTC": "bitcoin",
    "ETH": "ethereum", 
    "USDT": "tether",
    "USDC": "usd-coin",
    "LTC": "litecoin",
    "ADA": "cardano",
    "DOT": "polkadot",
    "LINK": "chainlink"
}

def get_crypto_to_ngn_rate(crypto: str = "BTC") -> float:
    """
    Fetch live conversion rate for cryptocurrency to Nigerian Naira
    
    Args:
        crypto: Cryptocurrency symbol (BTC, ETH, USDT, etc.)
    
    Returns:
        float: Current rate in NGN, returns 0 if error
    """
    try:
        crypto_upper = crypto.upper()
        crypto_id = CRYPTO_MAPPING.get(crypto_upper)
        
        if not crypto_id:
            logger.error(f"Unsupported cryptocurrency: {crypto}")
            return 0
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=ngn"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rate = data.get(crypto_id, {}).get('ngn', 0)
            logger.info(f"Fetched {crypto_upper} rate: ₦{rate:,.2f}")
            return float(rate)
        else:
            logger.error(f"CoinGecko API error: {response.status_code}")
            return 0
            
    except requests.exceptions.Timeout:
        logger.error("CoinGecko API request timed out")
        return 0
    except Exception as e:
        logger.error(f"Error fetching crypto rate: {str(e)}")
        return 0

def get_multiple_crypto_rates(cryptos: list = None) -> Dict[str, float]:
    """
    Fetch rates for multiple cryptocurrencies at once
    
    Args:
        cryptos: List of cryptocurrency symbols
    
    Returns:
        dict: Dictionary with crypto symbols as keys and NGN rates as values
    """
    if cryptos is None:
        cryptos = ["BTC", "ETH", "USDT", "USDC"]
    
    try:
        # Map crypto symbols to CoinGecko IDs
        crypto_ids = []
        symbol_to_id = {}
        
        for crypto in cryptos:
            crypto_upper = crypto.upper()
            crypto_id = CRYPTO_MAPPING.get(crypto_upper)
            if crypto_id:
                crypto_ids.append(crypto_id)
                symbol_to_id[crypto_id] = crypto_upper
        
        if not crypto_ids:
            return {}
        
        # Make single API call for all cryptocurrencies
        ids_string = ",".join(crypto_ids)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=ngn"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            rates = {}
            
            for crypto_id, price_data in data.items():
                symbol = symbol_to_id.get(crypto_id)
                ngn_rate = price_data.get('ngn', 0)
                if symbol and ngn_rate:
                    rates[symbol] = float(ngn_rate)
            
            logger.info(f"Fetched rates for {len(rates)} cryptocurrencies")
            return rates
        else:
            logger.error(f"CoinGecko API error: {response.status_code}")
            return {}
            
    except Exception as e:
        logger.error(f"Error fetching multiple crypto rates: {str(e)}")
        return {}

def calculate_ngn_equivalent(crypto_amount: float, crypto_symbol: str) -> Optional[float]:
    """
    Calculate NGN equivalent for a given cryptocurrency amount
    
    Args:
        crypto_amount: Amount of cryptocurrency
        crypto_symbol: Cryptocurrency symbol (BTC, ETH, etc.)
    
    Returns:
        float: NGN equivalent or None if error
    """
    try:
        rate = get_crypto_to_ngn_rate(crypto_symbol)
        if rate > 0:
            ngn_amount = crypto_amount * rate
            logger.info(f"{crypto_amount} {crypto_symbol} = ₦{ngn_amount:,.2f}")
            return ngn_amount
        return None
    except Exception as e:
        logger.error(f"Error calculating NGN equivalent: {str(e)}")
        return None

def format_crypto_rates_message(rates: Dict[str, float]) -> str:
    """
    Format cryptocurrency rates into a user-friendly message
    
    Args:
        rates: Dictionary of crypto rates
    
    Returns:
        str: Formatted message with current rates
    """
    if not rates:
        return "❌ Unable to fetch current crypto rates. Please try again later."
    
    message_lines = ["💹 **Current Crypto Rates (NGN)**\n"]
    
    for crypto, rate in rates.items():
        if rate > 0:
            # Format large numbers with commas
            formatted_rate = f"₦{rate:,.2f}"
            message_lines.append(f"🪙 **{crypto}**: {formatted_rate}")
    
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_lines.append(f"\n📊 Rates updated: {current_time}")
    message_lines.append("💡 *Rates are live and may fluctuate*")
    
    return "\n".join(message_lines)
