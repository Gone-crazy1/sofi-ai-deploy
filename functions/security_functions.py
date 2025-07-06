"""
Security-related functions for Sofi AI Assistant
Handles PIN verification and security operations
"""

import logging
from typing import Dict, Any
from supabase import create_client
import os
import hashlib

logger = logging.getLogger(__name__)

async def verify_pin(chat_id: str, pin: str, **kwargs) -> Dict[str, Any]:
    """
    Verify user's transaction PIN
    
    Args:
        chat_id (str): User's Telegram chat ID
        pin (str): PIN to verify
        
    Returns:
        Dict containing verification result
    """
    try:
        logger.info(f"🔐 Verifying PIN for user {chat_id}")
        
        if not pin or len(pin) != 4 or not pin.isdigit():
            return {
                "valid": False,
                "error": "PIN must be exactly 4 digits"
            }
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get user data
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        if not user_result.data:
            return {
                "valid": False,
                "error": "User not found"
            }
        
        user_data = user_result.data[0]
        stored_pin_hash = user_data.get("pin_hash")  # Updated to match onboarding column name
        
        if not stored_pin_hash:
            return {
                "valid": False,
                "error": "No PIN set. Please set up your transaction PIN first."
            }
        
        # Hash the provided PIN using the same method as storage (SHA256)
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        if pin_hash == stored_pin_hash:
            return {
                "valid": True,
                "message": "PIN verified successfully"
            }
        else:
            # Log failed attempt
            logger.warning(f"❌ Failed PIN attempt for user {chat_id}")
            return {
                "valid": False,
                "error": "Invalid PIN"
            }
            
    except Exception as e:
        logger.error(f"❌ Error verifying PIN: {str(e)}")
        return {
            "valid": False,
            "error": f"PIN verification failed: {str(e)}"
        }

async def set_pin(chat_id: str, pin: str, **kwargs) -> Dict[str, Any]:
    """
    Set user's transaction PIN
    
    Args:
        chat_id (str): User's Telegram chat ID
        pin (str): New PIN to set
        
    Returns:
        Dict containing result
    """
    try:
        logger.info(f"🔐 Setting PIN for user {chat_id}")
        
        if not pin or len(pin) != 4 or not pin.isdigit():
            return {
                "success": False,
                "error": "PIN must be exactly 4 digits"
            }
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Check if user exists
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        if not user_result.data:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Hash the PIN using SHA256 (same as storage)
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        # Update user record with correct column name
        update_result = supabase.table("users")\
            .update({
                "pin_hash": pin_hash,
                "has_pin": True,
                "pin_set_at": "now()"
            })\
            .eq("telegram_chat_id", str(chat_id))\
            .execute()
        
        if update_result.data:
            return {
                "success": True,
                "message": "Transaction PIN set successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to set PIN"
            }
            
    except Exception as e:
        logger.error(f"❌ Error setting PIN: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to set PIN: {str(e)}"
        }
