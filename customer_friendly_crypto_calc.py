#!/usr/bin/env python3
"""
🎯 CUSTOMER-FRIENDLY CRYPTO MARGIN CALCULATOR
==============================================

This shows your realistic profit projections with customer-friendly rates.
"""

def calculate_customer_friendly_margins():
    """Calculate profits with customer-friendly margin settings"""
    
    # Your updated settings (customer-friendly)
    margins = {
        'USDT': 0.025,  # 2.5% margin
        'BTC': 0.035,   # 3.5% margin
    }
    
    min_profits = {
        'USDT': 250,    # ₦250 minimum
        'BTC': 500000,  # ₦500K minimum
    }
    
    # Current market rates (from recent test)
    market_rates = {
        'BTC': 162532667,  # ₦162.5M per BTC
        'USDT': 1543       # ₦1,543 per USDT
    }
    
    print("💰 CUSTOMER-FRIENDLY CRYPTO RATES & PROFITS")
    print("=" * 55)
    print("🎯 Goal: Balance profitability with customer retention")
    print()
    
    for crypto in ['USDT', 'BTC']:
        market_rate = market_rates[crypto]
        margin = margins[crypto]
        min_profit = min_profits[crypto]
        
        # Calculate your rate
        rate_after_margin = market_rate * (1 - margin)
        profit_per_unit = max(market_rate - rate_after_margin, min_profit)
        your_rate = market_rate - profit_per_unit
        
        print(f"{'🟢 USDT (Tether)' if crypto == 'USDT' else '🟠 BTC (Bitcoin)'}")
        print(f"   Market Rate: ₦{market_rate:,.2f}")
        print(f"   Your Rate: ₦{your_rate:,.2f}")
        print(f"   Margin: {margin*100:.1f}%")
        print(f"   Profit per unit: ₦{profit_per_unit:,.2f}")
        print()
        
        # Sample deposit calculations
        if crypto == 'USDT':
            print("   📊 Sample USDT Deposits & Profits:")
            deposits = [50, 100, 500, 1000]
            for deposit in deposits:
                total_profit = deposit * profit_per_unit
                user_gets = deposit * your_rate
                print(f"      {deposit:,} USDT → User gets ₦{user_gets:,.0f}, You profit ₦{total_profit:,.0f}")
        else:
            print("   📊 Sample BTC Deposits & Profits:")
            deposits = [0.01, 0.05, 0.1, 0.5]
            for deposit in deposits:
                total_profit = deposit * profit_per_unit
                user_gets = deposit * your_rate
                print(f"      {deposit} BTC → User gets ₦{user_gets:,.0f}, You profit ₦{total_profit:,.0f}")
        
        print()

def calculate_monthly_revenue_realistic():
    """Calculate realistic monthly revenue projections"""
    
    print("📈 REALISTIC MONTHLY REVENUE PROJECTIONS")
    print("=" * 50)
    print("Based on conservative customer volume estimates:")
    print()
    
    # Conservative volume estimates
    monthly_estimates = {
        'usdt_deposits': 100,    # 100 USDT deposits/month
        'usdt_avg_size': 150,    # Average 150 USDT per deposit
        'btc_deposits': 20,      # 20 BTC deposits/month
        'btc_avg_size': 0.02     # Average 0.02 BTC per deposit
    }
    
    # Profit per unit (from calculations above)
    usdt_profit = 38.58  # ₦38.58 per USDT
    btc_profit = 5688184  # ₦5.7M per BTC
    
    # Monthly calculations
    usdt_monthly = (monthly_estimates['usdt_deposits'] * 
                   monthly_estimates['usdt_avg_size'] * 
                   usdt_profit)
    
    btc_monthly = (monthly_estimates['btc_deposits'] * 
                  monthly_estimates['btc_avg_size'] * 
                  btc_profit)
    
    total_monthly = usdt_monthly + btc_monthly
    
    print(f"💎 USDT Revenue:")
    print(f"   {monthly_estimates['usdt_deposits']} deposits × {monthly_estimates['usdt_avg_size']} USDT = {monthly_estimates['usdt_deposits'] * monthly_estimates['usdt_avg_size']:,} USDT/month")
    print(f"   × ₦{usdt_profit:.2f} profit = ₦{usdt_monthly:,.0f}/month")
    print()
    
    print(f"🟠 BTC Revenue:")
    print(f"   {monthly_estimates['btc_deposits']} deposits × {monthly_estimates['btc_avg_size']} BTC = {monthly_estimates['btc_deposits'] * monthly_estimates['btc_avg_size']} BTC/month")
    print(f"   × ₦{btc_profit:,.0f} profit = ₦{btc_monthly:,.0f}/month")
    print()
    
    print(f"💰 TOTAL MONTHLY CRYPTO PROFIT: ₦{total_monthly:,.0f}")
    print(f"📅 ANNUAL PROJECTION: ₦{total_monthly * 12:,.0f}")
    print()
    
    # Add other revenue streams
    transfer_revenue = 1000 * 50  # 1000 transfers × ₦50 fee
    airtime_revenue = 500 * 25   # 500 airtime purchases × ₦25 avg profit
    
    print("📊 COMBINED MONTHLY REVENUE (All Services):")
    print(f"   Crypto profits: ₦{total_monthly:,.0f}")
    print(f"   Transfer fees: ₦{transfer_revenue:,.0f}")
    print(f"   Airtime profits: ₦{airtime_revenue:,.0f}")
    print(f"   TOTAL: ₦{total_monthly + transfer_revenue + airtime_revenue:,.0f}/month")

def customer_retention_benefits():
    """Show benefits of customer-friendly rates"""
    
    print("\n🎯 CUSTOMER RETENTION BENEFITS")
    print("=" * 40)
    print("Why customer-friendly rates are better for long-term success:")
    print()
    
    print("✅ COMPETITIVE ADVANTAGES:")
    print("   • USDT rate only 2.5% below market (very competitive)")
    print("   • BTC rate only 3.5% below market (attractive to users)")
    print("   • Users get fair value = more repeat customers")
    print("   • Word-of-mouth referrals increase")
    print()
    
    print("💡 GROWTH STRATEGY:")
    print("   • Start with competitive rates to build customer base")
    print("   • Gradually increase margins as customer loyalty grows")
    print("   • Monitor competitor rates and adjust accordingly")
    print("   • Focus on volume over high margins initially")
    print()
    
    print("📊 LONG-TERM SUCCESS METRICS:")
    print("   • Customer retention rate > 80%")
    print("   • Monthly transaction volume growth")
    print("   • Positive customer reviews and referrals")
    print("   • Steady monthly revenue of ₦2M+ achievable")

if __name__ == "__main__":
    calculate_customer_friendly_margins()
    calculate_monthly_revenue_realistic()
    customer_retention_benefits()
