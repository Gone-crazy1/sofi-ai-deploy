#!/usr/bin/env python3
"""
Minimal main.py test to identify the hanging issue
"""

print("🔍 Testing minimal main.py setup...")

try:
    print("1. Basic imports...")
    from flask_cors import CORS
    import os, requests, hashlib, logging, json, asyncio, tempfile
    from datetime import datetime
    from supabase import create_client
    import openai
    from typing import Dict, Optional
    print("✅ Basic imports successful")
    
    print("2. Loading environment...")
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment loaded")
    
    print("3. Getting environment variables...")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    print("✅ Environment variables loaded")
    
    print("4. Testing Flask app creation...")
    from flask import Flask
    app = Flask(__name__)
    CORS(app)
    print("✅ Flask app created")
    
    print("5. Testing OpenAI API key...")
    openai.api_key = OPENAI_API_KEY
    print("✅ OpenAI API key set")
    
    print("6. Testing Supabase client creation...")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client created")
    else:
        print("⚠️ Supabase credentials missing")
    
    print("\n🎯 Minimal main.py setup successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
