"""
Notification-related functions for Sofi AI Assistant
Handles receipts, alerts, and status updates
"""

import logging
from typing import Dict, Any
from supabase import create_client
import os
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

async def send_receipt(chat_id: str, transaction_id: str, **kwargs) -> Dict[str, Any]:
    """
    Send transaction receipt to user
    
    Args:
        chat_id (str): User's Telegram chat ID
        transaction_id (str): Transaction ID to generate receipt for
        
    Returns:
        Dict containing receipt sending result
    """
    try:
        logger.info(f"🧾 Sending receipt for transaction {transaction_id} to user {chat_id}")
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Get transaction details
        tx_result = supabase.table("bank_transactions")\
            .select("*")\
            .eq("transaction_id", transaction_id)\
            .eq("user_id", chat_id)\
            .execute()
        
        if not tx_result.data:
            return {
                "success": False,
                "error": "Transaction not found"
            }
        
        transaction = tx_result.data[0]
        
        # Get user details
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", str(chat_id)).execute()
        user_name = "User"
        if user_result.data:
            user_name = user_result.data[0].get("full_name", "User")
        
        # Generate receipt text
        receipt = await _generate_receipt(transaction, user_name)
        
        # Send receipt via Telegram
        success = await _send_telegram_message(chat_id, receipt)
        
        if success:
            return {
                "success": True,
                "message": "Receipt sent successfully",
                "transaction_id": transaction_id
            }
        else:
            return {
                "success": False,
                "error": "Failed to send receipt"
            }
            
    except Exception as e:
        logger.error(f"❌ Error sending receipt: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to send receipt: {str(e)}"
        }

async def send_alert(chat_id: str, alert_type: str, message: str, **kwargs) -> Dict[str, Any]:
    """
    Send alert notification to user
    
    Args:
        chat_id (str): User's Telegram chat ID
        alert_type (str): Type of alert (security, balance, transaction, etc.)
        message (str): Alert message
        
    Returns:
        Dict containing alert sending result
    """
    try:
        logger.info(f"🚨 Sending {alert_type} alert to user {chat_id}")
        
        # Format alert message
        alert_icons = {
            "security": "🔐",
            "balance": "💰",
            "transaction": "💸",
            "deposit": "💰",
            "transfer": "📤",
            "system": "⚙️",
            "warning": "⚠️",
            "success": "✅",
            "error": "❌"
        }
        
        icon = alert_icons.get(alert_type, "🔔")
        formatted_message = f"{icon} **{alert_type.upper()} ALERT**\n\n{message}\n\n_Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        # Send alert via Telegram
        success = await _send_telegram_message(chat_id, formatted_message)
        
        if success:
            # Log alert in database
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            alert_data = {
                "user_id": chat_id,
                "alert_type": alert_type,
                "message": message,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            
            supabase.table("user_alerts").insert(alert_data).execute()
            
            return {
                "success": True,
                "message": "Alert sent successfully",
                "alert_type": alert_type
            }
        else:
            return {
                "success": False,
                "error": "Failed to send alert"
            }
            
    except Exception as e:
        logger.error(f"❌ Error sending alert: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to send alert: {str(e)}"
        }

async def update_transaction_status(chat_id: str, transaction_id: str, status: str, **kwargs) -> Dict[str, Any]:
    """
    Update transaction status and notify user
    
    Args:
        chat_id (str): User's Telegram chat ID
        transaction_id (str): Transaction ID to update
        status (str): New status (pending, completed, failed, etc.)
        
    Returns:
        Dict containing update result
    """
    try:
        logger.info(f"📊 Updating transaction {transaction_id} status to {status}")
        
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Update transaction status
        update_result = supabase.table("bank_transactions")\
            .update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            })\
            .eq("transaction_id", transaction_id)\
            .eq("user_id", chat_id)\
            .execute()
        
        if not update_result.data:
            return {
                "success": False,
                "error": "Transaction not found or update failed"
            }
        
        # Send status update notification
        status_messages = {
            "pending": "Your transaction is being processed. You'll be notified when it's complete.",
            "completed": "✅ Your transaction has been completed successfully!",
            "failed": "❌ Your transaction failed. Please contact support if you need assistance.",
            "cancelled": "🚫 Your transaction has been cancelled.",
            "refunded": "💰 Your transaction has been refunded."
        }
        
        notification_message = status_messages.get(status, f"Transaction status updated to: {status}")
        
        await send_alert(
            chat_id=chat_id,
            alert_type="transaction",
            message=f"Transaction {transaction_id}: {notification_message}"
        )
        
        return {
            "success": True,
            "message": "Transaction status updated successfully",
            "transaction_id": transaction_id,
            "new_status": status
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating transaction status: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to update transaction status: {str(e)}"
        }

async def _generate_receipt(transaction: Dict, user_name: str) -> str:
    """Generate formatted receipt text"""
    tx_type = transaction.get("type", "transaction")
    amount = transaction.get("amount", 0)
    fee = transaction.get("fee", 0)
    total = transaction.get("total_amount", amount + fee)
    reference = transaction.get("reference", "N/A")
    tx_id = transaction.get("transaction_id", "N/A")
    created_at = transaction.get("created_at", "")
    
    # Format date
    try:
        date_formatted = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M:%S")
    except:
        date_formatted = "N/A"
    
    receipt = f"""
🧾 **SOFI AI TRANSACTION RECEIPT**
═══════════════════════════════════
📅 Date: {date_formatted}
🆔 Transaction ID: {tx_id}
📋 Reference: {reference}
───────────────────────────────────
👤 Customer: {user_name}
💰 Amount: ₦{amount:,.2f}
💸 Fee: ₦{fee:,.2f}
💵 Total: ₦{total:,.2f}
📝 Type: {tx_type.replace('_', ' ').title()}
"""
    
    # Add recipient details for transfers
    if tx_type == "transfer_out":
        recipient_account = transaction.get("recipient_account", "N/A")
        recipient_bank = transaction.get("recipient_bank", "N/A")
        receipt += f"🏦 To: {recipient_account} ({recipient_bank})\n"
    
    receipt += f"""───────────────────────────────────
✅ Status: {transaction.get("status", "completed").title()}
═══════════════════════════════════
Thank you for using Sofi AI! 💙
"""
    
    return receipt

async def _send_telegram_message(chat_id: str, message: str) -> bool:
    """Send message via Telegram Bot API"""
    try:
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            logger.error("Telegram bot token not configured")
            return False
        
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"❌ Error sending Telegram message: {str(e)}")
        return False
