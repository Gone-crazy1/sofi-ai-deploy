#!/usr/bin/env python3
"""
Quick fix for the PIN callback status error in main.py
"""

import sys
import os
import re

def fix_pin_status_error():
    """Fix the PIN callback status error in main.py"""
    
    print("🔧 FIXING PIN STATUS ERROR")
    print("=" * 40)
    
    try:
        # Read main.py
        with open("main.py", "r", encoding="utf-8") as f:
            main_content = f.read()
        
        # Use regex to find and fix the PIN status check
        pattern = r'result\["status"\] == "complete"'
        replacement = r'result.get("status") == "complete"'
        
        if pattern in main_content:
            # Count occurrences for reporting
            count = main_content.count(pattern)
            
            # Replace all occurrences
            main_content = main_content.replace(pattern, replacement)
            
            # Write back to main.py
            with open("main.py", "w", encoding="utf-8") as f:
                f.write(main_content)
            
            print(f"✅ Successfully fixed {count} occurrences of the PIN status error")
        else:
            print("❌ Could not find the pattern to fix")
            
        print("=" * 40)
        print("🔄 Please restart the bot to apply the changes.")
        
    except Exception as e:
        print(f"❌ Error fixing PIN status error: {e}")
        print("=" * 40)

if __name__ == "__main__":
    fix_pin_status_error()
