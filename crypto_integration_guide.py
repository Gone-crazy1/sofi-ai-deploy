#!/usr/bin/env python3
"""
🔧 CRYPTO RATE INTEGRATION FOR MAIN.PY
======================================

This shows exactly how to integrate the crypto rate management system
into your existing main.py file for seamless operation.

INTEGRATION POINTS:
1. Import crypto rate functions
2. Add crypto rate command handler
3. Integrate with crypto wallet display
4. Add crypto deposit webhook handler
"""

# ==========================================
# STEP 1: ADD IMPORTS TO MAIN.PY
# ==========================================

"""
Add these imports after your existing imports in main.py:
"""

# ADD TO MAIN.PY IMPORTS:
# from crypto_rate_manager import (
#     get_crypto_rates_message,
#     handle_crypto_deposit,
#     crypto_ui,
#     rate_manager
# )

# ==========================================
# STEP 2: MODIFY CRYPTO WALLET DISPLAY
# ==========================================

def integrate_crypto_rates_in_wallet_display():
    """
    Modify your existing crypto wallet display to show YOUR rates, not market rates
    """
    
    code_to_add = '''
async def get_crypto_wallet_info(user_id: str) -> str:
    """
    Enhanced crypto wallet display with YOUR rates (not market rates)
    """
    try:
        # Get your custom rates (not market rates)
        from crypto_rate_manager import get_crypto_rates_message
        
        wallet_message = "🚀 **Your Crypto Wallet**\\n\\n"
        
        # Add wallet addresses (your existing code)
        wallet_message += "📬 **Your Deposit Addresses:**\\n"
        wallet_message += f"🟠 **Bitcoin (BTC):**\\n"
        wallet_message += f"`{get_user_btc_address(user_id)}`\\n\\n"
        wallet_message += f"🟢 **USDT (TRC20):**\\n" 
        wallet_message += f"`{get_user_usdt_address(user_id)}`\\n\\n"
        
        # Add YOUR rates (not market rates)
        rate_info = await get_crypto_rates_message()
        wallet_message += rate_info
        
        wallet_message += "\\n\\n💡 **How it works:**\\n"
        wallet_message += "1. Send crypto to your addresses above\\n"
        wallet_message += "2. We'll detect and convert to Naira automatically\\n"
        wallet_message += "3. Your balance updates in 2-10 minutes\\n"
        wallet_message += "4. Use your Naira balance for transfers & bills\\n"
        
        return wallet_message
        
    except Exception as e:
        logger.error(f"Error getting crypto wallet info: {e}")
        return "❌ Error loading crypto wallet information"
    '''
    
    print("📍 CRYPTO WALLET INTEGRATION:")
    print("Location: Replace or enhance your existing crypto wallet display function")
    print(code_to_add)

# ==========================================
# STEP 3: ADD CRYPTO RATE COMMAND HANDLER
# ==========================================

def integrate_crypto_rate_commands():
    """
    Add command handlers for crypto rate requests
    """
    
    code_to_add = '''
async def handle_crypto_commands(chat_id: str, message: str, user_data: dict = None) -> str:
    """
    Handle crypto-related commands with custom rates
    """
    message_lower = message.lower().strip()
    
    # Rate checking commands
    if any(keyword in message_lower for keyword in ['crypto rate', 'crypto price', 'btc rate', 'usdt rate', 'exchange rate']):
        try:
            from crypto_rate_manager import get_crypto_rates_message
            return await get_crypto_rates_message()
        except Exception as e:
            return f"❌ Error fetching crypto rates: {e}"
    
    # Crypto wallet commands  
    elif any(keyword in message_lower for keyword in ['crypto wallet', 'deposit crypto', 'bitcoin address', 'usdt address']):
        try:
            return await get_crypto_wallet_info(str(chat_id))
        except Exception as e:
            return f"❌ Error loading crypto wallet: {e}"
    
    return None  # Not a crypto command
    '''
    
    print("📍 CRYPTO COMMAND INTEGRATION:")
    print("Location: Add this function to main.py")
    print(code_to_add)

# ==========================================
# STEP 4: INTEGRATE WITH GENERATE_AI_REPLY
# ==========================================

def integrate_with_ai_reply():
    """
    Integrate crypto rate commands with your AI reply system
    """
    
    code_to_add = '''
# ADD THIS TO YOUR generate_ai_reply() function BEFORE the OpenAI call:

async def generate_ai_reply(chat_id: int, user_message: str, user_data: dict = None) -> str:
    """Enhanced AI reply with crypto rate integration"""
    
    try:
        # ... existing code ...
        
        # Check for crypto commands BEFORE OpenAI call
        crypto_response = await handle_crypto_commands(str(chat_id), user_message, user_data)
        if crypto_response:
            return crypto_response
        
        # ... rest of your existing generate_ai_reply code ...
        
    except Exception as e:
        logger.error(f"Error in generate_ai_reply: {e}")
        return "Sorry, I encountered an error. Please try again."
    '''
    
    print("📍 AI REPLY INTEGRATION:")
    print("Location: Add to generate_ai_reply() function in main.py")
    print(code_to_add)

# ==========================================
# STEP 5: CRYPTO DEPOSIT WEBHOOK HANDLER
# ==========================================

def integrate_crypto_deposit_webhook():
    """
    Add webhook handler for when crypto deposits are received
    """
    
    code_to_add = '''
@app.route('/crypto_webhook', methods=['POST'])
async def handle_crypto_webhook():
    """
    Webhook to handle crypto deposit confirmations
    Call this when your crypto provider (Bitnob, etc.) confirms a deposit
    """
    try:
        data = request.get_json()
        
        # Extract deposit information
        user_id = data.get('user_id')  # or derive from wallet address
        crypto_type = data.get('crypto_type')  # 'BTC' or 'USDT'
        amount = float(data.get('amount', 0))
        transaction_hash = data.get('transaction_hash')
        
        if not all([user_id, crypto_type, amount]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Process the deposit with profit calculation
        from crypto_rate_manager import handle_crypto_deposit
        
        result_message = await handle_crypto_deposit(
            user_id=str(user_id),
            crypto_type=crypto_type.upper(),
            amount=amount,
            tx_hash=transaction_hash
        )
        
        # Send notification to user
        await send_reply(user_id, result_message)
        
        return jsonify({
            'success': True,
            'message': 'Crypto deposit processed successfully'
        })
        
    except Exception as e:
        logger.error(f"Crypto webhook error: {e}")
        return jsonify({'error': str(e)}), 500
    '''
    
    print("📍 CRYPTO WEBHOOK INTEGRATION:")
    print("Location: Add this route to main.py")
    print(code_to_add)

# ==========================================
# STEP 6: MARGIN CONFIGURATION
# ==========================================

def explain_margin_configuration():
    """
    Explain how to configure profit margins
    """
    
    print("📍 PROFIT MARGIN CONFIGURATION:")
    print("File: crypto_rate_manager.py")
    print("Location: CryptoRateConfig class")
    print()
    print("Current Settings:")
    print("• USDT Margin: 3% (₦46.50 profit per ₦1,550 market rate)")
    print("• BTC Margin: 4% (₦2M profit per ₦50M market rate)")
    print()
    print("To Change Margins:")
    print("1. Edit MARGINS in CryptoRateConfig class")
    print("2. Adjust MIN_PROFIT for minimum guaranteed profit")
    print("3. Modify CACHE_DURATION for rate refresh frequency")
    print()
    
    example_config = '''
# EXAMPLE: More aggressive margins
MARGINS = {
    'USDT': 0.05,  # 5% margin (₦77.50 profit per ₦1,550)
    'BTC': 0.06,   # 6% margin (₦3M profit per ₦50M)
}

# EXAMPLE: Conservative margins  
MARGINS = {
    'USDT': 0.02,  # 2% margin (₦31 profit per ₦1,550)
    'BTC': 0.025,  # 2.5% margin (₦1.25M profit per ₦50M)
}
    '''
    
    print("Configuration Examples:")
    print(example_config)

# ==========================================
# STEP 7: TESTING THE INTEGRATION
# ==========================================

def create_integration_test():
    """
    Create test script for the crypto rate integration
    """
    
    test_code = '''
#!/usr/bin/env python3
"""Test crypto rate integration"""

import asyncio
import sys
import os

async def test_crypto_integration():
    """Test all crypto rate functionality"""
    
    print("🧪 TESTING CRYPTO RATE INTEGRATION")
    print("=" * 50)
    
    try:
        # Test 1: Import check
        print("1️⃣ Testing imports...")
        from crypto_rate_manager import get_crypto_rates_message, handle_crypto_deposit
        print("   ✅ Crypto rate imports successful")
        
        # Test 2: Rate fetching
        print("\\n2️⃣ Testing rate fetching...")
        rate_message = await get_crypto_rates_message()
        if "Bitcoin" in rate_message and "USDT" in rate_message:
            print("   ✅ Rate fetching working")
            print(f"   Sample: {rate_message[:100]}...")
        else:
            print("   ❌ Rate fetching failed")
            return False
        
        # Test 3: Deposit simulation
        print("\\n3️⃣ Testing deposit processing...")
        deposit_result = await handle_crypto_deposit("test_user", "USDT", 10, "test_hash")
        if "Deposit Confirmed" in deposit_result:
            print("   ✅ Deposit processing working")
        else:
            print("   ❌ Deposit processing failed")
            return False
        
        # Test 4: Database integration
        print("\\n4️⃣ Testing database integration...")
        from crypto_rate_manager import rate_manager
        rates = await rate_manager.get_current_rates()
        if rates and 'your_rates' in rates:
            print("   ✅ Database integration working")
            usdt_info = rates['your_rates'].get('USDT', {})
            if usdt_info:
                print(f"   USDT: Market=₦{usdt_info.get('market_rate', 0):,.2f}, Your=₦{usdt_info.get('your_rate', 0):,.2f}")
        else:
            print("   ❌ Database integration failed")
            return False
        
        print("\\n🎉 ALL CRYPTO INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_crypto_integration())
    if success:
        print("\\n🚀 CRYPTO RATE SYSTEM READY FOR PRODUCTION!")
    else:
        print("\\n❌ Fix issues before deploying to production")
    '''
    
    with open("test_crypto_integration.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    print("📍 INTEGRATION TEST:")
    print("File created: test_crypto_integration.py")
    print("Run: python test_crypto_integration.py")

# ==========================================
# MAIN INTEGRATION GUIDE
# ==========================================

def main():
    """Complete integration guide for crypto rates"""
    
    print("🔧 CRYPTO RATE INTEGRATION GUIDE")
    print("=" * 60)
    print()
    
    print("🎯 WHAT THIS ACHIEVES:")
    print("• Fetches real CoinGecko rates (₦1,550 USDT)")
    print("• Applies your margin (3% = ₦46.50 profit)")
    print("• Shows users YOUR rate (₦1,503.50 USDT)")
    print("• Credits users at your rate")
    print("• Tracks profit automatically")
    print("• Records everything in Supabase")
    print()
    
    print("🏗️ INTEGRATION STEPS:")
    print("=" * 60)
    
    integrate_crypto_rates_in_wallet_display()
    print("\n" + "="*60 + "\n")
    
    integrate_crypto_rate_commands()
    print("\n" + "="*60 + "\n")
    
    integrate_with_ai_reply()
    print("\n" + "="*60 + "\n")
    
    integrate_crypto_deposit_webhook()
    print("\n" + "="*60 + "\n")
    
    explain_margin_configuration()
    print("\n" + "="*60 + "\n")
    
    create_integration_test()
    
    print("\n🎉 INTEGRATION COMPLETE!")
    print("=" * 60)
    print()
    print("💰 PROFIT EXAMPLE:")
    print("User deposits 100 USDT:")
    print("• CoinGecko rate: ₦1,550")
    print("• Your rate (3% margin): ₦1,503.50")
    print("• User gets: ₦150,350")
    print("• Your profit: ₦4,650")
    print("• Service fee: ₦800 (tracked separately)")
    print("• Total profit: ₦5,450")
    print()
    print("📊 TRACKING:")
    print("• Rate difference profit: Automatic")
    print("• Service fee: Logged to crypto_trades table")
    print("• Financial summary: Updated in real-time")
    print("• Historical rates: Saved for analysis")

if __name__ == "__main__":
    main()
