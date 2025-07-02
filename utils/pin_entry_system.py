"""
PIN Entry System for Sofi AI
Provides secure inline keyboard PIN entry for transfers
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def create_pin_entry_keyboard() -> Dict:
    """
    Create an inline keyboard for PIN entry
    Returns a Telegram inline keyboard markup
    """
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "1", "callback_data": "pin_1"},
                {"text": "2", "callback_data": "pin_2"},
                {"text": "3", "callback_data": "pin_3"}
            ],
            [
                {"text": "4", "callback_data": "pin_4"},
                {"text": "5", "callback_data": "pin_5"},
                {"text": "6", "callback_data": "pin_6"}
            ],
            [
                {"text": "7", "callback_data": "pin_7"},
                {"text": "8", "callback_data": "pin_8"},
                {"text": "9", "callback_data": "pin_9"}
            ],
            [
                {"text": "⬅️ Clear", "callback_data": "pin_clear"},
                {"text": "0", "callback_data": "pin_0"},
                {"text": "✅ Submit", "callback_data": "pin_submit"}
            ],
            [
                {"text": "❌ Cancel", "callback_data": "pin_cancel"}
            ]
        ]
    }
    return keyboard

def create_transfer_confirmation_keyboard(transfer_data: Dict) -> Dict:
    """
    Create confirmation keyboard for transfer
    """
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Confirm Transfer", "callback_data": f"confirm_transfer_{transfer_data.get('temp_id')}"},
                {"text": "❌ Cancel", "callback_data": "cancel_transfer"}
            ]
        ]
    }
    return keyboard

class PINEntrySession:
    """Manages PIN entry sessions for users"""
    
    def __init__(self):
        self.sessions = {}  # Store user PIN entry sessions
    
    def start_pin_session(self, chat_id: str, session_type: str, transfer_data: Dict = None) -> str:
        """
        Start a new PIN entry session
        
        Args:
            chat_id: User's telegram chat ID
            session_type: 'transfer', 'set_pin', etc.
            transfer_data: Transfer details if this is for a transfer
            
        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[chat_id] = {
            "session_id": session_id,
            "type": session_type,
            "pin_digits": "",
            "transfer_data": transfer_data,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"🔐 Started PIN session for user {chat_id}: {session_type}")
        return session_id
    
    def add_pin_digit(self, chat_id: str, digit: str) -> Dict:
        """
        Add a digit to the current PIN entry
        
        Returns:
            Dict with status and current PIN length
        """
        if chat_id not in self.sessions:
            return {"success": False, "error": "No active PIN session"}
        
        session = self.sessions[chat_id]
        
        if len(session["pin_digits"]) >= 4:
            return {"success": False, "error": "PIN already complete"}
        
        session["pin_digits"] += digit
        pin_length = len(session["pin_digits"])
        
        return {
            "success": True,
            "length": pin_length,
            "status": "complete" if pin_length == 4 else "in_progress",
            "display": "•" * pin_length  # Show dots for security
        }
    
    def clear_pin(self, chat_id: str) -> Dict:
        """Clear the current PIN entry"""
        if chat_id not in self.sessions:
            return {"success": False, "error": "No active PIN session"}
        
        self.sessions[chat_id]["pin_digits"] = ""
        return {"success": True, "length": 0}
    
    def get_pin(self, chat_id: str) -> Optional[str]:
        """Get the completed PIN"""
        if chat_id not in self.sessions:
            return None
        
        session = self.sessions[chat_id]
        if len(session["pin_digits"]) == 4:
            return session["pin_digits"]
        return None
    
    def get_transfer_data(self, chat_id: str) -> Optional[Dict]:
        """Get transfer data for the session"""
        if chat_id not in self.sessions:
            return None
        
        return self.sessions[chat_id].get("transfer_data")
    
    def end_session(self, chat_id: str):
        """End the PIN entry session"""
        if chat_id in self.sessions:
            del self.sessions[chat_id]
            logger.info(f"🔐 Ended PIN session for user {chat_id}")
    
    def get_session(self, chat_id: str) -> Optional[Dict]:
        """Get the current PIN session for a user"""
        return self.sessions.get(chat_id)
    
    def clear_session(self, chat_id: str):
        """Clear/end the PIN session"""
        if chat_id in self.sessions:
            del self.sessions[chat_id]
            logger.info(f"🔐 Cleared PIN session for user {chat_id}")

# Global PIN entry manager
pin_manager = PINEntrySession()
