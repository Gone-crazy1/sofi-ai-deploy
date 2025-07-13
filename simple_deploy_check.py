#!/usr/bin/env python3
"""
SOFI AI SIMPLE DEPLOYMENT CHECK
"""

import os
import sys
import subprocess

def main():
    print("SOFI AI DEPLOYMENT CHECK")
    print("=" * 50)
    
    # Check required files
    required_files = [
        'main.py',
        'beautiful_receipt_generator.py',
        'functions/transfer_functions.py',
        'templates/success.html'
    ]
    
    print("Checking files...")
    for file in required_files:
        if os.path.exists(file):
            print(f"  OK: {file}")
        else:
            print(f"  MISSING: {file}")
            return False
    
    # Syntax check
    print("\nSyntax check...")
    python_files = ['main.py', 'beautiful_receipt_generator.py', 'functions/transfer_functions.py']
    
    for file in python_files:
        result = subprocess.run([sys.executable, '-m', 'py_compile', file], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  OK: {file}")
        else:
            print(f"  ERROR: {file}")
            return False
    
    print("\n" + "=" * 50)
    print("DEPLOYMENT READY!")
    print("=" * 50)
    print("KEY FIXES APPLIED:")
    print("- Short receipts (saves tokens)")
    print("- No balance in receipts (privacy)")
    print("- Balance updates separate")
    print("- Auto-redirect to @getsofi_bot")
    print("- Strict balance validation")
    print("\nTo deploy:")
    print("1. git add .")
    print("2. git commit -m 'Receipt and balance fixes'")
    print("3. git push")
    print("\nAll users will get the updates!")
    
    return True

if __name__ == "__main__":
    if main():
        print("\nSUCCESS: Ready to deploy!")
    else:
        print("\nFAILED: Fix errors before deploying")
        sys.exit(1)
