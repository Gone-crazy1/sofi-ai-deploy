"""
SOFI AI - INBOUND TRANSFER BRANDING & SENDER INFORMATION

This document explains what sender information is available when users RECEIVE money
to their Monnify virtual accounts, and how to use it for branding purposes.

🔍 AVAILABLE SENDER INFORMATION (from Monnify Webhooks):

When someone sends money TO your user's virtual account, Monnify webhook provides:
"""

# Sample Monnify webhook data for INBOUND transfers
sample_webhook_data = {
    "event_type": "virtual_account_credit",
    "data": {
        "reference": "TXN_20250617_001234",
        "amount": 5000.00,
        "currency": "NGN",
        "account_number": "8012345678",  # User's virtual account
        "account_name": "JOHN ADEYEMI/MONNIFY",
        
        # 🎯 SENDER INFORMATION (what you can show users)
        "sender_name": "ADEBAYO MICHAEL",      # ✅ Available
        "sender_account": "0123456789",        # ✅ Available  
        "sender_bank": "First Bank",           # ✅ Available
        "sender_bank_code": "011",             # ✅ Available
        "narration": "Payment for services",   # ✅ Available
        
        # Other metadata
        "transaction_date": "2025-06-17T08:30:00Z",
        "status": "successful",
        "channel": "bank_transfer"
    }
}

def create_branded_deposit_notification(webhook_data: dict, user_name: str) -> str:
    """
    Create branded deposit notification showing sender information
    
    This is what YOUR users will see when they receive money - you can brand it!
    """
    
    data = webhook_data.get("data", {})
    amount = data.get("amount", 0)
    sender_name = data.get("sender_name", "Unknown Sender")
    sender_bank = data.get("sender_bank", "Unknown Bank")
    sender_account = data.get("sender_account", "")
    narration = data.get("narration", "Transfer")
    
    # 🔥 YOUR BRANDED NOTIFICATION (full control!)
    branded_message = f"""
💰 **MONEY RECEIVED!**

Hey {user_name}! 👋

You just received ₦{amount:,.2f} in your Sofi Wallet!

📊 **Transfer Details:**
• From: {sender_name}
• Bank: {sender_bank}
• Account: {sender_account[-4:].rjust(len(sender_account), '*') if sender_account else 'N/A'}
• Purpose: {narration}
• Amount: ₦{amount:,.2f}
• Your New Balance: ₦{amount + 20000:,.2f} 

⏰ Received: {data.get('transaction_date', 'Just now')}
✅ Status: Confirmed & Secured

💡 **What happens next?**
• Money is instantly available in your wallet
• No fees charged for receiving money
• You can transfer, buy airtime, or withdraw anytime

🎯 **Quick Actions:**
• Type "balance" to check your wallet
• Type "transfer" to send money to others
• Type "airtime" to buy airtime/data

Thanks for using Sofi AI Wallet! 
Powered by Pip install -ai Tech 🚀
"""
    
    return branded_message

def create_sender_info_breakdown():
    """Show what sender information you can display"""
    
    print("🔍 SENDER INFORMATION AVAILABLE FOR BRANDING")
    print("=" * 60)
    print()
    
    # What Monnify provides vs what you can show
    available_data = {
        "✅ Sender Full Name": "ADEBAYO MICHAEL (exactly as registered)",
        "✅ Sender Bank": "First Bank, GTBank, Access Bank, etc.",
        "✅ Sender Account": "0123456789 (can mask for privacy)", 
        "✅ Transfer Purpose": "Payment for services, Salary, etc.",
        "✅ Amount & Currency": "₦5,000.00 NGN",
        "✅ Transaction Time": "2025-06-17 08:30:00",
        "✅ Reference Number": "TXN_20250617_001234",
        "✅ Channel": "Bank Transfer, USSD, etc."
    }
    
    for item, description in available_data.items():
        print(f"{item}: {description}")
    
    print()
    print("🎯 BRANDING OPPORTUNITIES:")
    print("• Welcome message with sender details")
    print("• Professional transaction summary") 
    print("• Your company branding throughout")
    print("• Suggested next actions for user")
    print("• Security assurances and confirmations")
    print()

def demo_different_notification_styles():
    """Show different ways to present sender information"""
    
    print("🎨 DIFFERENT NOTIFICATION STYLES")
    print("=" * 60)
    print()
    
    # Style 1: Professional/Corporate
    print("1️⃣ PROFESSIONAL STYLE:")
    print("-" * 30)
    professional = f"""
💼 TRANSFER NOTIFICATION

Dear John,

Your Sofi Wallet has been credited with ₦5,000.00

Transfer Information:
- Sender: ADEBAYO MICHAEL
- Bank: First Bank (011)
- Reference: TXN_20250617_001234
- Time: June 17, 2025 08:30 AM

Your current balance: ₦25,000.00

Best regards,
Sofi AI Team
Powered by Pip install -ai Tech
"""
    print(professional)
    
    # Style 2: Friendly/Casual  
    print("2️⃣ FRIENDLY STYLE:")
    print("-" * 30)
    friendly = f"""
🎉 Awesome news, John!

Someone just sent you money! 💰

Who: ADEBAYO MICHAEL (First Bank)
Amount: ₦5,000.00  
When: Just now!

Your wallet balance jumped to ₦25,000.00! 

Ready to do something cool with it? 
• Buy airtime for friends 📱
• Send money instantly 💸  
• Save for future goals 💎

Sofi AI - Making money moves easy!
By Pip install -ai Tech ✨
"""
    print(friendly)
    
    # Style 3: Detailed/Security-focused
    print("3️⃣ SECURITY-FOCUSED STYLE:")
    print("-" * 30)
    security = f"""
🔒 SECURE TRANSFER CONFIRMED

Hello John,

Transaction Security Report:
✅ Transfer verified and processed
✅ Sender identity confirmed
✅ Amount validated: ₦5,000.00

Sender Details:
• Name: ADEBAYO MICHAEL  
• Bank: First Bank
• Account: ****6789 (masked for security)
• Verification: Passed

Your funds are secured in your Sofi Wallet.
Balance: ₦25,000.00

Questions? Contact our support team.

Sofi AI Security Team
Pip install -ai Tech - Trusted Financial Solutions
"""
    print(security)

def key_benefits_of_showing_sender_info():
    """Explain why showing sender info is good for business"""
    
    print("💡 WHY SHOW SENDER INFORMATION?")
    print("=" * 60)
    print()
    
    benefits = [
        "🎯 Professional Appearance: Users see detailed, bank-level notifications",
        "🛡️ Security & Trust: Users know exactly who sent money (fraud prevention)", 
        "📋 Record Keeping: Users have complete transaction history",
        "🔍 Transparency: Full visibility builds confidence in your platform",
        "💼 Business Branding: Every notification reinforces your company name",
        "📱 User Experience: Rich, informative notifications vs basic alerts",
        "🤝 Relationship Building: Users associate quality service with your brand",
        "📊 Compliance: Detailed records help with financial regulations"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")
    
    print()
    print("🚀 BOTTOM LINE:")
    print("Even though Pip install -ai Tech didn't send the money,")
    print("you're providing the VALUE-ADDED SERVICE of:")
    print("• Professional notification delivery")
    print("• Enhanced security and transparency") 
    print("• Better user experience than basic bank SMS")
    print("• Your branded wallet ecosystem")
    print()

if __name__ == "__main__":
    print("💰 SOFI AI - INBOUND TRANSFER BRANDING DEMO")
    print("=" * 80)
    print()
    
    # Demo the branded notification
    sample_user = "John"
    notification = create_branded_deposit_notification({"data": sample_webhook_data["data"]}, sample_user)
    print("📱 SAMPLE BRANDED NOTIFICATION:")
    print("=" * 40)
    print(notification)
    
    # Show available sender data
    create_sender_info_breakdown()
    
    # Demo different styles
    demo_different_notification_styles()
    
    # Explain benefits
    key_benefits_of_showing_sender_info()
    
    print("🎉 CONCLUSION:")
    print("You have FULL CONTROL over how to present sender information!")
    print("Use it to build trust, provide transparency, and strengthen your brand!")
    print("Pip install -ai Tech gets credit for the superior notification experience! 🚀")
