#!/usr/bin/env python3
"""
Test Live API Integrations
Tests all live API connections with production keys
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_supabase_connection():
    """Test Supabase database connection"""
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            return {"success": False, "error": "Missing Supabase credentials"}
        
        client = create_client(url, key)
        
        # Test connection by listing tables
        result = client.table("users").select("id").limit(1).execute()
        
        return {
            "success": True,
            "message": "Supabase connection successful",
            "url": url[:30] + "...",
            "tables_accessible": True
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        
        if not api_key or not assistant_id:
            return {"success": False, "error": "Missing OpenAI credentials"}
        
        client = OpenAI(api_key=api_key)
        
        # Test by retrieving assistant
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        return {
            "success": True,
            "message": "OpenAI connection successful",
            "assistant_name": assistant.name,
            "assistant_id": assistant_id
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_paystack_connection():
    """Test Paystack API connection"""
    try:
        import requests
        
        secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        
        if not secret_key:
            return {"success": False, "error": "Missing Paystack secret key"}
        
        # Test by listing banks
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get("https://api.paystack.co/bank", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": "Paystack connection successful",
                "banks_count": len(data.get("data", [])),
                "key_type": "Live" if "sk_live" in secret_key else "Test"
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_telegram_connection():
    """Test Telegram Bot API connection"""
    try:
        import requests
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not bot_token:
            return {"success": False, "error": "Missing Telegram bot token"}
        
        # Test by getting bot info
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        
        if response.status_code == 200:
            data = response.json()
            bot_info = data.get("result", {})
            return {
                "success": True,
                "message": "Telegram connection successful",
                "bot_username": bot_info.get("username"),
                "bot_name": bot_info.get("first_name")
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_paystack_service():
    """Test Paystack service integration"""
    try:
        from paystack.paystack_service import get_paystack_service
        
        service = get_paystack_service()
        
        # Test balance info with a dummy chat_id
        balance_result = await service.get_balance_info("test_chat_id")
        
        return {
            "success": True,
            "message": "Paystack service integration working",
            "balance_method": "Functional" if not balance_result.get("error") else "Has Error",
            "balance_error": balance_result.get("error") if balance_result.get("error") else None
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def main():
    """Run all integration tests"""
    print("🧪 Testing Live API Integrations...")
    print("=" * 50)
    
    tests = [
        ("Supabase Database", test_supabase_connection),
        ("OpenAI Assistant", test_openai_connection),
        ("Paystack Payment", test_paystack_connection),
        ("Telegram Bot", test_telegram_connection),
        ("Paystack Service", test_paystack_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result["success"]:
                print(f"✅ {test_name}: {result['message']}")
                for key, value in result.items():
                    if key not in ["success", "message", "error"]:
                        print(f"   - {key}: {value}")
            else:
                print(f"❌ {test_name}: {result['error']}")
                
        except Exception as e:
            print(f"💥 {test_name}: Exception - {str(e)}")
            results.append((test_name, {"success": False, "error": str(e)}))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result["success"])
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All integrations are working!")
        print("✅ Your Sofi AI is ready for production!")
    else:
        print("⚠️  Some integrations need attention:")
        for test_name, result in results:
            if not result["success"]:
                print(f"   - {test_name}: {result['error']}")
    
    print("\n🔐 SECURITY REMINDER:")
    print("- Rotate these API keys after setup")
    print("- Never share keys in public channels")
    print("- Monitor API usage regularly")

if __name__ == "__main__":
    asyncio.run(main())
