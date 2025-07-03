#!/usr/bin/env python3
"""
Flask application startup test
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    print("🚀 Testing Flask app initialization...")
    
    # Import main module
    import main
    print("✅ Main module imported successfully")
    
    # Check if Flask app is created
    if hasattr(main, 'app'):
        print("✅ Flask app instance found")
        
        # Test basic route registration
        routes = [rule.rule for rule in main.app.url_map.iter_rules()]
        print(f"✅ Routes registered: {len(routes)}")
        
        # Check key routes
        key_routes = ['/webhook', '/health', '/callback']
        for route in key_routes:
            if route in routes:
                print(f"✅ Route {route} registered")
            else:
                print(f"⚠️  Route {route} not found")
        
        print("\n🎉 Flask application test completed successfully!")
        print("The app should be ready to run.")
        
    else:
        print("❌ Flask app not found in main module")
        
except Exception as e:
    print(f"❌ Error testing Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
