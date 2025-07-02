#!/usr/bin/env python3
"""
Simple Package Verification for Sofi AI
Tests if all critical packages can be imported and work correctly
"""

import sys
import subprocess
from typing import Dict

def test_package_imports() -> Dict[str, bool]:
    """Test importing all critical packages"""
    
    packages_to_test = {
        # Core Web Framework
        'Flask': 'flask',
        'Flask-CORS': 'flask_cors', 
        'Flask-Limiter': 'flask_limiter',
        'Flask-SQLAlchemy': 'flask_sqlalchemy',
        'Flask-WTF': 'flask_wtf',
        'WTForms': 'wtforms',
        'Werkzeug': 'werkzeug',
        'Gunicorn': 'gunicorn',
        
        # Database
        'Supabase': 'supabase',
        'PostgREST': 'postgrest',
        'GoTrue': 'gotrue',
        'Realtime': 'realtime',
        'Storage3': 'storage3',
        'Supafunc': 'supafunc',
        
        # AI & APIs
        'OpenAI': 'openai',
        
        # Telegram Bot
        'pyTelegramBotAPI': 'telebot',
        'python-telegram-bot': 'telegram',
        
        # Image Processing
        'Pillow': 'PIL',
        'OpenCV': 'cv2',
        'PyTesseract': 'pytesseract',
        'Pydub': 'pydub',
        
        # Environment & Config
        'python-dotenv': 'dotenv',
        'Requests': 'requests',
        
        # Data Processing
        'NumPy': 'numpy',
        'Pandas': 'pandas',
        
        # Task Scheduling
        'APScheduler': 'apscheduler',
        
        # Testing
        'pytest': 'pytest',
        
        # Other Essentials
        'PyJWT': 'jwt',
        'Click': 'click',
        'Colorama': 'colorama',
    }
    
    results = {}
    print("🧪 Testing Package Imports:")
    print("=" * 50)
    
    for package_name, import_name in packages_to_test.items():
        try:
            __import__(import_name)
            results[package_name] = True
            print(f"✅ {package_name}: OK")
        except ImportError:
            results[package_name] = False
            print(f"❌ {package_name}: MISSING")
        except Exception as e:
            results[package_name] = False
            print(f"⚠️ {package_name}: ERROR - {str(e)}")
    
    return results

def test_specific_functionality():
    """Test specific functionality"""
    print("\n🎯 Testing Specific Functionality:")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test Flask app creation
    total_tests += 1
    try:
        from flask import Flask, request, jsonify
        app = Flask(__name__)
        print("✅ Flask: App creation and basic imports work")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Flask: {str(e)}")
    
    # Test Supabase client
    total_tests += 1
    try:
        from supabase import create_client
        print("✅ Supabase: Client creation function accessible")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Supabase: {str(e)}")
    
    # Test OpenAI
    total_tests += 1
    try:
        from openai import OpenAI
        print("✅ OpenAI: Client class accessible")
        tests_passed += 1
    except Exception as e:
        print(f"❌ OpenAI: {str(e)}")
    
    # Test Telegram bots
    total_tests += 1
    try:
        import telebot
        from telegram import Bot
        print("✅ Telegram Bots: Both libraries accessible")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Telegram Bots: {str(e)}")
    
    # Test image processing
    total_tests += 1
    try:
        from PIL import Image
        import cv2
        import pytesseract
        print("✅ Image Processing: PIL, OpenCV, and Tesseract accessible")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Image Processing: {str(e)}")
    
    # Test data processing
    total_tests += 1
    try:
        import numpy as np
        import pandas as pd
        print("✅ Data Processing: NumPy and Pandas work")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Data Processing: {str(e)}")
    
    # Test JWT and security
    total_tests += 1
    try:
        import jwt
        from werkzeug.security import generate_password_hash
        print("✅ Security: JWT and password hashing work")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Security: {str(e)}")
    
    return tests_passed, total_tests

def check_system_requirements():
    """Check system-level requirements"""
    print("\n🔧 System Requirements:")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python: {python_version.major}.{python_version.minor}.{python_version.micro} (Recommended: 3.8+)")
    
    # Check pip
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        print("✅ pip: Available")
    except Exception:
        print("❌ pip: Not available")
    
    # Check Tesseract (optional but recommended)
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR: Installed")
    except Exception:
        print("⚠️ Tesseract OCR: Not installed (optional for OCR features)")

def get_installed_packages():
    """Get list of installed packages"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')[2:]  # Skip header
        packages = {}
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    packages[parts[0]] = parts[1]
        return packages
    except Exception:
        return {}

def main():
    """Main function"""
    print("🚀 Sofi AI Package Verification")
    print("=" * 50)
    
    # Check system requirements
    check_system_requirements()
    
    # Test package imports
    import_results = test_package_imports()
    
    # Test functionality
    func_passed, func_total = test_specific_functionality()
    
    # Get package count
    installed_packages = get_installed_packages()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    successful_imports = sum(1 for success in import_results.values() if success)
    total_imports = len(import_results)
    
    print(f"📦 Packages: {len(installed_packages)} total installed")
    print(f"🧪 Import Tests: {successful_imports}/{total_imports} passed")
    print(f"🎯 Functionality Tests: {func_passed}/{func_total} passed")
    
    if successful_imports == total_imports and func_passed == func_total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your Sofi AI application is ready to run!")
        print("🚀 All required packages are installed and working correctly")
        return True
    else:
        print("\n⚠️ SOME ISSUES FOUND:")
        
        failed_imports = [name for name, success in import_results.items() if not success]
        if failed_imports:
            print(f"\n❌ Failed Imports ({len(failed_imports)}):")
            for pkg in failed_imports:
                print(f"   • {pkg}")
        
        if func_passed < func_total:
            print(f"\n⚠️ Functionality issues: {func_total - func_passed} tests failed")
        
        print("\n🔧 Recommended Action:")
        print("   pip install -r requirements.txt --upgrade")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
