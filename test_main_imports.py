#!/usr/bin/env python3
"""
Test main.py imports without crypto modules
"""

print("🔍 Testing main.py imports without crypto...")

try:
    print("1. Testing Flask imports...")
    from flask_cors import CORS
    print("✅ Flask CORS imported")
    
    print("2. Testing basic imports...")
    import os, requests, hashlib, logging, json, asyncio, tempfile
    print("✅ Basic imports successful")
    
    print("3. Testing datetime...")
    from datetime import datetime
    print("✅ Datetime imported")
    
    print("4. Testing dotenv...")
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment loaded")
    
    print("5. Testing Supabase...")
    from supabase import create_client
    print("✅ Supabase imported")
    
    print("6. Testing OpenAI...")
    import openai
    print("✅ OpenAI imported")
    
    print("7. Testing utils...")
    from utils.bank_api import BankAPI
    print("✅ Bank API imported")
    
    from utils.memory import save_memory, list_memories, save_chat_message, get_chat_history
    print("✅ Memory utils imported")
    
    from utils.conversation_state import conversation_state
    print("✅ Conversation state imported")
    
    print("\n🎯 All main imports successful without crypto modules!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
