#!/usr/bin/env python3
"""
Check the state of main.py and create a diagnostics report
"""

import os
import sys

def check_main_py():
    """Check the state of main.py and report issues"""
    
    print("📊 MAIN.PY DIAGNOSTICS")
    print("=" * 50)
    
    try:
        # Check if file exists
        if not os.path.exists("main.py"):
            print("❌ main.py file not found!")
            return
            
        # Check file size
        file_size = os.path.getsize("main.py")
        print(f"📁 File size: {file_size} bytes")
        
        # Try to read the file
        try:
            with open("main.py", "r", encoding="utf-8") as f:
                content = f.read()
                print(f"✅ File can be read with UTF-8 encoding")
                lines = content.split("\n")
                print(f"📝 Line count: {len(lines)}")
                
                # Check for key components
                components = {
                    "webhook route": "@app.route('/webhook'," in content,
                    "message handler": "def process_message(" in content,
                    "callback handler": "def process_callback_query(" in content,
                    "PIN entry": "pin_entry" in content,
                    "Xara flow": "xara" in content.lower(),
                    "transfer verification": "verify_transfer_" in content,
                    "PIN digit handling": "add_pin_digit" in content
                }
                
                print("\n📋 Component Check:")
                for component, present in components.items():
                    status = "✅" if present else "❌"
                    print(f"{status} {component}")
                    
                # Check for corruption
                corruption = {
                    "NULL bytes": "\x00" in content,
                    "Invalid UTF-8": False,  # Already checked by reading with utf-8
                    "Truncated code blocks": content.count("{") != content.count("}"),
                    "Truncated strings": content.count('"') % 2 != 0 or content.count("'") % 2 != 0,
                    "Invalid indentation": any(line.startswith(" ") and len(line) > 0 and line[0] != " " for line in lines)
                }
                
                print("\n🔍 Corruption Check:")
                for issue, present in corruption.items():
                    status = "❌" if present else "✅"
                    print(f"{status} {issue}")
                
        except UnicodeDecodeError:
            print("❌ File cannot be read with UTF-8 encoding - likely binary corruption")
            
            # Try reading as binary
            with open("main.py", "rb") as f:
                binary_content = f.read()
                
                # Check first few bytes
                print(f"First 20 bytes (hex): {binary_content[:20].hex()}")
                
                # Look for common corruption patterns
                if binary_content.startswith(b"\xff\xfe"):
                    print("❗ File appears to be UTF-16 encoded (with BOM)")
                elif binary_content.startswith(b"\xef\xbb\xbf"):
                    print("❗ File appears to be UTF-8 with BOM")
                elif binary_content.startswith(b"\x00"):
                    print("❗ File starts with NULL bytes - severe corruption")
            
    except Exception as e:
        print(f"❌ Error checking main.py: {e}")
    
    print("\n🔧 Available Backups:")
    backup_files = [f for f in os.listdir(".") if f.startswith("main_") and f.endswith(".py")]
    for backup in backup_files:
        mod_time = datetime.fromtimestamp(os.path.getmtime(backup)).strftime("%Y-%m-%d %H:%M:%S")
        size = os.path.getsize(backup)
        print(f"📄 {backup} - {size} bytes, modified: {mod_time}")
    
    print("=" * 50)
    print("📝 Recommendation: Consider running the fix_pin_entry_flow.py script or using a recent backup")

if __name__ == "__main__":
    try:
        from datetime import datetime
        check_main_py()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
