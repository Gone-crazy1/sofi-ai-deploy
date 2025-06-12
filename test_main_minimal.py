#!/usr/bin/env python3
"""
Minimal test to identify what's causing main.py import to hang
"""

print("🧪 MINIMAL MAIN.PY IMPORT TEST")
print("=" * 50)

# Test imports one by one
try:
    print("1. Testing Flask imports...")
    from flask import Flask, request, jsonify, url_for, render_template, redirect
    from flask_cors import CORS
    print("✅ Flask imports successful")
    
    print("2. Testing standard library imports...")
    import os, requests, hashlib, logging, json, asyncio, tempfile
    from datetime import datetime
    print("✅ Standard library imports successful")
    
    print("3. Testing supabase import...")
    from supabase import create_client
    print("✅ Supabase import successful")
    
    print("4. Testing OpenAI import...")
    import openai
    print("✅ OpenAI import successful")
    
    print("5. Testing additional imports...")
    from typing import Dict, Optional
    from dotenv import load_dotenv
    import random, re, time
    print("✅ Additional imports successful")
    
    print("6. Testing PIL and pydub imports...")
    from PIL import Image
    from io import BytesIO
    from pydub import AudioSegment
    from pydub.utils import which
    print("✅ PIL and pydub imports successful")
    
    print("7. Testing utils imports...")
    from utils.bank_api import BankAPI
    from utils.conversation_state import conversation_state
    print("✅ Utils imports successful")
    
    print("8. Testing memory imports...")
    from utils.memory import save_memory, list_memories, save_chat_message, get_chat_history
    print("✅ Memory imports successful")
    
    print("9. Testing crypto imports...")
    from crypto.rates import get_crypto_to_ngn_rate, get_multiple_crypto_rates, format_crypto_rates_message
    print("✅ Crypto rates imported")
    
    from crypto.wallet import create_bitnob_wallet, get_user_wallet_addresses, get_user_ngn_balance
    print("✅ Crypto wallet imported")
    
    from crypto.webhook import handle_crypto_webhook
    print("✅ Crypto webhook imported")
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    print("Main.py should import without issues now.")

except Exception as e:
    print(f"❌ Import failed at step: {e}")
    import traceback
    traceback.print_exc()
