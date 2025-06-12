#!/usr/bin/env python3
"""
Quick test to import main.py with timeout
"""
import signal
import sys

def timeout_handler(signum, frame):
    print("❌ Import timed out after 15 seconds!")
    print("🔍 Main.py import is hanging - there may be blocking operations")
    sys.exit(1)

# Set timeout for 15 seconds
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(15)

try:
    print("🧪 Testing main.py import with 15-second timeout...")
    import main
    signal.alarm(0)  # Cancel the alarm
    print("✅ SUCCESS: Main.py imported successfully!")
except ImportError as e:
    signal.alarm(0)
    print(f"❌ IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    signal.alarm(0)
    print(f"❌ UNEXPECTED ERROR: {e}")
    sys.exit(1)
