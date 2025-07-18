"""
Legacy-Compatible Beneficiary Service for Sofi AI
Works with existing beneficiaries table structure (TEXT user_id = telegram_chat_id)
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from supabase import create_client

logger = logging.getLogger(__name__)

class LegacyBeneficiaryService:
    """Manages beneficiaries using existing table structure"""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    async def save_beneficiary(self, telegram_chat_id: str, name: str, bank_name: str, 
                              account_number: str, account_holder_name: str) -> Dict[str, Any]:
        """
        Save a new beneficiary using existing table structure
        
        Args:
            telegram_chat_id: User's Telegram chat ID (as string)
            name: Nickname/friendly name for the beneficiary
            bank_name: Bank name
            account_number: Account number
            account_holder_name: Real account holder name
        """
        try:
            # Check for duplicates (same user + account_number)
            existing = self.supabase.table("beneficiaries")\
                .select("*")\
                .eq("user_id", telegram_chat_id)\
                .eq("account_number", account_number)\
                .execute()
            
            if existing.data:
                return {
                    "success": False,
                    "error": f"Account {account_number} is already saved as '{existing.data[0]['nickname'] or existing.data[0]['beneficiary_name']}'"
                }
            
            # Insert new beneficiary using existing schema
            beneficiary_data = {
                "user_id": telegram_chat_id,  # telegram_chat_id as TEXT
                "beneficiary_name": account_holder_name,  # Real name from bank
                "account_number": account_number,
                "bank_name": bank_name,
                "bank_code": bank_name,  # Use bank_name as bank_code for now
                "nickname": name,  # User-friendly name
                "last_used": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("beneficiaries").insert(beneficiary_data).execute()
            
            if result.data:
                logger.info(f"✅ Beneficiary saved: {name} - {account_number}")
                return {
                    "success": True,
                    "beneficiary_id": result.data[0]["id"],
                    "message": f"✅ {account_holder_name} saved as '{name}' for future transfers!"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save beneficiary to database"
                }
                
        except Exception as e:
            logger.error(f"❌ Error saving beneficiary: {e}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }
    
    async def get_user_beneficiaries(self, telegram_chat_id: str) -> List[Dict]:
        """Get all beneficiaries for a user"""
        try:
            result = self.supabase.table("beneficiaries")\
                .select("*")\
                .eq("user_id", telegram_chat_id)\
                .order("last_used", desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error getting beneficiaries: {e}")
            return []
    
    async def find_beneficiary_by_name(self, telegram_chat_id: str, name: str) -> Optional[Dict]:
        """Find beneficiary by nickname (fuzzy matching)"""
        try:
            beneficiaries = await self.get_user_beneficiaries(telegram_chat_id)
            name_lower = name.lower().strip()
            
            # Check nickname first (exact match)
            for beneficiary in beneficiaries:
                nickname = beneficiary.get("nickname", "")
                if nickname and nickname.lower() == name_lower:
                    return beneficiary
            
            # Check nickname partial match
            for beneficiary in beneficiaries:
                nickname = beneficiary.get("nickname", "")
                if (nickname and 
                    (name_lower in nickname.lower() or nickname.lower() in name_lower)):
                    return beneficiary
            
            # Check beneficiary_name partial match
            for beneficiary in beneficiaries:
                beneficiary_name = beneficiary.get("beneficiary_name", "")
                if (beneficiary_name and 
                    (name_lower in beneficiary_name.lower() or beneficiary_name.lower() in name_lower)):
                    return beneficiary
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding beneficiary: {e}")
            return None
    
    async def format_beneficiaries_list(self, telegram_chat_id: str) -> str:
        """Format beneficiaries list for display"""
        try:
            beneficiaries = await self.get_user_beneficiaries(telegram_chat_id)
            
            if not beneficiaries:
                return """💳 **No Saved Recipients**

You haven't saved any recipients yet.

After completing a transfer, I'll ask if you want to save the recipient for faster future transfers."""
            
            response = "💳 **Your Saved Recipients**\n\n"
            
            for i, beneficiary in enumerate(beneficiaries, 1):
                nickname = beneficiary.get("nickname", "")
                display_name = nickname if nickname else beneficiary.get("beneficiary_name", "Unknown")
                
                response += f"{i}. **{display_name}**\n"
                response += f"   {beneficiary.get('beneficiary_name', 'Unknown')}\n"
                response += f"   {beneficiary.get('account_number', 'Unknown')} • {beneficiary.get('bank_name', 'Unknown')}\n\n"
            
            response += "💡 **Quick Tips:**\n"
            response += "• Just type a recipient's name to start a transfer\n"
            response += "• After any transfer, I'll offer to save the recipient\n"
            response += "• Say 'delete recipients' to manage your list"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error formatting beneficiaries: {e}")
            return "❌ Unable to load your saved recipients. Please try again."
    
    def create_save_beneficiary_prompt(self, recipient_name: str, bank_name: str, 
                                     account_number: str) -> str:
        """Create the prompt message for Assistant to ask about saving beneficiary"""
        return f"""👉 Would you like to save **{recipient_name}** - {bank_name} - {account_number} as a beneficiary for future transfers?

💡 This will let you send money to them instantly just by saying their name!

Reply **"yes"** or **"save"** to add them to your saved recipients."""
    
    async def handle_save_response(self, telegram_chat_id: str, response: str, 
                                 transfer_data: Dict) -> Dict[str, Any]:
        """Handle user's response to save beneficiary prompt"""
        try:
            response_lower = response.lower().strip()
            
            # Check if user wants to save
            if response_lower in ['yes', 'y', 'save', 'ok', 'sure']:
                # Use recipient's first name as default nickname
                recipient_name = transfer_data.get("recipient_name", "")
                default_name = recipient_name.split()[0] if recipient_name else "Recipient"
                
                return await self.save_beneficiary(
                    telegram_chat_id=telegram_chat_id,
                    name=default_name,
                    bank_name=transfer_data.get("bank_name", ""),
                    account_number=transfer_data.get("account_number", ""),
                    account_holder_name=recipient_name
                )
            
            elif response_lower in ['no', 'n', 'skip', 'not now']:
                return {
                    "success": True,
                    "message": "✅ Transfer completed. Recipient not saved."
                }
            
            elif response_lower.startswith('save as '):
                # Custom name provided
                custom_name = response[8:].strip()
                if not custom_name:
                    return {
                        "success": False,
                        "error": "Please provide a name. Example: 'save as Mum'"
                    }
                
                return await self.save_beneficiary(
                    telegram_chat_id=telegram_chat_id,
                    name=custom_name,
                    bank_name=transfer_data.get("bank_name", ""),
                    account_number=transfer_data.get("account_number", ""),
                    account_holder_name=transfer_data.get("recipient_name", "")
                )
            
            else:
                # Treat any other response as a custom nickname
                return await self.save_beneficiary(
                    telegram_chat_id=telegram_chat_id,
                    name=response.strip(),
                    bank_name=transfer_data.get("bank_name", ""),
                    account_number=transfer_data.get("account_number", ""),
                    account_holder_name=transfer_data.get("recipient_name", "")
                )
                
        except Exception as e:
            logger.error(f"❌ Error handling save response: {e}")
            return {
                "success": False,
                "error": "Failed to process your response. Please try again."
            }

# Global legacy beneficiary service instance
legacy_beneficiary_service = LegacyBeneficiaryService()
