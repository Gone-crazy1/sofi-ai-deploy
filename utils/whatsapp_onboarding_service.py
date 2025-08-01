"""
WhatsApp Onboarding Service
Handles multi-step onboarding flow for new WhatsApp users
"""

import logging
from typing import Dict, Any, Optional, Tuple
from utils.whatsapp_database import whatsapp_db

logger = logging.getLogger(__name__)

class WhatsAppOnboardingService:
    """Service for handling WhatsApp user onboarding"""
    
    def __init__(self):
        self.db = whatsapp_db
    
    def process_onboarding_message(self, phone: str, message: str) -> Tuple[bool, str]:
        """
        Process onboarding message and return (continue_onboarding, response)
        Returns (False, response) if onboarding is complete or user should be created
        """
        try:
            session = self.db.get_or_create_onboarding_session(phone)
            current_step = session.get("step", "asked_to_create")
            session_data = session.get("session_data", {})
            
            logger.info(f"📋 Processing onboarding for {phone}, step: {current_step}")
            
            if current_step == "asked_to_create":
                return self._handle_create_confirmation(session, message)
            elif current_step == "collecting_name":
                return self._handle_name_collection(session, message)
            elif current_step == "collecting_email":
                return self._handle_email_collection(session, message)
            elif current_step == "final_confirmation":
                return self._handle_final_confirmation(session, message)
            else:
                # Unknown step, restart onboarding
                return self._start_onboarding(session)
                
        except Exception as e:
            logger.error(f"Error in onboarding process for {phone}: {e}")
            return False, "❌ Sorry, there was an error with your registration. Please try again later."
    
    def _start_onboarding(self, session: dict) -> Tuple[bool, str]:
        """Start the onboarding process"""
        self.db.update_onboarding_session(session.get("id"), {
            "step": "asked_to_create",
            "session_data": {}
        })
        
        return True, """👋 Welcome to Sofi AI!

I couldn't find your account in our system. Would you like to create a new account?

🔐 **Benefits of Sofi Account:**
• Send & receive money instantly
• Check balance anytime  
• Buy airtime & pay bills
• Secure digital banking

Reply **YES** to create your account, or **NO** to cancel."""
    
    def _handle_create_confirmation(self, session: dict, message: str) -> Tuple[bool, str]:
        """Handle initial account creation confirmation"""
        message_lower = message.lower().strip()
        
        if message_lower in ["yes", "y", "ok", "okay", "sure", "create"]:
            # User confirmed, start collecting details
            self.db.update_onboarding_session(session.get("id"), {
                "step": "collecting_name"
            })
            
            return True, """✅ Great! Let's create your Sofi account.

First, I need your full name.

Please reply with your **First Name** and **Last Name** 
(Example: John Doe)"""
        
        elif message_lower in ["no", "n", "cancel", "stop"]:
            # User declined
            self.db.update_onboarding_session(session.get("id"), {
                "status": "cancelled"
            })
            
            return False, """❌ Account creation cancelled.

If you change your mind, just send me another message and I'll help you create your account!

You can also visit our website: https://pipinstallsofi.com"""
        
        else:
            # Unclear response, ask again
            return True, """🤔 I didn't understand your response.

To create a Sofi account, please reply:
• **YES** - to create your account
• **NO** - to cancel

Would you like to create a Sofi account?"""
    
    def _handle_name_collection(self, session: dict, message: str) -> Tuple[bool, str]:
        """Handle name collection step"""
        message = message.strip()
        
        # Basic validation
        if len(message) < 2:
            return True, "❌ Please enter a valid name (at least 2 characters)."
        
        # Try to split into first and last name
        name_parts = message.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
        else:
            first_name = message
            last_name = ""
        
        # Update session with name
        session_data = session.get("session_data", {})
        session_data.update({
            "first_name": first_name,
            "last_name": last_name,
            "full_name": message
        })
        
        self.db.update_onboarding_session(session.get("id"), {
            "step": "collecting_email",
            "session_data": session_data
        })
        
        return True, f"""✅ Nice to meet you, {first_name}!

Now, please provide your **email address** for account verification and updates.

(Example: john@email.com)"""
    
    def _handle_email_collection(self, session: dict, message: str) -> Tuple[bool, str]:
        """Handle email collection step"""
        email = message.strip().lower()
        
        # Basic email validation
        if "@" not in email or "." not in email or len(email) < 5:
            return True, """❌ Please enter a valid email address.

Example: john@email.com

Your email is needed for account verification and important updates."""
        
        # Update session with email
        session_data = session.get("session_data", {})
        session_data["email"] = email
        
        self.db.update_onboarding_session(session.get("id"), {
            "step": "final_confirmation",
            "session_data": session_data
        })
        
        first_name = session_data.get("first_name", "")
        
        return True, f"""✅ Perfect! Here's your account summary:

👤 **Name**: {session_data.get('full_name', '')}
📧 **Email**: {email}
📱 **WhatsApp**: {session.get('whatsapp_number', '')}

Reply **CONFIRM** to create your account, or **EDIT** to make changes."""
    
    def _handle_final_confirmation(self, session: dict, message: str) -> Tuple[bool, str]:
        """Handle final confirmation and account creation"""
        message_lower = message.lower().strip()
        
        if message_lower in ["confirm", "yes", "y", "create", "ok", "okay"]:
            # Create the user account
            user = self.db.create_user_from_onboarding(session)
            
            if user:
                first_name = session.get("session_data", {}).get("first_name", "")
                return False, f"""🎉 Welcome to Sofi, {first_name}!

Your account has been created successfully!

✅ **Account Features:**
• Send & receive money
• Check balance: type "balance"
• Buy airtime: type "airtime 1000"  
• Get help: type "help"

💰 **Try saying:** "What's my balance?" to get started!"""
            
            else:
                return False, """❌ Sorry, there was an error creating your account.

Please try again later or contact support."""
        
        elif message_lower in ["edit", "change", "back"]:
            # Go back to name collection
            self.db.update_onboarding_session(session.get("id"), {
                "step": "collecting_name",
                "session_data": {}
            })
            
            return True, """📝 Let's start over with your details.

Please provide your **First Name** and **Last Name**:
(Example: John Doe)"""
        
        else:
            return True, """🤔 Please reply with:

• **CONFIRM** - to create your account
• **EDIT** - to change your details

What would you like to do?"""
    
    def is_user_in_onboarding(self, phone: str) -> bool:
        """Check if user is currently in onboarding process"""
        try:
            session = self.db.get_or_create_onboarding_session(phone)
            return session.get("status") == "active" and session.get("step") != "completed"
        except:
            return False

# Global instance
whatsapp_onboarding = WhatsAppOnboardingService()
