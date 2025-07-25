"""
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
    return False

permanent_memory = PermanentMemory()
