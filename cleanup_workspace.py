"""
Safe Workspace Cleanup Script
============================
This script will remove unnecessary files while preserving your core application.
"""

import os
import shutil
from pathlib import Path

def cleanup_workspace():
    """Clean up workspace by removing test files, old migrations, and documentation"""
    
    base_path = Path(".")
    deleted_files = []
    deleted_dirs = []
    
    # Test files to remove
    test_patterns = [
        "test_*.py",
        "*_test.py", 
        "quick_test*.py",
        "simple_test*.py",
        "comprehensive_test*.py",
        "debug_*.py",
        "demo_*.py",
        "check_*.py",
        "verify_*.py",
        "run_*_test*.py"
    ]
    
    # Migration/fix files to remove
    migration_patterns = [
        "add_*.py",
        "fix_*.py", 
        "deploy_*.py",
        "create_*.py",
        "update_*.py",
        "migrate_*.py",
        "apply_*.py",
        "comprehensive_*.py",
        "*_deployment*.py",
        "*_fix*.py"
    ]
    
    # SQL files to remove (keep only essential schemas)
    sql_patterns = [
        "add_*.sql",
        "create_*.sql",
        "deploy_*.sql", 
        "fix_*.sql",
        "*_schema.sql",
        "enable_*.sql",
        "setup_*.sql"
    ]
    
    # Documentation to remove (keep only essential)
    doc_patterns = [
        "*_COMPLETE.md",
        "*_GUIDE.md",
        "*_STATUS.md", 
        "*_SUMMARY.md",
        "*_READY.md",
        "*_DEPLOYMENT*.md",
        "*_IMPLEMENTATION*.md",
        "*_VERIFICATION*.md"
    ]
    
    # Log and backup files
    misc_patterns = [
        "*.txt",
        "*_backup.py",
        "*_fixed.py",
        "*_alternative.py",
        "logs.*"
    ]
    
    # Files to specifically keep (override patterns)
    keep_files = [
        "requirements.txt",
        "runtime.txt", 
        "main.py",
        ".env",
        "Procfile",
        "render.yaml",
        ".gitignore"
    ]
    
    all_patterns = test_patterns + migration_patterns + sql_patterns + doc_patterns + misc_patterns
    
    print("🧹 Starting workspace cleanup...")
    print("=" * 50)
    
    for pattern in all_patterns:
        for file_path in base_path.glob(pattern):
            if file_path.name not in keep_files and file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_files.append(str(file_path))
                    print(f"❌ Deleted: {file_path}")
                except Exception as e:
                    print(f"⚠️  Could not delete {file_path}: {e}")
    
    # Remove empty directories  
    for item in base_path.iterdir():
        if item.is_dir() and item.name not in ['.git', '.vscode', 'venv', '__pycache__']:
            try:
                if not any(item.iterdir()):  # Empty directory
                    shutil.rmtree(item)
                    deleted_dirs.append(str(item))
                    print(f"📁 Removed empty dir: {item}")
            except Exception as e:
                print(f"⚠️  Could not remove directory {item}: {e}")
    
    print("\n" + "=" * 50)
    print(f"✅ Cleanup complete!")
    print(f"📁 Files deleted: {len(deleted_files)}")
    print(f"📂 Directories removed: {len(deleted_dirs)}")
    
    return deleted_files, deleted_dirs

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete many files!")
    print("Make sure you have a backup or are using git!")
    
    response = input("\\nProceed with cleanup? (yes/no): ").lower().strip()
    
    if response == 'yes':
        deleted_files, deleted_dirs = cleanup_workspace()
        
        print("\\n📝 Summary of essential files remaining:")
        essential_files = [
            "main.py", ".env", "requirements.txt", "Procfile", 
            "render.yaml", "runtime.txt", ".gitignore"
        ]
        
        for file in essential_files:
            if Path(file).exists():
                print(f"✅ {file}")
            else:
                print(f"❌ {file} - MISSING!")
                
        print("\\n📁 Essential directories remaining:")
        essential_dirs = [
            "assistant", "functions", "utils", "templates", 
            "monnify", "crypto", "nlp", "webhooks"
        ]
        
        for dir_name in essential_dirs:
            if Path(dir_name).exists():
                print(f"✅ {dir_name}/")
            else:
                print(f"❌ {dir_name}/ - MISSING!")
                
    else:
        print("❌ Cleanup cancelled.")
