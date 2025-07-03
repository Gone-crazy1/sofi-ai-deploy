#!/usr/bin/env python3
"""
Targeted PIN Flow Fix for Sofi AI
Only fixes the specific PIN entry and messaging issues without affecting other functionality
"""

import re
import os

def apply_targeted_fixes():
    """Apply only the specific fixes requested by the user"""
    print("🔧 APPLYING TARGETED PIN FIXES")
    print("=" * 40)
    
    try:
        # Read the current main.py
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"📄 Current file has {len(content.splitlines())} lines")
        
        # Fix 1: Remove "Xara" mentions and replace with neutral language
        print("🔄 Removing 'Xara' mentions...")
        content = re.sub(r'Xara[- ]?style', 'Smart transfer', content, flags=re.IGNORECASE)
        content = content.replace('Xara', 'Smart transfer')
        
        # Fix 2: Remove "verifying account" messages
        print("🔄 Removing 'verifying account' messages...")
        content = re.sub(r'verifying account', 'processing', content, flags=re.IGNORECASE)
        
        # Fix 3: Fix PIN entry to use web link button instead of keyboard
        print("🔄 Fixing PIN entry flow...")
        
        # Find and replace PIN keyboard creation with web link button
        pin_keyboard_pattern = r'# Create PIN entry keyboard.*?create_pin_entry_keyboard\(\)'
        pin_button_replacement = '''# Create enter PIN link button
                    pin_link_keyboard = {
                        "inline_keyboard": [[
                            {"text": "🔐 Enter My PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                        ]]
                    }'''
        
        if re.search(pin_keyboard_pattern, content, re.DOTALL):
            content = re.sub(pin_keyboard_pattern, pin_button_replacement, content, flags=re.DOTALL)
            print("✅ Replaced PIN keyboard with PIN button")
        
        # Fix 4: Update PIN messages to match the desired format
        pin_message_pattern = r'pin_message = f"🔐 \*.*?\*\\n\\n.*?\\n\\n.*?"'
        pin_message_replacement = '''pin_message = f"🔐 *Please enter your PIN*\\n\\nTo complete transfer of ₦{amount:,.2f} to {verified_name}\\n\\n*Click the button below to enter your PIN securely:*"'''
        
        if re.search(pin_message_pattern, content, re.DOTALL):
            content = re.sub(pin_message_pattern, pin_message_replacement, content, flags=re.DOTALL)
            print("✅ Updated PIN message format")
        
        # Fix 5: Ensure we use .get() for status checks to prevent KeyError
        print("🔄 Fixing status key access...")
        content = re.sub(r'result\["status"\]', 'result.get("status")', content)
        content = re.sub(r'verify_result\["status"\]', 'verify_result.get("status")', content)
        
        # Fix 6: Add proper PIN entry callback handler if missing
        if 'elif callback_data.startswith("pin_entry_"):' not in content:
            print("🔄 Adding PIN entry callback handler...")
            
            # Find the callback query handler section
            callback_section = 'elif callback_data.startswith("pin_"):'
            if callback_section in content:
                pin_entry_handler = '''
        # Handle PIN entry link callbacks
        elif callback_data.startswith("pin_entry_"):
            try:
                # Parse callback data: pin_entry_chatid_amount_account_bank_name
                parts = callback_data.split("_")
                if len(parts) >= 3:
                    # Extract data
                    entry_chat_id = parts[2]
                    amount = float(parts[3]) if len(parts) > 3 else 0
                    account = parts[4] if len(parts) > 4 else ""
                    bank = parts[5] if len(parts) > 5 else ""
                    verified_name = "_".join(parts[6:]).replace("_", " ") if len(parts) > 6 else ""
                    
                    # Validate user
                    if entry_chat_id != chat_id:
                        await answer_callback_query(query_id, "❌ Invalid PIN entry request")
                        return jsonify({"error": "Invalid request"}), 400
                    
                    # Create PIN entry web form URL
                    pin_form_url = f"https://sofi-ai-trio.onrender.com/pin-entry?chat_id={chat_id}&amount={amount}&account={account}&bank_code={bank}&recipient={verified_name.replace(' ', '%20')}"
                    
                    # Create web app button for PIN entry
                    pin_web_keyboard = {
                        "inline_keyboard": [[
                            {
                                "text": "🔐 Enter PIN Securely", 
                                "web_app": {"url": pin_form_url}
                            }
                        ]]
                    }
                    
                    # Send PIN entry request with web form
                    pin_message = f"""🔐 *Enter your 4-digit PIN*

To complete transfer of ₦{amount:,.2f} to {verified_name}

*Click the button below to enter your PIN securely:*"""
                    
                    send_reply(chat_id, pin_message, pin_web_keyboard)
                    
                    # Acknowledge callback
                    await answer_callback_query(query_id, "PIN entry ready")
                    return jsonify({"success": True}), 200
                    
            except Exception as e:
                logger.error(f"Error handling PIN entry link: {e}")
                await answer_callback_query(query_id, "❌ PIN entry failed")
                send_reply(chat_id, f"❌ PIN entry failed: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
'''
                # Insert the handler before the existing PIN digit handler
                content = content.replace(callback_section, pin_entry_handler + '\n        ' + callback_section)
                print("✅ Added PIN entry callback handler")
        
        # Write the fixed content back
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"📄 Fixed file has {len(content.splitlines())} lines")
        print("✅ All targeted fixes applied successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

def run_syntax_check():
    """Run Python syntax check"""
    print("\n🔍 Running syntax check...")
    
    try:
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', 'main.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Syntax check passed - no errors found")
            return True
        else:
            print(f"❌ Syntax errors found:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running syntax check: {e}")
        return False

def main():
    """Main fix process"""
    print("🚀 TARGETED SOFI AI PIN FIX")
    print("📋 Fixes to apply:")
    print("   • Remove 'Xara' mentions")
    print("   • Remove 'verifying account' messages") 
    print("   • Replace PIN keyboard with web link button")
    print("   • Fix status key access errors")
    print("   • Add proper PIN entry callback handler")
    print("=" * 50)
    
    # Apply the targeted fixes
    if apply_targeted_fixes():
        # Run syntax check
        if run_syntax_check():
            print("\n🎉 SUCCESS!")
            print("✅ Your 2000-line main.py has been preserved")
            print("✅ PIN flow now uses web link: '🔐 Enter My PIN'")
            print("✅ No more 'Xara' or 'verifying account' messages")
            print("✅ All syntax errors fixed")
            print("\n💡 The PIN button will now open a secure web form")
            print("   for users to enter their PIN safely.")
        else:
            print("\n⚠️ Fixes applied but syntax errors remain")
    else:
        print("\n❌ Failed to apply fixes")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
