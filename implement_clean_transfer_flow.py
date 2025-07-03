#!/usr/bin/env python3
"""
Implement clean transfer flow with proper verification feedback
"""

import sys
import os
import re

def implement_clean_transfer_flow():
    """Implement clean transfer flow with better account verification feedback"""
    
    print("🔧 IMPLEMENTING CLEAN TRANSFER FLOW")
    print("=" * 50)
    
    try:
        # Backup main.py first
        backup_file = f"main_backup_{int(os.path.getmtime('main.py'))}.py"
        print(f"📦 Creating backup as {backup_file}")
        with open("main.py", "r", encoding="utf-8") as src:
            with open(backup_file, "w", encoding="utf-8") as dest:
                dest.write(src.read())
        
        # Read main.py
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Fix the account verification and confirmation message
        print("✅ Updating account verification message...")
        verification_pattern = re.compile(
            r'verify_result = paystack\.verify_account_number.*?'
            r'send_reply\(chat_id, confirmation_msg, verify_keyboard\)',
            re.DOTALL
        )
        
        if verification_pattern.search(content):
            new_verification_code = '''verify_result = paystack.verify_account_number(parsed_xara['account_number'], bank_code)
                
                if not verify_result.get("success") or not verify_result.get("verified"):
                    return f"❌ *Account verification failed*\\n\\n{verify_result.get('error', 'Invalid account details')}"
                
                verified_name = verify_result["account_name"]
                
                # Step 2: Show professional confirmation with verified account details
                confirmation_msg = f"""✅ *Account Verified: {verified_name}*

You're about to send *₦{parsed_xara['amount']:,.2f}* to:
🏦 {verified_name} — {parsed_xara['account_number']} ({bank_name})

👉 Please click the button below to enter your 4-digit transaction PIN securely:"""
                
                # Send confirmation with enter PIN button
                verify_keyboard = {
                    "inline_keyboard": [[
                        {"text": "🔐 Enter My PIN", "callback_data": f"pin_entry_{chat_id}_{parsed_xara['amount']}_{parsed_xara['account_number']}_{bank_code}_{verified_name.replace(' ', '_')}"}
                    ]]
                }
                
                send_reply(chat_id, confirmation_msg, verify_keyboard)'''
            
            content = verification_pattern.sub(new_verification_code, content)
        else:
            print("⚠️ Could not find verification pattern")
        
        # 2. Fix the PIN entry callback handler
        print("✅ Updating PIN entry callback handler...")
        pin_entry_pattern = re.compile(
            r'# Handle PIN entry link callbacks.*?elif callback_data\.startswith\("pin_entry_"\):.*?return jsonify\(\{"success": True\}\), 200',
            re.DOTALL
        )
        
        if pin_entry_pattern.search(content):
            new_pin_entry_code = '''# Handle PIN entry link callbacks
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
                    return jsonify({"success": True}), 200'''
            
            content = pin_entry_pattern.sub(new_pin_entry_code, content)
        else:
            print("⚠️ Could not find PIN entry pattern")
        
        # 3. Fix PIN digit handling (result["status"] issue)
        print("✅ Fixing PIN status error...")
        content = content.replace('result["status"]', 'result.get("status")')
        
        # 4. Write updated content back to main.py
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("=" * 50)
        print("✅ Clean transfer flow implemented!")
        print("🔄 Please restart the bot to apply the changes.")
        
    except Exception as e:
        print(f"❌ Error implementing clean transfer flow: {e}")
        print("=" * 50)

if __name__ == "__main__":
    implement_clean_transfer_flow()
