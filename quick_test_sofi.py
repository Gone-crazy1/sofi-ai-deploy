"""
Quick Sofi AI Functionality Test
Tests core functionality before deployment
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_sofi_response():
    """Test basic Sofi AI response functionality"""
    try:
        # Import the Sharp AI handler
        from utils.sharp_sofi_ai import handle_smart_message
        
        # Test basic greeting
        test_chat_id = "test_user_123"
        test_message = "Hello Sofi"
        
        print("🧠 Testing Sharp AI Response...")
        response = await handle_smart_message(test_chat_id, test_message)
        
        if response and isinstance(response, str):
            print("✅ Sofi AI is responding correctly!")
            print(f"📝 Response: {response[:200]}...")
            return True
        else:
            print("❌ Sofi AI response failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Sofi response: {str(e)}")
        
        # Check if it's a database issue
        if "does not exist" in str(e):
            print("\n🔧 Database tables missing - need to run SQL deployment")
            print("💡 Execute the Sharp AI SQL script in Supabase first")
        
        return False

def check_environment():
    """Check if required environment variables exist"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'OPENAI_API_KEY']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("✅ Environment variables configured")
        return True

async def main():
    print("🚀 Quick Sofi AI Deployment Test")
    print("=" * 40)
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("🔧 Fix environment variables before deployment")
        return
    
    # Test Sofi response
    response_ok = await test_sofi_response()
    
    print("\n" + "=" * 40)
    if response_ok:
        print("🎉 SOFI AI IS READY!")
        print("✅ Core functionality working")
        print("\n🚀 Ready to deploy to Render!")
    else:
        print("⚠️ ISSUES FOUND")
        print("🔧 Fix database tables before deployment")
        print("💡 Run the Sharp AI SQL script in Supabase")

if __name__ == "__main__":
    asyncio.run(main())
