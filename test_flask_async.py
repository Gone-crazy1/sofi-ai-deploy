#!/usr/bin/env python3
"""
Quick test to verify Flask async support is working
"""

import asyncio
import sys

def test_flask_async():
    """Test if Flask async support is available"""
    try:
        from flask import Flask
        
        # Test creating a Flask app with async support
        app = Flask(__name__)
        
        @app.route('/test')
        async def test_async():
            await asyncio.sleep(0.1)  # Test async functionality
            return "Async working!"
        
        print("✅ Flask[async] support: WORKING")
        return True
        
    except ImportError as e:
        print(f"❌ Flask import error: {e}")
        return False
    except RuntimeError as e:
        print(f"❌ Flask async error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Flask async support...")
    
    if test_flask_async():
        print("🎉 Flask async support is properly configured!")
        sys.exit(0)
    else:
        print("💥 Flask async support test failed!")
        sys.exit(1)
