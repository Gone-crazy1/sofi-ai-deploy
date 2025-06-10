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

# Global instance
conversation_state = ConversationState()
