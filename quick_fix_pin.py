#!/usr/bin/env python3
"""
🚀 QUICK FIX - DISABLE PIN_ATTEMPTS TABLE DEPENDENCY
===============================================================
This script temporarily fixes the PIN validation by disabling
the pin_attempts table dependency and using existing users table
===============================================================
"""

import os
import sys

def fix_permanent_memory():
    """Fix permanent_memory.py to not use pin_attempts table"""
    file_path = "utils/permanent_memory.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found")
        return False
    
    # Read the current file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace pin_attempts table usage with users table usage
    fixes = [
        # Fix the track_pin_attempt function
        ('self.client.table("pin_attempts")', 'self.client.table("users")'),
        # Comment out complex pin_attempts logic for now
        ('result = self.client.table("users").select("*").eq("user_id", user_id).execute()', 
         'result = self.client.table("users").select("pin_attempts, pin_locked_until").eq("id", user_id).execute()'),
    ]
    
    modified = False
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"✅ Fixed: {old[:50]}...")
    
    if modified:
        # Backup original
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            with open(file_path, 'r', encoding='utf-8') as original:
                f.write(original.read())
        print(f"📁 Backup created: {backup_path}")
        
        # Write fixed version
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed {file_path}")
        return True
    else:
        print("ℹ️ No changes needed")
        return True

def main():
    """Main function"""
    print("🚀 QUICK FIX - PIN VALIDATION")
    print("=" * 40)
    
    # Option 1: Quick fix by modifying permanent_memory.py
    print("📝 Creating a simpler permanent_memory.py that uses users table...")
    
    # Create a simplified version
    simplified_content = '''"""
🔧 SIMPLIFIED PERMANENT MEMORY - QUICK FIX
===============================================
Temporary fix that uses users table instead of pin_attempts
"""

import os
import logging
from datetime import datetime, timedelta
from supabase import create_client

logger = logging.getLogger(__name__)

class PermanentMemory:
    """Simplified permanent memory using users table only"""
    
    def __init__(self):
        self.client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        logger.info("✅ Simplified PermanentMemory initialized (using users table)")
    
    def track_pin_attempt(self, user_id: str, success: bool) -> dict:
        """Track PIN attempt using users table columns"""
        try:
            logger.info(f"📝 Tracking PIN attempt for user {user_id}: {'success' if success else 'failed'}")
            
            # Get current user data
            result = self.client.table("users").select("pin_attempts, pin_locked_until").eq("id", user_id).execute()
            
            if not result.data:
                logger.error(f"❌ User {user_id} not found")
                return {"success": False, "error": "User not found"}
            
            user_data = result.data[0]
            current_attempts = user_data.get("pin_attempts", 0)
            locked_until = user_data.get("pin_locked_until")
            
            # Check if locked
            now = datetime.now()
            if locked_until:
                try:
                    locked_until_dt = datetime.fromisoformat(locked_until.replace('Z', '+00:00'))
                    if now < locked_until_dt:
                        minutes_remaining = int((locked_until_dt - now).total_seconds() / 60)
                        return {
                            "locked": True,
                            "minutes_remaining": minutes_remaining,
                            "message": f"Account locked. Try again in {minutes_remaining} minutes."
                        }
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing locked_until: {e}")
            
            if success:
                # Reset attempts on success
                self.client.table("users").update({
                    "pin_attempts": 0,
                    "pin_locked_until": None
                }).eq("id", user_id).execute()
                
                return {
                    "success": True,
                    "attempts_remaining": 3,
                    "message": "PIN verified successfully"
                }
            else:
                # Increment failed attempts
                new_attempts = current_attempts + 1
                update_data = {"pin_attempts": new_attempts}
                
                # Lock after 3 failed attempts
                if new_attempts >= 3:
                    lock_until = now + timedelta(minutes=15)
                    update_data["pin_locked_until"] = lock_until.isoformat()
                    
                    self.client.table("users").update(update_data).eq("id", user_id).execute()
                    
                    return {
                        "locked": True,
                        "failed_count": new_attempts,
                        "minutes_remaining": 15,
                        "message": "Too many failed attempts. Account locked for 15 minutes."
                    }
                else:
                    self.client.table("users").update(update_data).eq("id", user_id).execute()
                    
                    return {
                        "failed_count": new_attempts,
                        "attempts_remaining": 3 - new_attempts,
                        "message": f"Invalid PIN. {3 - new_attempts} attempts remaining."
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error tracking PIN attempt: {e}")
            return {"success": False, "error": str(e)}
    
    def check_lock_status(self, user_id: str) -> dict:
        """Check if user is locked"""
        try:
            result = self.client.table("users").select("pin_locked_until").eq("id", user_id).execute()
            
            if not result.data:
                return {"locked": False}
            
            locked_until = result.data[0].get("pin_locked_until")
            
            if not locked_until:
                return {"locked": False}
            
            locked_until_dt = datetime.fromisoformat(locked_until.replace('Z', '+00:00'))
            now = datetime.now()
            
            if now >= locked_until_dt:
                # Clear the lock
                self.client.table("users").update({
                    "pin_locked_until": None,
                    "pin_attempts": 0
                }).eq("id", user_id).execute()
                return {"locked": False}
            
            minutes_remaining = int((locked_until_dt - now).total_seconds() / 60)
            return {
                "locked": True,
                "minutes_remaining": minutes_remaining
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking lock status: {e}")
            return {"locked": False}

# Global instance
permanent_memory = PermanentMemory()
'''
    
    # Write the simplified version
    with open("utils/permanent_memory.py", 'w', encoding='utf-8') as f:
        f.write(simplified_content)
    
    print("✅ Created simplified permanent_memory.py")
    print("📝 This version uses the existing users table columns:")
    print("   - pin_attempts (for tracking failed attempts)")
    print("   - pin_locked_until (for account locking)")
    print("\n🎯 PIN validation should now work without the pin_attempts table!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
