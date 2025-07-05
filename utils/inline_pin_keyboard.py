"""
Inline Keyboard PIN Entry System for Sofi AI
Provides a fast, interactive PIN entry experience using Telegram inline keyboards
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class InlinePINManager:
    """Manages inline keyboard PIN entry sessions"""
    
    def __init__(self):
        self.sessions = {}  # Store user PIN entry sessions
    
    def create_pin_display(self, entered_length: int) -> str:
        """Create the PIN display with dots"""
        display = "● " * entered_length  # Filled dots
        display += "_ " * (4 - entered_length)  # Empty spaces
        return display.strip()
    
    def create_pin_keyboard(self) -> Dict:
        """Create the inline keyboard for PIN entry"""
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
    
    def start_pin_session(self, chat_id: str, transfer_data: Dict) -> str:
        """
        Start a new PIN entry session for a transfer
        
        Args:
            chat_id: User's telegram chat ID
            transfer_data: Transfer details (amount, account, bank, etc.)
            
        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[chat_id] = {
            "session_id": session_id,
            "pin_digits": "",
            "transfer_data": transfer_data,
            "created_at": datetime.now().isoformat(),
            "message_id": None  # Will be set when message is sent
        }
        
        logger.info(f"🔐 Started inline PIN session for user {chat_id}")
        return session_id
    
    def add_pin_digit(self, chat_id: str, digit: str) -> Dict:
        """
        Add a digit to the current PIN entry
        
        Returns:
            Dict with status and current PIN display
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
            "display": self.create_pin_display(pin_length),
            "can_submit": pin_length == 4
        }
    
    def clear_pin(self, chat_id: str) -> Dict:
        """Clear the current PIN entry"""
        if chat_id not in self.sessions:
            return {"success": False, "error": "No active PIN session"}
        
        self.sessions[chat_id]["pin_digits"] = ""
        return {
            "success": True,
            "length": 0,
            "display": self.create_pin_display(0),
            "can_submit": False
        }
    
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
    
    def set_message_id(self, chat_id: str, message_id: int):
        """Set the message ID for the PIN entry message"""
        if chat_id in self.sessions:
            self.sessions[chat_id]["message_id"] = message_id
    
    def get_message_id(self, chat_id: str) -> Optional[int]:
        """Get the message ID for the PIN entry message"""
        if chat_id in self.sessions:
            return self.sessions[chat_id].get("message_id")
        return None
    
    def end_session(self, chat_id: str):
        """End the PIN entry session"""
        if chat_id in self.sessions:
            del self.sessions[chat_id]
            logger.info(f"🔐 Ended inline PIN session for user {chat_id}")
    
    def get_session(self, chat_id: str) -> Optional[Dict]:
        """Get the current PIN session for a user"""
        return self.sessions.get(chat_id)
    
    def create_transfer_confirmation_message(self, transfer_data: Dict) -> str:
        """Create the transfer confirmation message"""
        amount = transfer_data.get('amount', 0)
        account_number = transfer_data.get('account_number', '')
        bank_name = transfer_data.get('bank_name', '')
        recipient_name = transfer_data.get('recipient_name', '')
        fee = transfer_data.get('fee', 0)
        total = amount + fee
        
        message = f"""💸 You're about to send ₦{amount:,.0f} to:
👤 Name: *{recipient_name}*
🏦 Bank: {bank_name}
🔢 Account: {account_number}
💰 Fee: ₦{fee:,.0f}
💵 Total: ₦{total:,.0f}

Please confirm by entering your 4-digit PIN.

🔐 PIN: {self.create_pin_display(0)}"""
        
        return message
    
    def create_pin_progress_message(self, transfer_data: Dict, pin_length: int) -> str:
        """Create the PIN progress message"""
        amount = transfer_data.get('amount', 0)
        account_number = transfer_data.get('account_number', '')
        bank_name = transfer_data.get('bank_name', '')
        recipient_name = transfer_data.get('recipient_name', '')
        fee = transfer_data.get('fee', 0)
        total = amount + fee
        
        message = f"""💸 You're about to send ₦{amount:,.0f} to:
👤 Name: *{recipient_name}*
🏦 Bank: {bank_name}
🔢 Account: {account_number}
💰 Fee: ₦{fee:,.0f}
💵 Total: ₦{total:,.0f}

Please confirm by entering your 4-digit PIN.

🔐 PIN: {self.create_pin_display(pin_length)}"""
        
        return message
    
    def is_session_expired(self, chat_id: str, timeout_minutes: int = 5) -> bool:
        """Check if a PIN session has expired"""
        if chat_id not in self.sessions:
            return True
        
        session = self.sessions[chat_id]
        created_at = datetime.fromisoformat(session["created_at"])
        elapsed = datetime.now() - created_at
        
        return elapsed.total_seconds() > (timeout_minutes * 60)
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 5):
        """Clean up expired PIN sessions"""
        expired_sessions = []
        
        for chat_id, session in self.sessions.items():
            if self.is_session_expired(chat_id, timeout_minutes):
                expired_sessions.append(chat_id)
        
        for chat_id in expired_sessions:
            del self.sessions[chat_id]
            logger.info(f"🧹 Cleaned up expired PIN session for user {chat_id}")
        
        return len(expired_sessions)

# Global inline PIN manager
inline_pin_manager = InlinePINManager()

def create_inline_pin_keyboard() -> Dict:
    """Create the inline keyboard for PIN entry"""
    return inline_pin_manager.create_pin_keyboard()

def start_inline_pin_session(chat_id: str, transfer_data: Dict) -> str:
    """Start a new inline PIN entry session"""
    return inline_pin_manager.start_pin_session(chat_id, transfer_data)

def handle_pin_button(chat_id: str, callback_data: str) -> Dict:
    """Handle PIN button press"""
    # Check if session exists and is not expired
    if chat_id not in inline_pin_manager.sessions:
        return {"success": False, "error": "No active PIN session"}
    
    if inline_pin_manager.is_session_expired(chat_id):
        inline_pin_manager.end_session(chat_id)
        return {"success": False, "error": "PIN session expired. Please start a new transfer."}
    
    if callback_data.startswith("pin_") and callback_data != "pin_clear" and callback_data != "pin_submit" and callback_data != "pin_cancel":
        # Extract digit from callback_data (e.g., "pin_1" -> "1")
        digit = callback_data.split("_")[1]
        return inline_pin_manager.add_pin_digit(chat_id, digit)
    elif callback_data == "pin_clear":
        return inline_pin_manager.clear_pin(chat_id)
    elif callback_data == "pin_submit":
        pin = inline_pin_manager.get_pin(chat_id)
        if pin:
            return {
                "success": True,
                "action": "submit",
                "pin": pin,
                "transfer_data": inline_pin_manager.get_transfer_data(chat_id)
            }
        else:
            return {"success": False, "error": "Please enter a complete 4-digit PIN"}
    elif callback_data == "pin_cancel":
        inline_pin_manager.end_session(chat_id)
        return {"success": True, "action": "cancel"}
    
    return {"success": False, "error": "Invalid PIN button"}

def get_pin_session_message_id(chat_id: str) -> Optional[int]:
    """Get the message ID for the PIN entry message"""
    return inline_pin_manager.get_message_id(chat_id)

def set_pin_session_message_id(chat_id: str, message_id: int):
    """Set the message ID for the PIN entry message"""
    inline_pin_manager.set_message_id(chat_id, message_id)

def end_pin_session(chat_id: str):
    """End the PIN entry session"""
    inline_pin_manager.end_session(chat_id)
