"""
Test the updated fee calculation system
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fee_calculation():
    from functions.transfer_functions import calculate_transfer_fee
    
    test_amounts = [1000, 5000, 10000, 50000, 100000]
    
    print("🧮 Testing Updated Fee Calculation System")
    print("=" * 60)
    
    for amount in test_amounts:
        fee_result = await calculate_transfer_fee(amount)
        
        print(f"\n💰 Transfer Amount: ₦{amount:,}")
        print(f"   📱 User Sees:")
        print(f"      Transfer Fee: ₦{fee_result['total_fee']:,.2f}")
        print(f"      Total Charge: ₦{fee_result['total']:,.2f}")
        print(f"   🏢 Your Backend (Profit Tracking):")
        print(f"      Sofi Fee (Profit): ₦{fee_result['sofi_fee']:,.2f}")
        print(f"      Paystack Fee (Cost): ₦{fee_result['paystack_fee']:,.2f}")
        print(f"      Net Profit: ₦{fee_result['sofi_fee'] - fee_result['paystack_fee']:,.2f}")
        print(f"   📊 Analysis:")
        print(f"      Fee %: {fee_result['fee_percentage']:.2f}%")
        print(f"      Profit Margin: {((fee_result['sofi_fee'] - fee_result['paystack_fee']) / amount) * 100:.2f}%")

if __name__ == "__main__":
    asyncio.run(test_fee_calculation())
