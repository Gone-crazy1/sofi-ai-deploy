"""
Sofi AI Wallet Fees & Profit Management System

COMPREHENSIVE FEE STRUCTURE (All Admin-Editable via Supabase):

1. DEPOSIT FEES (OPay Virtual Account):
   - Sofi Deposit Fee: ₦50 (charged to user, pure profit)
   - OPay Processing Fee: ₦10 (hidden, paid by Sofi)
   - User sees: "Deposit fee: ₦50"
   - Sofi Profit: ₦40 per deposit

2. TRANSFER FEES (Bank Transfers via OPay):
   - Sofi Transfer Fee: ₦10 (charged to user)
   - OPay Transfer Fee: ₦20 (processing cost)
   - Total charged: ₦30
   - User sees: "Transfer fee: ₦30 (Service: ₦10 + Processing: ₦20)"
   - Sofi Profit: ₦10 per transfer

3. CRYPTO RATES & MARGINS:
   - Buy Rate: $1 = ₦1,550 (Sofi buys from user)
   - Sell Rate: $1 = ₦1,600 (Sofi sells to user)
   - Profit Margin: ₦50 per USD
   - Deposit Fee: $1 per crypto deposit
   
4. AIRTIME/DATA COMMISSIONS:
   - Airtime: 3% commission on all purchases
   - Data: 5% commission on all purchases

All fees automatically calculated, logged as profits, and fully customizable by admin.
"""

import os
import logging
from datetime import datetime, date
from typing import Dict, Optional, Tuple, Any
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

logger = logging.getLogger(__name__)

class SofiFeeCalculator:
    """
    Sofi AI Wallet Comprehensive Fee Calculation System
    
    Handles all fee calculations with admin-editable settings:
    - Deposit fees with profit margins
    - Transfer fees with transparent breakdown
    - Crypto rate margins and deposit fees
    - Airtime/data commissions
    - Daily profit tracking and reporting
    """
    
    def __init__(self):
        self.settings_cache = {}
        self._load_settings()
    
    def _load_settings(self):
        """Load all fee settings from Supabase settings table"""
        try:
            if not supabase:
                logger.warning("Supabase not initialized, using default settings")
                self._set_default_settings()
                return
            
            response = supabase.table('settings').select('*').execute()
            
            if response.data:
                for setting in response.data:
                    self.settings_cache[setting['key']] = float(setting['value'])
                logger.info(f"Loaded {len(response.data)} fee settings from database")
            
            # Ensure all required defaults exist
            self._set_default_settings()
                    
        except Exception as e:
            logger.error(f"Error loading fee settings: {e}")
            self._set_default_settings()
    
    def _set_default_settings(self):
        """Set default fee values if not found in database"""
        defaults = {
            # Deposit fees
            'sofi_deposit_fee': 50.00,        # Sofi's deposit fee (shown to user)
            'opay_deposit_fee': 10.00,        # OPay's processing fee (hidden)
            
            # Transfer fees  
            'sofi_transfer_fee': 10.00,       # Sofi's transfer fee
            'opay_transfer_fee': 20.00,       # OPay's transfer processing fee
            
            # Crypto rates and margins
            'crypto_buy_rate': 1550.00,       # Rate when Sofi buys from user (lower)
            'crypto_sell_rate': 1600.00,      # Rate when Sofi sells to user (higher)
            'crypto_deposit_fee_usd': 1.00,   # $1 fee for crypto deposits
            
            # Airtime/Data commissions
            'airtime_commission_rate': 3.0,   # 3% commission on airtime
            'data_commission_rate': 5.0,      # 5% commission on data
            
            # User limits
            'daily_limit_unverified': 200000.00,  # ₦200k for unverified
            'daily_limit_verified': 1000000.00,   # ₦1M for verified
        }
        
        for key, value in defaults.items():
            if key not in self.settings_cache:
                self.settings_cache[key] = value    
    def get_setting(self, key: str, default: float = 0.0) -> float:
        """Get a fee setting value with automatic refresh if needed"""
        if key not in self.settings_cache:
            self._load_settings()
        return self.settings_cache.get(key, default)
    
    def calculate_deposit_fees(self, amount: float) -> Dict[str, Any]:
        """
        Calculate deposit fees when user deposits to OPay virtual account
        
        DEPOSIT FEE STRUCTURE:
        - Sofi Deposit Fee: ₦50 (shown to user, our revenue)
        - OPay Processing Fee: ₦10 (hidden, our cost)
        - Net Profit: ₦40 per deposit
        
        Args:
            amount: Deposit amount in Naira
            
        Returns:
            Dict with complete fee breakdown and profit calculation
        """
        try:
            sofi_fee = self.get_setting('sofi_deposit_fee', 50.00)
            opay_fee = self.get_setting('opay_deposit_fee', 10.00)
            
            # User only sees and pays Sofi fee
            user_fee = sofi_fee
            credited_amount = amount - user_fee
            
            # Sofi's actual profit after paying OPay
            sofi_profit = sofi_fee - opay_fee
            total_cost = opay_fee  # Our cost
            
            return {
                'deposit_amount': amount,
                'user_fee': user_fee,              # What user pays (₦50)
                'credited_amount': credited_amount,  # What user receives
                'sofi_profit': sofi_profit,        # Our profit (₦40)
                'opay_cost': opay_fee,             # Our cost (₦10)
                'total_cost': total_cost,
                'fee_description': f"Deposit fee: ₦{user_fee:,.2f}",
                'user_message': f"Deposit successful! ₦{credited_amount:,.2f} credited to your wallet (₦{user_fee:,.2f} deposit fee applied)",
                'profit_details': f"Deposit profit: ₦{sofi_profit:,.2f} (Fee: ₦{sofi_fee:,.2f} - Cost: ₦{opay_fee:,.2f})"
            }
            
        except Exception as e:
            logger.error(f"Error calculating deposit fees: {e}")
            return {}
      
    def calculate_transfer_fees(self, amount: float) -> Dict[str, Any]:
        """
        Calculate transfer fees when user sends money to another bank
        
        TRANSFER FEE STRUCTURE:
        - Sofi Transfer Fee: ₦10 (our service fee, profit)
        - OPay Processing Fee: ₦20 (payment processor cost)
        - Total charged to user: ₦30
        - Net Profit: ₦10 per transfer
        
        Args:
            amount: Transfer amount in Naira
            
        Returns:
            Dict with complete fee breakdown and profit calculation
        """
        try:
            sofi_fee = self.get_setting('sofi_transfer_fee', 10.00)
            opay_fee = self.get_setting('opay_transfer_fee', 20.00)
            
            total_fee = sofi_fee + opay_fee  # Total charged to user
            total_deduction = amount + total_fee  # Amount + fees
            sofi_profit = sofi_fee  # Our profit (service fee)
            
            return {
                'transfer_amount': amount,
                'sofi_fee': sofi_fee,              # Our service fee (₦10)
                'opay_fee': opay_fee,              # Processing fee (₦20)
                'total_fee': total_fee,            # Total fee (₦30)
                'total_deduction': total_deduction, # Amount debited from wallet
                'sofi_profit': sofi_profit,        # Our profit (₦10)
                'fee_description': f"Transfer fee: ₦{total_fee:,.2f} (Service: ₦{sofi_fee:,.2f} + Processing: ₦{opay_fee:,.2f})",
                'user_message': f"Transfer of ₦{amount:,.2f} initiated. Total debited: ₦{total_deduction:,.2f} (including ₦{total_fee:,.2f} transfer fee)",
                'profit_details': f"Transfer profit: ₦{sofi_profit:,.2f} (Service fee: ₦{sofi_fee:,.2f})"
            }
            
        except Exception as e:
            logger.error(f"Error calculating transfer fees: {e}")
            return {}
      
    def calculate_crypto_deposit_fees(self, crypto_amount: float, crypto_type: str = "USDT") -> Dict[str, Any]:
        """
        Calculate fees when user deposits crypto (USDT/BTC) to Sofi
        
        CRYPTO DEPOSIT STRUCTURE:
        - Deposit Fee: $1 per deposit (converted to Naira)
        - Exchange Rate: Current buy rate (e.g., $1 = ₦1,550)
        - User gets: (Crypto Amount - $1) × Buy Rate
        
        Args:
            crypto_amount: Amount in crypto (USD equivalent)
            crypto_type: Type of crypto (USDT, BTC, ETH)
            
        Returns:
            Dict with complete crypto deposit breakdown
        """
        try:
            deposit_fee_usd = self.get_setting('crypto_deposit_fee_usd', 1.00)
            buy_rate = self.get_setting('crypto_buy_rate', 1550.00)
            
            # Calculate after fee deduction
            crypto_after_fee = max(0, crypto_amount - deposit_fee_usd)
            naira_credited = crypto_after_fee * buy_rate
            
            # Profit calculation
            fee_in_naira = deposit_fee_usd * buy_rate
            sofi_profit = fee_in_naira
            
            return {
                'crypto_amount': crypto_amount,
                'crypto_type': crypto_type.upper(),
                'deposit_fee_usd': deposit_fee_usd,
                'deposit_fee_naira': fee_in_naira,
                'crypto_after_fee': crypto_after_fee,
                'exchange_rate': buy_rate,
                'naira_credited': naira_credited,
                'sofi_profit': sofi_profit,
                'fee_description': f"Crypto deposit fee: ${deposit_fee_usd:,.2f} (₦{fee_in_naira:,.2f})",
                'user_message': f"${crypto_amount:,.2f} {crypto_type.upper()} received! ₦{naira_credited:,.2f} credited to your wallet (${deposit_fee_usd:,.2f} processing fee applied)",
                'profit_details': f"Crypto deposit profit: ₦{sofi_profit:,.2f} (${deposit_fee_usd:,.2f} fee @ ₦{buy_rate:,.2f}/$)"
            }
            
        except Exception as e:
            logger.error(f"Error calculating crypto deposit fees: {e}")
            return {}
      
    def calculate_crypto_buy_sell_profit(self, usd_amount: float, operation: str) -> Dict[str, Any]:
        """
        Calculate profit from crypto buy/sell rate margins
        
        CRYPTO RATE STRUCTURE:
        - Buy Rate: $1 = ₦1,550 (when we buy from user - lower rate)
        - Sell Rate: $1 = ₦1,600 (when we sell to user - higher rate)  
        - Profit Margin: ₦50 per USD
        
        Args:
            usd_amount: USD amount for the transaction
            operation: 'buy' (user buying crypto) or 'sell' (user selling crypto)
            
        Returns:
            Dict with rate breakdown and profit calculation
        """
        try:
            buy_rate = self.get_setting('crypto_buy_rate', 1550.00)   # Lower rate
            sell_rate = self.get_setting('crypto_sell_rate', 1600.00) # Higher rate
            margin_per_usd = sell_rate - buy_rate  # ₦50 profit per USD
            
            if operation.lower() == 'buy':
                # User is buying crypto from us, pays at higher rate
                naira_charged = usd_amount * sell_rate    # User pays more
                our_cost = usd_amount * buy_rate          # Our cost (if buying from market)
                sofi_profit = naira_charged - our_cost    # Margin profit
                
                return {
                    'operation': 'buy',
                    'usd_amount': usd_amount,
                    'user_rate': sell_rate,             # Rate user pays at
                    'market_rate': buy_rate,            # Our cost rate
                    'naira_charged': naira_charged,     # What user pays
                    'sofi_cost': our_cost,              # Our cost
                    'sofi_profit': sofi_profit,         # Our profit
                    'margin_per_usd': margin_per_usd,
                    'fee_description': f"Crypto rate: $1 = ₦{sell_rate:,.2f}",
                    'user_message': f"${usd_amount:,.2f} crypto purchased for ₦{naira_charged:,.2f} (Rate: $1 = ₦{sell_rate:,.2f})",
                    'profit_details': f"Crypto sell profit: ₦{sofi_profit:,.2f} (₦{margin_per_usd:,.2f}/USD margin)"
                }
            
            elif operation.lower() == 'sell':
                # User is selling crypto to us, gets paid at lower rate
                naira_paid = usd_amount * buy_rate        # User gets less
                market_value = usd_amount * sell_rate     # Market value (if selling to market)
                sofi_profit = market_value - naira_paid   # Margin profit
                
                return {
                    'operation': 'sell',
                    'usd_amount': usd_amount,
                    'user_rate': buy_rate,              # Rate user gets paid at
                    'market_rate': sell_rate,           # Market value rate
                    'naira_paid': naira_paid,           # What user receives
                    'market_value': market_value,       # Market value
                    'sofi_profit': sofi_profit,         # Our profit
                    'margin_per_usd': margin_per_usd,
                    'fee_description': f"Crypto rate: $1 = ₦{buy_rate:,.2f}",
                    'user_message': f"${usd_amount:,.2f} crypto sold for ₦{naira_paid:,.2f} (Rate: $1 = ₦{buy_rate:,.2f})",
                    'profit_details': f"Crypto buy profit: ₦{sofi_profit:,.2f} (₦{margin_per_usd:,.2f}/USD margin)"                }
            
            else:
                raise ValueError(f"Invalid operation: {operation}. Must be 'buy' or 'sell'")
                
        except Exception as e:
            logger.error(f"Error calculating crypto profit: {e}")
            return {}
    
    def calculate_airtime_commission(self, amount: float, provider: str = "MTN") -> Dict[str, Any]:
        """
        Calculate commission from airtime purchases
        
        AIRTIME COMMISSION STRUCTURE:
        - Commission Rate: 3% of purchase amount
        - All commission is profit (no additional costs)
        
        Args:
            amount: Airtime purchase amount in Naira
            provider: Network provider (MTN, GLO, AIRTEL, 9MOBILE)
            
        Returns:
            Dict with commission calculation and profit details
        """
        try:
            commission_rate = self.get_setting('airtime_commission_rate', 3.0)  # 3%
            commission_amount = (amount * commission_rate) / 100
            user_pays = amount  # User pays full amount
            sofi_profit = commission_amount  # Commission is pure profit
            
            return {
                'purchase_amount': amount,
                'provider': provider.upper(),
                'commission_rate': commission_rate,
                'commission_amount': commission_amount,
                'user_pays': user_pays,
                'sofi_profit': sofi_profit,
                'fee_description': f"Airtime purchase: ₦{amount:,.2f} ({provider.upper()})",
                'user_message': f"₦{amount:,.2f} {provider.upper()} airtime purchased successfully!",
                'profit_details': f"Airtime commission: ₦{commission_amount:,.2f} ({commission_rate}% of ₦{amount:,.2f})"
            }
            
        except Exception as e:
            logger.error(f"Error calculating airtime commission: {e}")
            return {}
    
    def calculate_data_commission(self, amount: float, provider: str = "MTN") -> Dict[str, Any]:
        """
        Calculate commission from data purchases
        
        DATA COMMISSION STRUCTURE:
        - Commission Rate: 5% of purchase amount
        - All commission is profit (no additional costs)
        
        Args:
            amount: Data purchase amount in Naira
            provider: Network provider (MTN, GLO, AIRTEL, 9MOBILE)
            
        Returns:
            Dict with commission calculation and profit details
        """
        try:
            commission_rate = self.get_setting('data_commission_rate', 5.0)  # 5%
            commission_amount = (amount * commission_rate) / 100
            user_pays = amount  # User pays full amount
            sofi_profit = commission_amount  # Commission is pure profit
            
            return {
                'purchase_amount': amount,
                'provider': provider.upper(),
                'commission_rate': commission_rate,
                'commission_amount': commission_amount,
                'user_pays': user_pays,
                'sofi_profit': sofi_profit,
                'fee_description': f"Data purchase: ₦{amount:,.2f} ({provider.upper()})",
                'user_message': f"₦{amount:,.2f} {provider.upper()} data purchased successfully!",
                'profit_details': f"Data commission: ₦{commission_amount:,.2f} ({commission_rate}% of ₦{amount:,.2f})"
            }
            
        except Exception as e:
            logger.error(f"Error calculating data commission: {e}")
            return {}
    
    def log_profit(self, source: str, amount: float, details: str = "") -> bool:
        """
        Log profit to Supabase profits table
        
        Args:
            source: Profit source ('deposit', 'transfer', 'crypto', etc.)
            amount: Profit amount in Naira
            details: Additional details
            
        Returns:
            bool: Success status
        """
        try:
            if not supabase:
                return False
            
            profit_data = {
                'source': source,
                'amount': amount,
                'details': details,
                'date': date.today().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            supabase.table('profits').insert(profit_data).execute()
            logger.info(f"Logged profit: {source} - ₦{amount:,.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging profit: {e}")
            return False
    
    def get_daily_profit_summary(self, target_date: date = None) -> Dict:
        """
        Get daily profit summary by source
        
        Args:
            target_date: Date to get summary for (default: today)
            
        Returns:
            Dict with profit breakdown by source
        """
        try:
            if not supabase:
                return {}
            
            if not target_date:
                target_date = date.today()
            
            response = supabase.table('profits').select('*').eq('date', target_date.isoformat()).execute()
            
            if not response.data:
                return {'total': 0, 'breakdown': {}}
            
            breakdown = {}
            total = 0
            
            for profit in response.data:
                source = profit['source']
                amount = float(profit['amount'])
                
                if source not in breakdown:
                    breakdown[source] = 0
                
                breakdown[source] += amount
                total += amount
            
            return {
                'date': target_date.isoformat(),
                'total': total,
                'breakdown': breakdown,
                'count': len(response.data)
            }
            
        except Exception as e:
            logger.error(f"Error getting profit summary: {e}")
            return {}
    
    def update_fee_setting(self, key: str, value: float) -> bool:
        """
        Update a fee setting in the database
        
        Args:
            key: Setting key
            value: New value
            
        Returns:
            bool: Success status
        """
        try:
            if not supabase:
                return False
            
            # Update or insert setting
            response = supabase.table('settings').upsert({
                'key': key,
                'value': str(value),
                'updated_at': datetime.now().isoformat()
            }, on_conflict='key').execute()
            
            if response.data:
                self.settings_cache[key] = value
                logger.info(f"Updated fee setting: {key} = {value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating fee setting: {e}")
            return False
      
    def get_fee_explanation(self, transaction_type: str, amount: float, **kwargs) -> str:
        """
        Generate user-friendly fee explanation based on your specifications
        
        Args:
            transaction_type: 'deposit', 'transfer', 'crypto_deposit', 'airtime', 'data'
            amount: Transaction amount
            **kwargs: Additional parameters (crypto_type, provider, etc.)
            
        Returns:
            str: Clear, branded fee explanation for users
        """
        try:
            if transaction_type == 'deposit':
                fees = self.calculate_deposit_fees(amount)
                return fees.get('user_message', f"Deposit fee explanation not available")
            
            elif transaction_type == 'transfer':
                fees = self.calculate_transfer_fees(amount)
                return fees.get('user_message', f"Transfer fee explanation not available")
            
            elif transaction_type == 'crypto_deposit':
                crypto_type = kwargs.get('crypto_type', 'USDT')
                fees = self.calculate_crypto_deposit_fees(amount, crypto_type)
                return fees.get('user_message', f"Crypto deposit explanation not available")
            
            elif transaction_type == 'airtime':
                provider = kwargs.get('provider', 'MTN')
                fees = self.calculate_airtime_commission(amount, provider)
                return fees.get('user_message', f"Airtime purchase completed")
            
            elif transaction_type == 'data':
                provider = kwargs.get('provider', 'MTN')
                fees = self.calculate_data_commission(amount, provider)
                return fees.get('user_message', f"Data purchase completed")
            
            elif transaction_type == 'crypto_buy':
                operation = 'buy'
                fees = self.calculate_crypto_buy_sell_profit(amount, operation)
                return fees.get('user_message', f"Crypto purchase completed")
            
            elif transaction_type == 'crypto_sell':
                operation = 'sell'
                fees = self.calculate_crypto_buy_sell_profit(amount, operation)
                return fees.get('user_message', f"Crypto sale completed")
            
            else:
                return f"Transaction type '{transaction_type}' not recognized. Contact support for fee details."
                
        except Exception as e:
            logger.error(f"Error generating fee explanation: {e}")
            return "Unable to provide fee breakdown at this time. Contact support if you have questions."
    
    def get_detailed_fee_breakdown(self, transaction_type: str, amount: float, **kwargs) -> str:
        """
        Generate detailed fee breakdown for admin/debugging purposes
        
        Returns:
            str: Detailed breakdown including profit calculations
        """
        try:
            if transaction_type == 'deposit':
                fees = self.calculate_deposit_fees(amount)
                return f"DEPOSIT: {fees.get('profit_details', 'N/A')}"
            
            elif transaction_type == 'transfer': 
                fees = self.calculate_transfer_fees(amount)
                return f"TRANSFER: {fees.get('profit_details', 'N/A')}"
            
            elif transaction_type == 'crypto_deposit':
                crypto_type = kwargs.get('crypto_type', 'USDT')
                fees = self.calculate_crypto_deposit_fees(amount, crypto_type)
                return f"CRYPTO DEPOSIT: {fees.get('profit_details', 'N/A')}"
            
            else:
                return f"No detailed breakdown available for {transaction_type}"
                
        except Exception as e:
            logger.error(f"Error generating detailed breakdown: {e}")
            return "Breakdown unavailable"

# Global fee calculator instance
fee_calculator = SofiFeeCalculator()
