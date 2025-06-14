#!/usr/bin/env python3
"""
🚀 SOFI AI CRYPTO RATE MANAGEMENT SYSTEM
========================================

This system handles:
1. Fetching real-time rates from CoinGecko
2. Applying your custom profit margins
3. Displaying your rates to users (not market rates)
4. Processing crypto deposits with profit tracking
5. Recording all transactions in Supabase

PROFIT STRATEGY:
- Fetch CoinGecko rate: ₦1,550 per USDT
- Apply your margin: 3% (configurable)
- Your rate to users: ₦1,503.5 per USDT
- User deposits 100 USDT → Gets ₦150,350
- Your profit: (₦1,550 - ₦1,503.5) × 100 = ₦4,650
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
# CRYPTO RATE CONFIGURATION
# ==========================================

class CryptoRateConfig:
    """Configuration for crypto rates and margins - Customer-friendly settings"""
    
    # Your profit margins (balanced for customer retention)
    MARGINS = {
        'USDT': 0.025,  # 2.5% margin on USDT (competitive)
        'BTC': 0.035,   # 3.5% margin on BTC (reasonable)
    }
    
    # Minimum profit per transaction (in Naira) - Realistic targets
    MIN_PROFIT = {
        'USDT': 250,   # Minimum ₦250 profit on USDT (₦25 per 100 USDT)
        'BTC': 500000, # Minimum ₦500K profit on BTC (₦5K per 0.01 BTC)
    }
    
    # Rate cache duration (in minutes)
    CACHE_DURATION = 5  # Refresh rates every 5 minutes
    
    # CoinGecko API endpoints
    COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"
    
    # Supported cryptocurrencies
    SUPPORTED_CRYPTOS = ['bitcoin', 'tether']  # BTC, USDT

# ==========================================
# RATE FETCHING AND MANAGEMENT
# ==========================================

class CryptoRateManager:
    """Manages crypto rates, margins, and profit calculations"""
    
    def __init__(self):
        self.rate_cache = {}
        self.cache_timestamp = {}
    
    async def fetch_real_time_rates(self) -> Dict:
        """Fetch current market rates from CoinGecko"""
        try:
            # CoinGecko API call
            params = {
                'ids': ','.join(CryptoRateConfig.SUPPORTED_CRYPTOS),
                'vs_currencies': 'ngn'  # Nigerian Naira
            }
            
            response = requests.get(CryptoRateConfig.COINGECKO_API, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to our format
            rates = {
                'BTC': data.get('bitcoin', {}).get('ngn', 0),
                'USDT': data.get('tether', {}).get('ngn', 0),
                'timestamp': datetime.now().isoformat(),
                'source': 'coingecko'
            }
            
            print(f"✅ Real-time rates fetched: BTC=₦{rates['BTC']:,.2f}, USDT=₦{rates['USDT']:,.2f}")
            return rates
            
        except Exception as e:
            print(f"❌ Error fetching rates from CoinGecko: {e}")
            # Fallback to cached rates or default rates
            return self._get_fallback_rates()
    
    def _get_fallback_rates(self) -> Dict:
        """Fallback rates if CoinGecko is unavailable"""
        return {
            'BTC': 50000000,  # ₦50M (conservative estimate)
            'USDT': 1550,     # ₦1,550 (typical rate)
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def calculate_your_rates(self, market_rates: Dict) -> Dict:
        """Calculate your rates by applying profit margins to market rates"""
        your_rates = {}
        
        for crypto in ['BTC', 'USDT']:
            market_rate = market_rates.get(crypto, 0)
            margin = CryptoRateConfig.MARGINS.get(crypto, 0.03)
            
            # Apply margin (reduce market rate by margin percentage)
            your_rate = market_rate * (1 - margin)
            
            # Ensure minimum profit
            min_profit = CryptoRateConfig.MIN_PROFIT.get(crypto, 500)
            if (market_rate - your_rate) < min_profit:
                your_rate = market_rate - min_profit
            
            your_rates[crypto] = {
                'market_rate': market_rate,
                'your_rate': round(your_rate, 2),
                'margin_percentage': margin * 100,
                'profit_per_unit': round(market_rate - your_rate, 2)
            }
        
        your_rates['timestamp'] = datetime.now().isoformat()
        return your_rates
    
    async def get_current_rates(self, force_refresh: bool = False) -> Dict:
        """Get current rates (cached or fresh)"""
        now = datetime.now()
        
        # Check if we need to refresh cache
        if force_refresh or not self.rate_cache or self._cache_expired():
            print("🔄 Refreshing crypto rates...")
            market_rates = await self.fetch_real_time_rates()
            your_rates = self.calculate_your_rates(market_rates)
            
            # Update cache
            self.rate_cache = {
                'market_rates': market_rates,
                'your_rates': your_rates,
                'cached_at': now.isoformat()
            }
            
            # Save to database for record keeping
            await self._save_rates_to_db(self.rate_cache)
            
        return self.rate_cache
    
    def _cache_expired(self) -> bool:
        """Check if rate cache has expired"""
        if not self.rate_cache:
            return True
        
        cached_time = datetime.fromisoformat(self.rate_cache.get('cached_at', '2000-01-01'))
        return (datetime.now() - cached_time).total_seconds() > (CryptoRateConfig.CACHE_DURATION * 60)
    
    async def _save_rates_to_db(self, rates_data: Dict):
        """Save rate data to Supabase for historical tracking"""
        try:
            rate_record = {
                'btc_market_rate': rates_data['market_rates']['BTC'],
                'btc_sofi_rate': rates_data['your_rates']['BTC']['your_rate'],
                'usdt_market_rate': rates_data['market_rates']['USDT'],
                'usdt_sofi_rate': rates_data['your_rates']['USDT']['your_rate'],
                'source': rates_data['market_rates']['source'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to crypto_rates table (we'll create this)
            result = supabase.table("crypto_rates").insert(rate_record).execute()
            if result.data:
                print("📊 Rates saved to database")
                
        except Exception as e:
            print(f"⚠️ Error saving rates to database: {e}")

# ==========================================
# CRYPTO DEPOSIT PROCESSING
# ==========================================

class CryptoDepositProcessor:
    """Processes crypto deposits and calculates profits"""
    
    def __init__(self):
        self.rate_manager = CryptoRateManager()
    
    async def process_crypto_deposit(self, user_id: str, crypto_type: str, crypto_amount: float, 
                                   transaction_hash: str = None) -> Dict:
        """
        Process a crypto deposit and credit user's account
        
        Args:
            user_id: User's telegram chat ID
            crypto_type: 'BTC' or 'USDT'
            crypto_amount: Amount of crypto received
            transaction_hash: Blockchain transaction hash
            
        Returns:
            Dict with transaction details and profit information
        """
        try:
            # Get current rates
            rates_data = await self.rate_manager.get_current_rates()
            your_rates = rates_data['your_rates']
            market_rates = rates_data['market_rates']
            
            if crypto_type not in your_rates:
                raise ValueError(f"Unsupported crypto type: {crypto_type}")
            
            # Calculate amounts
            rate_info = your_rates[crypto_type]
            market_rate = rate_info['market_rate']
            your_rate = rate_info['your_rate']
            
            # Amount to credit user (at YOUR rate)
            naira_to_credit = crypto_amount * your_rate
            
            # Your profit (market rate - your rate) × amount
            total_profit = crypto_amount * rate_info['profit_per_unit']
            
            # Create transaction record
            transaction_data = {
                'user_id': str(user_id),
                'crypto_type': crypto_type,
                'crypto_amount': crypto_amount,
                'market_rate': market_rate,
                'your_rate': your_rate,
                'naira_credited': naira_to_credit,
                'profit_made': total_profit,
                'transaction_hash': transaction_hash,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Credit user's virtual account
            await self._credit_user_account(user_id, naira_to_credit, transaction_data)
            
            # Save to crypto_trades table for revenue tracking
            await self._save_crypto_trade(transaction_data)
            
            # Update financial summary
            await self._update_financial_summary(total_profit)
            
            print(f"✅ Crypto deposit processed: {crypto_amount} {crypto_type} = ₦{naira_to_credit:,.2f} (Profit: ₦{total_profit:,.2f})")
            
            return {
                'success': True,
                'naira_credited': naira_to_credit,
                'profit_made': total_profit,
                'rate_used': your_rate,
                'market_rate': market_rate,
                'transaction_data': transaction_data
            }
            
        except Exception as e:
            print(f"❌ Error processing crypto deposit: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _credit_user_account(self, user_id: str, amount: float, transaction_data: Dict):
        """Credit user's virtual account balance"""
        try:
            # Update user balance
            from webhooks.monnify_webhook import update_user_balance
            update_user_balance(user_id, amount)
            
            # Save transaction record
            from webhooks.monnify_webhook import save_bank_transaction
            save_bank_transaction(
                user_id=user_id,
                transaction_reference=f"CRYPTO_{transaction_data.get('transaction_hash', 'UNKNOWN')}",
                amount=amount,
                account_number="CRYPTO_DEPOSIT",
                status="success",
                webhook_data=transaction_data
            )
            
            print(f"💰 User {user_id} credited with ₦{amount:,.2f}")
            
        except Exception as e:
            print(f"❌ Error crediting user account: {e}")
            raise
    
    async def _save_crypto_trade(self, transaction_data: Dict):
        """Save crypto trade to revenue tracking table"""
        try:
            from fee_collection import save_crypto_trade
            
            save_crypto_trade(
                user_id=transaction_data['user_id'],
                crypto_type=transaction_data['crypto_type'],
                crypto_amount=transaction_data['crypto_amount'],
                naira_equivalent=transaction_data['naira_credited'],
                conversion_rate=transaction_data['your_rate']
            )
            
        except Exception as e:
            print(f"⚠️ Error saving crypto trade: {e}")
    
    async def _update_financial_summary(self, profit: float):
        """Update financial summary with new profit"""
        try:
            from fee_collection import update_financial_summary
            update_financial_summary()
            
        except Exception as e:
            print(f"⚠️ Error updating financial summary: {e}")

# ==========================================
# USER INTERFACE FUNCTIONS
# ==========================================

class CryptoUserInterface:
    """User-facing functions for crypto operations"""
    
    def __init__(self):
        self.rate_manager = CryptoRateManager()
        self.deposit_processor = CryptoDepositProcessor()
    
    async def get_crypto_rates_for_user(self) -> str:
        """Get formatted crypto rates to show users (YOUR rates, not market rates)"""
        try:
            rates_data = await self.rate_manager.get_current_rates()
            your_rates = rates_data['your_rates']
            
            rate_message = "💱 **Current Crypto Rates** (Sofi AI Exchange)\n\n"
            
            for crypto in ['BTC', 'USDT']:
                if crypto in your_rates:
                    rate_info = your_rates[crypto]
                    rate = rate_info['your_rate']
                    
                    if crypto == 'BTC':
                        rate_message += f"🟠 **Bitcoin (BTC)**\n"
                        rate_message += f"   1 BTC = ₦{rate:,.2f}\n\n"
                    else:
                        rate_message += f"🟢 **Tether (USDT)**\n" 
                        rate_message += f"   1 USDT = ₦{rate:,.2f}\n\n"
            
            rate_message += "📝 *Rates updated every 5 minutes*\n"
            rate_message += "💰 *Send crypto to your wallet addresses above*"
            
            return rate_message
            
        except Exception as e:
            return f"❌ Error fetching rates: {e}"
    
    async def process_user_crypto_deposit(self, user_id: str, crypto_type: str, 
                                        crypto_amount: float, transaction_hash: str = None) -> str:
        """Process crypto deposit and return user-friendly message"""
        try:
            result = await self.deposit_processor.process_crypto_deposit(
                user_id, crypto_type, crypto_amount, transaction_hash
            )
            
            if result['success']:
                naira_amount = result['naira_credited']
                rate_used = result['rate_used']
                
                message = f"✅ **Crypto Deposit Confirmed!**\n\n"
                message += f"💰 **Received:** {crypto_amount} {crypto_type}\n"
                message += f"💱 **Rate Used:** 1 {crypto_type} = ₦{rate_used:,.2f}\n"
                message += f"🏦 **Credited:** ₦{naira_amount:,.2f}\n\n"
                message += f"📊 **Your new balance will be updated shortly**\n"
                message += f"🎯 **You can now use this balance for transfers, airtime, and bills!**"
                
                return message
            else:
                return f"❌ **Deposit Failed:** {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ **Error processing deposit:** {e}"

# ==========================================
# INTEGRATION WITH MAIN BOT
# ==========================================

# Global instances
crypto_ui = CryptoUserInterface()
rate_manager = CryptoRateManager()

async def get_crypto_rates_message() -> str:
    """Function to call from main.py for crypto rates"""
    return await crypto_ui.get_crypto_rates_for_user()

async def handle_crypto_deposit(user_id: str, crypto_type: str, amount: float, tx_hash: str = None) -> str:
    """Function to call from webhooks when crypto is received"""
    return await crypto_ui.process_user_crypto_deposit(user_id, crypto_type, amount, tx_hash)

async def test_rate_system():
    """Test the complete rate system"""
    print("🧪 TESTING CRYPTO RATE SYSTEM")
    print("=" * 50)
    
    # Test 1: Fetch rates
    print("1️⃣ Testing rate fetching...")
    rates = await rate_manager.get_current_rates(force_refresh=True)
    
    if rates:
        print("✅ Rates fetched successfully")
        for crypto in ['BTC', 'USDT']:
            if crypto in rates['your_rates']:
                rate_info = rates['your_rates'][crypto]
                print(f"   {crypto}: Market=₦{rate_info['market_rate']:,.2f}, Your=₦{rate_info['your_rate']:,.2f}, Profit=₦{rate_info['profit_per_unit']:,.2f}")
    
    # Test 2: Generate user message
    print("\n2️⃣ Testing user rate display...")
    rate_message = await crypto_ui.get_crypto_rates_for_user()
    print("✅ User rate message generated")
    print(rate_message[:200] + "..." if len(rate_message) > 200 else rate_message)
    
    # Test 3: Simulate deposit
    print("\n3️⃣ Testing deposit simulation...")
    deposit_result = await crypto_ui.process_user_crypto_deposit("test_user", "USDT", 100, "test_hash")
    print("✅ Deposit simulation completed")
    print(deposit_result[:200] + "..." if len(deposit_result) > 200 else deposit_result)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_rate_system())
