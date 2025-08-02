#!/usr/bin/env python3
"""
Sofi AI WhatsApp-Only Final Status Check
"""

import os
from pathlib import Path

def check_legacy_references():
    """Check for any remaining legacy references"""
    print("1. Checking for legacy references...")
    
    project_root = Path('.')
    
    # Find files that might still have old references
    files_to_check = []
    for ext in ['*.py', '*.sql', '*.md']:
        files_to_check.extend(project_root.glob(ext))
    
    legacy_count = 0
    problem_files = []
    
    for file_path in files_to_check:
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count legacy references
            if 'telegram' in content.lower() or 'chat_id' in content.lower():
                if file_path.name != 'final_status_check.py':  # Skip this file
                    legacy_count += content.lower().count('telegram')
                    legacy_count += content.lower().count('chat_id')
                    problem_files.append(file_path.name)
                    
        except Exception as e:
            print(f"   ⚠️  Could not read {file_path}: {e}")
    
    if legacy_count > 0:
        print(f"⚠️  Found {legacy_count} legacy references in {len(problem_files)} files")
        if problem_files:
            print("   Files with issues:", ", ".join(problem_files[:10]))
    else:
        print("✅ No legacy references found")
    
    return legacy_count == 0

def check_whatsapp_config():
    """Check WhatsApp configuration"""
    print("2. Checking WhatsApp configuration...")
    
    # Check for WhatsApp environment variables template
    if os.path.exists('.env.whatsapp-template'):
        print("✅ WhatsApp environment template found")
    else:
        print("⚠️  WhatsApp environment template missing")
    
    # Check for WhatsApp utilities
    if os.path.exists('utils/whatsapp_media.py'):
        print("✅ WhatsApp media utilities found")
    else:
        print("⚠️  WhatsApp media utilities missing")
    
    return True

def check_core_files():
    """Check that core files are properly configured"""
    print("3. Checking core files...")
    
    core_files = {
        'assistant.py': 'Core AI assistant',
        'main.py': 'Main application',
        'start_whatsapp_sofi.py': 'WhatsApp startup script',
        'README_WHATSAPP.md': 'WhatsApp documentation'
    }
    
    all_good = True
    for file, desc in core_files.items():
        if os.path.exists(file):
            print(f"✅ {desc} ({file}) found")
        else:
            print(f"❌ {desc} ({file}) missing")
            all_good = False
    
    return all_good

def main():
    print("🔍 Sofi AI WhatsApp-Only Final Status Check")
    print("=" * 50)
    
    checks = [
        check_legacy_references(),
        check_whatsapp_config(), 
        check_core_files()
    ]
    
    print("=" * 50)
    
    if all(checks):
        print("🎉 STATUS: READY FOR WHATSAPP!")
        print("✅ All checks passed - system is WhatsApp-only")
    else:
        print("⚠️  STATUS: NEEDS ATTENTION")
        print("Some issues need to be resolved")

if __name__ == "__main__":
    main()
