"""
Telegram ID to UUID Resolver Utility
Resolves Telegram chat IDs to Supabase UUIDs for database queries
"""

import os
import logging
from typing import Optional, Dict, Any
from supabase import create_client

logger = logging.getLogger(__name__)

class TelegramUUIDResolver:
    """Utility class for resolving Telegram IDs to Supabase UUIDs"""
    
    def __init__(self):
        """Initialize the resolver - Supabase client will be created lazily"""
        self._supabase = None
    
    @property
    def supabase(self):
        """Lazy initialization of Supabase client"""
        if self._supabase is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not found in environment variables")
            
            self._supabase = create_client(supabase_url, supabase_key)
        
        return self._supabase
    
    async def resolve_telegram_to_uuid(self, telegram_chat_id: str) -> Dict[str, Any]:
        """
        Resolve Telegram chat ID to Supabase UUID
        
        Args:
            telegram_chat_id: The Telegram chat ID (string/number)
        
        Returns:
            dict: {'success': bool, 'uuid': str or None, 'error': str or None}
        """
        try:
            # Ensure telegram_chat_id is a string
            telegram_chat_id = str(telegram_chat_id)
            
            # Query Supabase users table to find UUID by telegram_chat_id
            result = self.supabase.table("users").select("id").eq("telegram_chat_id", telegram_chat_id).execute()
            
            if result.data and len(result.data) > 0:
                user_uuid = result.data[0]["id"]
                logger.info(f"✅ Resolved Telegram ID {telegram_chat_id} to UUID {user_uuid}")
                return {
                    'success': True,
                    'uuid': user_uuid,
                    'error': None
                }
            else:
                logger.warning(f"❌ No user found for Telegram ID {telegram_chat_id}")
                return {
                    'success': False,
                    'uuid': None,
                    'error': f"User not found. Please complete onboarding first by visiting https://pipinstallsofi.com/onboard"
                }
                
        except Exception as e:
            logger.error(f"❌ Error resolving Telegram ID {telegram_chat_id} to UUID: {str(e)}")
            return {
                'success': False,
                'uuid': None,
                'error': f"Database error while resolving user ID: {str(e)}"
            }
    
    async def get_uuid_or_raise(self, telegram_chat_id: str) -> str:
        """
        Quick helper to get UUID from Telegram ID or raise an exception
        
        Args:
            telegram_chat_id: The Telegram chat ID
        
        Returns:
            str: The UUID if found
            
        Raises:
            ValueError: If user not found or database error
        """
        result = await self.resolve_telegram_to_uuid(telegram_chat_id)
        
        if result['success']:
            return result['uuid']
        else:
            raise ValueError(result['error'])
    
    def resolve_telegram_to_uuid_sync(self, telegram_chat_id: str) -> Dict[str, Any]:
        """
        Synchronous version of resolve_telegram_to_uuid
        
        Args:
            telegram_chat_id: The Telegram chat ID (string/number)
        
        Returns:
            dict: {'success': bool, 'uuid': str or None, 'error': str or None}
        """
        try:
            # Ensure telegram_chat_id is a string
            telegram_chat_id = str(telegram_chat_id)
            
            # Query Supabase users table to find UUID by telegram_chat_id
            result = self.supabase.table("users").select("id").eq("telegram_chat_id", telegram_chat_id).execute()
            
            if result.data and len(result.data) > 0:
                user_uuid = result.data[0]["id"]
                logger.info(f"✅ Resolved Telegram ID {telegram_chat_id} to UUID {user_uuid}")
                return {
                    'success': True,
                    'uuid': user_uuid,
                    'error': None
                }
            else:
                logger.warning(f"❌ No user found for Telegram ID {telegram_chat_id}")
                return {
                    'success': False,
                    'uuid': None,
                    'error': f"User not found. Please complete onboarding first by visiting https://pipinstallsofi.com/onboard"
                }
                
        except Exception as e:
            logger.error(f"❌ Error resolving Telegram ID {telegram_chat_id} to UUID: {str(e)}")
            return {
                'success': False,
                'uuid': None,
                'error': f"Database error while resolving user ID: {str(e)}"
            }

# Global instance for easy import
telegram_uuid_resolver = TelegramUUIDResolver()

# Convenience functions for quick import
async def resolve_telegram_to_uuid(telegram_chat_id: str) -> Dict[str, Any]:
    """Quick function to resolve Telegram ID to UUID"""
    return await telegram_uuid_resolver.resolve_telegram_to_uuid(telegram_chat_id)

async def get_uuid_from_telegram_id(telegram_chat_id: str) -> str:
    """Quick function to get UUID from Telegram ID or raise exception"""
    return await telegram_uuid_resolver.get_uuid_or_raise(telegram_chat_id)

def resolve_telegram_to_uuid_sync(telegram_chat_id: str) -> Dict[str, Any]:
    """Quick synchronous function to resolve Telegram ID to UUID"""
    return telegram_uuid_resolver.resolve_telegram_to_uuid_sync(telegram_chat_id)
