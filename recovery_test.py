#!/usr/bin/env python3
"""
SOFI AI Project Recovery Test
Testing basic functionality after project recovery
"""

import os
import sys
from datetime import datetime

def test_environment():
    """Test basic environment setup"""
    print("🚀 SOFI AI PROJECT RECOVERY TEST")
    print("=" * 50)
    
    # Test Python version
    print(f"✅ Python Version: {sys.version}")
    
    # Test working directory
    print(f"✅ Working Directory: {os.getcwd()}")
    
    # Test .env file exists
    env_exists = os.path.exists('.env')
    print(f"{'✅' if env_exists else '❌'} .env file: {'Found' if env_exists else 'Missing'}")
    
    # Test main requirements
    required_files = [
        'main.py',
        'requirements.txt',
        'Procfile',
        'utils/',
        'monnify/',
        'crypto/'
    ]
    
    print("\n📁 CHECKING PROJECT STRUCTURE:")
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print(f"{'✅' if exists else '❌'} {file_path}: {'Found' if exists else 'Missing'}")
    
    # Test imports
    print("\n📦 TESTING IMPORTS:")
    import_tests = [
        ('flask', 'Flask web framework'),
        ('requests', 'HTTP requests'),
        ('dotenv', 'Environment variables'),
        ('supabase', 'Database client'),
        ('openai', 'OpenAI API'),
        ('PIL', 'Image processing'),
        ('pydub', 'Audio processing')
    ]
    
    for module, description in import_tests:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError as e:
            print(f"❌ {module}: Missing - {e}")
    
    print(f"\n🕐 Test completed at: {datetime.now()}")
    print("\n🎯 NEXT STEPS:")
    print("1. Configure your .env file with API keys")
    print("2. Set up Telegram bot token")
    print("3. Configure Supabase database")
    print("4. Test the bot functionality")
    
if __name__ == "__main__":
    test_environment()
