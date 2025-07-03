#!/usr/bin/env python3
"""
Restore corrupted main.py file by creating a fresh copy with proper Xara-style transfer flow
"""

import os
import sys
import shutil
from datetime import datetime

def restore_main_py():
    """Restore the corrupted main.py file"""
    
    print("🔧 RESTORING CORRUPTED main.py FILE")
    print("=" * 50)
    
    # Create a backup of the corrupted file
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"main_corrupted_{backup_time}.py"
    
    try:
        # Make backup of current corrupted file
        print(f"📦 Creating backup: {backup_file}")
        shutil.copy("main.py", backup_file)
        
        # Find most recent backup that's not corrupted
        backup_files = [f for f in os.listdir(".") if f.startswith("main_") and f.endswith(".py")]
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Try to find a working backup
        working_backup = None
        for backup in backup_files:
            # Skip the corrupted backup we just created
            if backup == backup_file:
                continue
                
            # Check if this backup contains PIN handler code
            with open(backup, "r", encoding="utf-8") as f:
                content = f.read()
                
            if "def add_pin_digit" in content and not "\\u0" in content:
                working_backup = backup
                break
        
        if working_backup:
            print(f"✅ Found working backup: {working_backup}")
            shutil.copy(working_backup, "main.py")
            print("✅ Restored main.py from backup")
            
            # Now apply the necessary fixes for the PIN entry flow
            fix_pin_entry_flow()
            
        else:
            print("❌ No working backup found. Need to manually reconstruct the file.")
            # In this case we'd need to manually reconstruct the file from scratch
            # This would be a much larger effort
    
    except Exception as e:
        print(f"❌ Error restoring main.py: {e}")
    
    print("=" * 50)
    print("🔄 Please restart the bot after checking the file for errors.")

def fix_pin_entry_flow():
    """Fix the PIN entry flow in main.py to match the requirements"""
    
    print("🔧 Fixing PIN entry flow...")
    
    try:
        # Read the restored main.py
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Fix PIN status check
        content = content.replace('result["status"] == "complete"', 'result.get("status") == "complete"')
        
        # 2. Fix confirmation messages
        content = content.replace("Xara-style confirmation sent", "Transfer confirmation sent")
        content = content.replace("🔍 *Verifying recipient account...*", "✅ *Account Verified*")
        
        # 3. Update verification callback section
        verify_section_start = "        elif callback_data.startswith(\"verify_transfer_\"):"
        verify_section_pos = content.find(verify_section_start)
        
        if verify_section_pos > 0:
            # Find the PIN entry keyboard section
            post_verify = content[verify_section_pos:]
            pin_entry_pos = post_verify.find("# Create PIN entry keyboard")
            
            if pin_entry_pos > 0:
                # Find the end of PIN entry section
                pin_send_pos = post_verify.find("send_reply(chat_id,", pin_entry_pos)
                pin_end_pos = post_verify.find("\n", pin_send_pos)
                
                if pin_end_pos > 0:
                    # Split the content
                    before_pin = content[:verify_section_pos + pin_entry_pos]
                    after_pin = content[verify_section_pos + pin_entry_pos + pin_end_pos:]
                    
                    # Create new PIN entry code
                    new_pin_code = """# Create enter PIN link button
                    pin_link_keyboard = {
                        "inline_keyboard": [[
                            {"text": "🔐 Enter My PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                        ]]
                    }
                    
                    # Send PIN entry request
                    pin_message = f"✅ *Account Verified: {verified_name}*\\n\\nYou're about to send ₦{amount:,.2f} to:\\n🏦 {verified_name} — {account_number} ({bank_name})\\n\\n👉 Please click the button below to enter your 4-digit transaction PIN securely:"
                    send_reply(chat_id, pin_message, pin_link_keyboard)"""
                    
                    # Combine the parts
                    new_content = before_pin + new_pin_code + after_pin
                    
                    # Update the content
                    content = new_content
        
        # 4. Ensure PIN entry callback is present
        callback_handler_start = "        # Handle transfer verification callbacks"
        callback_handler_pos = content.find(callback_handler_start)
        
        if callback_handler_pos > 0:
            # Find position to insert the new PIN entry callback handler
            pin_entry_pos = content.find("        # Handle PIN entry callbacks", callback_handler_pos)
            
            if pin_entry_pos > 0:
                # Check if pin_entry_ callback exists
                if "callback_data.startswith(\"pin_entry_\")" not in content:
                    # Create new PIN entry callback handler
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
                    # Insert the new callback handler before the PIN entry section
                    content = content[:pin_entry_pos] + pin_entry_callback + content[pin_entry_pos:]
        
        # Write the updated content back to main.py
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Successfully fixed PIN entry flow!")
        
    except Exception as e:
        print(f"❌ Error fixing PIN entry flow: {e}")

if __name__ == "__main__":
    restore_main_py()
