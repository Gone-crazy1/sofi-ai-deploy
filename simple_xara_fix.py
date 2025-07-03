#!/usr/bin/env python3
"""
Quick fix: Create a simple Xara command handler that works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simple Xara-style command detection
def detect_xara_command(message: str):
    """Simple Xara command detector"""
    import re
    
    # Pattern: account_number bank send amount
    pattern = r'^(\d{10,11})\s+(\w+)\s+send\s+(\d+(?:\.\d{2})?)$'
    match = re.match(pattern, message.strip(), re.IGNORECASE)
    
    if match:
        return {
            'account_number': match.group(1),
            'bank': match.group(2),
            'amount': float(match.group(3)),
            'is_xara': True
        }
    return None

def test_detection():
    """Test the detection"""
    test_commands = [
        "8104965538 Opay send 100",
        "6115491450 Opay send 100", 
        "1234567890 Access send 500",
        "regular message"
    ]
    
    print("🧪 TESTING XARA DETECTION")
    print("=" * 30)
    
    for cmd in test_commands:
        result = detect_xara_command(cmd)
        if result:
            print(f"✅ '{cmd}' → XARA DETECTED: {result}")
        else:
            print(f"❌ '{cmd}' → Not Xara")
    
    print("\n💡 QUICK FIX STRATEGY:")
    print("=" * 25)
    print("1. Add this simple detector to main.py")
    print("2. Put it FIRST in handle_message()")
    print("3. Return early if Xara command detected")
    print("4. This will bypass OpenAI Assistant")

if __name__ == "__main__":
    test_detection()
