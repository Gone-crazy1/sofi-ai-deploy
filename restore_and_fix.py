#!/usr/bin/env python3
"""
Restore main.py from backup and apply Xara-style flow fixes
"""

import os
import sys
import shutil
from datetime import datetime

def restore_from_backup():
    """Restore main.py from the most recent non-corrupted backup"""
    
    print("🔧 RESTORING FROM BACKUP")
    print("=" * 50)
    
    try:
        # Create a backup of the corrupted main.py
        backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupted_backup = f"main_corrupted_{backup_time}.py"
        
        print(f"📦 Creating backup of corrupted file: {corrupted_backup}")
        shutil.copy("main.py", corrupted_backup)
        
        # Find the most recent viable backup
        backup_candidates = [
            "main_backup_1751536956.py",
            "main_backup_17515364851759467.py",
            "main_backup.py",
            "main_fixed.py"
        ]
        
        for backup in backup_candidates:
            if os.path.exists(backup):
                print(f"📂 Checking backup: {backup}")
                
                # Verify backup integrity
                try:
                    with open(backup, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Simple integrity check
                    if len(content) > 1000 and "@app.route" in content:
                        print(f"✅ Found valid backup: {backup}")
                        
                        # Restore from this backup
                        print(f"🔄 Restoring main.py from {backup}...")
                        shutil.copy(backup, "main.py")
                        
                        # Apply Xara-style flow fixes
                        apply_fixes()
                        
                        print(f"✅ Restoration complete!")
                        return True
                        
                except Exception as e:
                    print(f"❌ Error checking backup {backup}: {e}")
                    continue
        
        print("❌ No valid backups found!")
        return False
        
    except Exception as e:
        print(f"❌ Error in restoration process: {e}")
        return False

def apply_fixes():
    """Apply Xara-style flow fixes to the restored main.py"""
    
    print("\n🔧 APPLYING XARA-STYLE FLOW FIXES")
    print("=" * 50)
    
    try:
        # Read main.py
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Fix PIN status check
        print("🔧 Fixing PIN status error...")
        content = content.replace('result["status"] == "complete"', 'result.get("status") == "complete"')
        
        # 2. Remove "Verifying recipient account..." message
        print("🔧 Removing verification message...")
        content = content.replace('send_reply(chat_id, "🔍 *Verifying recipient account...*")', '# No verification message shown to user')
        
        # 3. Replace "Xara-style confirmation sent" message
        print("🔧 Updating confirmation message...")
        content = content.replace('send_reply(chat_id, "Xara-style confirmation sent")', 'send_reply(chat_id, "Transfer confirmation sent")')
        
        # 4. Update verification callback to show account name properly
        print("🔧 Enhancing verification flow...")
        verify_pattern = "confirmation_msg = f\"\"\"Click the Verify Transaction button"
        enhanced_msg = """confirmation_msg = f\"\"\"✅ *Account Verified: {verified_name}*

You're about to send ₦{parsed_xara['amount']:,.2f} to:
🏦 {verified_name} — {parsed_xara['account_number']} ({bank_name.title()})

👉 Please click the button below to verify this transaction:\"\"\"
"""
        content = content.replace(verify_pattern, enhanced_msg)
        
        # 5. Update PIN entry button
        print("🔧 Enhancing PIN entry flow...")
        pin_pattern = "# Create PIN entry keyboard"
        enhanced_pin = """# Create enter PIN link button
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
                    
        if pin_pattern in content:
            # Find the section end to replace
            pin_section_start = content.find(pin_pattern)
            pin_section_end = content.find("send_reply(chat_id,", pin_section_start)
            pin_section_end = content.find("\n", pin_section_end)
            
            if pin_section_end > pin_section_start:
                pin_section = content[pin_section_start:pin_section_end]
                content = content.replace(pin_section, enhanced_pin)
        
        # 6. Add PIN entry callback handler
        print("🔧 Adding PIN entry callback handler...")
        callback_handler = """        # Handle PIN entry link callbacks
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
        # Find a good place to insert the callback handler
        pin_callback_section = "        # Handle PIN entry callbacks"
        if pin_callback_section in content:
            content = content.replace(pin_callback_section, callback_handler + pin_callback_section)
        
        # Write the updated content back to main.py
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("✅ Xara-style flow fixes applied successfully!")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")

if __name__ == "__main__":
    success = restore_from_backup()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ RESTORATION COMPLETE")
        print("🔄 Please restart the bot to apply all changes")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ RESTORATION FAILED")
        print("Please manually copy a working backup to main.py and run fix_pin_entry_flow.py")
        print("=" * 50)
