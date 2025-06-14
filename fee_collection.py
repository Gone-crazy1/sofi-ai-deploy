#!/usr/bin/env python3
"""
💰 SOFI AI FEE COLLECTION INTEGRATION
====================================

This module provides functions to integrate fee collection into your existing
transfer, crypto, airtime, and data systems.

Add these functions to your main.py or create a new utils/fee_collection.py module.
"""

import os
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fee Configuration
TRANSFER_FEE = 50.0  # ₦50 per transfer
DEPOSIT_FEE_MIN = 10.0  # ₦10 minimum deposit fee
DEPOSIT_FEE_MAX = 25.0  # ₦25 maximum deposit fee
CRYPTO_PROFIT_MARGIN = 500.0  # Base profit margin for crypto trades

def calculate_deposit_fee(amount: float) -> float:
    """
    Calculate deposit fee based on amount
    ₦10-25 per deposit depending on amount
    """
    if amount <= 1000:
        return DEPOSIT_FEE_MIN
    elif amount >= 10000:
        return DEPOSIT_FEE_MAX
    else:
        # Linear scale between 10-25 based on amount
        fee_rate = DEPOSIT_FEE_MIN + ((amount - 1000) / 9000) * (DEPOSIT_FEE_MAX - DEPOSIT_FEE_MIN)
        return round(fee_rate, 2)

def calculate_crypto_profit(crypto_type: str, amount: float, market_rate: float) -> float:
    """
    Calculate profit margin for crypto trades
    ₦500-1000 per conversion based on amount and crypto type
    """
    base_profit = CRYPTO_PROFIT_MARGIN
    
    # Adjust profit based on crypto type
    if crypto_type == "BTC":
        base_profit *= 1.5  # Higher profit for BTC
    elif crypto_type == "USDT":
        base_profit *= 1.0  # Standard profit for USDT
    elif crypto_type == "ETH":
        base_profit *= 1.2  # Medium profit for ETH
    
    # Scale profit based on transaction amount
    if amount >= 100000:  # Large transactions
        base_profit *= 1.5
    elif amount >= 50000:  # Medium transactions
        base_profit *= 1.2
    
    return min(base_profit, 1000.0)  # Cap at ₦1000

def save_transfer_fee(user_id: str, transfer_amount: float, transaction_reference: str = None):
    """
    Save transfer fee to database
    Call this function after every successful transfer
    """
    try:
        fee_data = {
            "telegram_chat_id": str(user_id),
            "transfer_amount": transfer_amount,
            "fee_charged": TRANSFER_FEE,
            "transaction_reference": transaction_reference,
            "timestamp": datetime.now().isoformat()
        }
        
        result = supabase.table("transfer_charges").insert(fee_data).execute()
        print(f"✅ Transfer fee saved: ₦{TRANSFER_FEE}")
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"❌ Error saving transfer fee: {e}")
        return None

def save_deposit_fee(user_id: str, deposit_amount: float, fee_type: str = "bank_deposit"):
    """
    Save deposit fee to database
    Call this function after every successful deposit
    """
    try:
        fee_charged = calculate_deposit_fee(deposit_amount)
        
        fee_data = {
            "telegram_chat_id": str(user_id),
            "deposit_amount": deposit_amount,
            "fee_charged": fee_charged,
            "fee_type": fee_type,
            "timestamp": datetime.now().isoformat()
        }
        
        result = supabase.table("deposit_fees").insert(fee_data).execute()
        print(f"✅ Deposit fee saved: ₦{fee_charged}")
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"❌ Error saving deposit fee: {e}")
        return None

def save_crypto_trade(user_id: str, crypto_type: str, crypto_amount: float, 
                     naira_equivalent: float, conversion_rate: float):
    """
    Save crypto trade with profit calculation
    Call this function after every crypto conversion
    """
    try:
        profit = calculate_crypto_profit(crypto_type, naira_equivalent, conversion_rate)
        
        trade_data = {
            "telegram_chat_id": str(user_id),
            "crypto_type": crypto_type,
            "crypto_amount": crypto_amount,
            "naira_equivalent": naira_equivalent,
            "conversion_rate_used": conversion_rate,
            "profit_made_on_trade": profit,
            "timestamp": datetime.now().isoformat()
        }
        
        result = supabase.table("crypto_trades").insert(trade_data).execute()
        print(f"✅ Crypto trade saved with ₦{profit} profit")
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"❌ Error saving crypto trade: {e}")
        return None

def save_airtime_sale(user_id: str, network: str, amount: float, cost_price: float = None):
    """
    Save airtime sale with profit calculation
    Call this function after every airtime purchase
    """
    try:
        # Default cost price if not provided (assuming 2% profit margin)
        if cost_price is None:
            cost_price = amount * 0.98
        
        sale_data = {
            "telegram_chat_id": str(user_id),
            "network": network,
            "amount_sold": amount,
            "sale_price": amount,
            "cost_price": cost_price,
            "timestamp": datetime.now().isoformat()
        }
        
        result = supabase.table("airtime_sales").insert(sale_data).execute()
        profit = amount - cost_price
        print(f"✅ Airtime sale saved with ₦{profit:.2f} profit")
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"❌ Error saving airtime sale: {e}")
        return None

def save_data_sale(user_id: str, network: str, bundle_size: str, amount: float, cost_price: float = None):
    """
    Save data bundle sale with profit calculation
    Call this function after every data purchase
    """
    try:
        # Default cost price if not provided (assuming 5% profit margin)
        if cost_price is None:
            cost_price = amount * 0.95
        
        sale_data = {
            "telegram_chat_id": str(user_id),
            "network": network,
            "bundle_size": bundle_size,
            "amount_sold": amount,
            "sale_price": amount,
            "cost_price": cost_price,
            "timestamp": datetime.now().isoformat()
        }
        
        result = supabase.table("data_sales").insert(sale_data).execute()
        profit = amount - cost_price
        print(f"✅ Data sale saved with ₦{profit:.2f} profit")
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"❌ Error saving data sale: {e}")
        return None

def get_total_revenue():
    """
    Get total accumulated revenue from all sources
    """
    try:
        result = supabase.rpc('calculate_total_revenue').execute()
        return result.data if result.data else 0.0
    except Exception as e:
        print(f"❌ Error calculating total revenue: {e}")
        return 0.0

def update_financial_summary():
    """
    Manually trigger financial summary update
    """
    try:
        # Get latest totals from each table
        crypto_result = supabase.table("crypto_trades").select("profit_made_on_trade").execute()
        crypto_profit = sum(row['profit_made_on_trade'] for row in crypto_result.data) if crypto_result.data else 0
        
        airtime_result = supabase.table("airtime_sales").select("sale_price, cost_price").execute()
        airtime_profit = sum(row['sale_price'] - row['cost_price'] for row in airtime_result.data) if airtime_result.data else 0
        
        data_result = supabase.table("data_sales").select("sale_price, cost_price").execute()
        data_profit = sum(row['sale_price'] - row['cost_price'] for row in data_result.data) if data_result.data else 0
        
        transfer_result = supabase.table("transfer_charges").select("fee_charged").execute()
        transfer_fees = sum(row['fee_charged'] for row in transfer_result.data) if transfer_result.data else 0
        
        deposit_result = supabase.table("deposit_fees").select("fee_charged").execute()
        deposit_fees = sum(row['fee_charged'] for row in deposit_result.data) if deposit_result.data else 0
        
        total_revenue = crypto_profit + airtime_profit + data_profit + transfer_fees + deposit_fees
        
        # Update summary table
        update_data = {
            "total_revenue": total_revenue,
            "total_crypto_profit": crypto_profit,
            "total_airtime_revenue": airtime_profit,
            "total_data_revenue": data_profit,
            "total_transfer_fee_collected": transfer_fees,
            "total_deposit_fee_collected": deposit_fees,
            "last_updated": datetime.now().isoformat()
        }
        
        # Check if summary record exists
        existing = supabase.table("sofi_financial_summary").select("id").limit(1).execute()
        
        if existing.data:
            # Update existing record
            result = supabase.table("sofi_financial_summary").update(update_data).eq("id", existing.data[0]["id"]).execute()
        else:
            # Insert new record
            result = supabase.table("sofi_financial_summary").insert(update_data).execute()
        
        print(f"✅ Financial summary updated - Total Revenue: ₦{total_revenue:,.2f}")
        return total_revenue
        
    except Exception as e:
        print(f"❌ Error updating financial summary: {e}")
        return 0.0

# Integration Examples for your existing code:

def integrate_with_transfer_flow():
    """
    Example integration with your transfer flow
    Add this call after successful transfer in main.py
    """
    example_code = '''
# In your transfer completion code in main.py, add:
from fee_collection import save_transfer_fee

# After successful transfer:
save_transfer_fee(
    user_id=user_id,
    transfer_amount=transfer_amount,
    transaction_reference=transaction_reference
)
'''
    print(example_code)

def integrate_with_crypto_system():
    """
    Example integration with crypto system
    """
    example_code = '''
# In your crypto conversion code, add:
from fee_collection import save_crypto_trade

# After successful crypto conversion:
save_crypto_trade(
    user_id=user_id,
    crypto_type="BTC",  # or "USDT", "ETH"
    crypto_amount=crypto_amount,
    naira_equivalent=naira_amount,
    conversion_rate=rate_used
)
'''
    print(example_code)

if __name__ == "__main__":
    print("💰 SOFI AI FEE COLLECTION INTEGRATION")
    print("=" * 50)
    print("This module provides fee collection functions for:")
    print("✅ Transfer fees (₦50 per transfer)")
    print("✅ Deposit fees (₦10-25 per deposit)")
    print("✅ Crypto trading profits (₦500-1000 per conversion)")
    print("✅ Airtime/Data markup profits")
    print("\n📋 Integration required in main.py - see function examples above")
