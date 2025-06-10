#!/usr/bin/env python3
"""
Simple test to verify Supabase RLS fix
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_service_role_key():
    """Check if we're using the service role key"""
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    anon_key = os.getenv("SUPABASE_KEY")
    
    print("🔍 Checking Supabase configuration:")
    print(f"   Service Role Key available: {'✅' if service_key else '❌'}")
    print(f"   Anon Key available: {'✅' if anon_key else '❌'}")
    
    if service_key:
        # Check if it's a service role key by examining the JWT payload
        import base64
        import json
        try:
            # JWT has 3 parts separated by dots
            parts = service_key.split('.')
            if len(parts) == 3:
                # Decode the payload (second part)
                payload = parts[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload).decode('utf-8')
                jwt_data = json.loads(decoded)
                role = jwt_data.get('role', 'unknown')
                print(f"   JWT Role: {role}")
                
                if role == 'service_role':
                    print("   ✅ Using SERVICE ROLE key (bypasses RLS)")
                    return True
                else:
                    print("   ⚠️ Using ANON key (subject to RLS)")
                    return False
        except Exception as e:
            print(f"   ❌ Error decoding JWT: {e}")
            return False
    
    print("   ⚠️ No service role key found, using anon key")
    return False

async def test_actual_supabase_insert():
    """Test actual Supabase insert operation"""
    from utils.memory import save_chat_message, get_chat_history
    
    test_chat_id = "rls_test_chat_123"
    test_message = "Testing RLS bypass with service role key"
    
    print("\n📝 Testing actual Supabase operations:")
    
    try:
        # Try to save a message
        print(f"   Attempting to save message to chat_id: {test_chat_id}")
        result = await save_chat_message(test_chat_id, "user", test_message)
        
        if result:
            print("   ✅ Message saved successfully!")
            
            # Try to retrieve the message
            print("   Retrieving saved messages...")
            history = await get_chat_history(test_chat_id, limit=1)
            
            if history and len(history) > 0:
                print(f"   ✅ Retrieved {len(history)} message(s)")
                print(f"   Last message: {history[-1]['content'][:50]}...")
                return True
            else:
                print("   ⚠️ No messages retrieved")
                return False
        else:
            print("   ❌ Failed to save message (likely RLS blocking)")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during Supabase operation: {e}")
        return False

def main():
    print("🧪 Supabase RLS Test\n")
    
    # Check configuration
    has_service_key = check_service_role_key()
    
    # Test actual operations
    success = asyncio.run(test_actual_supabase_insert())
    
    print("\n📊 Test Results:")
    if has_service_key and success:
        print("🎉 SUCCESS: Service role key is working and RLS is bypassed!")
    elif success:
        print("⚠️ PARTIAL: Operations work but may be using anon key")
    else:
        print("💥 FAILED: RLS is still blocking operations")
        print("\n🔧 Recommended actions:")
        print("1. Verify SUPABASE_SERVICE_ROLE_KEY is set correctly")
        print("2. Check Supabase RLS policies on chat_history table")
        print("3. Consider temporarily disabling RLS for testing")

if __name__ == "__main__":
    main()
