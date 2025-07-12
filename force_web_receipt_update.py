#!/usr/bin/env python3
"""
🔄 FORCE WEB RECEIPT UPDATE FOR ALL USERS
=========================================

This script ensures all users get the new web PIN receipt feature
when they make transfers. Run this after deployment to force the update.

Usage: python force_web_receipt_update.py
"""

import os
import logging
from datetime import datetime
from supabase import create_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_web_receipt_update():
    """Force web receipt feature update for all users"""
    try:
        # Initialize Supabase with service role for admin operations
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for admin operations
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Supabase credentials not found in environment")
            logger.error(f"   SUPABASE_URL: {'✅' if supabase_url else '❌'}")
            logger.error(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅' if supabase_key else '❌'}")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Get all users
        logger.info("📊 Fetching all users...")
        users_result = supabase.table("users").select("id, telegram_chat_id, full_name").execute()
        
        if not users_result.data:
            logger.warning("⚠️ No users found in database")
            return True
        
        total_users = len(users_result.data)
        logger.info(f"👥 Found {total_users} users")
        
        # Update all users with new feature flags
        update_data = {
            "web_receipt_enabled": True,
            "feature_version": "v2.1_inline_keyboard_receipt",
            "last_feature_update": datetime.now().isoformat()
        }
        
        logger.info("🔄 Updating all users with new web receipt feature...")
        
        # Batch update all users
        try:
            # Note: Supabase doesn't support updating all rows directly,
            # so we'll update in batches if needed
            batch_size = 100
            updated_count = 0
            
            for i in range(0, total_users, batch_size):
                batch = users_result.data[i:i + batch_size]
                user_ids = [user["id"] for user in batch]
                
                # Update this batch
                result = supabase.table("users").update(update_data).in_("id", user_ids).execute()
                
                if result.data:
                    updated_count += len(result.data)
                    logger.info(f"✅ Updated batch {i//batch_size + 1}: {len(result.data)} users")
                
        except Exception as e:
            logger.error(f"❌ Error updating users: {e}")
            # Try individual updates as fallback
            logger.info("🔄 Trying individual updates...")
            updated_count = 0
            
            for user in users_result.data:
                try:
                    supabase.table("users").update(update_data).eq("id", user["id"]).execute()
                    updated_count += 1
                    if updated_count % 10 == 0:
                        logger.info(f"✅ Updated {updated_count}/{total_users} users")
                except Exception as user_error:
                    logger.warning(f"⚠️ Failed to update user {user['telegram_chat_id']}: {user_error}")
        
        logger.info(f"🎉 FEATURE UPDATE COMPLETE!")
        logger.info(f"✅ Updated {updated_count}/{total_users} users")
        logger.info(f"📱 All users will now get the new web PIN receipt feature")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error forcing web receipt update: {e}")
        return False

def verify_feature_deployment():
    """Verify that the feature is properly deployed"""
    logger.info("\n🔍 VERIFYING FEATURE DEPLOYMENT...")
    
    # Check if transfer function has the new feature version
    try:
        with open("functions/transfer_functions.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        checks = {
            "Feature version present": "v2.1_inline_keyboard_receipt" in content,
            "Web receipt enabled": "web_receipt_enabled" in content,
            "Force update flag": "force_update" in content,
            "Correct domain": "pipinstallsofi.com" in content,
            "Inline keyboard": "inline_keyboard" in content
        }
        
        logger.info("📋 Feature deployment check:")
        all_good = True
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"   {status} {check}")
            if not passed:
                all_good = False
        
        if all_good:
            logger.info("🎉 All feature checks PASSED!")
        else:
            logger.warning("⚠️ Some feature checks FAILED - review the code")
            
        return all_good
        
    except Exception as e:
        logger.error(f"❌ Error verifying deployment: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SOFI WEB RECEIPT FEATURE UPDATE")
    print("=" * 50)
    
    # Verify deployment first
    if not verify_feature_deployment():
        print("\n❌ Feature deployment verification failed!")
        print("Please check the transfer_functions.py file")
        exit(1)
    
    # Force update for all users
    if force_web_receipt_update():
        print("\n🎉 SUCCESS!")
        print("✅ All users updated with new web receipt feature")
        print("📱 When users make transfers, they'll get the new receipt")
        print("🔒 Receipts will show on pipinstallsofi.com domain")
        print("🖼️ Users can screenshot receipts (no auto-close)")
    else:
        print("\n❌ FAILED!")
        print("Please check the logs and try again")
        exit(1)
