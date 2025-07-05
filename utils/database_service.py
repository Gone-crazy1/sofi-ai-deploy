"""
Sofi AI Database Service
Comprehensive service for managing all Supabase tables and operations
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from supabase import create_client
import uuid

logger = logging.getLogger(__name__)

class SofiDatabaseService:
    """Manages all Sofi AI database operations"""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    # =================== TRANSFER REQUESTS ===================
    
    async def create_transfer_request(self, user_data: Dict, transfer_data: Dict) -> Dict:
        """Create a new transfer request"""
        try:
            request_data = {
                "user_id": user_data["id"],
                "telegram_chat_id": str(user_data["telegram_chat_id"]),
                "amount": float(transfer_data["amount"]),
                "reason": transfer_data.get("narration", "Sofi AI Transfer"),
                "recipient_code": transfer_data.get("bank_code", ""),
                "recipient_name": transfer_data.get("recipient_name", ""),
                "recipient_account": transfer_data["account_number"],
                "recipient_bank": transfer_data.get("bank_name", ""),
                "status": "pending"
            }
            
            result = self.supabase.table("transfer_requests").insert(request_data).execute()
            
            if result.data:
                logger.info(f"✅ Transfer request created: {result.data[0]['id']}")
                return {"success": True, "request_id": result.data[0]["id"], "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create transfer request"}
                
        except Exception as e:
            logger.error(f"❌ Error creating transfer request: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_transfer_request_status(self, request_id: str, status: str) -> Dict:
        """Update transfer request status"""
        try:
            result = self.supabase.table("transfer_requests").update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            }).eq("id", request_id).execute()
            
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"❌ Error updating transfer request: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== PAYMENT ATTEMPTS ===================
    
    async def create_payment_attempt(self, request_id: str, reference: str, amount: float, channel: str = "telegram") -> Dict:
        """Log a payment attempt"""
        try:
            attempt_data = {
                "reference": reference,
                "request_id": request_id,
                "amount": amount,
                "channel": channel,
                "provider": "paystack",
                "status": "pending"
            }
            
            result = self.supabase.table("payment_attempts").insert(attempt_data).execute()
            
            if result.data:
                logger.info(f"✅ Payment attempt logged: {reference}")
                return {"success": True, "attempt_id": result.data[0]["id"], "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to log payment attempt"}
                
        except Exception as e:
            logger.error(f"❌ Error logging payment attempt: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_payment_attempt(self, reference: str, status: str, response_payload: Dict = None) -> Dict:
        """Update payment attempt with response"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if response_payload:
                update_data["response_payload"] = response_payload
            
            result = self.supabase.table("payment_attempts").update(update_data).eq("reference", reference).execute()
            
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"❌ Error updating payment attempt: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== BANK VERIFICATION CACHE ===================
    
    async def get_cached_verification(self, account_number: str, bank_code: str) -> Optional[Dict]:
        """Get cached bank verification"""
        try:
            result = self.supabase.table("bank_verification").select("*").eq("account_number", account_number).eq("bank_code", bank_code).execute()
            
            if result.data:
                cache_entry = result.data[0]
                # Check if cache is recent (less than 7 days old)
                created_at = datetime.fromisoformat(cache_entry["created_at"].replace('Z', '+00:00'))
                age_days = (datetime.now() - created_at).days
                
                if age_days < 7:
                    logger.info(f"✅ Using cached verification for {account_number}")
                    return cache_entry
                else:
                    logger.info(f"🕒 Cache expired for {account_number}, will re-verify")
                    
            return None
        except Exception as e:
            logger.error(f"❌ Error getting cached verification: {e}")
            return None
    
    async def cache_verification(self, account_number: str, bank_code: str, account_name: str, verification_response: Dict) -> Dict:
        """Cache bank verification result"""
        try:
            cache_data = {
                "account_number": account_number,
                "bank_code": bank_code,
                "account_name": account_name,
                "verified": True,
                "verification_response": verification_response
            }
            
            # Use upsert to handle duplicates
            result = self.supabase.table("bank_verification").upsert(cache_data).execute()
            
            logger.info(f"✅ Cached verification for {account_number}")
            return {"success": True, "data": result.data}
        except Exception as e:
            logger.error(f"❌ Error caching verification: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== BENEFICIARIES ===================
    
    async def get_user_beneficiaries(self, user_id: str) -> List[Dict]:
        """Get all beneficiaries for a user"""
        try:
            result = self.supabase.table("beneficiaries").select("*").eq("user_id", user_id).order("is_default", desc=True).order("created_at", desc=False).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"❌ Error getting beneficiaries: {e}")
            return []
    
    async def add_beneficiary(self, user_id: str, name: str, account_number: str, bank_code: str, account_name: str, is_default: bool = False) -> Dict:
        """Add a new beneficiary"""
        try:
            # If this is default, unset other defaults
            if is_default:
                self.supabase.table("beneficiaries").update({"is_default": False}).eq("user_id", user_id).execute()
            
            beneficiary_data = {
                "user_id": user_id,
                "name": name,
                "account_number": account_number,
                "bank_code": bank_code,
                "account_name": account_name,
                "is_default": is_default
            }
            
            result = self.supabase.table("beneficiaries").insert(beneficiary_data).execute()
            
            if result.data:
                logger.info(f"✅ Beneficiary added: {name}")
                return {"success": True, "beneficiary_id": result.data[0]["id"], "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to add beneficiary"}
                
        except Exception as e:
            logger.error(f"❌ Error adding beneficiary: {e}")
            return {"success": False, "error": str(e)}
    
    async def suggest_beneficiary_save(self, chat_id: str, recipient_data: Dict) -> str:
        """Suggest saving a recipient as beneficiary"""
        try:
            # Get user ID
            user_result = self.supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
            if not user_result.data:
                return ""
            
            user_id = user_result.data[0]["id"]
            
            # Check if already saved
            existing = self.supabase.table("beneficiaries").select("*").eq("user_id", user_id).eq("account_number", recipient_data["account_number"]).execute()
            
            if existing.data:
                return f"💾 Recipient already saved as '{existing.data[0]['name']}'"
            
            # Suggest saving
            save_message = f"""💡 **Save Recipient?**
            
Would you like to save *{recipient_data['account_name']}* for future transfers?

Just say "Save as [nickname]" to add them to your beneficiaries.
Example: "Save as Mum" or "Save as John's account" """
            
            return save_message
            
        except Exception as e:
            logger.error(f"❌ Error suggesting beneficiary save: {e}")
            return ""
    
    # =================== PROFIT TRACKING ===================
    
    async def record_transfer_profit(self, reference: str, transfer_amount: float, paystack_fee: float, platform_fee: float) -> Dict:
        """Record transfer profit"""
        try:
            profit_data = {
                "transfer_reference": reference,
                "transfer_amount": transfer_amount,
                "paystack_fee": paystack_fee,
                "platform_fee": platform_fee,
                "withdrawable": True
            }
            
            result = self.supabase.table("sofi_transfer_profit").insert(profit_data).execute()
            
            if result.data:
                logger.info(f"✅ Profit recorded: ₦{platform_fee} from {reference}")
                return {"success": True, "profit_id": result.data[0]["id"], "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to record profit"}
                
        except Exception as e:
            logger.error(f"❌ Error recording profit: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_total_profits(self, withdrawable_only: bool = True) -> Dict:
        """Get total platform profits"""
        try:
            query = self.supabase.table("sofi_transfer_profit").select("*")
            
            if withdrawable_only:
                query = query.eq("withdrawable", True)
            
            result = query.execute()
            
            if result.data:
                total_revenue = sum(row["net_revenue"] for row in result.data)
                total_transactions = len(result.data)
                
                return {
                    "success": True,
                    "total_revenue": total_revenue,
                    "total_transactions": total_transactions,
                    "average_profit": total_revenue / total_transactions if total_transactions > 0 else 0
                }
            else:
                return {"success": True, "total_revenue": 0, "total_transactions": 0, "average_profit": 0}
                
        except Exception as e:
            logger.error(f"❌ Error getting total profits: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== ERROR LOGGING ===================
    
    async def log_paystack_error(self, context: str, request_payload: Dict = None, response_payload: Dict = None, error_code: str = None, error_message: str = None, related_reference: str = None) -> Dict:
        """Log Paystack errors for debugging"""
        try:
            error_data = {
                "context": context,
                "request_payload": request_payload,
                "response_payload": response_payload,
                "error_code": error_code,
                "error_message": error_message,
                "related_reference": related_reference
            }
            
            result = self.supabase.table("paystack_errors").insert(error_data).execute()
            
            logger.error(f"🚨 Paystack error logged: {context} - {error_message}")
            return {"success": True, "error_id": result.data[0]["id"] if result.data else None}
            
        except Exception as e:
            logger.error(f"❌ Error logging Paystack error: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== AUDIT LOGGING ===================
    
    async def log_user_action(self, user_id: str, telegram_chat_id: str, action: str, target_table: str = None, target_id: str = None, metadata: Dict = None) -> Dict:
        """Log user actions for audit trail"""
        try:
            audit_data = {
                "user_id": user_id,
                "telegram_chat_id": telegram_chat_id,
                "action": action,
                "target_table": target_table,
                "target_id": target_id,
                "metadata": metadata or {}
            }
            
            result = self.supabase.table("audit_logs").insert(audit_data).execute()
            
            logger.info(f"📝 Audit log: {action} by {telegram_chat_id}")
            return {"success": True, "audit_id": result.data[0]["id"] if result.data else None}
            
        except Exception as e:
            logger.error(f"❌ Error logging audit: {e}")
            return {"success": False, "error": str(e)}
    
    # =================== REFUNDS ===================
    
    async def create_refund(self, original_payment_id: str, amount: float, reason: str) -> Dict:
        """Create a refund record"""
        try:
            refund_reference = f"refund_{uuid.uuid4().hex[:12]}"
            
            refund_data = {
                "original_payment_id": original_payment_id,
                "refund_reference": refund_reference,
                "amount": amount,
                "reason": reason,
                "status": "pending"
            }
            
            result = self.supabase.table("refunds").insert(refund_data).execute()
            
            if result.data:
                logger.info(f"✅ Refund created: {refund_reference}")
                return {"success": True, "refund_id": result.data[0]["id"], "refund_reference": refund_reference, "data": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create refund"}
                
        except Exception as e:
            logger.error(f"❌ Error creating refund: {e}")
            return {"success": False, "error": str(e)}

# Global database service instance
db_service = SofiDatabaseService()
