"""
WSGI entry point for Sofi AI application.
This file is used by production servers like Gunicorn to run the Flask app.
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    # Import the Flask application from main.py
    from main import app
    
    # Make sure the app is properly configured
    if __name__ == "__main__":
        # For development with waitress (Windows compatible)
        try:
            from waitress import serve
            print("🚀 Starting Sofi AI with Waitress server...")
            print("🌐 Server will be available at: http://localhost:8000")
            print("📱 WhatsApp webhook: http://localhost:8000/whatsapp-webhook")
            serve(app, host='0.0.0.0', port=8000, threads=4)
        except ImportError:
            # Fallback to Flask development server
            print("⚠️ Waitress not available, using Flask development server...")
            print("🌐 Server will be available at: http://localhost:5000")
            app.run(host='0.0.0.0', port=5000, debug=False)
    
    # Export the app for WSGI servers (Gunicorn, uWSGI, etc.)
    application = app

except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    print("📁 Current directory:", os.getcwd())
    print("🐍 Python path:", sys.path[:3])
    raise

except Exception as e:
    print(f"❌ Error starting application: {e}")
    raise
