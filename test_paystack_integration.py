"""
Test Paystack Virtual Account Creation
=====================================
Quick test to verify Paystack account creation works before WhatsApp integration
"""

import asyncio
import logging
from utils.paystack_account_manager import paystack_account_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_paystack_account_creation():
    """Test creating a Paystack virtual account"""
    
    print("🧪 Testing Paystack Virtual Account Creation")
    print("=" * 50)
    
    # Test data
    test_data = {
        'whatsapp_number': '+2348056487759',
        'full_name': 'Test User Sofi',
        'email': 'test@sofibank.com',
        'phone': '08056487759'
    }
    
    try:
        print(f"📱 Creating account for: {test_data['whatsapp_number']}")
        print(f"👤 Name: {test_data['full_name']}")
        
        # Create account
        result = await paystack_account_manager.create_whatsapp_account(test_data)
        
        if result['success']:
            print("\n✅ Account Creation Successful!")
            print(f"📧 Email: {result['user']['email']}")
            print(f"🏦 Account Number: {result['account']['account_number']}")
            print(f"🏪 Bank: {result['account']['bank_name']}")
            print(f"💰 Balance: ₦{result['account']['balance']:,.2f}")
            
            # Test getting account details
            print("\n🔍 Testing account retrieval...")
            account_details = await paystack_account_manager.get_virtual_account(test_data['whatsapp_number'])
            
            if account_details:
                print("✅ Account retrieval successful!")
                print(f"Account: {account_details['account_number']}")
                print(f"Balance: ₦{account_details['balance']:,.2f}")
            else:
                print("❌ Failed to retrieve account details")
            
            # Format message for WhatsApp
            print("\n📱 WhatsApp Message Format:")
            formatted_message = paystack_account_manager.format_account_message(result)
            print(formatted_message)
            
        else:
            print(f"\n❌ Account Creation Failed!")
            print(f"Error: {result['error']}")
            
            # Check if it's a duplicate account issue
            if 'already exists' in result['error']:
                print("\n🔍 Checking existing account...")
                existing = await paystack_account_manager.get_user_by_whatsapp(test_data['whatsapp_number'])
                if existing:
                    print(f"✅ Found existing account for {existing['full_name']}")
                    print(f"Account: {existing['account_number']}")
                    print(f"Bank: {existing['bank_name']}")
        
    except Exception as e:
        print(f"\n💥 Test Failed with Exception!")
        print(f"Error: {e}")
        logger.error(f"Test error: {e}")

async def test_whatsapp_integration():
    """Test the WhatsApp GPT integration with account creation"""
    
    print("\n\n🤖 Testing WhatsApp GPT Integration")
    print("=" * 50)
    
    from utils.whatsapp_gpt_integration import sofi_whatsapp_gpt
    
    test_phone = "+2348056487759"
    
    test_messages = [
        "Hello",
        "I want to create an account",
        "My name is John Doe",
        "create account please", 
        "signup",
        "what's my balance?"
    ]
    
    for message in test_messages:
        print(f"\n📱 User: {message}")
        try:
            response, button_data = await sofi_whatsapp_gpt.process_whatsapp_message(test_phone, message)
            print(f"🤖 Sofi: {response}")
            
            if button_data:
                print(f"🔘 Button: {button_data['title']} -> {button_data['url']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    print("🚀 Starting Paystack & WhatsApp Integration Tests")
    print("This will test the new account creation system")
    print()
    
    asyncio.run(test_paystack_account_creation())
    asyncio.run(test_whatsapp_integration())
    
    print("\n🎉 Tests completed!")
    print("If successful, your WhatsApp users can now create accounts directly via chat!")
