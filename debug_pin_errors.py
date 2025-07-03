#!/usr/bin/env python3
"""
Quick fix for PIN callback errors and Xara-style flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_pin_callback_errors():
    """Fix the PIN callback handling errors"""
    
    print("🔧 FIXING PIN CALLBACK ERRORS")
    print("=" * 40)
    
    # The main issue is in the callback query handler
    # 1. Error when accessing 'status' key in add_pin_digit result
    # 2. Xara-style flow issues: mentioning Xara name
    # 3. Showing "Verifying recipient account" message
    # 4. Using PIN keyboard instead of a link/button
    
    print("✅ Starting fixes...")
    
    # Read main.py
    with open("main.py", "r", encoding="utf-8") as f:
        main_content = f.read()
    
    # Fix 1: Fix the PIN callback handler to safely access status key
    print("🔧 Fixing PIN callback error handling...")
    
    old_pin_code = """                    result = pin_manager.add_pin_digit(chat_id, digit)
                    
                    if result["status"] == "complete":"""
    
    new_pin_code = """                    result = pin_manager.add_pin_digit(chat_id, digit)
                    
                    if result.get("status") == "complete":"""
    
    main_content = main_content.replace(old_pin_code, new_pin_code)
    
    # Fix 2: Update Xara detection to remove Xara name mention
    print("🔧 Removing Xara name mentions...")
    
    old_xara_log = """            logger.info(f"🎯 Xara-style command detected: {parsed_xara}")"""
    new_xara_log = """            logger.info(f"🎯 Smart transfer command detected: {parsed_xara}")"""
    
    main_content = main_content.replace(old_xara_log, new_xara_log)
    
    # Also fix any other Xara mentions in the code
    main_content = main_content.replace("Error handling Xara command", "Error handling smart transfer command")
    main_content = main_content.replace("Xara-style confirmation sent", "Transfer confirmation sent")
    main_content = main_content.replace("# Handle Xara-style verification callbacks", "# Handle transfer verification callbacks")
    
    # Fix 3: Replace "Verifying recipient account" message
    print("🔧 Removing account verification message...")
    
    old_verify_msg = """                # Step 1: Auto-verify account and get real name
                send_reply(chat_id, "🔍 *Verifying recipient account...*")"""
    
    new_verify_msg = """                # Step 1: Auto-verify account and get real name (silently)
                # No verification message shown to user"""
    
    main_content = main_content.replace(old_verify_msg, new_verify_msg)
    
    # Fix 4: Replace PIN keyboard with link button
    print("🔧 Replacing PIN keyboard with link button...")
    
    old_pin_flow = """                    # Create PIN entry keyboard
                    from utils.pin_entry_system import create_pin_entry_keyboard
                    pin_keyboard = create_pin_entry_keyboard()
                    
                    # Send PIN entry request
                    pin_message = f"🔐 *Enter your 4-digit PIN*\n\nTo complete transfer of ₦{amount:,.2f} to {verified_name}\n\n*Use the keypad below:*"
                    send_reply(chat_id, pin_message, pin_keyboard)"""
    
    new_pin_flow = """                    # Create enter PIN link button
                    pin_link_keyboard = {
                        "inline_keyboard": [[
                            {"text": "🔐 Enter PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                        ]]
                    }
                    
                    # Send PIN entry request
                    pin_message = f"🔐 *Please enter your PIN*\n\nTo complete transfer of ₦{amount:,.2f} to {verified_name}\n\n*Click the button below to enter your PIN securely:*"
                    send_reply(chat_id, pin_message, pin_link_keyboard)"""
    
    main_content = main_content.replace(old_pin_flow, new_pin_flow)
    
    # Fix 5: Add proper callback handler for pin_entry button
    print("🔧 Adding callback handler for PIN entry link...")
    
    # Find the beginning of the callback handler function
    callback_handler_start = "        # Handle transfer verification callbacks"
    callback_handler_pos = main_content.find(callback_handler_start)
    
    if callback_handler_pos > 0:
        # Find position to insert the new PIN entry callback handler
        pin_entry_pos = main_content.find("        # Handle PIN entry callbacks", callback_handler_pos)
        
        if pin_entry_pos > 0:
            pin_entry_callback = """        # Handle PIN entry link callbacks
        elif callback_data.startswith("pin_entry_"):
            try:
                # Parse callback data: pin_entry_chatid_amount_account_bank
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
                    pin_message = f"🔐 *Enter your 4-digit PIN*\n\nPlease enter your PIN securely to complete the transfer of ₦{amount:,.2f} to {verified_name}"
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
            # Insert the new callback handler before the PIN entry section
            main_content = main_content[:pin_entry_pos] + pin_entry_callback + main_content[pin_entry_pos:]
    
    # Write updated content back to main.py
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(main_content)
    
    print("✅ All fixes applied successfully!")
    print("=" * 40)
    print("🔄 Please restart the bot to apply the changes.")

if __name__ == "__main__":
    fix_pin_callback_errors()
