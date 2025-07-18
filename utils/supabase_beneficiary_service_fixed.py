"""
Supabase Beneficiary Service - Database Compatible Version

Manages beneficiary operations using Supabase as the backend database.
This service is designed to work with existing database schema where user_id is BIGINT.
"""

import asyncio
import os
import logging
from typing import List, Dict, Optional, Any, Union
from supabase import create_client, Client
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseBeneficiaryService:
    def __init__(self):
        """Initialize the Supabase beneficiary service."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase beneficiary service initialized")

    def _convert_user_id(self, user_id: Union[str, int]) -> int:
        """
        Convert user_id to integer format as expected by the database.
        
        Args:
            user_id: User ID as string or int
            
        Returns:
            User ID as integer
        """
        if isinstance(user_id, str):
            try:
                return int(user_id)
            except ValueError:
                # If it's a string that can't be converted to int, 
                # it might be a telegram chat_id or other identifier
                # For now, we'll try to extract numbers
                import re
                numbers = re.findall(r'\d+', str(user_id))
                if numbers:
                    return int(numbers[0])
                else:
                    raise ValueError(f"Cannot convert user_id to integer: {user_id}")
        return int(user_id)

    async def get_user_beneficiaries(self, user_id: Union[str, int], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get all beneficiaries for a specific user.
        
        Args:
            user_id: The user's unique identifier (string or int)
            limit: Maximum number of beneficiaries to return
            
        Returns:
            List of beneficiary dictionaries
        """
        try:
            user_id_int = self._convert_user_id(user_id)
            logger.info(f"Fetching beneficiaries for user: {user_id_int}")
            
            result = self.client.table('beneficiaries')\
                .select('*')\
                .eq('user_id', user_id_int)\
                .eq('is_active', True)\
                .order('last_used', desc=True)\
                .limit(limit)\
                .execute()
            
            beneficiaries = result.data if result.data else []
            logger.info(f"Found {len(beneficiaries)} beneficiaries for user {user_id_int}")
            
            return beneficiaries
            
        except Exception as e:
            logger.error(f"Error fetching beneficiaries for user {user_id}: {str(e)}")
            return []

    async def save_beneficiary(self, user_id: Union[str, int], beneficiary_name: str, account_number: str, 
                             bank_code: str, bank_name: str, nickname: Optional[str] = None,
                             telegram_chat_id: Optional[str] = None) -> bool:
        """
        Save a new beneficiary for a user.
        
        Args:
            user_id: The user's unique identifier (string or int)
            beneficiary_name: Full name of the beneficiary
            account_number: Bank account number
            bank_code: Bank code/identifier
            bank_name: Full bank name
            nickname: Optional nickname for the beneficiary
            telegram_chat_id: Optional telegram chat ID
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            user_id_int = self._convert_user_id(user_id)
            logger.info(f"Saving beneficiary for user {user_id_int}: {beneficiary_name}")
            
            # Check for duplicates
            existing = await self._check_duplicate_beneficiary(user_id_int, account_number, bank_code)
            if existing:
                logger.info(f"Beneficiary already exists for user {user_id_int}: {account_number}")
                return True  # Consider existing as success
            
            # Prepare beneficiary data according to existing schema
            beneficiary_data = {
                'user_id': user_id_int,
                'beneficiary_name': beneficiary_name,
                'account_number': account_number,
                'bank_code': bank_code,
                'bank_name': bank_name,
                'nickname': nickname or beneficiary_name,
                'telegram_chat_id': telegram_chat_id,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'last_used': datetime.utcnow().isoformat(),
                'is_default': False
            }
            
            # Insert into Supabase
            result = self.client.table('beneficiaries').insert(beneficiary_data).execute()
            
            if result.data:
                logger.info(f"Successfully saved beneficiary for user {user_id_int}")
                return True
            else:
                logger.error(f"Failed to save beneficiary for user {user_id_int}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving beneficiary for user {user_id}: {str(e)}")
            return False

    async def find_beneficiary_by_name(self, user_id: Union[str, int], search_term: str) -> Optional[Dict[str, Any]]:
        """
        Find a beneficiary by name or nickname using fuzzy search.
        
        Args:
            user_id: The user's unique identifier (string or int)
            search_term: Name or nickname to search for
            
        Returns:
            Beneficiary dictionary if found, None otherwise
        """
        try:
            user_id_int = self._convert_user_id(user_id)
            logger.info(f"Searching beneficiary for user {user_id_int} with term: {search_term}")
            
            # Get all active beneficiaries for the user
            beneficiaries = await self.get_user_beneficiaries(user_id_int, limit=50)
            
            search_term_lower = search_term.lower()
            
            # Search by exact match first
            for beneficiary in beneficiaries:
                if (beneficiary.get('nickname', '').lower() == search_term_lower or 
                    beneficiary.get('beneficiary_name', '').lower() == search_term_lower):
                    logger.info(f"Found exact match for user {user_id_int}")
                    return beneficiary
            
            # Search by partial match
            for beneficiary in beneficiaries:
                nickname = beneficiary.get('nickname', '').lower()
                name = beneficiary.get('beneficiary_name', '').lower()
                
                if (search_term_lower in nickname or search_term_lower in name):
                    logger.info(f"Found partial match for user {user_id_int}")
                    return beneficiary
            
            logger.info(f"No beneficiary found for user {user_id_int} with search term: {search_term}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching beneficiary for user {user_id}: {str(e)}")
            return None

    async def _check_duplicate_beneficiary(self, user_id: int, account_number: str, 
                                         bank_code: str) -> bool:
        """
        Check if a beneficiary already exists for the user.
        
        Args:
            user_id: The user's unique identifier (integer)
            account_number: Bank account number
            bank_code: Bank code
            
        Returns:
            True if duplicate exists, False otherwise
        """
        try:
            result = self.client.table('beneficiaries')\
                .select('id')\
                .eq('user_id', user_id)\
                .eq('account_number', account_number)\
                .eq('bank_code', bank_code)\
                .eq('is_active', True)\
                .execute()
            
            return len(result.data) > 0 if result.data else False
            
        except Exception as e:
            logger.error(f"Error checking duplicate beneficiary: {str(e)}")
            return False

    def create_save_prompt(self, beneficiary_name: str, bank_name: str, account_number: str) -> str:
        """
        Create a user-friendly prompt for saving beneficiaries.
        
        Args:
            beneficiary_name: Name of the beneficiary
            bank_name: Name of the bank
            account_number: Account number
            
        Returns:
            Formatted prompt string
        """
        return f"👉 Would you like to save {beneficiary_name} - {bank_name} - {account_number} as a beneficiary for future transfers?"

# Create a global instance
beneficiary_service = SupabaseBeneficiaryService()

# Helper functions for backward compatibility
async def get_user_beneficiaries(user_id: Union[str, int], limit: int = 10) -> List[Dict[str, Any]]:
    """Get user beneficiaries (compatibility wrapper)."""
    return await beneficiary_service.get_user_beneficiaries(user_id, limit)

async def save_beneficiary(user_id: Union[str, int], beneficiary_name: str, account_number: str, 
                         bank_code: str, bank_name: str, nickname: Optional[str] = None,
                         telegram_chat_id: Optional[str] = None) -> bool:
    """Save beneficiary (compatibility wrapper)."""
    return await beneficiary_service.save_beneficiary(
        user_id, beneficiary_name, account_number, bank_code, bank_name, nickname, telegram_chat_id
    )

async def find_beneficiary_by_name(user_id: Union[str, int], search_term: str) -> Optional[Dict[str, Any]]:
    """Find beneficiary by name (compatibility wrapper)."""
    return await beneficiary_service.find_beneficiary_by_name(user_id, search_term)
