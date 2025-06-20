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
            from crypto.wallet import create_bitnob_wallet, create_real_wallet, get_supabase_client
            from crypto.rates import get_multiple_crypto_rates
            
            # Check for crypto keywords
            crypto_keywords = ['wallet', 'bitcoin', 'btc', 'ethereum', 'eth', 'usdt', 'crypto', 'cryptocurrency']
            message_lower = message.lower()
            
            if not any(keyword in message_lower for keyword in crypto_keywords):
                return None  # Not a crypto request
            
            # Handle wallet creation requests
            if any(phrase in message_lower for phrase in ['create wallet', 'new wallet', 'generate wallet']):
                if 'btc' in message_lower or 'bitcoin' in message_lower:
                    result = create_bitnob_wallet(chat_id)
                    if result and not result.get('error'):
                        address = result.get('data', {}).get('address') or result.get('address')
                        if address:
                            return f"🔑 **Bitcoin Wallet Created!**\n\n" \
                                   f"📍 **Your BTC Address:**\n`{address}`\n\n" \
                                   f"✨ **Ready to receive Bitcoin!**\n" \
                                   f"Send BTC to this address and it will be instantly converted to NGN in your Sofi wallet.\n\n" \
                                   f"💡 Tap the address to copy it!"
                        else:
                            return f"❌ Failed to create Bitcoin wallet: No address returned"
                    else:
                        return f"❌ Failed to create Bitcoin wallet: {result.get('error', 'Unknown error')}"
                
                elif 'eth' in message_lower or 'ethereum' in message_lower:
                    # Placeholder: implement create_ethereum_wallet if available
                    return "❌ Ethereum wallet creation is not yet supported."
                
                elif 'usdt' in message_lower:
                    # Placeholder: implement create_usdt_wallet if available
                    return "❌ USDT wallet creation is not yet supported."
                
                else:
                    return ("🚀 **Create Your Crypto Wallet**\n\n"
                           "Which cryptocurrency wallet would you like to create?\n\n"
                           "🔸 **Bitcoin (BTC)** - Say 'create btc wallet'\n"
                           "🔸 **Ethereum (ETH)** - Say 'create eth wallet'\n"
                           "🔸 **USDT** - Say 'create usdt wallet'\n\n"
                           "💡 All crypto deposits are instantly converted to NGN!")
            
            # Handle wallet address requests
            elif any(phrase in message_lower for phrase in ['my wallet', 'wallet address', 'my address', 'show wallet']):
                # Placeholder: implement get_user_addresses if available
                return ("🔑 **No Crypto Wallets Found**\n\n"
                       "Create your first crypto wallet:\n\n"
                       "🔸 Say 'create btc wallet' for Bitcoin\n"
                       "🔸 Say 'create eth wallet' for Ethereum\n"
                       "🔸 Say 'create usdt wallet' for USDT\n\n"
                       "💡 All deposits are instantly converted to NGN!")
            
            # Handle crypto rates requests
            elif any(phrase in message_lower for phrase in ['crypto rates', 'bitcoin price', 'eth price', 'usdt price', 'rates']):
                rates = get_multiple_crypto_rates(["BTC", "ETH", "USDT"])
                if rates:
                    response = "💹 **Current Crypto Rates (NGN)**\n\n"
                    if rates.get('BTC'):
                        response += f"₿ **Bitcoin:** ₦{rates['BTC']:,.2f}\n"
                    if rates.get('ETH'):
                        response += f"⟠ **Ethereum:** ₦{rates['ETH']:,.2f}\n"
                    if rates.get('USDT'):
                        response += f"₮ **USDT:** ₦{rates['USDT']:,.2f}\n"
                    from datetime import datetime
                    response += f"\n🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    response += "\n💡 Send crypto to your Sofi wallet for instant conversion!"
                    return response
                else:
                    return "❌ Unable to fetch crypto rates right now. Please try again later."
            
            # Handle balance/transaction requests
            elif any(phrase in message_lower for phrase in ['crypto balance', 'crypto transactions', 'crypto history']):
                # Placeholder: implement get_user_transactions if available
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
