"""
🤖 SOFI AI - NATURAL LANGUAGE INTERACTION GUIDE

This demonstrates how users can interact with Sofi AI using natural language
for ALL features - no need for bot commands or app redirects!

Sofi AI understands conversational Nigerian English, handles context,
and provides comprehensive assistant capabilities.
"""

import random
from datetime import datetime, timedelta

class SofiInteractionDemo:
    """Demonstrate natural language interactions with Sofi AI"""
    
    def __init__(self):
        self.user_name = "John"
        self.balance = 45750.00
        self.account_number = "8104567890"
        
    def show_greeting_interactions(self):
        """Show how Sofi handles greetings and introductions"""
        
        print("👋 GREETINGS & GETTING TO KNOW SOFI")
        print("=" * 60)
        print()
        
        interactions = [
            {
                "user": "Hi there! Who are you?",
                "sofi": f"""Hey {self.user_name}! 👋 

I'm Sofi AI, your friendly virtual financial assistant! I'm developed by the innovative team at Pip install -ai Tech, a company that specializes in cutting-edge AI financial solutions.

I'm here to help you with all your banking needs:
💰 Send & receive money instantly
📱 Buy airtime & data at great rates  
📊 Check balances & transaction history
💡 Get personalized financial advice
🎯 And much more!

What can I help you with today?"""
            },
            {
                "user": "Good morning Sofi! How are you doing?",
                "sofi": f"""Good morning {self.user_name}! 😊

I'm doing great, thank you for asking! I'm powered up and ready to help you tackle any financial tasks today. 

Your Sofi wallet is looking good with ₦{self.balance:,.2f} available. 

How can I make your day easier? Want to:
• Send money to someone?
• Buy airtime or data?
• Check your recent transactions?
• Or just chat about anything?"""
            }
        ]
        
        for interaction in interactions:
            print(f"👤 USER: {interaction['user']}")
            print(f"🤖 SOFI: {interaction['sofi']}")
            print("\n" + "-"*60 + "\n")
    
    def show_money_transfer_interactions(self):
        """Show natural language money transfer requests"""
        
        print("💸 MONEY TRANSFERS - NATURAL LANGUAGE")
        print("=" * 60)
        print()
        
        interactions = [
            {
                "user": "I want to send 10,000 naira to my sister Mary at GTBank account 0123456789",
                "sofi": f"""Got it {self.user_name}! Let me help you send ₦10,000 to Mary.

📋 **Transfer Summary:**
• Amount: ₦10,000.00
• Recipient: Mary (your sister)
• Bank: GTBank  
• Account: 0123456789
• Transfer Fee: ₦30.00
• Total to debit: ₦10,030.00

Your balance after: ₦{self.balance - 10030:,.2f}

Type "confirm" to proceed or "cancel" to stop. Need to change anything? Just tell me!"""
            },
            {
                "user": "Please transfer 5k to Access Bank 0987654321 for Michael",
                "sofi": f"""Sure thing! I'll help you send ₦5,000 to Michael.

📋 **Transfer Details:**
• Amount: ₦5,000.00  
• Recipient: Michael
• Bank: Access Bank
• Account: 0987654321
• Transfer Fee: ₦30.00
• Total charge: ₦5,030.00

Remaining balance: ₦{self.balance - 5030:,.2f}

Should I go ahead with this transfer? Reply "yes" to confirm!"""
            },
            {
                "user": "Send money to John Doe",
                "sofi": """I'd be happy to help you send money to John Doe! 

I just need a few more details:
• How much do you want to send?
• Which bank is John's account with?
• What's his account number?

You can tell me like: "Send 15,000 to John Doe at UBA account 1234567890" """
            },
            {
                "user": "Can you help me transfer money?",
                "sofi": """Absolutely! I can help you transfer money quickly and securely.

Just tell me:
💰 How much you want to send
👤 Who you're sending to (name)
🏦 Their bank name  
💳 Their account number

For example, you can say:
"Send 20,000 to Sarah at First Bank 0123456789"
or
"Transfer 50k to my brother at Zenith Bank"

What transfer would you like to make?"""
            }
        ]
        
        for interaction in interactions:
            print(f"👤 USER: {interaction['user']}")
            print(f"🤖 SOFI: {interaction['sofi']}")
            print("\n" + "-"*60 + "\n")
    
    def show_airtime_data_interactions(self):
        """Show natural language airtime and data requests"""
        
        print("📱 AIRTIME & DATA - NATURAL LANGUAGE")
        print("=" * 60)
        print()
        
        interactions = [
            {
                "user": "Buy me 1000 naira MTN airtime please",
                "sofi": f"""Perfect! I'll get you ₦1,000 MTN airtime right away.

📱 **Airtime Purchase:**
• Network: MTN
• Amount: ₦1,000.00
• Phone: Your registered number
• Cost: ₦1,000.00 (no extra fees!)

New balance: ₦{self.balance - 1000:,.2f}

Processing your airtime now... 

✅ **Done!** Your ₦1,000 MTN airtime has been delivered instantly! 
Check your phone balance by dialing *556#"""
            },
            {
                "user": "I need 2GB data for my Glo line",
                "sofi": f"""Got it! Let me get you 2GB data for your Glo number.

📶 **Data Purchase:**
• Network: Glo
• Plan: 2GB Monthly (30 days)
• Cost: ₦1,200.00
• Valid for: 30 days

New balance: ₦{self.balance - 1200:,.2f}

Shall I activate this for you? Reply "yes" to proceed!"""
            },
            {
                "user": "Can you recharge my phone?",
                "sofi": """Of course! I can help you recharge your phone with airtime or data.

What would you like:
📱 **Airtime** - for calls and SMS
📶 **Data** - for internet browsing

Just tell me:
• Which network? (MTN, Glo, Airtel, 9mobile)
• How much airtime or what data plan?
• Which phone number? (if different from registered)

Example: "Buy 500 airtime for MTN" or "Get me 1GB Airtel data"

What can I get for you?"""
            },
            {
                "user": "Get me airtime worth 500 naira for 08123456789 on MTN network",
                "sofi": f"""Perfect! I'll load ₦500 MTN airtime to 08123456789.

📱 **Airtime Details:**
• Network: MTN
• Amount: ₦500.00
• Phone: 08123456789
• Cost: ₦500.00

New balance: ₦{self.balance - 500:,.2f}

⚡ Processing... 

✅ **Success!** ₦500 MTN airtime sent to 08123456789!
The recipient can check balance with *556#"""
            }
        ]
        
        for interaction in interactions:
            print(f"👤 USER: {interaction['user']}")
            print(f"🤖 SOFI: {interaction['sofi']}")
            print("\n" + "-"*60 + "\n")
    
    def show_balance_transaction_interactions(self):
        """Show balance and transaction history requests"""
        
        print("💰 BALANCE & TRANSACTION HISTORY")
        print("=" * 60)
        print()
        
        # Generate sample transactions
        transactions = [
            {"date": "June 17, 2025", "type": "Credit", "description": "Transfer from MARY JOHN", "amount": "+₦10,000.00", "balance": "₦45,750.00"},
            {"date": "June 16, 2025", "type": "Debit", "description": "MTN Airtime Purchase", "amount": "-₦1,000.00", "balance": "₦35,750.00"},
            {"date": "June 16, 2025", "type": "Debit", "description": "Transfer to SARAH AHMED (GTBank)", "amount": "-₦5,000.00", "balance": "₦36,750.00"},
            {"date": "June 15, 2025", "type": "Credit", "description": "USDT Deposit ($15.00)", "amount": "+₦23,250.00", "balance": "₦41,750.00"},
            {"date": "June 15, 2025", "type": "Debit", "description": "GLO 3GB Data Bundle", "amount": "-₦1,500.00", "balance": "₦18,500.00"}
        ]
        
        interactions = [
            {
                "user": "What's my balance?",
                "sofi": f"""Hi {self.user_name}! Here's your current wallet status:

💰 **Current Balance: ₦{self.balance:,.2f}**

📊 **Account Details:**
• Account Number: {self.account_number}
• Account Type: Sofi Virtual Account
• Daily Limit: ₦200,000 available
• Status: Active & Verified ✅

Need anything else? I can help you:
• Send money to someone
• Buy airtime or data  
• Check transaction history
• Or anything else you need!"""
            },
            {
                "user": "Show me my transaction history",
                "sofi": f"""Here's your recent transaction history, {self.user_name}:

📋 **Recent Transactions:**
```
{transactions[0]['date']} | {transactions[0]['type']}
{transactions[0]['description']}
{transactions[0]['amount']} | Bal: {transactions[0]['balance']}

{transactions[1]['date']} | {transactions[1]['type']} 
{transactions[1]['description']}
{transactions[1]['amount']} | Bal: {transactions[1]['balance']}

{transactions[2]['date']} | {transactions[2]['type']}
{transactions[2]['description']} 
{transactions[2]['amount']} | Bal: {transactions[2]['balance']}

{transactions[3]['date']} | {transactions[3]['type']}
{transactions[3]['description']}
{transactions[3]['amount']} | Bal: {transactions[3]['balance']}

{transactions[4]['date']} | {transactions[4]['type']}
{transactions[4]['description']}
{transactions[4]['amount']} | Bal: {transactions[4]['balance']}
```

Need details about any specific transaction? Just ask!"""
            },
            {
                "user": "How much money do I have?",
                "sofi": f"""You currently have **₦{self.balance:,.2f}** in your Sofi wallet! 💰

That's enough for:
• 45 x ₦1,000 airtime purchases 📱
• 30 x ₦1,500 data bundles 📶  
• 15 x ₦3,000 bank transfers 💸
• Or save it for bigger goals! 💎

What would you like to do with your money today?"""
            },
            {
                "user": "Check my account details",
                "sofi": f"""Here are your complete account details, {self.user_name}:

👤 **Profile Information:**
• Name: {self.user_name} Adeyemi
• Phone: 08123456789
• Account Status: Verified ✅

💳 **Account Details:**
• Account Number: {self.account_number}
• Bank Name: Sofi AI (Powered by OPay)
• Account Type: Virtual Account
• Current Balance: ₦{self.balance:,.2f}

⚡ **Limits & Features:**
• Daily Transfer Limit: ₦200,000
• Monthly Limit: ₦2,000,000
• Instant transfers: ✅ Active
• Crypto trading: ✅ Available
• Bill payments: 🔄 Coming soon

Need to update any information or have questions?"""
            }
        ]
        
        for interaction in interactions:
            print(f"👤 USER: {interaction['user']}")
            print(f"🤖 SOFI: {interaction['sofi']}")
            print("\n" + "-"*60 + "\n")
    
    def show_general_assistant_interactions(self):
        """Show Sofi as a general assistant beyond banking"""
        
        print("🎯 GENERAL ASSISTANT CAPABILITIES")
        print("=" * 60)
        print()
        
        interactions = [
            {
                "user": "Can you help me plan my budget for this month?",
                "sofi": f"""Absolutely! I'd love to help you create a smart budget plan.

Based on your current balance of ₦{self.balance:,.2f}, let's work together:

💡 **Tell me about:**
• Your monthly income
• Fixed expenses (rent, bills, food)
• Savings goals
• How much you typically spend on transfers/airtime

💰 **Smart Budgeting Tips:**
• Save 20% of income first
• Allocate 50% for needs, 30% for wants
• Use Sofi for fee-free transfers to save money
• Set up automatic savings (coming soon!)

What's your monthly income, and what are your main expenses? I'll create a personalized budget for you!"""
            },
            {
                "user": "What's the best way to save money in Nigeria?",
                "sofi": f"""Great question! Here are proven money-saving strategies for Nigeria:

💰 **Smart Saving Tips:**

1. **Pay Yourself First**
   • Save 20% before any spending
   • Use Sofi for instant transfers to savings

2. **Cut Banking Fees**  
   • Use Sofi for free transfers (save ₦50+ per transfer)
   • Buy airtime through Sofi (no extra charges)

3. **Investment Options**
   • Government bonds (low risk, 10-15% returns)
   • Treasury bills (safe, liquid)
   • Dollar savings (hedge against inflation)

4. **Daily Habits**
   • Cook more, eat out less
   • Use public transport when possible
   • Buy airtime in bulk for discounts

💡 **Sofi Advantage:**
With your ₦{self.balance:,.2f}, you're already ahead! Want me to help you set specific savings goals?"""
            },
            {
                "user": "Tell me about cryptocurrency",
                "sofi": f"""I'd love to explain crypto! It's actually one of my specialties 😊

💰 **Cryptocurrency Basics:**

**What is Crypto?**
Digital money that exists online, secured by advanced encryption. Think of it as internet money that no single government controls.

**Popular Types:**
• Bitcoin (BTC) - Digital gold, store of value
• USDT - Stable coin pegged to US Dollar  
• Ethereum (ETH) - Smart contract platform

**Why Nigerians Love Crypto:**
• Hedge against Naira devaluation
• Send/receive international payments easily
• Investment opportunity (but risky!)
• Financial freedom from traditional banks

💡 **Sofi Crypto Features:**
• Buy/sell USDT, BTC, ETH instantly
• Competitive rates: $1 = ₦1,550-₦1,600
• Secure storage in your wallet
• Convert to Naira anytime

**Want to start?** I can help you buy your first crypto with your ₦{self.balance:,.2f} balance!"""
            },
            {
                "user": "What's the weather like today?",
                "sofi": f"""Hey {self.user_name}! While I don't have real-time weather data, I'm primarily focused on being your financial assistant! 😊

But I can still chat about anything you'd like! Here's what I can help with:

🤖 **My Strengths:**
• All banking and financial tasks
• Money management advice
• Crypto and investment guidance  
• Nigerian fintech insights
• General conversation and support

🌤️ **For weather updates, I'd suggest:**
• Checking your phone's weather app
• Asking Google Assistant or Siri
• Checking weather.com or local news

Is there anything financial I can help you with today? Or want to just chat about life, business, or your goals? I'm here for you!"""
            },
            {
                "user": "I'm feeling stressed about money",
                "sofi": f"""I hear you, {self.user_name}, and I understand. Money stress is real and you're not alone in feeling this way. 💙

**Let's tackle this together:**

💪 **Immediate Relief:**
• You have ₦{self.balance:,.2f} - that's something to build on
• We can create a plan to make it grow
• Small steps lead to big changes

🎯 **Actionable Steps:**
1. **Track your spending** - I can help monitor transactions
2. **Set small savings goals** - even ₦500/day adds up
3. **Find extra income** - selling, freelancing, side hustles
4. **Cut unnecessary costs** - use Sofi to avoid bank fees

💡 **You've Got This Because:**
• You're already using smart financial tools
• You're thinking about your money (that's 50% of success!)
• Every financial expert started where you are

Want to talk about what's specifically stressing you? I can help create a plan to improve your situation step by step."""
            }
        ]
        
        for interaction in interactions:
            print(f"👤 USER: {interaction['user']}")
            print(f"🤖 SOFI: {interaction['sofi']}")
            print("\n" + "-"*60 + "\n")
    
    def show_advanced_natural_language(self):
        """Show advanced conversational abilities"""
        
        print("🧠 ADVANCED NATURAL LANGUAGE UNDERSTANDING")
        print("=" * 60)
        print()
        
        interactions = [
            {
                "user": "Abeg help me send 20k to my guy for business",
                "sofi": f"""No wahala! I go help you send that 20k to your guy for business.

I just need small details:
• Wetin be your guy name?
• Which bank him dey use?
• Wetin be him account number?

Once you give me these details, I go process the transfer sharp sharp! 

You fit talk like: "Send 20k to Emeka at UBA 1234567890" """
            },
            {
                "user": "My phone credit don finish, I need recharge",
                "sofi": f"""I understand! Your airtime done finish. Let me help you recharge am quick.

💡 **Tell me:**
• How much you wan buy? (e.g. 500, 1000, 2000)
• Na which network? (MTN, Glo, Airtel, 9mobile)
• Na for which number? (if different from your registered number)

You fit just talk say "Buy me 1000 MTN airtime" and I go do am instantly! 

Your balance na ₦{self.balance:,.2f}, so you get enough money for recharge."""
            },
            {
                "user": "I mistakenly sent money to wrong account yesterday, can you help me reverse it?",
                "sofi": f"""Oh no! I understand how stressful that must be, {self.user_name}. Let me help you with this situation.

🚨 **Quick Action Steps:**

1. **Check your transaction history** - Let me pull up yesterday's transfers
2. **Contact recipient's bank** - If the account exists, they can help
3. **File a complaint** - I can guide you through the process

📋 **I need these details:**
• Exact amount you sent
• Recipient account number you sent to  
• Which bank it was
• Time you sent it
• What the correct details should have been

💡 **Good News:**
• If account doesn't exist, money usually returns automatically
• If account exists, bank can help contact the owner
• Most people are honest and will return mistaken transfers

Let me check your yesterday's transactions first. Can you tell me the amount you sent by mistake?"""
            },
            {
                "user": "Business has been slow, I need to make some extra money. Any ideas?",
                "sofi": f"""I feel you, {self.user_name}! Business can be tough, but there are many ways to generate extra income. Let me share some practical ideas:

💰 **Quick Income Ideas:**

**Using Your Skills:**
• Freelance writing, graphic design, or social media management
• Tutoring (online or offline)
• Photography for events
• Hairdressing, makeup, or tailoring

**Small Business Ideas:**
• Food delivery (especially weekend specials)
• Phone accessories/data sales  
• Recharge card business (I can help with bulk purchases!)
• Online thrift store

**Digital Opportunities:**
• Affiliate marketing
• YouTube content creation
• Online courses teaching your expertise
• Virtual assistant services

💡 **Sofi Can Help:**
• No-fee transfers for your business payments
• Bulk airtime purchases for resale
• Track business income/expenses
• Crypto trading for investment

**With your ₦{self.balance:,.2f}, you could:**
• Start a recharge card business
• Buy items to resell online
• Invest in small crypto amounts

What type of work interests you most? I can give specific advice!"""
            }
        ]
        
        for interaction in interactions:
            print(f"👤 USER: {interaction['user']}")
            print(f"🤖 SOFI: {interaction['sofi']}")
            print("\n" + "-"*60 + "\n")

def demonstrate_sofi_interactions():
    """Run complete demonstration of Sofi's natural language abilities"""
    
    print("🤖 SOFI AI - NATURAL LANGUAGE INTERACTION DEMO")
    print("🚀 Powered by Pip install -ai Tech")
    print("=" * 80)
    print()
    
    print("💡 **KEY FEATURES:**")
    print("✅ Understands natural conversational language")
    print("✅ No bot commands required - just talk normally!")
    print("✅ Handles context across conversations")
    print("✅ Supports Nigerian English and Pidgin")
    print("✅ Works as both financial assistant AND general chat companion")
    print("✅ Provides personalized advice and support")
    print("✅ Never redirects to app - everything happens in chat!")
    print()
    
    demo = SofiInteractionDemo()
    
    # Show all interaction categories
    demo.show_greeting_interactions()
    demo.show_money_transfer_interactions()
    demo.show_airtime_data_interactions()
    demo.show_balance_transaction_interactions()
    demo.show_general_assistant_interactions()
    demo.show_advanced_natural_language()
    
    print("🎯 **WHAT MAKES SOFI SPECIAL:**")
    print("=" * 60)
    print()
    
    features = [
        "🗣️ **Natural Language**: Users talk normally, no commands needed",
        "🧠 **Context Awareness**: Remembers conversation history",
        "🇳🇬 **Nigerian-First**: Understands local expressions and needs",
        "💰 **Full Banking**: Complete financial services in chat",
        "🤖 **AI Assistant**: Beyond banking - life advice, planning, support",
        "📱 **Multi-Modal**: Handles text, voice, and images",
        "🚀 **No App Required**: Everything happens in Telegram",
        "💬 **Conversational**: Feels like chatting with a smart friend",
        "🔒 **Secure**: Bank-level security with friendly interface",
        "📈 **Learning**: Gets smarter with each interaction"
    ]
    
    for feature in features:
        print(f"  {feature}")
    print()
    
    print("🏆 **COMPETITIVE ADVANTAGE:**")
    print("=" * 60)
    print()
    
    comparison = """
    🏦 **TRADITIONAL BANKS:**           🤖 **SOFI AI:**
    "Press 1 for transfers"       →    "Send 5k to my sister Mary"
    "Invalid USSD code"           →    "I understand! Let me help you"
    "Visit branch for support"    →    "I'm here 24/7 to chat and help"
    "Use our app"                 →    "Everything works right here in chat"
    "Transaction successful"      →    "Done! Here's your beautiful receipt 🧾"
    """
    
    print(comparison)
    print()
    
    print("🎉 **CONCLUSION:**")
    print("Sofi AI isn't just a chatbot - it's a comprehensive financial companion")
    print("that understands natural language, provides emotional support, gives")
    print("financial advice, and handles all banking needs conversationally!")
    print()
    print("🚀 **Ready to revolutionize how Nigerians bank!**")

if __name__ == "__main__":
    demonstrate_sofi_interactions()
