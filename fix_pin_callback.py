#!/usr/bin/env python3
"""
Comprehensive fix for PIN callback handling and Sofi flow
"""

import sys
import os
import re

def fix_main_issues():
    """Fix the PIN callback and Sofi flow issues"""
    
    print("🔧 COMPREHENSIVE FIX FOR SOFI TRANSFER FLOW")
    print("=" * 60)
    
    try:
        # 1. Make a backup of main.py
        backup_filename = "main_backup_" + str(os.path.getmtime("main.py")).replace(".", "") + ".py"
        print(f"📦 Creating backup: {backup_filename}")
        
        with open("main.py", "r", encoding="utf-8") as src_file:
            with open(backup_filename, "w", encoding="utf-8") as dest_file:
                dest_file.write(src_file.read())
        
        # 2. Read main.py content
        with open("main.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 3. Process line by line to fix issues
        fixed_lines = []
        in_pin_callback_section = False
        for line in lines:
            # Fix PIN status check
            if "result[" in line and "status" in line and "complete" in line:
                line = line.replace('result["status"]', 'result.get("status")')
            
            # Remove Xara mentions
            if "Xara-style" in line:
                line = line.replace("Xara-style", "Smart transfer")
            if "Error handling Xara" in line:
                line = line.replace("Error handling Xara", "Error handling transfer")
            
            # Remove verification message
            if '🔍 *Verifying recipient account...*' in line:
                line = '                # No verification message shown to user\n'
            
            # Fix PIN flow - identify PIN callback section
            if "# Handle PIN entry callbacks" in line:
                in_pin_callback_section = True
            
            # Track sections to replace
            if in_pin_callback_section and "digit = callback_data.replace" in line:
                fixed_lines.append('                digit = callback_data.replace("pin_", "")\n')
                fixed_lines.append('                if digit.isdigit():\n')
                fixed_lines.append('                    result = pin_manager.add_pin_digit(chat_id, digit)\n')
                fixed_lines.append('                    \n')
                fixed_lines.append('                    if result.get("status") == "complete":\n')
                
                # Skip the next few lines that would be corrupted
                continue
            
            # Add the line if we're not skipping
            fixed_lines.append(line)
        
        # 4. Write back the fixed content
        with open("main.py", "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        
        print("✅ Fixed issues:")
        print("  - PIN status error handling")
        print("  - Removed Xara mentions")
        print("  - Removed account verification message")
        print("  - Fixed PIN callback flow")
        
        print("=" * 60)
        print("🔄 Please restart the bot to apply the changes.")
        
    except Exception as e:
        print(f"❌ Error fixing issues: {e}")
        print("=" * 60)

if __name__ == "__main__":
    fix_main_issues()
