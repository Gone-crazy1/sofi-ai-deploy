#!/usr/bin/env python3
"""
🧹 SOFI AI PROJECT CLEANUP SCRIPT
Removes all unused, duplicate, and legacy files from the project
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """Create a backup before cleanup"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📦 Creating backup in: {backup_dir}")
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy all files to backup (excluding .git and node_modules)
    import glob
    for item in glob.glob("*"):
        if item not in ['.git', 'node_modules', '__pycache__', backup_dir]:
            if os.path.isfile(item):
                shutil.copy2(item, backup_dir)
            elif os.path.isdir(item):
                shutil.copytree(item, os.path.join(backup_dir, item), ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    
    print(f"✅ Backup created successfully in: {backup_dir}")
    return backup_dir

def remove_legacy_files():
    """Remove all legacy and unused files"""
    
    # Legacy main files
    legacy_main_files = [
        "main_broken.py",
        "main_temp.py", 
        "main_clean.py",
        "main_minimal.py",
        "main_fixed.py",
        "main_corrupted_20250703_212650.py",
        "main_corrupted_20250703_113041.py",
        "main_corrupted_20250703_112338.py",
        "main_clean_restore.py",
        "web_app.py"
    ]
    
    # Legacy HTML templates
    legacy_templates = [
        "templates/onboarding.html",
        "templates/pin-entry.html"
    ]
    
    # Legacy Python files
    legacy_python_files = [
        "complete_sofi_restart.py",
        "critical_bot_restoration.py",
        "ensure_pin_button.py",
        "fix_pin_entry_flow.py",
        "restore_main_py.py",
        "debug_pin_errors.py",
        "test_inline_pin_complete.py",
        "test_complete_inline_flow.py",
        "test_inline_keyboard_system.py",
        "deployment_readiness_check.py",
        "post_deployment_setup.py",
        "airtime_domain_fix_summary.py",
        "apply_security_patches.py",
        "beautiful_receipt_generator.py",
        "comprehensive_crypto_verification.py",
        "comprehensive_deployment.py",
        "comprehensive_end_to_end_test.py",
        "comprehensive_pre_deployment_test.py",
        "comprehensive_system_audit.py",
        "comprehensive_test_all_fixes.py",
        "focused_audit.py",
        "advanced_bitnob_test.py",
        "complete_feature_test.py",
        "admin_profit_demo.py",
        "crypto_rate_manager.py",
        "crypto_webhook_handler.py",
        "customer_friendly_crypto_calc.py",
        "debug_account_names.py",
        "debug_bitcoin_address_issue.py",
        "debug_constraint_issue.py",
        "debug_paystack_dedicated_account.py",
        "debug_paystack_pages.py"
    ]
    
    # Legacy documentation/guide files
    legacy_docs = [
        "ADMIN_PROFIT_SYSTEM_COMPLETE.md",
        "ADMIN_SECURITY_COMPLETE.md",
        "ADMIN_SECURITY_SETUP.md",
        "BANKING_SERVICE_SOLUTION.md",
        "BEAUTIFUL_RECEIPTS_COMPLETE.md",
        "BENEFICIARY_SYSTEM_CONFIRMATION.md",
        "CLEAN_DEPLOYMENT_GUIDE.md",
        "CLEANUP_COMPLETE.md",
        "COMPLETE_INTEGRATION_GUIDE.md",
        "COMPLETE_ONBOARDING_FLOW_IMPLEMENTED.md",
        "COMPREHENSIVE_DEPLOYMENT_STATUS.md",
        "CRITICAL_FIXES_DEPLOYED.md",
        "CRITICAL_MONNIFY_WEBHOOK_FIX.md",
        "CRYPTO_DEPLOYMENT_INSTRUCTIONS.md",
        "INLINE_KEYBOARD_SUCCESS.md",
        "INLINE_KEYBOARD_PIN_COMPLETE.md",
        "PIN_ENTRY_FLOW_VERIFICATION.md",
        "REVENUE_INTEGRATION_GUIDE.py",
        "MAIN_PY_INTEGRATION_CODE.py"
    ]
    
    # Legacy check/create/add files
    legacy_utility_files = [
        "check_airtime_status.py",
        "check_existing_addresses.py",
        "check_phone_column.py",
        "check_supabase_data.py",
        "check_supabase_schema.py",
        "check_table_count.py",
        "check_users_schema.py",
        "check_users_table_type.py",
        "add_balance_column_fix.py",
        "add_balance_column.py",
        "add_missing_columns.py",
        "add_phone_column.py",
        "create_beneficiaries_table.py",
        "create_crypto_table_simple.py",
        "create_crypto_table.py",
        "create_revenue_tracking_system.py",
        "create_schema_workaround.py",
        "CRITICAL_DATABASE_FIX.py",
        "CRITICAL_PROFIT_SYSTEM_FIX.py"
    ]
    
    # Legacy SQL files
    legacy_sql_files = [
        "add_crypto_rates_table.sql",
        "add_enhanced_onboarding_columns.sql",
        "add_user_columns.sql",
        "admin_profit_system.sql",
        "COMPLETE_CRYPTO_SETUP.sql",
        "complete_sofi_database_schema.sql",
        "create_beneficiaries_table.sql",
        "create_complete_crypto_tables.sql",
        "create_crypto_transactions_table.sql",
        "create_revenue_tracking_tables.sql",
        "create_settings_table.sql"
    ]
    
    # Combine all legacy files
    all_legacy_files = (
        legacy_main_files + 
        legacy_templates + 
        legacy_python_files + 
        legacy_docs + 
        legacy_utility_files + 
        legacy_sql_files
    )
    
    removed_count = 0
    
    print("\n🗑️  REMOVING LEGACY FILES:")
    print("=" * 50)
    
    for file_path in all_legacy_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
        else:
            print(f"⚠️  Not found: {file_path}")
    
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"✅ Files removed: {removed_count}")
    print(f"📁 Total files checked: {len(all_legacy_files)}")
    
    return removed_count

def main():
    """Main cleanup function"""
    print("🧹 SOFI AI PROJECT CLEANUP")
    print("=" * 50)
    print("This script will remove all unused, duplicate, and legacy files.")
    print("A backup will be created before any files are removed.")
    print("")
    
    response = input("Do you want to proceed? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cleanup cancelled.")
        return
    
    try:
        # Create backup
        backup_dir = create_backup()
        
        # Remove legacy files
        removed_count = remove_legacy_files()
        
        print(f"\n🎉 CLEANUP COMPLETE!")
        print(f"✅ {removed_count} legacy files removed")
        print(f"📦 Backup saved in: {backup_dir}")
        print(f"")
        print(f"🚀 PRODUCTION FILES REMAINING:")
        print(f"   - main.py (Flask app)")
        print(f"   - web_onboarding.html (onboarding page)")
        print(f"   - templates/secure_pin_verification.html (PIN page)")
        print(f"   - templates/index.html (landing page)")
        print(f"   - functions/transfer_functions.py (transfer logic)")
        print(f"   - sofi_assistant_functions.py (assistant)")
        print(f"   - utils/inline_pin_keyboard.py (PIN system)")
        print(f"   - Procfile (deployment config)")
        print(f"   - requirements.txt (dependencies)")
        print(f"")
        print(f"✨ Your project is now clean and ready for production!")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Project cleanup completed successfully!")
    else:
        print("\n❌ Project cleanup failed!")
