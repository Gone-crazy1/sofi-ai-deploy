"""
Beneficiary Management System for Sofi AI
Allows users to save and manage recipient accounts for faster transfers
"""

import logging
from typing import Dict, List, Optional
from utils.database_service import db_service

logger = logging.getLogger(__name__)

class BeneficiaryManager:
    """Manages saved beneficiaries for users"""
    
    async def handle_beneficiary_command(self, chat_id: str, message: str, user_data: Dict) -> Optional[str]:
        """Handle beneficiary-related commands"""
        message_lower = message.lower().strip()
        
        # Check for beneficiary keywords
        if any(keyword in message_lower for keyword in ['beneficiary', 'beneficiaries', 'saved', 'save', 'my recipients']):
            
            if any(cmd in message_lower for cmd in ['show', 'list', 'my beneficiaries', 'saved recipients']):
                return await self.list_beneficiaries(user_data["id"])
            
            elif message_lower.startswith('save as '):
                # Extract nickname from "save as [nickname]"
                nickname = message[8:].strip()
                return await self.save_last_recipient(chat_id, user_data["id"], nickname)
            
            elif 'delete' in message_lower or 'remove' in message_lower:
                # Handle delete beneficiary
                return await self.show_delete_options(user_data["id"])
        
        # Check if message matches a beneficiary name
        beneficiary = await self.find_beneficiary_by_name(user_data["id"], message_lower)
        if beneficiary:
            return await self.suggest_transfer_to_beneficiary(beneficiary)
        
        return None
    
    async def list_beneficiaries(self, user_id: str) -> str:
        """List all beneficiaries for a user"""
        try:
            beneficiaries = await db_service.get_user_beneficiaries(user_id)
            
            if not beneficiaries:
                return """💳 **No Saved Recipients**

You haven't saved any recipients yet.

To save someone for future transfers:
1. Complete any transfer first
2. Then say "Save as [nickname]"

Example: "Save as Mum" or "Save as John's account" """
            
            response = "💳 **Your Saved Recipients**\n\n"
            
            for i, beneficiary in enumerate(beneficiaries, 1):
                default_indicator = " ⭐" if beneficiary["is_default"] else ""
                response += f"{i}. **{beneficiary['name']}**{default_indicator}\n"
                response += f"   {beneficiary['account_name']}\n"
                response += f"   {beneficiary['account_number']} • {beneficiary['bank_code']}\n\n"
            
            response += "💡 **Quick Tips:**\n"
            response += "• Just type a recipient's name to start a transfer\n"
            response += "• Say 'Save as [name]' after any transfer to save them\n"
            response += "• Say 'Delete recipients' to manage your list"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error listing beneficiaries: {e}")
            return "Sorry, I couldn't load your saved recipients. Please try again."
    
    async def save_last_recipient(self, chat_id: str, user_id: str, nickname: str) -> str:
        """Save the last transfer recipient as a beneficiary"""
        try:
            if not nickname:
                return "Please provide a nickname. Example: 'Save as Mum'"
            
            # Get the most recent transfer request for this user
            from supabase import create_client
            import os
            
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            recent_transfer = supabase.table("transfer_requests")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if not recent_transfer.data:
                return "No recent transfers found. Complete a transfer first, then save the recipient."
            
            transfer = recent_transfer.data[0]
            
            # Check if already saved
            existing = await db_service.get_user_beneficiaries(user_id)
            for beneficiary in existing:
                if beneficiary["account_number"] == transfer["recipient_account"]:
                    return f"✅ {transfer['recipient_name']} is already saved as '{beneficiary['name']}'"
            
            # Save as beneficiary
            result = await db_service.add_beneficiary(
                user_id=user_id,
                name=nickname,
                account_number=transfer["recipient_account"],
                bank_code=transfer["recipient_code"],
                account_name=transfer["recipient_name"],
                is_default=(len(existing) == 0)  # First beneficiary is default
            )
            
            if result["success"]:
                # Log the action
                await db_service.log_user_action(
                    user_id=user_id,
                    telegram_chat_id=str(chat_id),
                    action="beneficiary_added",
                    target_table="beneficiaries",
                    target_id=result["beneficiary_id"],
                    metadata={"nickname": nickname, "account_name": transfer["recipient_name"]}
                )
                
                default_msg = " and set as your default recipient" if len(existing) == 0 else ""
                
                return f"""✅ **Recipient Saved!**

*{transfer['recipient_name']}* has been saved as *"{nickname}"*{default_msg}.

💡 **Quick Transfer:** Just type "{nickname}" to send money to them instantly!"""
            else:
                return f"❌ Failed to save recipient: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"❌ Error saving beneficiary: {e}")
            return "Sorry, I couldn't save the recipient. Please try again."
    
    async def find_beneficiary_by_name(self, user_id: str, name: str) -> Optional[Dict]:
        """Find a beneficiary by name (fuzzy matching)"""
        try:
            beneficiaries = await db_service.get_user_beneficiaries(user_id)
            
            name_lower = name.lower().strip()
            
            # Exact match first
            for beneficiary in beneficiaries:
                if beneficiary["name"].lower() == name_lower:
                    return beneficiary
            
            # Partial match
            for beneficiary in beneficiaries:
                if name_lower in beneficiary["name"].lower() or beneficiary["name"].lower() in name_lower:
                    return beneficiary
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding beneficiary: {e}")
            return None
    
    async def suggest_transfer_to_beneficiary(self, beneficiary: Dict) -> str:
        """Suggest a transfer to a beneficiary"""
        return f"""💳 **Send to {beneficiary['name']}?**

Recipient: *{beneficiary['account_name']}*
Account: {beneficiary['account_number']} ({beneficiary['bank_code']})

💰 **How much would you like to send?**

Just say the amount like "Send 5000" or "Transfer 1000" """
    
    async def show_delete_options(self, user_id: str) -> str:
        """Show options to delete beneficiaries"""
        try:
            beneficiaries = await db_service.get_user_beneficiaries(user_id)
            
            if not beneficiaries:
                return "You don't have any saved recipients to delete."
            
            response = "🗑️ **Delete Saved Recipients**\n\n"
            response += "Which recipient would you like to remove?\n\n"
            
            for i, beneficiary in enumerate(beneficiaries, 1):
                response += f"{i}. {beneficiary['name']} ({beneficiary['account_name']})\n"
            
            response += f"\nSay 'Delete [number]' to remove a recipient."
            response += f"\nExample: 'Delete 1' or 'Delete 2'"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error showing delete options: {e}")
            return "Sorry, I couldn't load your recipients. Please try again."
    
    async def auto_suggest_save_after_transfer(self, chat_id: str, transfer_result: Dict) -> str:
        """Auto-suggest saving recipient after successful transfer"""
        try:
            if not transfer_result.get("success"):
                return ""
            
            recipient_name = transfer_result.get("recipient_name", "")
            if not recipient_name:
                return ""
            
            # Get user data
            from supabase import create_client
            import os
            
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            user_result = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
            
            if not user_result.data:
                return ""
            
            user_id = user_result.data[0]["id"]
            
            # Check if already saved
            existing = await db_service.get_user_beneficiaries(user_id)
            account_number = transfer_result.get("account_number", "")
            
            for beneficiary in existing:
                if beneficiary["account_number"] == account_number:
                    return ""  # Already saved
            
            # Suggest saving
            suggestion = f"""
💡 **Save for faster transfers?**

Would you like to save *{recipient_name}* for future transfers?

Just reply with: "Save as [nickname]"
Example: "Save as Mum" or "Save as {recipient_name.split()[0]}" """
            
            return suggestion
            
        except Exception as e:
            logger.error(f"❌ Error suggesting save: {e}")
            return ""

# Global beneficiary manager
beneficiary_manager = BeneficiaryManager()
