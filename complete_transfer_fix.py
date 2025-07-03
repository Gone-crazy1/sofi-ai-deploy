#!/usr/bin/env python3
"""
Complete replacement of key code sections for Sofi transfer flow
"""

import sys
import os
import re
import shutil

def ensure_pin_callback_handler():
    """Ensure the PIN callback handler is properly implemented"""
    
    # First check if utils/pin_entry_system.py exists
    if not os.path.exists("utils/pin_entry_system.py"):
        print("❌ PIN entry system not found")
        return False
        
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found")
        return False
    
    # Make a backup of main.py
    backup_path = f"main_backup_{int(os.path.getmtime('main.py'))}.py"
    shutil.copy2("main.py", backup_path)
    print(f"📦 Created backup: {backup_path}")
    
    # Read main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace key sections
    
    # 1. PIN callback handler - replace any existing handler with a fixed version
    pin_handler = """
        # Handle PIN entry callbacks
        elif callback_data.startswith("pin_"):
            # Extract the digit or command
            if callback_data == "pin_clear":
                # Handle PIN clear
                pin_manager.clear_pin_session(chat_id)
                await answer_callback_query(query_id, "PIN cleared")
                return jsonify({"success": True}), 200
            elif callback_data == "pin_submit":
                # Handle PIN submit
                await answer_callback_query(query_id, "PIN submitted")
                return await handle_pin_submit(chat_id)
            elif callback_data == "pin_cancel":
                # Handle PIN cancel
                pin_manager.clear_pin_session(chat_id)
                await answer_callback_query(query_id, "PIN entry cancelled")
                send_reply(chat_id, "❌ Transfer cancelled")
                return jsonify({"success": True}), 200
            else:
                # Handle PIN digit pressed
                digit = callback_data.replace("pin_", "")
                if digit.isdigit():
                    result = pin_manager.add_pin_digit(chat_id, digit)
                    
                    if result.get("status") == "complete":
                        await answer_callback_query(query_id, "PIN complete - submitting...")
                        # Auto-submit when 4 digits entered
                        submit_result = await handle_pin_submit(chat_id)
                        if submit_result.get("success"):
                            # Send basic confirmation first
                            send_reply(chat_id, "✅ Transfer completed successfully!")
                            
                            # Then send beautiful receipt if available
                            if submit_result.get("receipt_sent"):
                                logger.info(f"📧 Beautiful receipt already sent to {chat_id}")
                            else:
                                logger.info(f"📋 Sending basic receipt to {chat_id}")
                                # Basic receipt already sent in handle_pin_submit
                        else:
                            send_reply(chat_id, f"❌ {submit_result.get('error', 'Transfer failed')}")
                    else:
                        # Show PIN progress
                        pin_display = "•" * result.get("length", 0)
                        await answer_callback_query(query_id, f"PIN: {pin_display}")
                    
                    return jsonify({"success": True}), 200
                else:
                    await answer_callback_query(query_id, "Invalid PIN input")
                    return jsonify({"error": "Invalid PIN input"}), 400
"""

    # 2. PIN entry link handler
    pin_entry_handler = """
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
                    
                    # Create PIN entry keyboard
                    from utils.pin_entry_system import create_pin_entry_keyboard
                    pin_keyboard = create_pin_entry_keyboard()
                    
                    # Send PIN entry request privately
                    pin_message = f"🔐 *Enter your 4-digit PIN*\\n\\nPlease enter your PIN securely to complete the transfer of ₦{amount:,.2f} to {verified_name}"
                    send_reply(chat_id, pin_message, pin_keyboard)
                    
                    # Store transfer details in pin session
                    from utils.pin_entry_system import initialize_pin_session
                    initialize_pin_session(chat_id, "transfer", {
                        "amount": amount,
                        "account_number": account,
                        "bank_code": bank,
                        "verified_name": verified_name
                    })
                    
                    # Acknowledge callback
                    await answer_callback_query(query_id, "PIN entry ready")
                    return jsonify({"success": True}), 200
                    
            except Exception as e:
                logger.error(f"Error handling PIN entry link: {e}")
                await answer_callback_query(query_id, "❌ PIN entry failed")
                send_reply(chat_id, f"❌ PIN entry failed: {str(e)}")
                return jsonify({"error": str(e)}), 500
"""

    # Find key locations in the file
    # Look for a pattern that's likely to be near the PIN callback handler
    pattern1 = "# Handle callback queries"
    pattern2 = "# Parse the callback data"
    
    # Try to find one of the patterns
    pos1 = content.find(pattern1)
    pos2 = content.find(pattern2)
    
    if pos1 > 0:
        insert_pos = pos1
    elif pos2 > 0:
        insert_pos = pos2
    else:
        print("❌ Could not find insertion point for PIN handlers")
        return False
    
    # Split the content at the insertion point
    first_part = content[:insert_pos]
    second_part = content[insert_pos:]
    
    # Insert our handlers
    new_content = first_part + "\n    # ==== FIXED PIN HANDLERS ====\n" + pin_entry_handler + pin_handler + "\n    # ==== END FIXED PIN HANDLERS ====\n" + second_part
    
    # Write back to main.py
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Added fixed PIN handlers to main.py")
    return True

def fix_verify_transfer_handler():
    """Fix the verify_transfer handler to use PIN button"""
    
    # Read main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the verify_transfer handler
    verify_pattern = "elif callback_data.startswith(\"verify_transfer_\"):"
    verify_pos = content.find(verify_pattern)
    
    if verify_pos < 0:
        print("❌ Could not find verify_transfer handler")
        return False
    
    # Find the PIN keyboard creation part
    pin_keyboard_pattern = "# Create PIN entry keyboard"
    pin_keyboard_pos = content.find(pin_keyboard_pattern, verify_pos)
    
    if pin_keyboard_pos < 0:
        print("❌ Could not find PIN keyboard creation section")
        return False
    
    # Find the end of the pin keyboard section
    send_reply_pattern = "send_reply(chat_id,"
    send_reply_pos = content.find(send_reply_pattern, pin_keyboard_pos)
    
    if send_reply_pos < 0:
        print("❌ Could not find send_reply after PIN keyboard")
        return False
    
    # Get the line after send_reply by finding the next newline
    next_line_pos = content.find("\n", send_reply_pos)
    
    if next_line_pos < 0:
        print("❌ Could not find end of send_reply line")
        return False
    
    # Extract the parts
    before_pin = content[:pin_keyboard_pos]
    after_pin = content[next_line_pos:]
    
    # Create our replacement PIN button code
    pin_button_code = """                    # Create enter PIN link button
                    pin_link_keyboard = {
                        "inline_keyboard": [[
                            {"text": "🔐 Enter PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                        ]]
                    }
                    
                    # Send PIN entry request
                    pin_message = f"🔐 *Please enter your PIN*\\n\\nTo complete transfer of ₦{amount:,.2f} to {verified_name}\\n\\n*Click the button below to enter your PIN securely:*"
                    send_reply(chat_id, pin_message, pin_link_keyboard)"""
    
    # Combine the parts
    new_content = before_pin + pin_button_code + after_pin
    
    # Write back to main.py
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Updated verify_transfer handler to use PIN button")
    return True

def remove_xara_mentions():
    """Remove any Xara mentions from the code"""
    
    # Read main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace Xara mentions
    new_content = content.replace("Xara-style", "Smart transfer")
    new_content = new_content.replace("Error handling Xara", "Error handling transfer")
    new_content = new_content.replace("Xara-style confirmation sent", "Transfer confirmation sent")
    
    # Replace verification message
    new_content = new_content.replace("🔍 *Verifying recipient account...*", "")
    
    # Write back to main.py
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Removed Xara mentions from main.py")
    return True

def main():
    """Main function to fix all issues"""
    
    print("🔧 COMPLETE SOFI TRANSFER FLOW FIX")
    print("=" * 40)
    
    try:
        # Fix PIN callback handler
        ensure_pin_callback_handler()
        
        # Fix verify_transfer handler
        fix_verify_transfer_handler()
        
        # Remove Xara mentions
        remove_xara_mentions()
        
        print("=" * 40)
        print("✅ All fixes applied!")
        print("🔄 Please restart the bot to apply the changes.")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        print("=" * 40)

if __name__ == "__main__":
    main()
