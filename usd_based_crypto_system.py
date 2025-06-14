#!/usr/bin/env python3
"""
🚀 FIXED CRYPTO RATE SYSTEM - USD-BASED CONVERSION
=================================================

This system now works like real exchanges:
1. Convert any crypto to USD value first
2. Apply your USD/NGN rate 
3. Credit user with consistent Naira amount

USER EXPECTATION: $100 worth of ANY crypto = ₦150,000 (at ₦1,500/$1 rate)
"""

import os
import requests
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# USD-BASED CRYPTO CONFIGURATION
# ==========================================

class USDCryptoConfig:
    """USD-based crypto configuration - Like real exchanges"""
    
    # Your USD/NGN rate (this is what matters!)
    USD_TO_NGN = {
        'market_rate': 1543,    # Current USD/NGN market rate
        'your_rate': 1500,      # Your competitive rate (₦1,500 per $1)
        'profit_per_usd': 43    # ₦43 profit per $1 (2.8% margin)
    }
    
    # Minimum transaction limits
    MIN_DEPOSIT = {
        'usd_value': 10,        # Minimum $10 deposit
        'naira_value': 15000    # Minimum ₦15,000 deposit
    }
    
    # Rate cache duration
    CACHE_DURATION = 5  # Refresh every 5 minutes
    
    # Supported cryptocurrencies (we get their USD prices)
    SUPPORTED_CRYPTOS = {
        'BTC': 'bitcoin',
        'USDT': 'tether',
        'ETH': 'ethereum'
    }
    
    # CoinGecko API endpoints
    COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

# ==========================================
# USD-BASED RATE MANAGER
# ==========================================

class USDBasedCryptoManager:
    """Manages crypto rates based on USD value - Like real exchanges"""
    
    def __init__(self):
        self.crypto_usd_prices = {}
        self.last_update = None
    
    async def fetch_crypto_usd_prices(self) -> Dict:
        """Fetch current crypto prices in USD from CoinGecko"""
        try:
            # Get crypto prices in USD
            params = {
                'ids': ','.join(USDCryptoConfig.SUPPORTED_CRYPTOS.values()),
                'vs_currencies': 'usd'
            }
            
            response = requests.get(USDCryptoConfig.COINGECKO_API, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to our format
            prices = {
                'BTC': data.get('bitcoin', {}).get('usd', 65000),      # Default $65k
                'USDT': data.get('tether', {}).get('usd', 1.0),        # Default $1
                'ETH': data.get('ethereum', {}).get('usd', 3000),      # Default $3k
                'timestamp': datetime.now().isoformat(),
                'source': 'coingecko'
            }
            
            print(f"✅ Crypto USD prices: BTC=${prices['BTC']:,.2f}, USDT=${prices['USDT']:.3f}, ETH=${prices['ETH']:,.2f}")
            return prices
            
        except Exception as e:
            print(f"❌ Error fetching crypto USD prices: {e}")
            return self._get_fallback_usd_prices()
    
    def _get_fallback_usd_prices(self) -> Dict:
        """Fallback crypto USD prices"""
        return {
            'BTC': 65000,   # $65k
            'USDT': 1.0,    # $1
            'ETH': 3000,    # $3k
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def calculate_usd_value(self, crypto_type: str, crypto_amount: float) -> float:
        """Calculate USD value of crypto amount"""
        if crypto_type not in self.crypto_usd_prices:
            return 0
        
        crypto_usd_price = self.crypto_usd_prices[crypto_type]
        usd_value = crypto_amount * crypto_usd_price
        
        print(f"💰 {crypto_amount} {crypto_type} = ${usd_value:,.2f} USD")
        return usd_value
    
    def calculate_naira_amount(self, usd_value: float) -> Dict:
        """Calculate Naira amount to credit user"""
        your_rate = USDCryptoConfig.USD_TO_NGN['your_rate']
        market_rate = USDCryptoConfig.USD_TO_NGN['market_rate']
        
        naira_to_credit = usd_value * your_rate
        profit = usd_value * USDCryptoConfig.USD_TO_NGN['profit_per_usd']
        
        return {
            'naira_amount': naira_to_credit,
            'profit': profit,
            'usd_value': usd_value,
            'rate_used': your_rate,
            'market_rate': market_rate
        }
    
    async def get_current_crypto_prices(self, force_refresh: bool = False) -> Dict:
        """Get current crypto USD prices (cached or fresh)"""
        now = datetime.now()
        
        # Check if we need to refresh
        if (force_refresh or not self.crypto_usd_prices or 
            not self.last_update or 
            (now - self.last_update).total_seconds() > (USDCryptoConfig.CACHE_DURATION * 60)):
            
            print("🔄 Refreshing crypto USD prices...")
            prices = await self.fetch_crypto_usd_prices()
            self.crypto_usd_prices = prices
            self.last_update = now
            
            # Save to database
            await self._save_prices_to_db(prices)
        
        return self.crypto_usd_prices
    
    async def _save_prices_to_db(self, prices: Dict):
        """Save crypto prices to database"""
        try:
            # Calculate Naira rates for display
            btc_naira = prices['BTC'] * USDCryptoConfig.USD_TO_NGN['your_rate']
            usdt_naira = prices['USDT'] * USDCryptoConfig.USD_TO_NGN['your_rate']
            
            rate_record = {
                'btc_market_rate': prices['BTC'] * USDCryptoConfig.USD_TO_NGN['market_rate'],
                'btc_sofi_rate': btc_naira,
                'usdt_market_rate': prices['USDT'] * USDCryptoConfig.USD_TO_NGN['market_rate'],
                'usdt_sofi_rate': usdt_naira,
                'source': prices['source'],
                'timestamp': datetime.now().isoformat()
            }
            
            result = supabase.table("crypto_rates").insert(rate_record).execute()
            if result.data:
                print("📊 USD-based rates saved to database")
                
        except Exception as e:
            print(f"⚠️ Error saving rates: {e}")

# ==========================================
# USD-BASED DEPOSIT PROCESSOR
# ==========================================

class USDBasedDepositProcessor:
    """Process crypto deposits using USD value conversion"""
    
    def __init__(self):
        self.rate_manager = USDBasedCryptoManager()
    
    async def process_crypto_deposit(self, user_id: str, crypto_type: str, crypto_amount: float, 
                                   transaction_hash: str = None) -> Dict:
        """
        Process crypto deposit using USD value conversion
        
        Example:
        - User deposits 0.00154 BTC (worth $100)
        - System calculates: $100 × ₦1,500 = ₦150,000
        - User gets ₦150,000 regardless of BTC amount
        """
        try:
            # Get current crypto USD prices
            await self.rate_manager.get_current_crypto_prices()
            
            if crypto_type not in USDCryptoConfig.SUPPORTED_CRYPTOS:
                raise ValueError(f"Unsupported crypto: {crypto_type}")
            
            # Step 1: Calculate USD value of crypto
            usd_value = self.rate_manager.calculate_usd_value(crypto_type, crypto_amount)
            
            if usd_value < USDCryptoConfig.MIN_DEPOSIT['usd_value']:
                raise ValueError(f"Minimum deposit: ${USDCryptoConfig.MIN_DEPOSIT['usd_value']}")
            
            # Step 2: Calculate Naira amount
            calculation = self.rate_manager.calculate_naira_amount(usd_value)
            
            # Step 3: Create transaction record
            transaction_data = {
                'user_id': str(user_id),
                'crypto_type': crypto_type,
                'crypto_amount': crypto_amount,
                'usd_value': usd_value,
                'naira_credited': calculation['naira_amount'],
                'profit_made': calculation['profit'],
                'rate_used': calculation['rate_used'],
                'transaction_hash': transaction_hash,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Step 4: Credit user account
            await self._credit_user_account(user_id, calculation['naira_amount'], transaction_data)
            
            # Step 5: Save transaction for revenue tracking
            await self._save_crypto_trade(transaction_data)
            
            print(f"✅ Deposit processed: {crypto_amount} {crypto_type} (${usd_value:.2f}) = ₦{calculation['naira_amount']:,.2f}")
            
            return {
                'success': True,
                'usd_value': usd_value,
                'naira_credited': calculation['naira_amount'],
                'profit_made': calculation['profit'],
                'rate_used': calculation['rate_used'],
                'transaction_data': transaction_data
            }
            
        except Exception as e:
            print(f"❌ Error processing deposit: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _credit_user_account(self, user_id: str, amount: float, transaction_data: Dict):
        """Credit user's virtual account"""
        try:
            from webhooks.monnify_webhook import update_user_balance, save_bank_transaction
            
            # Update balance
            update_user_balance(user_id, amount)
            
            # Save transaction
            save_bank_transaction(
                user_id=user_id,
                transaction_reference=f"CRYPTO_{transaction_data.get('transaction_hash', 'UNKNOWN')}",
                amount=amount,
                account_number="CRYPTO_DEPOSIT",
                status="success",
                webhook_data=transaction_data
            )
            
            print(f"💰 User {user_id} credited ₦{amount:,.2f}")
            
        except Exception as e:
            print(f"❌ Error crediting account: {e}")
            raise
    
    async def _save_crypto_trade(self, transaction_data: Dict):
        """Save crypto trade to database"""
        try:
            from fee_collection import save_crypto_trade
            
            save_crypto_trade(
                user_id=transaction_data['user_id'],
                crypto_type=transaction_data['crypto_type'],
                crypto_amount=transaction_data['crypto_amount'],
                naira_equivalent=transaction_data['naira_credited'],
                conversion_rate=transaction_data['rate_used']
            )
            
        except Exception as e:
            print(f"⚠️ Error saving trade: {e}")

# ==========================================
# USER INTERFACE
# ==========================================

class USDBasedCryptoUI:
    """User interface for USD-based crypto system"""
    
    def __init__(self):
        self.rate_manager = USDBasedCryptoManager()
        self.deposit_processor = USDBasedDepositProcessor()
    
    async def get_crypto_rates_for_user(self) -> str:
        """Get user-friendly crypto rates display"""
        try:
            await self.rate_manager.get_current_crypto_prices()
            
            usd_rate = USDCryptoConfig.USD_TO_NGN['your_rate']
            
            rate_message = "💱 **Current Exchange Rates** (Sofi AI)\n\n"
            rate_message += f"🇺🇸 **US Dollar Rate**\n"
            rate_message += f"   $1 USD = ₦{usd_rate:,.2f}\n\n"
            
            rate_message += "💰 **Crypto Conversion Examples:**\n"
            
            # Example calculations
            examples = [
                ("$50", 50),
                ("$100", 100),
                ("$500", 500)
            ]
            
            for label, usd_amount in examples:
                naira_amount = usd_amount * usd_rate
                rate_message += f"   {label} worth of crypto = ₦{naira_amount:,.0f}\n"
            
            rate_message += f"\n📝 *Rates updated every 5 minutes*\n"
            rate_message += f"💎 *All cryptos converted at same USD rate*\n"
            rate_message += f"🎯 *Send any supported crypto to your wallet*"
            
            return rate_message
            
        except Exception as e:
            return f"❌ Error fetching rates: {e}"
    
    async def process_user_deposit(self, user_id: str, crypto_type: str, 
                                 crypto_amount: float, tx_hash: str = None) -> str:
        """Process user deposit and return message"""
        try:
            result = await self.deposit_processor.process_crypto_deposit(
                user_id, crypto_type, crypto_amount, tx_hash
            )
            
            if result['success']:
                usd_value = result['usd_value']
                naira_amount = result['naira_credited']
                rate_used = result['rate_used']
                
                message = f"✅ **Crypto Deposit Confirmed!**\n\n"
                message += f"💰 **Received:** {crypto_amount} {crypto_type}\n"
                message += f"💵 **USD Value:** ${usd_value:,.2f}\n"
                message += f"💱 **Rate Used:** $1 = ₦{rate_used:,.2f}\n"
                message += f"🏦 **Credited:** ₦{naira_amount:,.2f}\n\n"
                message += f"🎯 **Consistent rate regardless of crypto type!**"
                
                return message
            else:
                return f"❌ **Deposit Failed:** {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ **Processing Error:** {e}"

# ==========================================
# GLOBAL INSTANCES & INTEGRATION
# ==========================================

# Global instances for main.py integration
usd_crypto_ui = USDBasedCryptoUI()
usd_rate_manager = USDBasedCryptoManager()

async def get_crypto_rates_message() -> str:
    """Function for main.py - Get crypto rates"""
    return await usd_crypto_ui.get_crypto_rates_for_user()

async def handle_crypto_deposit(user_id: str, crypto_type: str, amount: float, tx_hash: str = None) -> str:
    """Function for main.py - Handle crypto deposit"""
    return await usd_crypto_ui.process_user_deposit(user_id, crypto_type, amount, tx_hash)

# ==========================================
# TESTING & EXAMPLES
# ==========================================

async def test_usd_based_system():
    """Test the USD-based crypto system"""
    print("🧪 TESTING USD-BASED CRYPTO SYSTEM")
    print("=" * 50)
    
    # Test 1: Get current prices
    print("1️⃣ Testing crypto USD price fetching...")
    await usd_rate_manager.get_current_crypto_prices(force_refresh=True)
    
    # Test 2: Test deposit scenarios
    print("\n2️⃣ Testing deposit scenarios...")
    
    test_deposits = [
        ("BTC", 0.00154, "$100 worth of BTC"),
        ("USDT", 100, "$100 worth of USDT"),
        ("ETH", 0.033, "$100 worth of ETH")
    ]
    
    for crypto_type, amount, description in test_deposits:
        print(f"\n   Testing: {description}")
        result = await usd_crypto_ui.process_user_deposit("test_user", crypto_type, amount)
        print(f"   Result: {result[:100]}...")
    
    # Test 3: User rate display
    print("\n3️⃣ Testing user rate display...")
    rates_message = await usd_crypto_ui.get_crypto_rates_for_user()
    print(f"   Rates message: {rates_message[:200]}...")
    
    print("\n🎉 USD-based system testing complete!")
    
    # Show profit calculations
    print("\n💰 PROFIT EXAMPLES:")
    usd_rate = USDCryptoConfig.USD_TO_NGN['your_rate']
    profit_per_usd = USDCryptoConfig.USD_TO_NGN['profit_per_usd']
    
    examples = [50, 100, 500, 1000]
    for usd_amount in examples:
        profit = usd_amount * profit_per_usd
        naira_credited = usd_amount * usd_rate
        print(f"   ${usd_amount} deposit: User gets ₦{naira_credited:,.0f}, You profit ₦{profit:,.0f}")

if __name__ == "__main__":
    asyncio.run(test_usd_based_system())
