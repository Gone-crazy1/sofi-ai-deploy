"""
Crypto Command Handler for Sofi AI
Handles cryptocurrency wallet and transaction commands
"""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class CryptoCommandHandler:
    """Handle crypto wallet and transaction commands"""
    
    def __init__(self):
        self.logger = logger
        
    async def handle_crypto_request(self, chat_id: str, message: str, user_data: dict) -> Optional[str]:
        """Process crypto wallet and transaction requests"""
        try:
            # Import the existing crypto modules
            from crypto.wallet import CryptoWallet
            from crypto.rates import CryptoRates
            
            # Check for crypto keywords
            crypto_keywords = ['wallet', 'bitcoin', 'btc', 'ethereum', 'eth', 'usdt', 'crypto', 'cryptocurrency']
            message_lower = message.lower()
            
            if not any(keyword in message_lower for keyword in crypto_keywords):
                return None  # Not a crypto request
            
            # Initialize crypto wallet
            crypto_wallet = CryptoWallet()
            
            # Handle wallet creation requests
            if any(phrase in message_lower for phrase in ['create wallet', 'new wallet', 'generate wallet']):
                if 'btc' in message_lower or 'bitcoin' in message_lower:
                    result = await crypto_wallet.create_bitcoin_wallet(chat_id)
                    if result.get('success'):
                        return f"🔑 **Bitcoin Wallet Created!**\n\n" \
                               f"📍 **Your BTC Address:**\n`{result['address']}`\n\n" \
                               f"✨ **Ready to receive Bitcoin!**\n" \
                               f"Send BTC to this address and it will be instantly converted to NGN in your Sofi wallet.\n\n" \
                               f"💡 Tap the address to copy it!"
                    else:
                        return f"❌ Failed to create Bitcoin wallet: {result.get('error', 'Unknown error')}"
                
                elif 'eth' in message_lower or 'ethereum' in message_lower:
                    result = await crypto_wallet.create_ethereum_wallet(chat_id)
                    if result.get('success'):
                        return f"🔑 **Ethereum Wallet Created!**\n\n" \
                               f"📍 **Your ETH Address:**\n`{result['address']}`\n\n" \
                               f"✨ **Ready to receive Ethereum!**\n" \
                               f"Send ETH to this address and it will be instantly converted to NGN in your Sofi wallet.\n\n" \
                               f"💡 Tap the address to copy it!"
                    else:
                        return f"❌ Failed to create Ethereum wallet: {result.get('error', 'Unknown error')}"
                
                elif 'usdt' in message_lower:
                    result = await crypto_wallet.create_usdt_wallet(chat_id)
                    if result.get('success'):
                        return f"🔑 **USDT Wallet Created!**\n\n" \
                               f"📍 **Your USDT Address:**\n`{result['address']}`\n\n" \
                               f"✨ **Ready to receive USDT!**\n" \
                               f"Send USDT to this address and it will be instantly converted to NGN in your Sofi wallet.\n\n" \
                               f"💡 Tap the address to copy it!"
                    else:
                        return f"❌ Failed to create USDT wallet: {result.get('error', 'Unknown error')}"
                
                else:
                    return ("🚀 **Create Your Crypto Wallet**\n\n"
                           "Which cryptocurrency wallet would you like to create?\n\n"
                           "🔸 **Bitcoin (BTC)** - Say 'create btc wallet'\n"
                           "🔸 **Ethereum (ETH)** - Say 'create eth wallet'\n"
                           "🔸 **USDT** - Say 'create usdt wallet'\n\n"
                           "💡 All crypto deposits are instantly converted to NGN!")
            
            # Handle wallet address requests
            elif any(phrase in message_lower for phrase in ['my wallet', 'wallet address', 'my address', 'show wallet']):
                addresses = await crypto_wallet.get_user_addresses(chat_id)
                
                if addresses:
                    response = "🔑 **Your Crypto Wallets**\n\n"
                    
                    if addresses.get('btc'):
                        response += f"₿ **Bitcoin:**\n`{addresses['btc']}`\n\n"
                    
                    if addresses.get('eth'):
                        response += f"⟠ **Ethereum:**\n`{addresses['eth']}`\n\n"
                    
                    if addresses.get('usdt'):
                        response += f"₮ **USDT:**\n`{addresses['usdt']}`\n\n"
                    
                    response += "💡 Tap any address to copy it!\n\n"
                    response += "🚀 Send crypto to these addresses for instant NGN conversion!"
                    
                    return response
                else:
                    return ("🔑 **No Crypto Wallets Found**\n\n"
                           "Create your first crypto wallet:\n\n"
                           "🔸 Say 'create btc wallet' for Bitcoin\n"
                           "🔸 Say 'create eth wallet' for Ethereum\n"
                           "🔸 Say 'create usdt wallet' for USDT\n\n"
                           "💡 All deposits are instantly converted to NGN!")
            
            # Handle crypto rates requests
            elif any(phrase in message_lower for phrase in ['crypto rates', 'bitcoin price', 'eth price', 'usdt price', 'rates']):
                crypto_rates = CryptoRates()
                rates = await crypto_rates.get_current_rates()
                
                if rates:
                    response = "💹 **Current Crypto Rates (NGN)**\n\n"
                    
                    if rates.get('btc'):
                        response += f"₿ **Bitcoin:** ₦{rates['btc']:,.2f}\n"
                    
                    if rates.get('eth'):
                        response += f"⟠ **Ethereum:** ₦{rates['eth']:,.2f}\n"
                    
                    if rates.get('usdt'):
                        response += f"₮ **USDT:** ₦{rates['usdt']:,.2f}\n"
                    
                    response += f"\n🕐 **Updated:** {rates.get('timestamp', 'Now')}\n"
                    response += "\n💡 Send crypto to your Sofi wallet for instant conversion!"
                    
                    return response
                else:
                    return "❌ Unable to fetch crypto rates right now. Please try again later."
            
            # Handle balance/transaction requests
            elif any(phrase in message_lower for phrase in ['crypto balance', 'crypto transactions', 'crypto history']):
                transactions = await crypto_wallet.get_user_transactions(chat_id)
                
                if transactions:
                    response = "💰 **Your Crypto Transactions**\n\n"
                    
                    for tx in transactions[:5]:  # Show last 5 transactions
                        response += f"📅 {tx.get('date', 'Unknown')}\n"
                        response += f"💎 {tx.get('amount', 0)} {tx.get('currency', 'CRYPTO')}\n"
                        response += f"💵 ₦{tx.get('ngn_amount', 0):,.2f}\n"
                        response += f"📝 {tx.get('status', 'Unknown')}\n\n"
                    
                    return response
                else:
                    return ("💰 **No Crypto Transactions**\n\n"
                           "Start by creating a crypto wallet:\n"
                           "🔸 Say 'create wallet' to get started\n\n"
                           "💡 All crypto deposits are instantly converted to NGN!")
            
            # General crypto help
            else:
                return ("🚀 **Sofi Crypto Services**\n\n"
                       "**Available Commands:**\n"
                       "🔸 'Create wallet' - Create crypto wallets\n"
                       "🔸 'My wallets' - View your addresses\n"
                       "🔸 'Crypto rates' - Current prices\n"
                       "🔸 'Crypto balance' - Transaction history\n\n"
                       "**Supported Cryptocurrencies:**\n"
                       "₿ Bitcoin (BTC)\n"
                       "⟠ Ethereum (ETH)\n"
                       "₮ USDT\n\n"
                       "💡 All crypto deposits are instantly converted to NGN!")
            
        except Exception as e:
            self.logger.error(f"Error in crypto handler: {e}")
            return "Sorry, I'm having trouble with crypto services right now. Please try again later."
