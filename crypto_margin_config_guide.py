#!/usr/bin/env python3
"""
🎯 CRYPTO MARGIN CONFIGURATION GUIDE
=====================================

This guide shows you how to adjust your crypto profit margins
and minimum profit settings for maximum revenue.

CURRENT SETTINGS (showing real profits):
- USDT: 3% margin + ₦500 minimum = ₦500 profit per USDT
- BTC: 4% margin = ₦6.5M profit per BTC

RECOMMENDED ADJUSTMENTS FOR HIGHER PROFITS:
"""

# ==========================================
# MARGIN CONFIGURATION OPTIONS
# ==========================================

class OptimizedCryptoConfig:
    """Optimized configuration for maximum profits"""
    
    # OPTION 1: AGGRESSIVE MARGINS (Higher Profits)
    AGGRESSIVE_MARGINS = {
        'USDT': 0.05,    # 5% margin (₦77 profit per USDT at ₦1,543 rate)
        'BTC': 0.06,     # 6% margin (₦9.7M profit per BTC!)
    }
    
    # OPTION 2: CONSERVATIVE MARGINS (Competitive Rates)
    CONSERVATIVE_MARGINS = {
        'USDT': 0.02,    # 2% margin (₦31 profit per USDT)
        'BTC': 0.03,     # 3% margin (₦4.9M profit per BTC)
    }
    
    # OPTION 3: CURRENT BALANCED MARGINS
    CURRENT_MARGINS = {
        'USDT': 0.03,    # 3% margin
        'BTC': 0.04,     # 4% margin
    }
    
    # MINIMUM PROFIT SETTINGS
    PROFIT_MINIMUMS = {
        # Conservative (competitive rates)
        'CONSERVATIVE': {
            'USDT': 250,    # ₦250 minimum profit per USDT
            'BTC': 500000,  # ₦500K minimum profit per BTC
        },
        
        # Current settings
        'CURRENT': {
            'USDT': 500,    # ₦500 minimum profit per USDT
            'BTC': 1000000, # ₦1M minimum profit per BTC
        },
        
        # Aggressive (higher profits)
        'AGGRESSIVE': {
            'USDT': 750,    # ₦750 minimum profit per USDT
            'BTC': 2000000, # ₦2M minimum profit per BTC
        }
    }

# ==========================================
# PROFIT CALCULATOR
# ==========================================

def calculate_profits_at_different_margins():
    """Calculate potential profits with different margin settings"""
    
    # Sample rates (using recent real rates)
    sample_rates = {
        'BTC': 162532667,  # ₦162.5M per BTC
        'USDT': 1543       # ₦1,543 per USDT
    }
    
    print("💰 CRYPTO PROFIT CALCULATOR")
    print("=" * 50)
    
    scenarios = [
        ("Conservative (2-3%)", OptimizedCryptoConfig.CONSERVATIVE_MARGINS, 'CONSERVATIVE'),
        ("Current Balanced (3-4%)", OptimizedCryptoConfig.CURRENT_MARGINS, 'CURRENT'),
        ("Aggressive (5-6%)", OptimizedCryptoConfig.AGGRESSIVE_MARGINS, 'AGGRESSIVE')
    ]
    
    for scenario_name, margins, profit_level in scenarios:
        print(f"\n📊 {scenario_name} Margins:")
        print("-" * 30)
        
        for crypto, market_rate in sample_rates.items():
            margin = margins[crypto]
            min_profit = OptimizedCryptoConfig.PROFIT_MINIMUMS[profit_level][crypto]
            
            # Calculate your rate
            rate_after_margin = market_rate * (1 - margin)
            profit_per_unit = market_rate - max(rate_after_margin, market_rate - min_profit)
            your_final_rate = market_rate - profit_per_unit
            
            print(f"  {crypto}:")
            print(f"    Market Rate: ₦{market_rate:,.2f}")
            print(f"    Your Rate: ₦{your_final_rate:,.2f}")
            print(f"    Profit per unit: ₦{profit_per_unit:,.2f}")
            
            # Calculate profits for sample deposits
            if crypto == 'USDT':
                sample_deposits = [100, 500, 1000]
                for deposit in sample_deposits:
                    total_profit = deposit * profit_per_unit
                    print(f"    {deposit} USDT deposit = ₦{total_profit:,.0f} profit")
            else:  # BTC
                sample_deposits = [0.01, 0.1, 1.0]
                for deposit in sample_deposits:
                    total_profit = deposit * profit_per_unit
                    print(f"    {deposit} BTC deposit = ₦{total_profit:,.0f} profit")

# ==========================================
# MONTHLY REVENUE PROJECTIONS
# ==========================================

def project_monthly_crypto_revenue():
    """Project monthly revenue from crypto operations"""
    
    print("\n\n📈 MONTHLY CRYPTO REVENUE PROJECTIONS")
    print("=" * 50)
    
    # Assumptions (adjust based on your expected volume)
    monthly_volumes = {
        'USDT_deposits': 2000,  # 2000 USDT deposits per month
        'USDT_avg_size': 200,   # Average 200 USDT per deposit
        'BTC_deposits': 50,     # 50 BTC deposits per month
        'BTC_avg_size': 0.05    # Average 0.05 BTC per deposit
    }
    
    # Using current margin settings
    usdt_profit_per_unit = 500  # ₦500 per USDT (current setting)
    btc_profit_per_unit = 6501306  # ₦6.5M per BTC (current setting)
    
    # Calculate monthly profits
    usdt_monthly_profit = (monthly_volumes['USDT_deposits'] * 
                          monthly_volumes['USDT_avg_size'] * 
                          usdt_profit_per_unit)
    
    btc_monthly_profit = (monthly_volumes['BTC_deposits'] * 
                         monthly_volumes['BTC_avg_size'] * 
                         btc_profit_per_unit)
    
    total_monthly_profit = usdt_monthly_profit + btc_monthly_profit
    
    print(f"💎 USDT Operations:")
    print(f"   {monthly_volumes['USDT_deposits']} deposits × {monthly_volumes['USDT_avg_size']} USDT avg")
    print(f"   = {monthly_volumes['USDT_deposits'] * monthly_volumes['USDT_avg_size']:,} USDT total")
    print(f"   × ₦{usdt_profit_per_unit} profit = ₦{usdt_monthly_profit:,.0f}/month")
    
    print(f"\n🟠 BTC Operations:")
    print(f"   {monthly_volumes['BTC_deposits']} deposits × {monthly_volumes['BTC_avg_size']} BTC avg")
    print(f"   = {monthly_volumes['BTC_deposits'] * monthly_volumes['BTC_avg_size']} BTC total")
    print(f"   × ₦{btc_profit_per_unit:,.0f} profit = ₦{btc_monthly_profit:,.0f}/month")
    
    print(f"\n💰 TOTAL MONTHLY CRYPTO PROFIT: ₦{total_monthly_profit:,.0f}")
    print(f"💸 ANNUAL PROJECTION: ₦{total_monthly_profit * 12:,.0f}")

# ==========================================
# CONFIGURATION INSTRUCTIONS
# ==========================================

def how_to_change_margins():
    """Instructions for changing margin settings"""
    
    print("\n\n🔧 HOW TO CHANGE YOUR MARGIN SETTINGS")
    print("=" * 50)
    
    print("""
📝 TO ADJUST YOUR CRYPTO MARGINS:

1️⃣ EDIT THE CONFIGURATION FILE:
   File: crypto_rate_manager.py
   Line: ~44-50 (CryptoRateConfig class)

2️⃣ CHANGE MARGIN PERCENTAGES:
   MARGINS = {
       'USDT': 0.05,  # Change to 5% for higher profits
       'BTC': 0.06,   # Change to 6% for higher profits
   }

3️⃣ ADJUST MINIMUM PROFITS:
   MIN_PROFIT = {
       'USDT': 750,   # Minimum ₦750 profit per USDT
       'BTC': 2000000, # Minimum ₦2M profit per BTC
   }

4️⃣ RESTART THE BOT:
   The new margins will take effect immediately

⚠️  IMPORTANT CONSIDERATIONS:
   • Higher margins = More profit but less competitive rates
   • Lower margins = More competitive but less profit
   • Monitor competitor rates to stay competitive
   • Start conservative and increase gradually

💡 RECOMMENDED STARTING POINT:
   • USDT: 3-4% margin (₦500-750 minimum profit)
   • BTC: 4-5% margin (₦1-2M minimum profit)
""")

if __name__ == "__main__":
    calculate_profits_at_different_margins()
    project_monthly_crypto_revenue()
    how_to_change_margins()
