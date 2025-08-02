#!/usr/bin/env python3
"""
Local development server runner for Sofi AI.
Use this script to run the application locally during development.
"""

import os
import sys
from pathlib import Path

def main():
    """Run the Sofi AI application locally."""
    
    # Ensure we're in the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🚀 Starting Sofi AI Development Server...")
    print("=" * 50)
    
    # Check if environment variables are loaded
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check critical environment variables
    missing_vars = []
    required_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID', 
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'OPENAI_API_KEY'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please check your .env file")
        return 1
    
    print("✅ Environment variables loaded")
    print(f"📱 WhatsApp Phone ID: {os.getenv('WHATSAPP_PHONE_NUMBER_ID')}")
    print(f"🔗 Supabase URL: {os.getenv('SUPABASE_URL')}")
    
    # Import and run the WSGI application
    try:
        from wsgi import app
        print("\n🌐 Starting server on http://localhost:8000")
        print("📱 WhatsApp webhook: http://localhost:8000/whatsapp-webhook")
        print("🔧 Admin dashboard: http://localhost:8000/admin")
        print("\n🔄 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Use waitress for Windows compatibility
        try:
            from waitress import serve
            serve(app, host='0.0.0.0', port=8000, threads=4)
        except ImportError:
            print("⚠️ Waitress not available, using Flask development server...")
            app.run(host='0.0.0.0', port=8000, debug=True)
            
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
