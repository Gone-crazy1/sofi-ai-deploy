# crypto/rates.py

import requests
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Rate limiting and caching
_last_request_time = 0
_rate_cache = {}
_cache_duration = 300  # 5 minutes cache

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
    Fetch live conversion rate for cryptocurrency to Nigerian Naira with caching and rate limiting
    
    Args:
        crypto: Cryptocurrency symbol (BTC, ETH, USDT, etc.)
    
    Returns:
        float: Current rate in NGN, returns cached or fallback if error
    """
    global _last_request_time, _rate_cache
    
    try:
        crypto_upper = crypto.upper()
        crypto_id = CRYPTO_MAPPING.get(crypto_upper)
        
        if not crypto_id:
            logger.error(f"Unsupported cryptocurrency: {crypto}")
            return 0
        
        # Check cache first
        cache_key = f"{crypto_upper}_rate"
        now = time.time()
        
        if cache_key in _rate_cache:
            cached_data = _rate_cache[cache_key]
            if now - cached_data['timestamp'] < _cache_duration:
                logger.info(f"Using cached {crypto_upper} rate: ₦{cached_data['rate']:,.2f}")
                return cached_data['rate']
        
        # Rate limiting: minimum 2 seconds between requests
        if now - _last_request_time < 2:
            time.sleep(2 - (now - _last_request_time))
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=ngn"
        response = requests.get(url, timeout=10)
        _last_request_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            rate = data.get(crypto_id, {}).get('ngn', 0)
            
            # Cache the result
            _rate_cache[cache_key] = {
                'rate': float(rate),
                'timestamp': now
            }
            
            logger.info(f"Fetched {crypto_upper} rate: ₦{rate:,.2f}")
            return float(rate)
        elif response.status_code == 429:
            logger.warning(f"Rate limited by CoinGecko API. Using cached or fallback rate for {crypto_upper}")
            
            # Return cached rate if available
            if cache_key in _rate_cache:
                cached_rate = _rate_cache[cache_key]['rate']
                logger.info(f"Using cached {crypto_upper} rate due to rate limit: ₦{cached_rate:,.2f}")
                return cached_rate
            
            # Fallback rates if no cache available
            fallback_rates = {
                'BTC': 120000000.0,  # ~₦120M (approximate)
                'ETH': 8500000.0,    # ~₦8.5M
                'USDT': 1800.0,      # ~₦1,800
                'USDC': 1800.0       # ~₦1,800
            }
            fallback_rate = fallback_rates.get(crypto_upper, 0)
            if fallback_rate > 0:
                logger.info(f"Using fallback {crypto_upper} rate: ₦{fallback_rate:,.2f}")
                # Cache fallback rate temporarily
                _rate_cache[cache_key] = {
                    'rate': fallback_rate,
                    'timestamp': now
                }
            return fallback_rate
        else:
            logger.error(f"CoinGecko API error: {response.status_code}")
            
            # Return cached rate if available
            if cache_key in _rate_cache:
                cached_rate = _rate_cache[cache_key]['rate']
                logger.info(f"Using cached {crypto_upper} rate due to API error: ₦{cached_rate:,.2f}")
                return cached_rate
            return 0
            
    except requests.exceptions.Timeout:
        logger.error("CoinGecko API request timed out")
        return 0
    except Exception as e:
        logger.error(f"Error fetching crypto rate: {str(e)}")
        return 0

def get_multiple_crypto_rates(cryptos: list = None) -> Dict[str, float]:
    """
    Fetch rates for multiple cryptocurrencies at once with caching and rate limiting
    
    Args:
        cryptos: List of cryptocurrency symbols
    
    Returns:
        dict: Dictionary with crypto symbols as keys and NGN rates as values
    """
    global _last_request_time, _rate_cache
    
    if cryptos is None:
        cryptos = ["BTC", "ETH", "USDT", "USDC"]
    
    try:
        # Check if we have cached rates for all requested cryptos
        now = time.time()
        cached_rates = {}
        missing_cryptos = []
        
        for crypto in cryptos:
            crypto_upper = crypto.upper()
            cache_key = f"{crypto_upper}_rate"
            
            if cache_key in _rate_cache:
                cached_data = _rate_cache[cache_key]
                if now - cached_data['timestamp'] < _cache_duration:
                    cached_rates[crypto_upper] = cached_data['rate']
                else:
                    missing_cryptos.append(crypto_upper)
            else:
                missing_cryptos.append(crypto_upper)
        
        # If all rates are cached, return them
        if not missing_cryptos:
            logger.info(f"Using cached rates for all {len(cached_rates)} cryptocurrencies")
            return cached_rates
        
        # Map crypto symbols to CoinGecko IDs for missing rates
        crypto_ids = []
        symbol_to_id = {}
        
        for crypto in missing_cryptos:
            crypto_id = CRYPTO_MAPPING.get(crypto)
            if crypto_id:
                crypto_ids.append(crypto_id)
                symbol_to_id[crypto_id] = crypto
        
        if not crypto_ids:
            return cached_rates
        
        # Rate limiting: minimum 2 seconds between requests
        if now - _last_request_time < 2:
            time.sleep(2 - (now - _last_request_time))
        
        # Make single API call for missing cryptocurrencies
        ids_string = ",".join(crypto_ids)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=ngn"
        response = requests.get(url, timeout=15)
        _last_request_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            new_rates = {}
            
            for crypto_id, price_data in data.items():
                symbol = symbol_to_id.get(crypto_id)
                ngn_rate = price_data.get('ngn', 0)
                if symbol and ngn_rate:
                    new_rates[symbol] = float(ngn_rate)
                    
                    # Cache the new rate
                    cache_key = f"{symbol}_rate"
                    _rate_cache[cache_key] = {
                        'rate': float(ngn_rate),
                        'timestamp': now
                    }
            
            # Combine cached and new rates
            all_rates = {**cached_rates, **new_rates}
            logger.info(f"Fetched rates for {len(new_rates)} new cryptocurrencies, {len(cached_rates)} from cache")
            return all_rates
            
        elif response.status_code == 429:
            logger.warning("Rate limited by CoinGecko API. Using cached and fallback rates")
            
            # Use cached rates plus fallback for missing ones
            fallback_rates = {
                'BTC': 120000000.0,
                'ETH': 8500000.0,
                'USDT': 1800.0,
                'USDC': 1800.0
            }
            
            for crypto in missing_cryptos:
                if crypto not in cached_rates and crypto in fallback_rates:
                    cached_rates[crypto] = fallback_rates[crypto]
                    
                    # Cache fallback rate temporarily
                    cache_key = f"{crypto}_rate"
                    _rate_cache[cache_key] = {
                        'rate': fallback_rates[crypto],
                        'timestamp': now
                    }
            
            return cached_rates
        else:
            logger.error(f"CoinGecko API error: {response.status_code}")
            return cached_rates
            
    except Exception as e:
        logger.error(f"Error fetching multiple crypto rates: {str(e)}")
        return cached_rates if 'cached_rates' in locals() else {}

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
