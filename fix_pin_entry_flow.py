#!/usr/bin/env python3
"""
Fix PIN entry flow to use button instead of keyboard and show clean confirmation
"""

import sys
import os

def fix_pin_entry_flow():
    """Fix PIN entry flow to use a button instead of keyboard and show clean confirmation"""
    
    print("🔧 FIXING PIN ENTRY FLOW")
    print("=" * 40)
    
    try:
        # Read main.py
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Fix PIN status check (this is critical)
        content = content.replace('result["status"] == "complete"', 'result.get("status") == "complete"')
        print("✅ Fixed PIN status check")
        
        # Find the transfer verification callback section
        verify_section_start = "        elif callback_data.startswith(\"verify_transfer_\"):"
        verify_section_pos = content.find(verify_section_start)
        
        if verify_section_pos > 0:
            # Get the part of the file after the verification section
            post_verify = content[verify_section_pos:]
            
            # Find position to insert PIN entry button code
            pin_entry_pos = post_verify.find("# Create PIN entry keyboard")
            
            if pin_entry_pos > 0:
                # Split the content
                before_pin = content[:verify_section_pos + pin_entry_pos]
                after_pin = content[verify_section_pos + pin_entry_pos:]
                
                # Find where the old code ends
                end_old_code = after_pin.find("send_reply(chat_id,")
                after_send_pos = after_pin.find("\n", end_old_code)
                after_send = after_pin[after_send_pos:]
                
                # Replace PIN keyboard with button
                new_pin_code = """# Create enter PIN link button
                    pin_link_keyboard = {
                        "inline_keyboard": [[
                            {"text": "🔐 Enter My PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                        ]]
                    }
                    
                    # Send PIN entry request
                    pin_message = f\"\"\"✅ *Account Verified: {verified_name}*

You're about to send ₦{amount:,.2f} to:
🏦 {verified_name} — {account_number} ({bank_name})

👉 Please click the button below to enter your 4-digit transaction PIN securely:\"\"\"
                    send_reply(chat_id, pin_message, pin_link_keyboard)"""
                
                # Combine the parts
                new_content = before_pin + new_pin_code + after_send
                
                # Write back to main.py
                with open("main.py", "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                print("✅ Successfully updated PIN entry flow to use a button")
                
                # 2. Add PIN entry callback handler
                add_pin_entry_callback(new_content)
            else:
                print("❌ Could not find PIN entry keyboard section")
        else:
            print("❌ Could not find verification callback section")
        
        # 3. Fix verification message and confirmation flow
        fix_verification_flow()
        
        print("=" * 40)
        print("🔄 Please restart the bot to apply the changes.")
        
    except Exception as e:
        print(f"❌ Error fixing PIN entry flow: {e}")
        print("=" * 40)

def add_pin_entry_callback(content):
    """Add PIN entry callback handler"""
    
    try:
        # Find position to insert the new PIN entry callback handler
        callback_section = "        # Handle PIN entry callbacks"
        callback_pos = content.find(callback_section)
        
        if callback_pos > 0:
            # Check if pin_entry_ callback already exists
            if "callback_data.startswith(\"pin_entry_\")" not in content:
                pin_entry_callback = """        # Handle PIN entry link callbacks
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
                    from utils.pin_entry_system import create_pin_entry_keyboard, initialize_pin_session
                    pin_keyboard = create_pin_entry_keyboard()
                    
                    # Send PIN entry request privately
                    pin_message = f"🔐 *Enter your 4-digit PIN*\\n\\nPlease enter your PIN securely to complete the transfer of ₦{amount:,.2f} to {verified_name}"
                    send_reply(chat_id, pin_message, pin_keyboard)
                    
                    # Store transfer details in pin session
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
                new_content = content[:callback_pos] + pin_entry_callback + content[callback_pos:]
                
                # Write back to main.py
                with open("main.py", "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                print("✅ Added PIN entry callback handler")
            else:
                print("✓ PIN entry callback already exists")
        else:
            print("❌ Could not find PIN entry callbacks section")
    
    except Exception as e:
        print(f"❌ Error adding PIN entry callback: {e}")

def fix_verification_flow():
    """Fix the verification message and confirmation flow"""
    
    try:
        # Read main.py
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Remove "Verifying recipient account" message
        content = content.replace('send_reply(chat_id, "🔍 *Verifying recipient account...*")', '# No verification message shown to user')
        
        # 2. Replace "Xara-style confirmation sent"
        content = content.replace('send_reply(chat_id, "Xara-style confirmation sent")', 'send_reply(chat_id, "Transfer confirmation sent")')
        
        # 3. Enhance verification message format
        old_confirmation = 'confirmation_msg = f"""Click the Verify Transaction button'
        new_confirmation = 'confirmation_msg = f"""✅ *Account Verified: {verified_name}*\n\nYou\'re about to send ₦{parsed_xara[\'amount\']:,.2f} to:\n🏦 {verified_name} — {parsed_xara[\'account_number\']} ({bank_name.title()})\n\n👉 Please click the button below to verify this transaction:'
        content = content.replace(old_confirmation, new_confirmation)
        
        # Write back to main.py
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Fixed verification flow and messages")
    
    except Exception as e:
        print(f"❌ Error fixing verification flow: {e}")

if __name__ == "__main__":
    fix_pin_entry_flow()
