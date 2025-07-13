#!/usr/bin/env python3
"""
Test server for PIN verification with minimal dependencies
"""

import sys
import os

# Setup test environment first
from test_env import setup_test_environment
setup_test_environment()

# Now import the main app
try:
    from main import app
    print("✅ Main app imported successfully")
except Exception as e:
    print(f"❌ Error importing main app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Sofi AI for Testing")
    print("=" * 40)
    print("📍 Test endpoints available:")
    print("   • http://localhost:5000/test-pin")
    print("   • http://localhost:5000/success")
    print("   • http://localhost:5000/api/verify-pin (POST)")
    print("=" * 40)
    
    # Set environment for testing
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "1"
    
    # Initialize temp_transfers if it doesn't exist
    if not hasattr(app, 'temp_transfers'):
        app.temp_transfers = {}
    
    # Add a sample transaction for testing
    from datetime import datetime
    app.temp_transfers["test_tx_12345678"] = {
        'chat_id': 'test_user_123',
        'amount': 5000.0,
        'recipient_name': 'John Doe',
        'bank_name': 'GTBank',
        'account_number': '0123456789',
        'narration': 'Test transfer',
        'fee': 20.0,
        'created_at': datetime.now().isoformat()
    }
    
    print(f"✅ Test transaction added: test_tx_12345678")
    print(f"💡 You can now test PIN verification!")
    print("=" * 40)
    
    try:
        # Start Flask app
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to prevent issues
        )
    except KeyboardInterrupt:
        print(f"\n👋 Sofi AI test server stopped.")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
