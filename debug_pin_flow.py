"""
Debug user data and PIN flow
"""
import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from functions.transfer_functions import send_money

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_user_status():
    """Check user status in database"""
    print("\n🔍 DEBUG: User Status Check")
    print("=" * 50)
    
    try:
        # Connect to Supabase
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Test chat ID
        chat_id = "1492735403"
        
        # Check user data
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        
        if user_result.data:
            user_data = user_result.data[0]
            print(f"✅ User found:")
            print(f"   ID: {user_data.get('id')}")
            print(f"   Name: {user_data.get('full_name')}")
            print(f"   Balance: ₦{user_data.get('wallet_balance', 0):,.2f}")
            print(f"   PIN set: {'Yes' if user_data.get('pin_hash') else 'No'}")
            print(f"   Chat ID: {user_data.get('telegram_chat_id')}")
            
            return user_data
        else:
            print("❌ User not found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None

async def debug_transfer_direct():
    """Test transfer function directly"""
    print("\n🔍 DEBUG: Direct Transfer Test")
    print("=" * 50)
    
    try:
        # Test parameters
        chat_id = "1492735403"
        
        # Call transfer function without PIN to trigger PIN entry
        result = await send_money(
            chat_id=chat_id,
            account_number="8104945538",
            bank_name="opay",
            amount=101.0,
            # No PIN provided - should trigger PIN entry
        )
        
        print(f"📝 Transfer result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Requires PIN: {result.get('requires_pin')}")
        print(f"   Show keyboard: {result.get('show_pin_keyboard')}")
        print(f"   Message: {result.get('message', 'No message')}")
        print(f"   Error: {result.get('error', 'No error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in transfer: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run debug tests"""
    print("🔍 DEBUGGING SOFI AI PIN FLOW")
    print("=" * 60)
    
    user_data = await debug_user_status()
    transfer_result = await debug_transfer_direct()
    
    print("\n📊 DEBUG SUMMARY")
    print("=" * 60)
    
    if user_data:
        print("✅ User exists in database")
        if user_data.get('wallet_balance', 0) >= 126:  # 101 + 25 fee
            print("✅ User has sufficient balance")
        else:
            print("❌ User has insufficient balance")
            
        if user_data.get('pin_hash'):
            print("✅ User has PIN set")
        else:
            print("❌ User has no PIN set")
    else:
        print("❌ User does not exist")
    
    if transfer_result:
        if transfer_result.get('requires_pin'):
            print("✅ Transfer correctly requires PIN")
        else:
            print("❌ Transfer does not require PIN")
            print(f"   Reason: {transfer_result.get('error', 'Unknown')}")
    else:
        print("❌ Transfer test failed")

if __name__ == "__main__":
    asyncio.run(main())
