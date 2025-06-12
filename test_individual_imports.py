#!/usr/bin/env python3
"""
Test imports one by one to identify the hanging point
"""

print("🔍 Testing imports one by one...")

try:
    print("1. Testing flask_cors...")
    from flask_cors import CORS
    print("✅ Flask CORS imported")
    
    print("2. Testing basic modules...")
    import os
    print("✅ OS imported")
    import requests
    print("✅ Requests imported")
    import hashlib
    print("✅ Hashlib imported")
    import logging
    print("✅ Logging imported")
    import json
    print("✅ JSON imported")
    import asyncio
    print("✅ Asyncio imported")
    import tempfile
    print("✅ Tempfile imported")
    
    print("3. Testing datetime...")
    from datetime import datetime
    print("✅ Datetime imported")
    
    print("4. Testing supabase...")
    from supabase import create_client
    print("✅ Supabase imported")
    
    print("5. Testing openai...")
    import openai
    print("✅ OpenAI imported")
    
    print("6. Testing typing...")
    from typing import Dict, Optional
    print("✅ Typing imported")
    
    print("7. Testing PIL...")
    from PIL import Image
    print("✅ PIL imported")
    
    print("8. Testing BytesIO...")
    from io import BytesIO
    print("✅ BytesIO imported")
    
    print("9. Testing pydub...")
    from pydub import AudioSegment
    print("✅ AudioSegment imported")
    from pydub.utils import which
    print("✅ pydub.utils imported")
    
    print("\n🎯 All individual imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
