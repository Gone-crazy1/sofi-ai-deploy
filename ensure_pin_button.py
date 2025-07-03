#!/usr/bin/env python3
"""
Ensure PIN entry uses "Enter My PIN" button instead of keyboard
"""

import sys
import os
import re

def ensure_pin_button():
    """Ensure PIN entry uses button instead of keyboard"""
    
    print("🔧 ENSURING PIN ENTRY USES BUTTON")
    print("=" * 50)
    
    try:
        # Read main.py
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for any remaining PIN keyboard code
        keyboard_pattern = re.compile(
            r'# Create PIN entry keyboard.*?pin_keyboard = create_pin_entry_keyboard\(\)',
            re.DOTALL
        )
        
        if keyboard_pattern.search(content):
            print("⚠️ Found remaining PIN keyboard code - replacing with button...")
            
            # Replace PIN keyboard with button
            new_button_code = '''# Create enter PIN button
                    pin_button_keyboard = {
                        "inline_keyboard": [[
                            {"text": "🔐 Enter My PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                        ]]
                    }'''
            
            content = keyboard_pattern.sub(new_button_code, content)
            
            # Also update PIN message if needed
            pin_msg_pattern = r'pin_message = f".*?keypad below'
            if re.search(pin_msg_pattern, content):
                new_pin_msg = 'pin_message = f"🔐 *Please enter your PIN*\\n\\nTo complete transfer of ₦{amount:,.2f} to {verified_name}\\n\\n*Click the button below to enter your PIN securely:*'
                content = re.sub(pin_msg_pattern, new_pin_msg, content)
            
            # Write updated content back to main.py
            with open("main.py", "w", encoding="utf-8") as f:
                f.write(content)
                
            print("✅ Successfully replaced PIN keyboard with button")
        else:
            print("✅ No PIN keyboard found - PIN button implementation is complete")
        
        # Also ensure there's no "Verifying recipient account..." message
        if "🔍 *Verifying recipient account...*" in content:
            content = content.replace('send_reply(chat_id, "🔍 *Verifying recipient account...*")', 
                                     '# No verification message shown to user')
            
            # Write updated content back to main.py
            with open("main.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("✅ Removed verification message")
        
        print("=" * 50)
        print("🔄 Please restart the bot to apply the changes.")
        
    except Exception as e:
        print(f"❌ Error ensuring PIN button: {e}")
        print("=" * 50)

if __name__ == "__main__":
    ensure_pin_button()
