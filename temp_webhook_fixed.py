"""
Paystack Webhook Handler for Sofi AI
====================================
Handles incoming webhooks from Paystack for payments and transfers
"""

import os
import json
import logging
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any
from supabase import create_client

logger = logging.getLogger(__name__)

class PaystackWebhookHandler:
    """Handle Paystack webhooks for Sofi AI"""
    
    def __init__(self):
        """Initialize webhook handler"""
        self.webhook_secret = os.getenv("PAYSTACK_WEBHOOK_SECRET")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.webhook_secret:
            logger.warning("PAYSTACK_WEBHOOK_SECRET not set - webhook verification disabled")
        
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
        else:
            logger.error("Supabase credentials missing")
            self.supabase = None
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Paystack webhook signature"""
        if not self.webhook_secret:
            logger.warning("ΓÜá∩╕Å PAYSTACK_WEBHOOK_SECRET not configured - skipping verification (DEVELOPMENT MODE)")
            logger.warning("ΓÜá∩╕Å For production, please set PAYSTACK_WEBHOOK_SECRET in your .env file")
            return True  # Allow for development/testing
        
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False
    
    async def handle_webhook(self, data: Dict, signature: str = None) -> Dict:
        """Main webhook handler"""
        try:
            event = data.get("event")
            data_payload = data.get("data", {})
            
            logger.info(f"≡ƒôÑ Webhook received: {event}")
            
            # Verify signature if provided
            if signature and not self.verify_signature(json.dumps(data).encode(), signature):
                logger.error("Γ¥î Invalid webhook signature")
                return {"success": False, "error": "Invalid signature"}
            else:
                logger.info("ΓÜá∩╕Å Skipping webhook signature verification (development mode)")
            
            # Route to appropriate handler
            if event == "charge.success":
                return await self.handle_charge_success(data_payload)
            elif event == "transfer.success":
                return await self.handle_transfer_success(data_payload)
            elif event == "transfer.failed":
                return await self.handle_transfer_failed(data_payload)
            elif event == "dedicated_account.assign":
                return await self.handle_dedicated_account_assign(data_payload)
            else:
                logger.info(f"≡ƒô¥ Unhandled webhook event: {event}")
                return {"success": True, "message": f"Unhandled event: {event}"}
        
        except Exception as e:
            logger.error(f"Γ¥î Webhook processing error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_charge_success(self, data: Dict) -> Dict:
        """Handle successful payment to dedicated account"""
        try:
            if not data or not isinstance(data, dict):
                logger.error("Γ¥î Invalid data received in charge.success handler")
                return {"success": False, "error": "Invalid data format"}
            
            # Extract payment details with safe defaults
            amount = data.get("amount", 0)
            if amount:
                amount = amount / 100  # Convert from kobo
            
            reference = data.get("reference", "")
            customer = data.get("customer") or {}
            customer_code = customer.get("customer_code", "") if isinstance(customer, dict) else ""
            
            # Enhanced sender information extraction
            sender_name = self._extract_sender_name(data, customer)
            sender_bank = self._extract_sender_bank(data)
            
            # Γ£à DEBUG: Log webhook structure to help identify missing sender fields
            logger.info(f"≡ƒöì DEBUG: Webhook payload keys: {list(data.keys())}")
            if data.get("authorization"):
                logger.info(f"≡ƒöì DEBUG: Authorization keys: {list(data.get('authorization', {}).keys())}")
            if data.get("metadata"):
                logger.info(f"≡ƒöì DEBUG: Metadata keys: {list(data.get('metadata', {}).keys())}")
            if data.get("customer"):
                logger.info(f"≡ƒöì DEBUG: Customer keys: {list(data.get('customer', {}).keys())}")
            
            narration = data.get("narration") or data.get("description") or "Money Transfer"
            
            # Get account details
            dedicated_account = data.get("authorization", {})
            account_number = dedicated_account.get("receiver_bank_account_number")
            
            logger.info(f"≡ƒÆ░ Payment received: Γéª{amount:,.2f} to account {account_number}")
            logger.info(f"≡ƒæñ Sender: {sender_name} via {sender_bank}")
            
            if not self.supabase:
                logger.error("Supabase not configured")
                return {"success": False, "error": "Database not configured"}
            
            # Find user by customer code or account number and get their UUID
            user_query = self.supabase.table("users").select("id, telegram_chat_id, wallet_balance").eq("paystack_customer_code", customer_code).execute()
            
            if not user_query.data:
                # Try finding by account number via virtual_accounts table
                account_query = self.supabase.table("virtual_accounts").select("telegram_chat_id").eq("account_number", account_number).execute()
                
                if not account_query.data:
                    logger.error(f"User not found for payment: {reference}")
                    return {"success": False, "error": "User not found"}
                
                # Get telegram_chat_id from virtual_accounts, then find user
                telegram_chat_id = account_query.data[0]["telegram_chat_id"]
                user_query = self.supabase.table("users").select("id, telegram_chat_id, wallet_balance").eq("telegram_chat_id", telegram_chat_id).execute()
                
                if not user_query.data:
                    logger.error(f"User not found for telegram_chat_id: {telegram_chat_id}")
                    return {"success": False, "error": "User not found"}
                
                user_data = user_query.data[0]
            else:
                # User found directly
                user_data = user_query.data[0]
            
            user_uuid = user_data["id"]  # This is the actual UUID
            telegram_chat_id = user_data["telegram_chat_id"]  # This is the Telegram ID for notifications
            current_balance = float(user_data.get("wallet_balance", 0))
            new_balance = current_balance + amount
            
            # Record transaction with correct UUID and all required fields
            transaction_data = {
                "user_id": user_uuid,  # Use actual UUID from users table
                "transaction_type": "credit",  # This is a deposit/credit
                "amount": amount,
                "reference": reference,
                "status": "success",
                "description": f"Deposit from {sender_name} via {sender_bank}",
                "bank_code": "999999",  # Paystack internal code
                "bank_name": sender_bank,  # Sender's bank name
                "account_number": account_number,  # Recipient account number
                "sender_name": sender_name,  # Store sender name
                "narration": narration,  # Store narration/description
                "created_at": data.get("created_at")
            }
            
            # Γ£à DEBUG: Log what sender information we're actually saving
            logger.info(f"≡ƒÆ╛ SAVING TO DB: sender_name='{sender_name}', sender_bank='{sender_bank}', narration='{narration}'")
            
            try:
                self.supabase.table("bank_transactions").insert(transaction_data).execute()
                logger.info(f"Γ£à Transaction recorded for user {user_uuid}")
            except Exception as e:
                logger.warning(f"Could not record transaction: {e}")
                # Continue anyway - the balance update is more important
            
            # Update user balance using UUID
            self.supabase.table("users").update({"wallet_balance": new_balance}).eq("id", user_uuid).execute()
            
            # ALSO update virtual_accounts balance for consistency
            try:
                self.supabase.table("virtual_accounts").update({"balance": new_balance}).eq("account_number", account_number).execute()
                logger.info(f"Γ£à Virtual account balance updated: Γéª{new_balance:,.2f}")
            except Exception as e:
                logger.warning(f"Could not update virtual account balance: {e}")
            
            # Send notification to user via Telegram with sender details
            await self.send_credit_notification(
                telegram_chat_id, 
                amount, 
                new_balance, 
                sender_name, 
                sender_bank, 
                narration
            )
            
            logger.info(f"Γ£à Credit processed: Γéª{amount:,.2f} for user {telegram_chat_id}")
            return {"success": True, "message": "Credit processed successfully"}
        
        except Exception as e:
            logger.error(f"Γ¥î Error processing charge success: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extract_sender_name(self, data: Dict, customer: Dict) -> str:
        """Extract sender name from payment data with enhanced filtering"""
        # Virtual account patterns to filter out (these are not real sender names)
        virtual_account_patterns = [
            r"mr\s+hawt",  # Your Sofi virtual account name - NOT the real sender!
            r"tobi\s*$",   # Single name "tobi"
            r"sofi\s+user", # Generic sofi user
            r"paystack",   # Paystack internal
            r"dva\s*\d+",  # Dedicated virtual account patterns
            r"virtual\s+account",
            r"temp\s+account",
            r"test\s+account",
            r"sofi\s+ai",  # Sofi AI patterns
            r"virtual\s+acc"
        ]
        
        # Try ALL possible fields for the REAL sender name (not virtual account names)
        potential_names = [
            # ≡ƒöÑ PRIORITY FIX: Move authorization.sender_name to TOP of list
            data.get("authorization", {}).get("sender_name") if isinstance(data.get("authorization"), dict) else None,
            
            # Primary sender fields (most likely to have real sender)
            data.get("real_sender_name"),  # Custom field for real sender
            data.get("originator_name"),   # Bank originator
            data.get("sender_account_name"), # Actual sender account name
            data.get("source_account_name"), # Source account holder
            data.get("payer_name"),        # Who actually paid
            data.get("sender_name"),       # General sender
            data.get("account_name"),      # Account holder name
            
            # Γ£à ADDITIONAL FIELDS - Common Paystack webhook fields for sender info
            data.get("channel", {}).get("account_name") if isinstance(data.get("channel"), dict) else None,
            data.get("channel", {}).get("sender_name") if isinstance(data.get("channel"), dict) else None,
            data.get("channel", {}).get("customer_name") if isinstance(data.get("channel"), dict) else None,
            data.get("gateway_response", {}).get("sender_name") if isinstance(data.get("gateway_response"), dict) else None,
            data.get("gateway_response", {}).get("account_name") if isinstance(data.get("gateway_response"), dict) else None,
            data.get("log", {}).get("sender_name") if isinstance(data.get("log"), dict) else None,
            data.get("log", {}).get("account_name") if isinstance(data.get("log"), dict) else None,
            data.get("fees_breakdown", {}).get("sender_name") if isinstance(data.get("fees_breakdown"), dict) else None,
        ]
        
        # Try customer object fields (these might have real sender info) - MOVE TO LOWER PRIORITY
        if isinstance(customer, dict):
            potential_names.extend([
                customer.get("name"),
                customer.get("account_name"),
                customer.get("customer_name"),
                customer.get("full_name"),
                customer.get("email"),
                # Move customer.first_name + last_name to BOTTOM as fallback
                (customer.get("first_name", "") + " " + customer.get("last_name", "")).strip() if customer.get("first_name") or customer.get("last_name") else None,
            ])
        
        # Try authorization fields (for bank transfers - often has real sender)
        auth = data.get("authorization", {})
        if isinstance(auth, dict):
            potential_names.extend([
                auth.get("account_name"),      # Most important - real account holder
                auth.get("sender_name"),
                auth.get("sender_account_name"),
                auth.get("originator_name"),    # Bank originator name
                # Γ£à Additional authorization fields
                auth.get("customer_name"),
                auth.get("bank_account_name"),
                auth.get("source_account_name"),
                auth.get("receiver_bank_account_name"),  # Sometimes has sender info
            ])
        
        # Try metadata fields (sometimes contains real sender info)
        metadata = data.get("metadata", {})
        if isinstance(metadata, dict):
            potential_names.extend([
                metadata.get("sender_name"),
                metadata.get("originator_name"),
                metadata.get("real_sender"),
                metadata.get("account_holder_name"),
                # Γ£à Additional metadata fields
                metadata.get("customer_name"),
                metadata.get("payer_name"),
                metadata.get("source_name"),
                metadata.get("transfer_source"),
            ])
        
        import re
        
        # Find first valid name that's NOT a virtual account pattern
        for name in potential_names:
            if name and name.strip() and name.lower() not in ["none", "unknown", "", "null"]:
                clean_name = name.strip()
                
                # Check if this looks like a virtual account name (IGNORE these!)
                is_virtual_account = False
                for pattern in virtual_account_patterns:
                    if re.search(pattern, clean_name.lower()):
                        is_virtual_account = True
                        logger.info(f"≡ƒÜ½ Ignoring virtual account name: {clean_name}")
                        break
                
                # Also check for very short names or obvious test patterns
                if len(clean_name) < 3 or clean_name.lower() in ["user", "temp", "test", "demo"]:
                    is_virtual_account = True
                
                # If this is NOT a virtual account name, it's probably the real sender
                if not is_virtual_account and len(clean_name) > 2:
                    logger.info(f"Γ£à Real sender found: {clean_name}")
                    return clean_name
        
        # Enhanced fallback: Try to extract real sender from narration/description
        possible_narration = data.get("narration") or data.get("description") or ""
        
        # Patterns to extract REAL sender names from transaction descriptions
        narration_patterns = [
            r"transfer\s+from\s+([A-Za-z\s]{3,30}?)(?:\s+to|\s*$)",
            r"credit\s+from\s+([A-Za-z\s]{3,30}?)(?:\s+to|\s*$)",
            r"payment\s+from\s+([A-Za-z\s]{3,30}?)(?:\s+to|\s*$)",
            r"sent\s+by\s+([A-Za-z\s]{3,30}?)(?:\s+to|\s*$)",
            r"from:\s*([A-Za-z\s]{3,30}?)(?:\s+to|\s*$)",
            r"sender:\s*([A-Za-z\s]{3,30}?)(?:\s+to|\s*$)",
            r"originator:\s*([A-Za-z\s]{3,30}?)(?:\s+to|\s*$)"
        ]
        
        for pattern in narration_patterns:
            match = re.search(pattern, possible_narration, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                
                # Validate extracted name isn't a virtual account pattern
                is_virtual = False
                for vpattern in virtual_account_patterns:
                    if re.search(vpattern, extracted_name.lower()):
                        is_virtual = True
                        break
                
                if not is_virtual and len(extracted_name) > 2:
                    logger.info(f"Γ£à Real sender extracted from narration: {extracted_name}")
                    return extracted_name
        
        # Final fallback: Return "Bank Transfer" instead of confusing virtual account names
        logger.warning("ΓÜá∩╕Å Could not identify real sender - using 'Bank Transfer'")
        return "Bank Transfer"

    def _normalize_bank_name(self, bank_name: str) -> str:
        """Normalize bank names to show user-friendly versions"""
        if not bank_name or not bank_name.strip():
            return bank_name
            
        bank_name = bank_name.strip()
        
        # Define bank name mappings for cleaner display
        bank_mappings = {
            # OPay variations
            "opay digital services limited (opay)": "OPay",
            "opay digital services limited": "OPay", 
            "opay digital services": "OPay",
            "opay (opay digital services limited)": "OPay",
            
            # Moniepoint variations
            "moniepoint microfinance bank": "Moniepoint",
            "moniepoint mfb": "Moniepoint",
            "moniepoint inc": "Moniepoint",
            
            # PalmPay variations
            "palmpay limited": "PalmPay",
            "palmpay": "PalmPay",
            
            # Kuda variations
            "kuda microfinance bank": "Kuda Bank",
            "kuda mfb": "Kuda Bank",
            
            # Major banks
            "guaranty trust bank plc": "GTBank",
            "access bank plc": "Access Bank",
            "united bank for africa plc": "UBA",
            "first bank of nigeria limited": "First Bank",
            "zenith bank plc": "Zenith Bank",
            "union bank of nigeria plc": "Union Bank",
            "sterling bank plc": "Sterling Bank",
            "fidelity bank plc": "Fidelity Bank",
            "first city monument bank limited": "FCMB",
            "ecobank nigeria limited": "Ecobank",
            "wema bank plc": "Wema Bank",
            "stanbic ibtc bank plc": "Stanbic IBTC",
            
            # Other fintech
            "carbon": "Carbon",
            "fairmoney microfinance bank": "FairMoney",
            "vfd microfinance bank": "VFD Bank",
            "providus bank limited": "Providus Bank",
        }
        
        # Check for exact match (case insensitive)
        bank_lower = bank_name.lower()
        if bank_lower in bank_mappings:
            return bank_mappings[bank_lower]
        
        # Check for partial matches and clean up
        for full_name, clean_name in bank_mappings.items():
            if full_name in bank_lower or bank_lower in full_name:
                return clean_name
        
        # Generic cleanup for unmatched banks
        # Remove common suffixes and cleanup
        cleaned = bank_name
        
        # Remove common bank suffixes
        suffixes_to_remove = [
            " plc", " limited", " ltd", " inc", " microfinance bank", 
            " mfb", " bank", " nigeria", " digital services"
        ]
        
        for suffix in suffixes_to_remove:
            if cleaned.lower().endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
        
        # Remove parenthetical duplicates like "Bank Name (Bank)"
        import re
        # Remove patterns like "(something)" at the end
        cleaned = re.sub(r'\s*\([^)]+\)$', '', cleaned)
        
        # Capitalize properly
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        return cleaned if cleaned else bank_name

    def _extract_sender_bank(self, data: Dict) -> str:
        """Extract sender bank from payment data with fallbacks"""
        potential_banks = [
            data.get("sender_bank"),
            data.get("bank_name"),
            data.get("bank"),
            data.get("originator_bank"),  # New field
            data.get("source_bank"),  # New field
            # Γ£à Additional common Paystack fields
            data.get("gateway_response", {}).get("bank_name") if isinstance(data.get("gateway_response"), dict) else None,
            data.get("gateway_response", {}).get("sender_bank") if isinstance(data.get("gateway_response"), dict) else None,
            data.get("channel", {}).get("bank_name") if isinstance(data.get("channel"), dict) else None,
            data.get("channel", {}).get("sender_bank") if isinstance(data.get("channel"), dict) else None,
        ]
        
        # Try authorization fields
        auth = data.get("authorization", {})
        if isinstance(auth, dict):
            potential_banks.extend([
                auth.get("bank"),
                auth.get("sender_bank"),
                auth.get("bank_name"),
                # Γ£à Additional authorization fields
                auth.get("sender_bank_name"),
                auth.get("originator_bank"),
                auth.get("source_bank_name"),
            ])
        
        # Γ£à Try metadata fields for bank information
        metadata = data.get("metadata", {})
        if isinstance(metadata, dict):
            potential_banks.extend([
                metadata.get("sender_bank"),
                metadata.get("bank_name"),
                metadata.get("originator_bank"),
                metadata.get("source_bank"),
            ])
        
        # Find first valid bank and normalize it
        for bank in potential_banks:
            if bank and bank.strip() and bank.lower() not in ["none", "unknown", "", "null"]:
                # Normalize the bank name for better display
                normalized_bank = self._normalize_bank_name(bank.strip())
                return normalized_bank
        
        # Fallback: Try to extract from narration or description
        possible_narration = data.get("narration") or data.get("description") or ""
        import re
        patterns = [
            r"via ([A-Za-z ]+)",
            r"from ([A-Za-z ]+) bank",
            r"transfer via ([A-Za-z ]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, possible_narration, re.IGNORECASE)
            if match:
                bank = match.group(1).strip()
                if len(bank) > 2:  # Reasonable bank name length
                    # Normalize the extracted bank name
                    normalized_bank = self._normalize_bank_name(bank)
                    return normalized_bank
        
        return "Paystack"  # Final fallback
    
    async def handle_transfer_success(self, data: Dict) -> Dict:
        """Handle successful outgoing transfer"""
        try:
            reference = data.get("reference")
            amount = data.get("amount", 0) / 100
            recipient = data.get("recipient", {})
            
            logger.info(f"Γ£à Transfer successful: Γéª{amount:,.2f} - {reference}")
            
            if not self.supabase:
                return {"success": False, "error": "Database not configured"}
            
            # Update transaction status with available columns
            self.supabase.table("bank_transactions").update({"status": "success"}).eq("reference", reference).execute()
            
            # Send notification (implement as needed)
            return {"success": True, "message": "Transfer success processed"}
        
        except Exception as e:
            logger.error(f"Γ¥î Error processing transfer success: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_transfer_failed(self, data: Dict) -> Dict:
        """Handle failed outgoing transfer"""
        try:
            reference = data.get("reference")
            amount = data.get("amount", 0) / 100
            
            logger.info(f"Γ¥î Transfer failed: Γéª{amount:,.2f} - {reference}")
            
            if not self.supabase:
                return {"success": False, "error": "Database not configured"}
            
            # Update transaction status
            self.supabase.table("bank_transactions").update({"status": "failed"}).eq("reference", reference).execute()
            
            # Refund user (basic implementation)
            transaction_query = self.supabase.table("bank_transactions").select("user_id").eq("reference", reference).execute()
            
            if transaction_query.data:
                user_id = transaction_query.data[0]["user_id"]
                current_balance = await self.get_user_balance(user_id)
                new_balance = current_balance + amount
                
                # Update user balance
                self.supabase.table("users").update({"wallet_balance": new_balance}).eq("telegram_chat_id", user_id).execute()
                
                # Record refund transaction
                refund_data = {
                    "user_id": user_id,
                    "amount": amount,
                    "reference": f"{reference}_refund",
                    "status": "success",
                    "wallet_balance_before": current_balance,
                    "wallet_balance_after": new_balance,
                    "created_at": datetime.now().isoformat()
                }
                self.supabase.table("bank_transactions").insert(refund_data).execute()
                
                logger.info(f"≡ƒÆ░ Refunded Γéª{amount:,.2f} to user {user_id}")
            
            return {"success": True, "message": "Transfer failure processed"}
        
        except Exception as e:
            logger.error(f"Γ¥î Error processing transfer failure: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_dedicated_account_assign(self, data: Dict) -> Dict:
        """Handle dedicated account assignment"""
        try:
            customer = data.get("customer", {})
            customer_code = customer.get("customer_code")
            account_number = data.get("account_number")
            bank_name = data.get("bank", {}).get("name")
            
            logger.info(f"≡ƒÅª Dedicated account assigned: {account_number} for {customer_code}")
            
            # Update virtual account record (implement as needed)
            return {"success": True, "message": "Dedicated account assignment processed"}
        
        except Exception as e:
            logger.error(f"Γ¥î Error processing account assignment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_balance(self, user_id: str) -> float:
        """Get current user balance"""
        try:
            if not self.supabase:
                return 0.0
            
            result = self.supabase.table("users").select("wallet_balance").eq("telegram_chat_id", user_id).execute()
            
            if result.data:
                return float(result.data[0].get("wallet_balance", 0))
            return 0.0
        
        except Exception as e:
            logger.error(f"Error getting user balance: {str(e)}")
            return 0.0
    
    async def send_credit_notification(self, user_id: str, amount: float, new_balance: float, sender_name: str = "Unknown", sender_bank: str = "Unknown Bank", narration: str = "Transfer"):
        """Send beautiful, friendly credit notification to user via Telegram"""
        try:
            from main import send_reply  # Import from main app
            
            # Get user's first name for personalization
            user_name = "there"  # Default greeting
            try:
                if self.supabase:
                    user_query = self.supabase.table("users").select("full_name").eq("telegram_chat_id", user_id).execute()
                    if user_query.data:
                        full_name = user_query.data[0].get("full_name", "")
                        user_name = full_name.split()[0] if full_name else "there"
            except Exception as e:
                logger.warning(f"Could not get user name: {e}")
            
            # Enhanced message with better sender info and clearer fallbacks
            if sender_name and sender_name not in ["Unknown", "Bank Transfer"]:
                if sender_bank and sender_bank not in ["Unknown Bank", "Paystack"]:
                    # Better formatting: Emphasize sender name, show bank as secondary info
                    sender_info = f"≡ƒÆ╕ *From:* **{sender_name}**\n≡ƒÅª *via* {sender_bank}"
                else:
                    sender_info = f"≡ƒÆ╕ *From:* **{sender_name}**"
            else:
                # When we can't identify the real sender, be more honest about it
                if sender_bank and sender_bank not in ["Unknown Bank", "Paystack"]:
                    sender_info = f"≡ƒÆ╕ *From:* Bank Transfer via {sender_bank}"
                else:
                    sender_info = "≡ƒÆ╕ *From:* Bank Transfer"
            
            message = f"""≡ƒÄë *Money Alert!*

Hi {user_name}! You just received Γéª{amount:,.0f}

{sender_info}
≡ƒÆ░ *New Balance:* Γéª{new_balance:,.0f}

Say "balance" to check your wallet or "transfer" to send money! ≡ƒÜÇ"""
            
            send_reply(user_id, message)
            logger.info(f"≡ƒô▒ Enhanced credit notification sent to {user_id}: {sender_name} via {sender_bank}")
        
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")

# Global instance
paystack_webhook_handler = PaystackWebhookHandler()

def handle_paystack_webhook(payload: Dict, signature: str = None) -> Dict:
    """Handle Paystack webhook (sync wrapper)"""
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            paystack_webhook_handler.handle_webhook(payload, signature)
        )
    except Exception as e:
        logger.error(f"Webhook handling error: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        loop.close()
