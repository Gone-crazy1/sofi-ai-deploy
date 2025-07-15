"""
🎫 SECURE TOKEN MANAGER

Manages secure tokens for PIN verification to prevent bot preview issues.
Maps short-lived tokens to transaction IDs for enhanced security.
"""

import secrets
import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecureTokenManager:
    """Manages secure tokens for PIN verification"""
    
    def __init__(self):
        self.token_store = {}  # token -> {txn_id, expires_at, used}
        self.cleanup_interval = 300  # Clean up expired tokens every 5 minutes
        self.last_cleanup = time.time()
        
    def generate_token(self, transaction_id: str, expiry_minutes: int = 15) -> str:
        """Generate a secure token for a transaction"""
        # Create a random token
        token = secrets.token_urlsafe(16)  # 22 characters, URL-safe
        
        # Store token mapping
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        self.token_store[token] = {
            'transaction_id': transaction_id,
            'expires_at': expires_at,
            'used': False,
            'created_at': datetime.now()
        }
        
        logger.info(f"🎫 Generated token {token[:8]}... for transaction {transaction_id}")
        return token
    
    def get_transaction_id(self, token: str, mark_as_used: bool = False) -> Optional[str]:
        """Get transaction ID from token"""
        self._cleanup_expired()
        
        token_data = self.token_store.get(token)
        if not token_data:
            logger.warning(f"❌ Token not found: {token[:8]}...")
            return None
            
        # Check if expired
        if datetime.now() > token_data['expires_at']:
            logger.warning(f"⏰ Expired token: {token[:8]}...")
            del self.token_store[token]
            return None
            
        # Check if already used (one-time use)
        if token_data['used']:
            logger.warning(f"🔒 Token already used: {token[:8]}...")
            return None
            
        # Mark as used if requested
        if mark_as_used:
            token_data['used'] = True
            logger.info(f"✅ Token marked as used: {token[:8]}...")
            
        return token_data['transaction_id']
    
    def is_token_valid(self, token: str) -> bool:
        """Check if token is valid without marking as used"""
        return self.get_transaction_id(token, mark_as_used=False) is not None
    
    def invalidate_token(self, token: str):
        """Invalidate a token"""
        if token in self.token_store:
            del self.token_store[token]
            logger.info(f"🗑️ Token invalidated: {token[:8]}...")
    
    def _cleanup_expired(self):
        """Clean up expired tokens"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
            
        now = datetime.now()
        expired_tokens = [
            token for token, data in self.token_store.items()
            if now > data['expires_at']
        ]
        
        for token in expired_tokens:
            del self.token_store[token]
            
        if expired_tokens:
            logger.info(f"🧹 Cleaned up {len(expired_tokens)} expired tokens")
            
        self.last_cleanup = current_time
    
    def get_stats(self) -> Dict:
        """Get token manager statistics"""
        self._cleanup_expired()
        
        now = datetime.now()
        active_tokens = len([
            token for token, data in self.token_store.items()
            if now <= data['expires_at'] and not data['used']
        ])
        
        used_tokens = len([
            token for token, data in self.token_store.items()
            if data['used']
        ])
        
        return {
            'active_tokens': active_tokens,
            'used_tokens': used_tokens,
            'total_tokens': len(self.token_store)
        }

# Global instance
secure_token_manager = SecureTokenManager()
