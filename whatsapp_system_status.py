#!/usr/bin/env python3
"""
Final WhatsApp-Only System Status Check
"""

import os
from pathlib import Path

def main():
    print("🎯 Final WhatsApp-Only System Status")
    print("=" * 40)
    
    # Count remaining files
    project_root = Path('.')
    
    # Core files that should exist
    required_files = {
        'assistant.py': '🤖 Core AI Assistant',
        'main.py': '🌐 Flask Web Server', 
        'start_whatsapp_sofi.py': '🚀 WhatsApp Startup',
        'README_WHATSAPP.md': '📖 Documentation',
        '.env.whatsapp-template': '⚙️ Environment Template',
        'utils/whatsapp_media.py': '📱 WhatsApp Media Handler'
    }
    
    print("CORE FILES CHECK:")
    all_core_present = True
    for file, desc in required_files.items():
        if os.path.exists(file):
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc} - MISSING!")
            all_core_present = False
    
    # Count remaining Python files
    py_files = list(project_root.glob('*.py'))
    py_files = [f for f in py_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
    
    print(f"\nFILE INVENTORY:")
    print(f"📁 Python files: {len(py_files)}")
    print(f"📁 SQL files: {len(list(project_root.glob('*.sql')))}")
    print(f"📁 Markdown files: {len(list(project_root.glob('*.md')))}")
    
    # Quick scan for legacy references in core files only
    legacy_in_core = 0
    core_files_to_check = ['assistant.py', 'main.py', 'start_whatsapp_sofi.py']
    
    print(f"\nCORE FILES LEGACY CHECK:")
    for file in core_files_to_check:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    legacy_count = content.lower().count('telegram')
                    legacy_count += content.lower().count('chat_id')
                    
                    if legacy_count > 0:
                        print(f"⚠️  {file}: {legacy_count} legacy references")
                        legacy_in_core += legacy_count
                    else:
                        print(f"✅ {file}: Clean")
            except Exception as e:
                print(f"❌ Could not check {file}: {e}")
    
    # Final status
    print(f"\n{'='*40}")
    if all_core_present and legacy_in_core == 0:
        print("🎉 STATUS: WHATSAPP-ONLY READY!")
        print("✅ Core system is clean and ready")
        print("✅ No legacy references in core files")
        print("📱 System configured for WhatsApp Cloud API only")
    elif all_core_present:
        print("⚠️  STATUS: MOSTLY READY")
        print("✅ All core files present")
        print(f"⚠️  {legacy_in_core} legacy references in core files")
    else:
        print("❌ STATUS: MISSING CORE FILES")
        print("Some essential files are missing")
    
    print(f"\n🎯 Next steps:")
    if all_core_present and legacy_in_core == 0:
        print("1. Configure your .env file with WhatsApp credentials")
        print("2. Run: python start_whatsapp_sofi.py")
        print("3. Test with a WhatsApp message!")
    else:
        print("1. Fix any missing core files")
        print("2. Clean remaining legacy references")
        print("3. Test the system")

if __name__ == "__main__":
    main()
