"""
SOFI AI WALLET - BEAUTIFUL DEBIT RECEIPTS

This module creates colorful, professional debit receipts for:
- Money transfers (bank transfers)
- Airtime purchases 
- Data purchases
- Other debit transactions

All receipts include transaction details, fees, balances, and Pip install -ai Tech branding
"""

from datetime import datetime
from typing import Dict, Any
import random

class SofiReceiptGenerator:
    """Generate beautiful, colorful receipts for all debit transactions"""
    
    def __init__(self):
        self.company_name = "Pip install -ai Tech"
        self.app_name = "Sofi AI Wallet"
        
    def format_currency(self, amount: float) -> str:
        """Format currency with proper Nigerian formatting"""
        return f"₦{amount:,.2f}"
    
    def generate_transaction_id(self) -> str:
        """Generate a unique transaction ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = random.randint(1000, 9999)
        return f"SOFI{timestamp}{random_suffix}"
    
    def create_bank_transfer_receipt(self, transaction_data: Dict[str, Any]) -> str:
        """
        Create beautiful receipt for bank transfers
        
        Args:
            transaction_data: Dict containing transaction details
            
        Returns:
            str: Formatted receipt with colors and styling
        """
        
        # Extract transaction details
        user_name = transaction_data.get('user_name', 'Valued Customer')
        first_name = user_name.split()[0] if user_name else 'there'
        amount = transaction_data.get('amount', 0)
        recipient_name = transaction_data.get('recipient_name', 'Unknown')
        recipient_account = transaction_data.get('recipient_account', 'N/A')
        recipient_bank = transaction_data.get('recipient_bank', 'Unknown Bank')
        transfer_fee = transaction_data.get('transfer_fee', 30)
        total_deducted = amount + transfer_fee
        new_balance = transaction_data.get('new_balance', 0)
        reference = transaction_data.get('reference', self.generate_transaction_id())
        
        # Create beautiful receipt with colors
        receipt = f"""
🧾 *TRANSFER RECEIPT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 *Transfer Successful, {first_name}!*

💸 *TRANSACTION SUMMARY*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 💰 Amount Sent: {self.format_currency(amount)}
┃ 💳 Transfer Fee: {self.format_currency(transfer_fee)}
┃ ➖ Total Debited: {self.format_currency(total_deducted)}
┃ 💵 New Balance: {self.format_currency(new_balance)}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

👤 *RECIPIENT DETAILS*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📛 Name: {recipient_name}
┃ 🏦 Bank: {recipient_bank}
┃ 💳 Account: {recipient_account}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📋 *TRANSACTION DETAILS*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🆔 Reference: {reference}
┃ ⏰ Date & Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
┃ 📱 Channel: Sofi AI Wallet
┃ ✅ Status: Successful
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

💡 *FEE BREAKDOWN*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔧 Service Fee: ₦10.00
┃ ⚡ Processing Fee: ₦20.00
┃ 📊 Total Fees: {self.format_currency(transfer_fee)}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 *QUICK ACTIONS*
• Type "balance" to check wallet
• Type "transfer" for another transfer
• Type "history" for transaction history

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ *{self.app_name}*
🚀 *Powered by {self.company_name}*
📞 Support: Type "help" anytime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💚 *Thank you for choosing Sofi AI!*
        """
        
        return receipt.strip()
    
    def create_airtime_purchase_receipt(self, transaction_data: Dict[str, Any]) -> str:
        """
        Create beautiful receipt for airtime purchases
        
        Args:
            transaction_data: Dict containing transaction details
            
        Returns:
            str: Formatted receipt with colors and styling
        """
        
        # Extract transaction details
        user_name = transaction_data.get('user_name', 'Valued Customer')
        first_name = user_name.split()[0] if user_name else 'there'
        amount = transaction_data.get('amount', 0)
        phone_number = transaction_data.get('phone_number', 'N/A')
        network = transaction_data.get('network', 'MTN').upper()
        new_balance = transaction_data.get('new_balance', 0)
        reference = transaction_data.get('reference', self.generate_transaction_id())
        
        # Network-specific colors and emojis
        network_info = {
            'MTN': {'emoji': '🟡', 'color': 'Yellow'},
            'GLO': {'emoji': '🟢', 'color': 'Green'}, 
            'AIRTEL': {'emoji': '🔴', 'color': 'Red'},
            '9MOBILE': {'emoji': '🟢', 'color': 'Green'}
        }
        
        net_emoji = network_info.get(network, {}).get('emoji', '📱')
        net_color = network_info.get(network, {}).get('color', 'Blue')
        
        # Create beautiful airtime receipt
        receipt = f"""
🧾 *AIRTIME PURCHASE RECEIPT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 *Airtime Delivered, {first_name}!*

📱 *AIRTIME SUMMARY*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {net_emoji} Network: {network} ({net_color})
┃ 📞 Phone: {phone_number}
┃ 💰 Amount: {self.format_currency(amount)}
┃ 💵 New Balance: {self.format_currency(new_balance)}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📋 *TRANSACTION DETAILS*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🆔 Reference: {reference}
┃ ⏰ Date & Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
┃ 📱 Channel: Sofi AI Wallet
┃ ✅ Status: Successful & Delivered
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

⚡ *DELIVERY INFO*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🚀 Delivery: Instant
┃ 📶 Network Status: Active
┃ 💳 Payment Method: Sofi Wallet
┃ 🎯 Success Rate: 99.9%
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 *QUICK ACTIONS*
• Type "airtime" to buy more
• Type "data" to buy data bundles
• Type "balance" to check wallet

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ *{self.app_name}*
🚀 *Powered by {self.company_name}*
📞 Support: Type "help" anytime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *Your airtime is ready to use!*
        """
        
        return receipt.strip()
    
    def create_data_purchase_receipt(self, transaction_data: Dict[str, Any]) -> str:
        """
        Create beautiful receipt for data purchases
        
        Args:
            transaction_data: Dict containing transaction details
            
        Returns:
            str: Formatted receipt with colors and styling
        """
        
        # Extract transaction details
        user_name = transaction_data.get('user_name', 'Valued Customer')
        first_name = user_name.split()[0] if user_name else 'there'
        amount = transaction_data.get('amount', 0)
        phone_number = transaction_data.get('phone_number', 'N/A')
        network = transaction_data.get('network', 'MTN').upper()
        data_plan = transaction_data.get('data_plan', '1GB Monthly')
        validity = transaction_data.get('validity', '30 days')
        new_balance = transaction_data.get('new_balance', 0)
        reference = transaction_data.get('reference', self.generate_transaction_id())
        
        # Network-specific colors and emojis
        network_info = {
            'MTN': {'emoji': '🟡', 'color': 'Yellow', 'icon': '📶'},
            'GLO': {'emoji': '🟢', 'color': 'Green', 'icon': '🌐'}, 
            'AIRTEL': {'emoji': '🔴', 'color': 'Red', 'icon': '📡'},
            '9MOBILE': {'emoji': '🟢', 'color': 'Green', 'icon': '🛜'}
        }
        
        net_emoji = network_info.get(network, {}).get('emoji', '📱')
        net_color = network_info.get(network, {}).get('color', 'Blue')
        net_icon = network_info.get(network, {}).get('icon', '📶')
        
        # Create beautiful data receipt
        receipt = f"""
🧾 *DATA PURCHASE RECEIPT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 *Data Activated, {first_name}!*

📶 *DATA BUNDLE SUMMARY*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {net_emoji} Network: {network} ({net_color})
┃ {net_icon} Plan: {data_plan}
┃ 📞 Phone: {phone_number}
┃ 💰 Amount: {self.format_currency(amount)}
┃ 💵 New Balance: {self.format_currency(new_balance)}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📋 *SUBSCRIPTION DETAILS*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🆔 Reference: {reference}
┃ ⏰ Activated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
┃ 📅 Expires: {(datetime.now()).strftime('%B %d, %Y')} ({validity})
┃ ✅ Status: Active & Ready
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🌐 *DATA INFO*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🚀 Activation: Instant
┃ 📶 Coverage: Nationwide
┃ 💳 Payment Method: Sofi Wallet
┃ 🔄 Auto-Renewal: Disabled
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

💡 *DATA TIPS*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📱 Check balance: Dial *131#
┃ 🔍 Monitor usage regularly  
┃ 🛜 Use WiFi when available
┃ 📶 Best speeds on 4G/5G
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 *QUICK ACTIONS*
• Type "data" to buy more bundles
• Type "airtime" to buy airtime
• Type "balance" to check wallet

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ *{self.app_name}*
🚀 *Powered by {self.company_name}*
📞 Support: Type "help" anytime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 *Your data is active and ready!*
        """
        
        return receipt.strip()
    
    def create_crypto_purchase_receipt(self, transaction_data: Dict[str, Any]) -> str:
        """
        Create beautiful receipt for crypto purchases
        
        Args:
            transaction_data: Dict containing transaction details
            
        Returns:
            str: Formatted receipt with colors and styling
        """
        
        # Extract transaction details
        user_name = transaction_data.get('user_name', 'Valued Customer')
        first_name = user_name.split()[0] if user_name else 'there'
        naira_amount = transaction_data.get('naira_amount', 0)
        crypto_amount = transaction_data.get('crypto_amount', 0)
        crypto_type = transaction_data.get('crypto_type', 'USDT').upper()
        exchange_rate = transaction_data.get('exchange_rate', 1600)
        new_balance = transaction_data.get('new_balance', 0)
        reference = transaction_data.get('reference', self.generate_transaction_id())
        
        # Crypto-specific emojis
        crypto_info = {
            'USDT': {'emoji': '💰', 'name': 'Tether USD', 'icon': '🪙'},
            'BTC': {'emoji': '₿', 'name': 'Bitcoin', 'icon': '🟠'}, 
            'ETH': {'emoji': '♦️', 'name': 'Ethereum', 'icon': '🔷'}
        }
        
        crypto_emoji = crypto_info.get(crypto_type, {}).get('emoji', '💎')
        crypto_name = crypto_info.get(crypto_type, {}).get('name', crypto_type)
        crypto_icon = crypto_info.get(crypto_type, {}).get('icon', '💰')
        
        # Create beautiful crypto receipt
        receipt = f"""
🧾 *CRYPTO PURCHASE RECEIPT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 *Crypto Purchased, {first_name}!*

{crypto_emoji} *CRYPTO SUMMARY*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {crypto_icon} Crypto: {crypto_name} ({crypto_type})
┃ 💰 Amount: ${crypto_amount:,.4f} {crypto_type}
┃ 💳 Paid: {self.format_currency(naira_amount)}
┃ 📈 Rate: $1 = {self.format_currency(exchange_rate)}
┃ 💵 New Balance: {self.format_currency(new_balance)}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📋 *TRANSACTION DETAILS*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🆔 Reference: {reference}
┃ ⏰ Date & Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
┃ 📱 Channel: Sofi AI Wallet
┃ ✅ Status: Successful
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🔒 *SECURITY & STORAGE*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🛡️ Secure Storage: Guaranteed
┃ 🔐 Multi-sig Wallet: Protected
┃ 📊 Market Rate: Competitive
┃ 🌍 24/7 Trading: Available
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 *QUICK ACTIONS*
• Type "crypto" to buy/sell more
• Type "balance" to check portfolio
• Type "rates" for current prices

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ *{self.app_name}*
🚀 *Powered by {self.company_name}*
📞 Support: Type "help" anytime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{crypto_emoji} *Welcome to the crypto world!*
        """
        
        return receipt.strip()

# Global receipt generator instance
receipt_generator = SofiReceiptGenerator()

def demo_all_receipts():
    """Demo all types of beautiful receipts"""
    
    print("🧾 SOFI AI - BEAUTIFUL DEBIT RECEIPTS DEMO")
    print("=" * 80)
    print()
    
    # 1. Bank Transfer Receipt
    print("1️⃣ BANK TRANSFER RECEIPT")
    print("=" * 50)
    transfer_data = {
        'user_name': 'John Adeyemi',
        'amount': 15000,
        'recipient_name': 'MARY JOHNSON',
        'recipient_account': '0123456789',
        'recipient_bank': 'GTBank',
        'transfer_fee': 30,
        'new_balance': 45970,
        'reference': 'SOFI20250617125430001'
    }
    
    transfer_receipt = receipt_generator.create_bank_transfer_receipt(transfer_data)
    print(transfer_receipt)
    print("\n" + "="*80 + "\n")
    
    # 2. Airtime Purchase Receipt
    print("2️⃣ AIRTIME PURCHASE RECEIPT")
    print("=" * 50)
    airtime_data = {
        'user_name': 'Sarah Okafor',
        'amount': 1000,
        'phone_number': '08123456789',
        'network': 'MTN',
        'new_balance': 18500,
        'reference': 'SOFI20250617125431002'
    }
    
    airtime_receipt = receipt_generator.create_airtime_purchase_receipt(airtime_data)
    print(airtime_receipt)
    print("\n" + "="*80 + "\n")
    
    # 3. Data Purchase Receipt
    print("3️⃣ DATA PURCHASE RECEIPT")
    print("=" * 50)
    data_data = {
        'user_name': 'David Okoro',
        'amount': 2500,
        'phone_number': '08087654321',
        'network': 'GLO',
        'data_plan': '3GB Monthly',
        'validity': '30 days',
        'new_balance': 12300,
        'reference': 'SOFI20250617125432003'
    }
    
    data_receipt = receipt_generator.create_data_purchase_receipt(data_data)
    print(data_receipt)
    print("\n" + "="*80 + "\n")
    
    # 4. Crypto Purchase Receipt
    print("4️⃣ CRYPTO PURCHASE RECEIPT")
    print("=" * 50)
    crypto_data = {
        'user_name': 'Ahmed Ibrahim',
        'naira_amount': 32000,
        'crypto_amount': 20.0,
        'crypto_type': 'USDT',
        'exchange_rate': 1600,
        'new_balance': 8000,
        'reference': 'SOFI20250617125433004'
    }
    
    crypto_receipt = receipt_generator.create_crypto_purchase_receipt(crypto_data)
    print(crypto_receipt)
    print("\n" + "="*80 + "\n")
    
    print("🎨 KEY FEATURES OF THESE RECEIPTS:")
    print("✅ Colorful with emojis and visual elements")
    print("✅ Professional formatting with borders")
    print("✅ Complete transaction details")
    print("✅ Network-specific colors and icons")
    print("✅ Clear fee breakdowns")
    print("✅ Quick action suggestions")
    print("✅ Pip install -ai Tech branding")
    print("✅ User-friendly and engaging")
    print()
    print("🚀 These receipts will make your users feel like they're using")
    print("   a premium, professional financial service!")

if __name__ == "__main__":
    demo_all_receipts()
