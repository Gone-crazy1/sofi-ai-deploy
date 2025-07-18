"""
Legacy Beneficiary Handler for backward compatibility
Bridges old beneficiary_manager calls to new Supabase service
"""

import logging
from typing import Dict, Optional
from utils.supabase_beneficiary_service import beneficiary_service
from supabase import create_client
import os

logger = logging.getLogger(__name__)

class LegacyBeneficiaryHandler:
    """Handles legacy beneficiary commands using new Supabase service"""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    async def handle_beneficiary_command(self, chat_id: str, message: str, user_data: Dict) -> Optional[str]:
        """Handle beneficiary-related commands (legacy compatibility)"""
        try:
            message_lower = message.lower().strip()
            
            # Get user UUID from chat_id
            user_uuid = await self._get_user_uuid_from_chat_id(chat_id)
            if not user_uuid:
                return None
            
            # Check for beneficiary keywords
            if any(keyword in message_lower for keyword in ['beneficiary', 'beneficiaries', 'saved', 'my recipients', 'contacts']):
                
                if any(cmd in message_lower for cmd in ['show', 'list', 'my beneficiaries', 'saved recipients']):
                    return await beneficiary_service.format_beneficiaries_list(user_uuid)
                
                elif message_lower.startswith('save as '):
                    # This is handled by the Assistant now, but keep for backward compatibility
                    return "Please complete a transfer first, then I'll ask if you want to save the recipient!"
                
                elif 'delete' in message_lower or 'remove' in message_lower:
                    return await self._show_delete_options(user_uuid)
            
            # Check if message matches a beneficiary name
            beneficiary = await beneficiary_service.find_beneficiary_by_name(user_uuid, message_lower)
            if beneficiary:
                return await self._suggest_transfer_to_beneficiary(beneficiary)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in legacy beneficiary handler: {e}")
            return None
    
    async def _get_user_uuid_from_chat_id(self, chat_id: str) -> Optional[str]:
        """Get user's UUID from telegram chat_id"""
        try:
            result = self.supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
            if result.data:
                return result.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting user UUID: {e}")
            return None
    
    async def _suggest_transfer_to_beneficiary(self, beneficiary: Dict) -> str:
        """Suggest a transfer to a beneficiary"""
        return f"""💳 **Send to {beneficiary['name']}?**

Recipient: *{beneficiary['account_holder_name']}*
Account: {beneficiary['account_number']} ({beneficiary['bank_name']})

💰 **How much would you like to send?**

Just say the amount like "Send 5000" or "Transfer 1000" """
    
    async def _show_delete_options(self, user_uuid: str) -> str:
        """Show options to delete beneficiaries"""
        try:
            beneficiaries = await beneficiary_service.get_user_beneficiaries(user_uuid)
            
            if not beneficiaries:
                return "You don't have any saved recipients to delete."
            
            response = "🗑️ **Delete Saved Recipients**\n\n"
            response += "Which recipient would you like to remove?\n\n"
            
            for i, beneficiary in enumerate(beneficiaries, 1):
                response += f"{i}. {beneficiary['name']} ({beneficiary['account_holder_name']})\n"
            
            response += f"\nSay 'Delete [number]' to remove a recipient."
            response += f"\nExample: 'Delete 1' or 'Delete 2'"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error showing delete options: {e}")
            return "Sorry, I couldn't load your recipients. Please try again."

# Global legacy handler instance
legacy_beneficiary_handler = LegacyBeneficiaryHandler()
