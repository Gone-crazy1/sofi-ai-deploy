#!/usr/bin/env python3
"""
Test main.py import by commenting out problematic imports temporarily
"""

print("🧪 TESTING MAIN.PY IMPORT WITH SELECTIVE IMPORTS")
print("=" * 60)

try:
    print("Step 1: Testing Flask imports...")
    from flask import Flask, request, jsonify, url_for, render_template, redirect
    from flask_cors import CORS
    print("✅ Flask imports successful")

    print("Step 2: Testing basic imports...")
    import os, requests, hashlib, logging, json, asyncio, tempfile
    from datetime import datetime
    from supabase import create_client
    import openai
    from typing import Dict, Optional
    from dotenv import load_dotenv
    import random, re, time
    from PIL import Image
    from io import BytesIO
    from pydub import AudioSegment
    from pydub.utils import which
    from unittest.mock import MagicMock
    print("✅ Basic imports successful")

    print("Step 3: Testing utils imports...")
    from utils.bank_api import BankAPI
    from utils.conversation_state import conversation_state
    print("✅ Utils imports successful")

    print("Step 4: Testing memory imports...")
    from utils.memory import save_memory, list_memories, save_chat_message, get_chat_history
    print("✅ Memory imports successful")
    
    print("Step 5: Testing crypto rates...")
    from crypto.rates import get_crypto_to_ngn_rate, get_multiple_crypto_rates, format_crypto_rates_message
    print("✅ Crypto rates imported")
    
    print("Step 6: Testing crypto wallet module level...")
    print("   Importing crypto.wallet module...")
    import crypto.wallet
    print("   ✅ Crypto wallet module imported")
    
    print("   Importing specific functions...")
    from crypto.wallet import create_bitnob_wallet, get_user_wallet_addresses, get_user_ngn_balance
    print("   ✅ Crypto wallet functions imported")
    
    print("Step 7: Testing crypto webhook...")
    from crypto.webhook import handle_crypto_webhook
    print("✅ Crypto webhook imported")
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    print("✅ The main.py file should be able to import without issues")
    
except Exception as e:
    print(f"\n❌ ERROR at import step: {e}")
    import traceback
    traceback.print_exc()
