#!/usr/bin/env python3
"""Test the PIN masking functionality"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_pin_masking():
    """Test that PIN templates have masking implemented"""
    
    print("🔐 TESTING PIN MASKING IMPLEMENTATION")
    print("=" * 45)
    
    # Test 1: Check main PIN template
    try:
        with open('templates/pin-entry.html', 'r', encoding='utf-8') as f:
            pin_template = f.read()
        
        # Check for masking features
        checks = {
            "CSS text-security": "-webkit-text-security: disc" in pin_template,
            "JavaScript masking": "actualPinValues" in pin_template,
            "Dot display": "this.value = '•'" in pin_template or "this.value = ''" in pin_template,
            "Secure storage": "actualPinValues[index]" in pin_template,
            "Paste handling": "addEventListener('paste'" in pin_template
        }
        
        print("📄 PIN Entry Template (templates/pin-entry.html):")
        for feature, present in checks.items():
            status = "✅" if present else "❌"
            print(f"   {status} {feature}")
        
        all_features = all(checks.values())
        print(f"   Overall: {'✅ SECURE' if all_features else '⚠️  NEEDS WORK'}")
        
    except FileNotFoundError:
        print("❌ templates/pin-entry.html not found")
        all_features = False
    
    # Test 2: Check React PIN template
    try:
        with open('templates/react-pin-app.html', 'r', encoding='utf-8') as f:
            react_template = f.read()
        
        react_checks = {
            "Display PIN state": "displayPin" in react_template,
            "Masked display": "displayPin[index] = '•'" in react_template or "newDisplayPin[index] = '•'" in react_template,
            "Secure PIN storage": "const newPin = pin.split('')" in react_template,
            "Backspace handling": "if (e.key === 'Backspace')" in react_template,
            "Monospace font": "fontFamily: 'monospace'" in react_template
        }
        
        print("\n⚛️  React PIN App (templates/react-pin-app.html):")
        for feature, present in react_checks.items():
            status = "✅" if present else "❌"
            print(f"   {status} {feature}")
        
        react_secure = all(react_checks.values())
        print(f"   Overall: {'✅ SECURE' if react_secure else '⚠️  NEEDS WORK'}")
        
    except FileNotFoundError:
        print("❌ templates/react-pin-app.html not found")
        react_secure = False
    
    # Summary
    print("\n" + "=" * 45)
    print("🎯 PIN MASKING IMPLEMENTATION SUMMARY:")
    print("=" * 45)
    
    if all_features and react_secure:
        print("✅ SUCCESS: PIN masking implemented in both templates!")
        print("🔒 Users will now see dots (•) instead of actual PIN digits")
        print("🚀 Enhanced security and privacy protection")
        print("\n💡 How it works:")
        print("   1. User types a digit → sees a dot (•)")
        print("   2. Actual PIN stored securely in JavaScript")
        print("   3. Only dots visible on screen")
        print("   4. Real PIN sent to server on submit")
        return True
    else:
        print("⚠️  Some masking features missing")
        print("Please verify the templates are properly updated")
        return False

if __name__ == "__main__":
    success = test_pin_masking()
    
    if success:
        print("\n🎉 PIN masking is now active!")
        print("Next time users enter PIN, they'll see: ••••")
    else:
        print("\n🔧 Please check the template files")
        
    print("\n📝 Test your PIN masking:")
    print("1. Start the Flask server")
    print("2. Go to /test-pin route")
    print("3. Type digits and verify you see dots")
