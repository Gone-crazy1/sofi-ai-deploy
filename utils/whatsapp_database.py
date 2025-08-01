"""
WhatsApp Database Service
Handles database operations for WhatsApp integration with Supabase
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from supabase import create_client

logger = logging.getLogger(__name__)

class WhatsAppDatabaseService:
    """Database service for WhatsApp integration"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ WhatsApp Database Service initialized")
    
    def has_processed_event(self, event_id: str) -> bool:
        """Check if webhook event has already been processed"""
        try:
            result = self.supabase.table("webhook_events").select("event_id").eq("event_id", event_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking processed event {event_id}: {e}")
            return False
    
    def log_webhook_event(self, event_id: str, payload: dict) -> bool:
        """Log webhook event for deduplication"""
        try:
            data = {
                "event_id": event_id,
                "payload": payload,
                "processed_at": datetime.utcnow().isoformat(),
                "source": "whatsapp"
            }
            
            result = self.supabase.table("webhook_events").insert(data).execute()
            logger.info(f"✅ Logged webhook event: {event_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging webhook event {event_id}: {e}")
            return False
    
    def get_user_by_whatsapp_number(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get user by WhatsApp phone number"""
        try:
            # Normalize phone number (ensure E.164 format)
            normalized_phone = self._normalize_phone(phone)
            
            result = self.supabase.table("users").select("*").eq("whatsapp_number", normalized_phone).eq("platform", "whatsapp").execute()
            
            if result.data:
                user = result.data[0]
                logger.info(f"✅ Found user for WhatsApp {normalized_phone}: {user.get('id')}")
                return user
            else:
                logger.info(f"❌ No user found for WhatsApp {normalized_phone}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by WhatsApp {phone}: {e}")
            return None
    
    def update_user_last_active(self, user_id: str) -> bool:
        """Update user's last active timestamp"""
        try:
            data = {"last_active_at": datetime.utcnow().isoformat()}
            result = self.supabase.table("users").update(data).eq("id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating last active for user {user_id}: {e}")
            return False
    
    def get_or_create_onboarding_session(self, phone: str) -> Dict[str, Any]:
        """Get existing onboarding session or create new one"""
        try:
            normalized_phone = self._normalize_phone(phone)
            
            # Check for existing session
            result = self.supabase.table("onboarding_sessions").select("*").eq("whatsapp_number", normalized_phone).eq("status", "active").execute()
            
            if result.data:
                session = result.data[0]
                logger.info(f"✅ Found existing onboarding session for {normalized_phone}")
                return session
            
            # Create new session
            session_data = {
                "whatsapp_number": normalized_phone,
                "step": "asked_to_create",
                "status": "active",
                "session_data": {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("onboarding_sessions").insert(session_data).execute()
            if result.data:
                session = result.data[0]
                logger.info(f"✅ Created new onboarding session for {normalized_phone}")
                return session
            else:
                raise Exception("Failed to create onboarding session")
                
        except Exception as e:
            logger.error(f"Error with onboarding session for {phone}: {e}")
            # Return default session structure
            return {
                "id": None,
                "whatsapp_number": self._normalize_phone(phone),
                "step": "asked_to_create",
                "status": "active",
                "session_data": {}
            }
    
    def update_onboarding_session(self, session_id: str, updates: dict) -> bool:
        """Update onboarding session"""
        try:
            if not session_id:
                logger.warning("No session ID provided for update")
                return False
                
            updates["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("onboarding_sessions").update(updates).eq("id", session_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating onboarding session {session_id}: {e}")
            return False
    
    def create_user_from_onboarding(self, session_data: dict) -> Optional[Dict[str, Any]]:
        """Create user from completed onboarding session"""
        try:
            phone = session_data.get("whatsapp_number")
            session_info = session_data.get("session_data", {})
            
            # Generate user data from session
            user_data = {
                "whatsapp_number": phone,
                "platform": "whatsapp",
                "first_name": session_info.get("first_name", "WhatsApp User"),
                "last_name": session_info.get("last_name", ""),
                "email": session_info.get("email"),
                "phone": phone,
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_active_at": datetime.utcnow().isoformat(),
                "onboarding_completed": True,
                "kyc_status": "pending"
            }
            
            # Create user
            result = self.supabase.table("users").insert(user_data).execute()
            if not result.data:
                raise Exception("Failed to create user")
            
            user = result.data[0]
            user_id = user["id"]
            
            # Initialize virtual account if needed
            self._initialize_virtual_account(user_id, phone)
            
            # Mark onboarding session as completed
            if session_data.get("id"):
                self.update_onboarding_session(session_data["id"], {
                    "status": "completed",
                    "user_id": user_id
                })
            
            logger.info(f"✅ Created user from onboarding: {user_id} for {phone}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user from onboarding: {e}")
            return None
    
    def log_message(self, user_id: str, platform: str, direction: str, content: str, 
                   intent: str, raw_payload: dict, session_state: dict) -> bool:
        """Log message in message_logs table"""
        try:
            message_data = {
                "user_id": user_id,
                "platform": platform,
                "direction": direction,
                "content": content,
                "intent": intent,
                "raw_payload": raw_payload,
                "session_state": session_state
            }
            
            result = self.supabase.table("message_logs").insert(message_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return False
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to E.164 format"""
        if not phone:
            return phone
            
        # Remove non-digits
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Handle Nigerian numbers
        if digits_only.startswith('234'):
            return f"+{digits_only}"
        elif digits_only.startswith('0') and len(digits_only) == 11:
            return f"+234{digits_only[1:]}"
        elif len(digits_only) == 10:
            return f"+234{digits_only}"
        else:
            # Assume already normalized or international
            return f"+{digits_only}" if not phone.startswith('+') else phone
    
    def _initialize_virtual_account(self, user_id: str, phone: str) -> bool:
        """Initialize virtual account for new user"""
        try:
            # Check if virtual account already exists
            existing = self.supabase.table("virtual_accounts").select("*").eq("user_id", user_id).execute()
            if existing.data:
                logger.info(f"Virtual account already exists for user {user_id}")
                return True
            
            # Create virtual account
            account_data = {
                "user_id": user_id,
                "account_number": self._generate_account_number(),
                "account_name": f"SOFI/{phone[-10:]}",
                "bank_name": "Sofi Digital Bank",
                "balance": 0.0,
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("virtual_accounts").insert(account_data).execute()
            success = len(result.data) > 0
            
            if success:
                logger.info(f"✅ Initialized virtual account for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing virtual account for user {user_id}: {e}")
            return False
    
    def _generate_account_number(self) -> str:
        """Generate unique account number"""
        import random
        import time
        
        # Simple account number generation (improve for production)
        timestamp = str(int(time.time()))[-6:]
        random_part = str(random.randint(1000, 9999))
        return f"110{timestamp}{random_part}"[:10]

# Global instance
whatsapp_db = WhatsAppDatabaseService()
