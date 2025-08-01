"""
Transaction-related functions for Sofi AI Assistant
Handles transaction recording, history, and statements
"""

import logging
from typing import Dict, Any, List
from supabase import create_client
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def record_deposit(chat_id: str, amount: float, reference: str = None, source: str = "paystack", **kwargs) -> Dict[str, Any]:
    """
    Record a deposit transaction
    
    Args:
        chat_id (str): User's Telegram chat ID
        amount (float): Deposit amount
        reference (str): Transaction reference
        source (str): Deposit source (paystack, manual, etc.)
        
    Returns:
        Dict containing deposit record result
    """
    try:
        logger.info(f"💰 Recording deposit for user {chat_id}: ₦{amount}")
        
        if amount <= 0:
            return {
                "success": False,
                "error": "Invalid deposit amount"
            }
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Check if user exists
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        if not user_result.data:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Record deposit transaction
        transaction_data = {
            "user_id": chat_id,
            "transaction_id": reference or f"DEP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "deposit",
            "amount": amount,
            "fee": 0,
            "total_amount": amount,
            "source": source,
            "status": "completed",
            "reference": reference,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("bank_transactions").insert(transaction_data).execute()
        
        if result.data:
            # Update user balance (assuming balance is tracked separately)
            return {
                "success": True,
                "transaction_id": transaction_data["transaction_id"],
                "amount": amount,
                "reference": reference,
                "message": f"Deposit of ₦{amount:,.2f} recorded successfully!"
            }
        else:
            return {
                "success": False,
                "error": "Failed to record deposit"
            }
            
    except Exception as e:
        logger.error(f"❌ Error recording deposit: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to record deposit: {str(e)}"
        }

async def get_transfer_history(chat_id: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
    """
    Get user's transfer history
    
    Args:
        chat_id (str): User's Telegram chat ID
        limit (int): Number of transactions to return
        
    Returns:
        Dict containing transfer history
    """
    try:
        logger.info(f"📄 Getting transfer history for user {chat_id}")
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # 🔧 RESOLVE TELEGRAM ID TO UUID FIRST
        # Find the user UUID from Telegram chat ID
        user_result = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            logger.warning(f"❌ No user found for Telegram ID {chat_id}")
            return {
                "success": False,
                "error": "User not found. Please complete onboarding first.",
                "transfers": []
            }
        
        user_uuid = user_result.data[0]["id"]
        logger.info(f"✅ Resolved Telegram ID {chat_id} to UUID {user_uuid}")
        
        # Get transfer transactions using the resolved UUID
        transfers_result = supabase.table("bank_transactions")\
            .select("*")\
            .eq("user_id", user_uuid)\
            .in_("type", ["transfer_out", "transfer_in"])\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        transfers = []
        for tx in transfers_result.data:
            transfer_info = {
                "transaction_id": tx.get("transaction_id"),
                "type": tx.get("type"),
                "amount": tx.get("amount"),
                "fee": tx.get("fee", 0),
                "total_amount": tx.get("total_amount"),
                "recipient_account": tx.get("recipient_account"),
                "recipient_bank": tx.get("recipient_bank"),
                "sender_account": tx.get("sender_account"),
                "sender_bank": tx.get("sender_bank"),
                "narration": tx.get("narration"),
                "status": tx.get("status"),
                "reference": tx.get("reference"),
                "date": tx.get("created_at"),
                "formatted_date": datetime.fromisoformat(tx.get("created_at", "")).strftime("%Y-%m-%d %H:%M") if tx.get("created_at") else None
            }
            transfers.append(transfer_info)
        
        return {
            "success": True,
            "transfers": transfers,
            "count": len(transfers),
            "total_available": len(transfers_result.data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting transfer history: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to get transfer history: {str(e)}",
            "transfers": []
        }

async def get_wallet_statement(chat_id: str, days: int = 30, **kwargs) -> Dict[str, Any]:
    """
    Get user's wallet statement for specified period
    
    Args:
        chat_id (str): User's Telegram chat ID
        days (int): Number of days to look back
        
    Returns:
        Dict containing wallet statement
    """
    try:
        logger.info(f"📊 Getting wallet statement for user {chat_id} ({days} days)")
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # 🔧 RESOLVE TELEGRAM ID TO UUID FIRST
        # Find the user UUID from Telegram chat ID
        user_result = supabase.table("users").select("id").eq("telegram_chat_id", str(chat_id)).execute()
        
        if not user_result.data:
            logger.warning(f"❌ No user found for Telegram ID {chat_id}")
            return {
                "success": False,
                "error": "User not found. Please complete onboarding first by visiting https://pipinstallsofi.com/onboard",
                "transactions": []
            }
        
        user_uuid = user_result.data[0]["id"]
        logger.info(f"✅ Resolved Telegram ID {chat_id} to UUID {user_uuid}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all transactions in the period using the resolved UUID
        transactions_result = supabase.table("bank_transactions")\
            .select("*")\
            .eq("user_id", user_uuid)\
            .gte("created_at", start_date.isoformat())\
            .lte("created_at", end_date.isoformat())\
            .order("created_at", desc=True)\
            .execute()
        
        # Process transactions
        transactions = []
        total_inflow = 0
        total_outflow = 0
        total_fees = 0
        
        for tx in transactions_result.data:
            tx_amount = tx.get("amount", 0)
            tx_fee = tx.get("fee", 0)
            tx_type = tx.get("transaction_type", "")  # Fixed: use transaction_type
            
            # Categorize transaction
            if tx_type in ["credit", "deposit", "transfer_in", "airtime_refund"]:
                total_inflow += tx_amount
            elif tx_type in ["transfer_out", "airtime_purchase", "data_purchase"]:
                total_outflow += tx_amount
                total_fees += tx_fee
            
            # Create proper description
            description = tx.get("description") or tx.get("narration") or _get_transaction_description(tx_type, tx_amount, tx)
            
            transaction_info = {
                "transaction_id": tx.get("transaction_id"),
                "type": tx.get("transaction_type"),  # Fixed: use transaction_type
                "amount": tx_amount,
                "fee": tx_fee,
                "description": description,
                "reference": tx.get("reference"),
                "status": tx.get("status"),
                "date": tx.get("created_at"),
                "formatted_date": datetime.fromisoformat(tx.get("created_at", "")).strftime("%Y-%m-%d %H:%M") if tx.get("created_at") else None
            }
            transactions.append(transaction_info)
        
        # Get current balance
        from functions.balance_functions import check_balance
        balance_result = await check_balance(chat_id)
        current_balance = balance_result.get("balance", 0) if balance_result.get("success") else 0
        
        return {
            "success": True,
            "period_days": days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "current_balance": current_balance,
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "total_fees": total_fees,
            "net_movement": total_inflow - total_outflow,
            "transaction_count": len(transactions),
            "transactions": transactions
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting wallet statement: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to get wallet statement: {str(e)}",
            "transactions": []
        }

def _get_transaction_description(tx_type: str, amount: float, tx_data: dict) -> str:
    """Generate proper transaction description based on type and data"""
    
    if tx_type == "credit":
        sender = tx_data.get("sender_name", "Unknown Sender")
        bank = tx_data.get("bank_name", "Bank")
        return f"Deposit from {sender} via {bank}"
    
    elif tx_type == "transfer_out":
        recipient = tx_data.get("recipient_name", "Recipient")
        bank = tx_data.get("bank_name", "Bank")
        return f"Transfer to {recipient} ({bank})"
    
    elif tx_type == "airtime_purchase":
        phone = tx_data.get("phone_number", "Phone")
        return f"Airtime Purchase: ₦{amount:,.0f} for {phone}"
    
    elif tx_type == "data_purchase":
        phone = tx_data.get("phone_number", "Phone")
        return f"Data Purchase: ₦{amount:,.0f} for {phone}"
    
    elif tx_type == "airtime_refund":
        return f"Airtime Refund: ₦{amount:,.0f}"
    
    elif tx_type == "transfer_in":
        return f"Transfer Received: ₦{amount:,.0f}"
    
    else:
        # Fallback for unknown types
        return f"{tx_type.replace('_', ' ').title()}: ₦{amount:,.0f}"
