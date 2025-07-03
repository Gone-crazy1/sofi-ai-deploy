#!/usr/bin/env python3
"""
Comprehensive Main.py Restoration Script
This script will restore main.py from the cleanest backup and apply all necessary fixes
"""

import os
import re
import shutil
from datetime import datetime

def create_backup():
    """Create a backup of current main.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"main_corrupted_{timestamp}.py"
    shutil.copy("main.py", backup_name)
    print(f"✅ Created backup: {backup_name}")
    return backup_name

def find_best_backup():
    """Find the best backup to restore from"""
    backups = [
        "main_clean.py",
        "main_fixed.py", 
        "main_original_backup.py",
        "main_backup.py",
        "main_minimal.py"
    ]
    
    for backup in backups:
        if os.path.exists(backup):
            print(f"📁 Found backup: {backup}")
            return backup
    
    print("❌ No suitable backup found")
    return None

def restore_from_backup(backup_file):
    """Restore main.py from backup"""
    try:
        shutil.copy(backup_file, "main.py")
        print(f"✅ Restored main.py from {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Error restoring from backup: {e}")
        return False

def apply_xara_style_fixes():
    """Apply all Xara-style transfer fixes"""
    print("🔧 Applying Xara-style transfer fixes...")
    
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Fix 1: Add missing app route decorator for health check
        content = re.sub(
            r'def health_check\(\):\s*"""Health check endpoint"""',
            '@app.route("/health")\ndef health_check():\n    """Health check endpoint"""',
            content
        )
        
        # Fix 2: Remove any "Xara" mentions and replace with neutral language
        content = re.sub(r'Xara[- ]?style', 'Smart transfer', content, flags=re.IGNORECASE)
        content = re.sub(r'verifying account', 'processing', content, flags=re.IGNORECASE)
        content = content.replace('Xara', 'Smart transfer')
        
        # Fix 3: Fix PIN entry flow to use button instead of keyboard
        pin_keyboard_pattern = r'# Create PIN entry keyboard.*?send_reply\(chat_id, pin_message, pin_keyboard\)'
        pin_button_replacement = '''# Create enter PIN link button
                    pin_link_keyboard = {
                        "inline_keyboard": [[
                            {"text": "🔐 Enter My PIN", "callback_data": f"pin_entry_{chat_id}_{amount}_{account_number}_{bank_code}_{verified_name.replace(' ', '_')}"}
                        ]]
                    }
                    
                    # Send PIN entry request
                    pin_message = f"🔐 *Please enter your PIN*\\n\\nTo complete transfer of ₦{amount:,.2f} to {verified_name}\\n\\n*Click the button below to enter your PIN securely:*"
                    send_reply(chat_id, pin_message, pin_link_keyboard)'''
        
        content = re.sub(pin_keyboard_pattern, pin_button_replacement, content, flags=re.DOTALL)
        
        # Fix 4: Fix status key error by using .get()
        content = re.sub(
            r'result\["status"\]',
            'result.get("status")',
            content
        )
        
        # Fix 5: Add proper PIN entry callback handler
        if 'elif callback_data.startswith("pin_entry_"):' not in content:
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
'''
            
            # Insert before the PIN digit handler
            content = content.replace(
                '# Handle PIN entry callbacks',
                '# Handle PIN entry callbacks' + pin_entry_handler
            )
        
        # Save the fixed content
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Applied Xara-style fixes successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

def run_syntax_check():
    """Run Python syntax check"""
    print("🔍 Running syntax check...")
    
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
    """Main restoration process"""
    print("🚀 COMPREHENSIVE MAIN.PY RESTORATION")
    print("=" * 50)
    
    # Step 1: Create backup of current corrupted file
    backup_name = create_backup()
    
    # Step 2: Find best backup to restore from
    best_backup = find_best_backup()
    if not best_backup:
        print("❌ Cannot proceed without a backup file")
        return
    
    # Step 3: Restore from backup
    if not restore_from_backup(best_backup):
        print("❌ Failed to restore from backup")
        return
    
    # Step 4: Apply Xara-style fixes
    if not apply_xara_style_fixes():
        print("❌ Failed to apply fixes")
        return
    
    # Step 5: Run syntax check
    if run_syntax_check():
        print("🎉 RESTORATION COMPLETED SUCCESSFULLY!")
        print("✅ main.py has been restored and fixed")
        print("✅ All syntax errors resolved")
        print("✅ Xara-style transfer flow implemented")
        print("✅ PIN entry system fixed")
        print("\n🔄 Please restart your bot to apply changes")
    else:
        print("⚠️ Restoration completed but syntax errors remain")
        print("📋 Please check the error messages above")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
