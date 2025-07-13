#!/usr/bin/env python3
"""
Quick deployment test script for Sofi AI
Tests critical imports before full deployment
"""

def test_critical_imports():
    """Test if all critical imports work"""
    print("🧪 Testing critical imports...")
    
    try:
        # Core Flask
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Database
        from supabase import create_client
        print("✅ Supabase imported successfully")
        
        # AI
        import openai
        from openai import OpenAI
        print("✅ OpenAI imported successfully")
        
        # Telegram
        import telebot
        print("✅ Telegram bot imported successfully")
        
        # Audio processing
        from pydub import AudioSegment
        from pydub.utils import which
        print("✅ Pydub imported successfully")
        
        # Image processing
        from PIL import Image
        print("✅ PIL imported successfully")
        
        # Essential utilities
        import requests
        from dotenv import load_dotenv
        print("✅ Essential utilities imported successfully")
        
        print("\n🎉 All critical imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_critical_imports()
    exit(0 if success else 1)
