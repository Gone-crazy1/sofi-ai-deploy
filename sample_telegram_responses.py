"""
SOFI AI WALLET - USER NOTIFICATION EXAMPLES

Sample Telegram responses for different fee scenarios based on user specifications.
These messages are clear, branded, and include full account details as requested.
"""

from utils.fee_calculator import fee_calculator
from datetime import datetime

def generate_sample_responses():
    """Generate sample Telegram responses for all fee scenarios"""
    
    print("💰 SOFI AI WALLET - SAMPLE USER NOTIFICATIONS")
    print("=" * 60)
    print()
    
    # 1. DEPOSIT NOTIFICATION (as per user specification)
    print("1️⃣ DEPOSIT NOTIFICATION")
    print("-" * 30)
    deposit_fees = fee_calculator.calculate_deposit_fees(5000)
    
    deposit_message = f"""
💰 **DEPOSIT SUCCESSFUL!**

Hey John! 👋

{deposit_fees.get('user_message', 'Deposit processed')}

📊 **Transaction Details:**
• Amount Received: ₦5,000.00
• Deposit Fee: ₦{deposit_fees.get('user_fee', 0):,.2f}
• Amount Credited: ₦{deposit_fees.get('credited_amount', 0):,.2f}
• New Balance: ₦24,950.00

⏰ Time: {datetime.now().strftime("%I:%M %p, %B %d, %Y")}
� Via: Sofi AI Wallet (OPay Infrastructure)

Need help? Ask me: "Sofi, why did you charge me ₦50 for deposit?"

Powered by Sofi AI Wallet | Pip install -ai Tech 🤖
"""
    print(deposit_message)
    
    # 2. TRANSFER NOTIFICATION
    print("2️⃣ TRANSFER NOTIFICATION")
    print("-" * 30)
    transfer_fees = fee_calculator.calculate_transfer_fees(1000)
    
    transfer_message = f"""
💸 **TRANSFER INITIATED!**

Hey John! 👋

{transfer_fees.get('user_message', 'Transfer processed')}

📊 **Transaction Details:**
• Recipient: ADEYEMI JOHN
• Bank: GTBank (058)
• Account: 0123456789
• Transfer Amount: ₦{transfer_fees.get('transfer_amount', 0):,.2f}
• Transfer Fee: ₦{transfer_fees.get('total_fee', 0):,.2f}
• Total Debited: ₦{transfer_fees.get('total_deduction', 0):,.2f}
• New Balance: ₦23,920.00

⏰ Time: {datetime.now().strftime("%I:%M %p, %B %d, %Y")}
🔄 Status: Processing...

{transfer_fees.get('fee_description', 'Fee breakdown available')}

Powered by Sofi AI Wallet 🤖
"""
    print(transfer_message)
    
    # 3. CRYPTO DEPOSIT NOTIFICATION
    print("3️⃣ CRYPTO DEPOSIT NOTIFICATION")
    print("-" * 30)
    crypto_fees = fee_calculator.calculate_crypto_deposit_fees(10, "USDT")
    
    crypto_message = f"""
₿ **CRYPTO RECEIVED!**

Hey John! 👋

{crypto_fees.get('user_message', 'Crypto processed')}

📊 **Transaction Details:**
• Crypto Received: ${crypto_fees.get('crypto_amount', 0):,.2f} {crypto_fees.get('crypto_type', 'USDT')}
• Processing Fee: ${crypto_fees.get('deposit_fee_usd', 0):,.2f}
• Exchange Rate: $1 = ₦{crypto_fees.get('exchange_rate', 0):,.2f}
• Naira Credited: ₦{crypto_fees.get('naira_credited', 0):,.2f}
• New Balance: ₦37,870.00

⏰ Time: {datetime.now().strftime("%I:%M %p, %B %d, %Y")}
🌐 Network: TRC20 (USDT)

{crypto_fees.get('fee_description', 'Fee breakdown available')}

Powered by Sofi AI Wallet 🤖
"""
    print(crypto_message)
    
    # 4. AIRTIME PURCHASE NOTIFICATION
    print("4️⃣ AIRTIME PURCHASE NOTIFICATION")
    print("-" * 30)
    airtime_fees = fee_calculator.calculate_airtime_commission(1000, "MTN")
    
    airtime_message = f"""
📱 **AIRTIME PURCHASED!**

Hey John! 👋

{airtime_fees.get('user_message', 'Airtime processed')}

📊 **Transaction Details:**
• Network: {airtime_fees.get('provider', 'MTN')}
• Amount: ₦{airtime_fees.get('purchase_amount', 0):,.2f}
• Phone: 08012345678
• New Balance: ₦36,870.00

⏰ Time: {datetime.now().strftime("%I:%M %p, %B %d, %Y")}
✅ Status: Successful

Your airtime has been delivered instantly!

Powered by Sofi AI Wallet 🤖
"""
    print(airtime_message)
    
    # 5. DATA PURCHASE NOTIFICATION
    print("5️⃣ DATA PURCHASE NOTIFICATION")
    print("-" * 30)
    data_fees = fee_calculator.calculate_data_commission(2000, "GLO")
    
    data_message = f"""
📶 **DATA PURCHASED!**

Hey John! 👋

{data_fees.get('user_message', 'Data processed')}

📊 **Transaction Details:**
• Network: {data_fees.get('provider', 'GLO')}
• Plan: 3GB Monthly
• Amount: ₦{data_fees.get('purchase_amount', 0):,.2f}
• Phone: 08012345678
• New Balance: ₦34,870.00

⏰ Time: {datetime.now().strftime("%I:%M %p, %B %d, %Y")}
✅ Status: Successful
📅 Expires: {datetime.now().strftime("%B %d, %Y")} (30 days)

Your data has been activated immediately!

Powered by Sofi AI Wallet 🤖
"""
    print(data_message)
    
    # 6. FEE EXPLANATION (when user asks why charged)
    print("6️⃣ FEE EXPLANATION RESPONSE")
    print("-" * 30)
    
    fee_explanation = f"""
💡 **FEE BREAKDOWN EXPLANATION**

Hey John! 👋

You asked about the ₦50 deposit fee. Here's the breakdown:

📊 **Deposit Fee Structure:**
• Sofi Service Fee: ₦50.00
• Processing & Infrastructure: Covered by Sofi
• Security & Compliance: Covered by Sofi

💰 **Why We Charge This Fee:**
• Maintaining secure OPay virtual accounts
• 24/7 instant processing & notifications  
• Advanced fraud protection
• Customer support & dispute resolution
• Platform maintenance & improvements

🎯 **Good News:**
• All other fees are clearly disclosed upfront
• No hidden charges ever
• Full transparency in all transactions
• Admin can adjust fees based on market conditions

Questions? Just ask! I'm here to help 🤖

Powered by Sofi AI Wallet 🤖
"""
    print(fee_explanation)
    
    # 7. DAILY SUMMARY NOTIFICATION
    print("7️⃣ DAILY SUMMARY NOTIFICATION")
    print("-" * 30)
    
    daily_summary = f"""
📊 **DAILY ACCOUNT SUMMARY**

Hey John! 👋

Here's your Sofi Wallet activity for today:

💰 **Balance Summary:**
• Starting Balance: ₦20,000.00
• Total Deposits: ₦5,000.00
• Total Spending: ₦4,080.00
• Current Balance: ₦34,870.00

📈 **Transaction Summary:**
• 1 Deposit: ₦5,000.00 (Fee: ₦50.00)
• 1 Transfer: ₦1,000.00 (Fee: ₦30.00)  
• 1 Crypto: $10.00 USDT → ₦13,950.00
• 1 Airtime: ₦1,000.00 MTN
• 1 Data: ₦2,000.00 GLO 3GB

⚡ **Quick Stats:**
• Total Transactions: 5
• Total Fees Paid: ₦80.00
• Savings vs Banks: ₦120.00 💚

⏰ Summary for: {datetime.now().strftime("%B %d, %Y")}

Have a great day! 🌟

Powered by Sofi AI Wallet 🤖
"""
    print(daily_summary)

if __name__ == "__main__":
    generate_sample_responses()
    
    print()
    print("🎯 KEY FEATURES OF THESE NOTIFICATIONS:")
    print("✅ Clear, branded messaging with 'Hey John!' greeting")
    print("✅ Full transaction details and account balances")
    print("✅ Transparent fee explanations when requested")
    print("✅ Professional formatting with emojis for clarity")
    print("✅ Timestamp and status information")
    print("✅ 'Powered by Sofi AI Wallet' branding")
    print("✅ Helpful context and next steps")
    print()
    print("💡 All messages can be easily customized based on:")
    print("• User's actual name from database")
    print("• Real-time balance calculations")
    print("• Dynamic fee settings from admin")
    print("• Personalized transaction history")
