import json
from datetime import datetime, timedelta
from typing import Dict, Optional

class ConversationState:
    def __init__(self):
        self._states: Dict[str, dict] = {}
        self._timeouts: Dict[str, datetime] = {}
        self.TIMEOUT_MINUTES = 5

    def get_state(self, chat_id: str) -> Optional[dict]:
        # Clear expired states
        self._clear_expired()
        
        # Return state if exists
        return self._states.get(str(chat_id))

    def set_state(self, chat_id: str, state: dict):
        chat_id = str(chat_id)
        self._states[chat_id] = state
        self._timeouts[chat_id] = datetime.now() + timedelta(minutes=self.TIMEOUT_MINUTES)

    def clear_state(self, chat_id: str):
        chat_id = str(chat_id)
        if chat_id in self._states:
            del self._states[chat_id]
        if chat_id in self._timeouts:
            del self._timeouts[chat_id]

    def _clear_expired(self):
        now = datetime.now()
        expired = [
            chat_id for chat_id, timeout in self._timeouts.items()
            if now > timeout
        ]
        for chat_id in expired:
            self.clear_state(chat_id)

    def get_pending_transfer(self, transaction_id: str) -> Optional[dict]:
        """Get pending transfer details by transaction ID"""
        for chat_id, state in self._states.items():
            if state and 'pending_transfer' in state:
                if state['pending_transfer'].get('transaction_id') == transaction_id:
                    return state['pending_transfer']
        return None
    
    def set_pending_transfer(self, chat_id: str, transfer_data: dict):
        """Set pending transfer for a user"""
        chat_id = str(chat_id)
        current_state = self.get_state(chat_id) or {}
        current_state['pending_transfer'] = transfer_data
        self.set_state(chat_id, current_state)
    
    def clear_pending_transfer(self, transaction_id: str):
        """Clear pending transfer by transaction ID"""
        for chat_id, state in self._states.items():
            if state and 'pending_transfer' in state:
                if state['pending_transfer'].get('transaction_id') == transaction_id:
                    del state['pending_transfer']
                    break
    
    def get_pin_attempts(self, transaction_id: str) -> int:
        """Get PIN attempt count for a transaction"""
        for chat_id, state in self._states.items():
            if state and 'pin_attempts' in state:
                return state['pin_attempts'].get(transaction_id, 0)
        return 0
    
    def set_pin_attempts(self, transaction_id: str, attempts: int):
        """Set PIN attempt count for a transaction"""
        for chat_id, state in self._states.items():
            if state and 'pending_transfer' in state:
                if state['pending_transfer'].get('transaction_id') == transaction_id:
                    if 'pin_attempts' not in state:
                        state['pin_attempts'] = {}
                    state['pin_attempts'][transaction_id] = attempts
                    break

# Global instance
conversation_state = ConversationState()
