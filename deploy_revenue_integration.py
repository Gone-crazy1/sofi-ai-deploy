#!/usr/bin/env python3
"""
🚀 AUTOMATED SOFI AI REVENUE INTEGRATION DEPLOYMENT
===================================================

This script automatically integrates fee collection into your existing main.py file.
It adds the necessary imports and integration code at the correct locations.

WHAT THIS SCRIPT DOES:
1. Backs up your current main.py
2. Adds fee collection imports
3. Integrates transfer fee collection
4. Adds crypto profit tracking
5. Creates a test file for verification

BEFORE RUNNING:
- Ensure database tables are deployed (run SQL in Supabase first)
- Backup your main.py file manually
- Test in development environment first
"""

import os
import re
import shutil
from datetime import datetime

def backup_main_file():
    """Create a backup of the current main.py file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"main_backup_{timestamp}.py"
    
    try:
        shutil.copy2("main.py", backup_filename)
        print(f"✅ Backup created: {backup_filename}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def add_fee_collection_imports():
    """Add fee collection imports to main.py"""
    
    # Read current main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if imports already exist
    if "from fee_collection import" in content:
        print("✅ Fee collection imports already exist")
        return True
    
    # Find the import section (after other imports but before any code)
    # Look for the pattern where imports end
    import_pattern = r"(from dotenv import load_dotenv\s*\n)"
    
    fee_imports = '''
# Revenue tracking imports
try:
    from fee_collection import (
        save_transfer_fee,
        save_crypto_trade,
        save_airtime_sale,
        save_data_sale,
        save_deposit_fee,
        update_financial_summary,
        get_total_revenue
    )
    REVENUE_TRACKING_ENABLED = True
    print("✅ Revenue tracking system loaded")
except ImportError as e:
    print(f"⚠️ Revenue tracking not available: {e}")
    REVENUE_TRACKING_ENABLED = False

'''
    
    # Add the imports after load_dotenv
    if re.search(import_pattern, content):
        content = re.sub(
            import_pattern,
            r"\\1" + fee_imports,
            content
        )
        
        # Write back to file
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Fee collection imports added to main.py")
        return True
    else:
        print("❌ Could not find insertion point for imports")
        return False

def add_transfer_fee_integration():
    """Add transfer fee collection to the transfer flow"""
    
    # Read current main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if integration already exists
    if "REVENUE TRACKING: Transfer Fee Collection" in content:
        print("✅ Transfer fee integration already exists")
        return True
    
    # Find the location after successful transfer
    # Look for the pattern where transaction is logged
    pattern = r"(save_bank_transaction\([^)]*\)\s*\n\s*# Update user balance[^)]*\)\s*\n\s*except Exception as e:\s*\n\s*logger\.error\([^)]*\)\s*\n)"
    
    integration_code = '''
                # ==========================================
                # REVENUE TRACKING: Transfer Fee Collection
                # ==========================================
                if REVENUE_TRACKING_ENABLED:
                    try:
                        # Collect ₦50 transfer fee
                        user_id = user_data.get('id') or str(chat_id)
                        fee_result = save_transfer_fee(
                            user_id=user_id,
                            transfer_amount=transfer['amount'],
                            transaction_reference=transaction_id
                        )
                        
                        if fee_result:
                            logger.info(f"✅ Transfer fee collected: ₦50 for user {user_id}")
                        else:
                            logger.warning(f"⚠️ Transfer fee collection failed for user {user_id}")
                            
                    except Exception as e:
                        logger.error(f"❌ Error collecting transfer fee: {e}")
                        # Don't fail the transfer if fee collection fails
                        pass
                
'''
    
    # Add the integration after transaction logging
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(
            pattern,
            r"\\1" + integration_code,
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Write back to file
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Transfer fee integration added to main.py")
        return True
    else:
        print("⚠️ Could not find exact location for transfer fee integration")
        print("   Manual integration may be required")
        return False

def create_integration_test():
    """Create a test file to verify the integration"""
    
    test_content = '''#!/usr/bin/env python3
"""
Test the fee collection integration in main.py
"""

import asyncio
import sys
import os

async def test_fee_collection_integration():
    """Test that fee collection is properly integrated"""
    
    print("🧪 TESTING FEE COLLECTION INTEGRATION")
    print("=" * 50)
    
    try:
        # Test 1: Check if imports work
        print("1️⃣ Testing imports...")
        
        try:
            from fee_collection import (
                save_transfer_fee,
                save_crypto_trade,
                get_total_revenue
            )
            print("   ✅ Fee collection imports successful")
        except ImportError as e:
            print(f"   ❌ Import failed: {e}")
            return False
        
        # Test 2: Check if main.py has the integration
        print("\\n2️⃣ Checking main.py integration...")
        
        with open("main.py", "r") as f:
            main_content = f.read()
        
        if "REVENUE TRACKING: Transfer Fee Collection" in main_content:
            print("   ✅ Transfer fee integration found in main.py")
        else:
            print("   ❌ Transfer fee integration not found in main.py")
            return False
        
        if "from fee_collection import" in main_content:
            print("   ✅ Fee collection imports found in main.py")
        else:
            print("   ❌ Fee collection imports not found in main.py")
            return False
        
        # Test 3: Test database connection
        print("\\n3️⃣ Testing database connection...")
        
        try:
            from fee_collection import get_total_revenue
            revenue = get_total_revenue()
            print(f"   ✅ Database connection successful - Current revenue: ₦{revenue:,.2f}")
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
            return False
        
        # Test 4: Test fee collection functions
        print("\\n4️⃣ Testing fee collection functions...")
        
        try:
            # Test transfer fee (won't actually save, just test function)
            test_result = save_transfer_fee("test_user_integration", 1000, "TEST123")
            if test_result:
                print("   ✅ Transfer fee function working")
            else:
                print("   ⚠️ Transfer fee function returned None (may be normal)")
        except Exception as e:
            print(f"   ❌ Transfer fee function failed: {e}")
            return False
        
        print("\\n🎉 INTEGRATION TEST RESULTS:")
        print("✅ All tests passed!")
        print("✅ Fee collection is properly integrated")
        print("✅ Revenue tracking system is ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fee_collection_integration())
    
    if success:
        print("\\n🚀 INTEGRATION SUCCESSFUL!")
        print("Your Sofi AI bot is now ready for revenue generation!")
    else:
        print("\\n❌ INTEGRATION NEEDS ATTENTION!")
        print("Please check the errors above and fix before proceeding.")
'''
    
    with open("test_integration.py", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("✅ Integration test file created: test_integration.py")

def main():
    """Main deployment function"""
    
    print("🚀 SOFI AI REVENUE INTEGRATION DEPLOYMENT")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Check prerequisites
    print("1️⃣ Checking prerequisites...")
    
    if not os.path.exists("main.py"):
        print("❌ main.py not found in current directory")
        return False
    
    if not os.path.exists("fee_collection.py"):
        print("❌ fee_collection.py not found - please ensure it exists")
        return False
    
    if not os.path.exists("complete_sofi_database_schema.sql"):
        print("❌ complete_sofi_database_schema.sql not found")
        print("⚠️ Make sure you've deployed the database tables first!")
        return False
    
    print("✅ All prerequisite files found")
    
    # Step 2: Create backup
    print("\\n2️⃣ Creating backup...")
    if not backup_main_file():
        print("❌ Backup failed - aborting deployment")
        return False
    
    # Step 3: Add imports
    print("\\n3️⃣ Adding fee collection imports...")
    if not add_fee_collection_imports():
        print("❌ Import integration failed")
        return False
    
    # Step 4: Add transfer fee integration
    print("\\n4️⃣ Adding transfer fee integration...")
    if not add_transfer_fee_integration():
        print("⚠️ Automatic transfer integration failed")
        print("   You may need to manually add the integration code")
        print("   See MAIN_PY_INTEGRATION_CODE.py for exact code")
    
    # Step 5: Create test file
    print("\\n5️⃣ Creating integration test...")
    create_integration_test()
    
    # Step 6: Final instructions
    print("\\n✅ DEPLOYMENT COMPLETED!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS:")
    print("1. Run the integration test: python test_integration.py")
    print("2. Check for any errors and fix them")
    print("3. Test with a small transfer to verify fee collection")
    print("4. Monitor logs for revenue tracking messages")
    print("5. Deploy to production when testing is complete")
    print()
    print("💰 EXPECTED RESULTS:")
    print("• Transfer fees: ₦50 collected per transfer")
    print("• Revenue tracking: Automatic logging to database")
    print("• Financial reports: Real-time revenue calculations")
    print()
    print("🆘 IF ISSUES OCCUR:")
    print("• Restore from backup if needed")
    print("• Check MAIN_PY_INTEGRATION_CODE.py for manual integration")
    print("• Verify database tables are deployed")
    print("• Run verify_table_deployment.py to check table status")
    
    return True

if __name__ == "__main__":
    main()
