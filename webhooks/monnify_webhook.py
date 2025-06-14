# webhooks/monnify_webhook.py

from flask import request, jsonify
from supabase import create_client
import os
import logging
import hashlib
import hmac
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
MONNIFY_SECRET_KEY = os.getenv("MONNIFY_SECRET_KEY")

# Only create supabase client if credentials are available
supabase = None

def get_supabase_client():
    global supabase
    if supabase is None and SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def verify_monnify_signature(payload, signature):
    """Verify Monnify webhook signature for security"""
    if not MONNIFY_SECRET_KEY:
        logger.warning("MONNIFY_SECRET_KEY not configured - skipping signature verification")
        return True  # Allow in development
    
    try:
        # Monnify typically uses HMAC-SHA256 or similar
        expected_signature = hmac.new(
            MONNIFY_SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    except Exception as e:
        logger.error(f"Error verifying Monnify signature: {e}")
        return False

def handle_monnify_webhook():
    """
    Handle incoming Monnify deposit webhooks
    
    Expected webhook events:
    - SUCCESSFUL_TRANSACTION: Credit user's NGN balance and send notification
    - FAILED_TRANSACTION: Log failed transaction
    - REVERSED_TRANSACTION: Handle reversal
    """
    try:
        # Get raw payload for signature verification
        raw_payload = request.get_data(as_text=True)
        data = request.json
        
        logger.info(f"Monnify Webhook Received: {data}")
        
        if not data:
            logger.error("No data received in Monnify webhook")
            return jsonify({"error": "No data received"}), 400
        
        # Verify signature if present (recommended for production)
        signature = request.headers.get('X-Monnify-Signature')
        if signature and not verify_monnify_signature(raw_payload, signature):
            logger.error("Invalid Monnify webhook signature")
            return jsonify({"error": "Invalid signature"}), 401
        
        # Extract event type
        event_type = data.get("eventType") or data.get("transactionStatus")
        
        if event_type == "SUCCESSFUL_TRANSACTION" or event_type == "PAID":
            return handle_successful_deposit(data)
        elif event_type == "FAILED_TRANSACTION" or event_type == "FAILED":
            return handle_failed_deposit(data)
        elif event_type == "REVERSED_TRANSACTION" or event_type == "REVERSED":
            return handle_reversed_deposit(data)
        else:
            logger.warning(f"Unhandled Monnify webhook event: {event_type}")
            return jsonify({"message": "Event acknowledged but not processed"}), 200
            
    except Exception as e:
        logger.error(f"Error processing Monnify webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def handle_successful_deposit(data):
    """Handle successful bank deposit and update user balance"""
    try:
        # Extract deposit information from Monnify webhook
        amount = float(data.get("settlementAmount") or data.get("amount", 0))
        account_number = data.get("destinationAccountNumber") or data.get("accountNumber")
        account_name = data.get("accountName") or data.get("customerName")
        reference = data.get("transactionReference") or data.get("paymentReference")
        customer_email = data.get("customerEmail")
        
        logger.info(f"Processing Monnify deposit: ₦{amount:,.2f} to account {account_number}")
        
        if not amount or not account_number:
            logger.error("Missing required deposit information")
            return jsonify({"error": "Missing required information"}), 400
        
        # Find user by virtual account number
        client = get_supabase_client()
        if not client:
            logger.error("Database not available")
            return jsonify({"error": "Database error"}), 500
        
        # Search for user with this virtual account number
        account_resp = client.table('virtual_accounts').select('*').eq('accountnumber', account_number).execute()
        
        if not account_resp.data:
            logger.error(f"Virtual account not found: {account_number}")
            return jsonify({"error": "Virtual account not found"}), 404
        
        virtual_account = account_resp.data[0]
        user_id = virtual_account.get('user_id')
        
        if not user_id:
            logger.error(f"User ID not found for virtual account: {account_number}")
            return jsonify({"error": "User not found"}), 404
        
        # Get user data for notification
        user_resp = client.table('users').select('telegram_chat_id, first_name').eq('id', user_id).execute()
        
        if not user_resp.data:
            logger.error(f"User not found: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        user_data = user_resp.data[0]
        chat_id = user_data.get('telegram_chat_id')
        first_name = user_data.get('first_name', 'User')
        
        # Save deposit transaction record
        transaction_saved = save_bank_transaction(
            user_id=user_id,
            transaction_reference=reference,
            amount=amount,
            account_number=account_number,
            status="success",
            webhook_data=data
        )
        
        if not transaction_saved:
            logger.error(f"Failed to save transaction record for user {user_id}")
            # Continue anyway - don't fail the whole process
        
        # Update user's NGN balance
        balance_updated = update_user_balance(user_id, amount)
        
        if balance_updated:
            # Get new balance for notification
            balance_info = get_user_balance(user_id)
            new_balance = balance_info.get("balance", 0)
            
            # Send notification to user via Telegram if chat_id exists
            if chat_id:
                send_deposit_notification(
                    chat_id=chat_id,
                    first_name=first_name,
                    amount=amount,
                    new_balance=new_balance,
                    reference=reference
                )
            
            logger.info(f"Successfully processed bank deposit for user {user_id}")
            return jsonify({
                "message": "Bank deposit processed successfully",
                "user_id": user_id,
                "amount": amount,
                "new_balance": new_balance,
                "reference": reference
            }), 200
        else:
            logger.error("Failed to update user balance")
            return jsonify({"error": "Failed to update balance"}), 500
            
    except Exception as e:
        logger.error(f"Error handling successful deposit: {str(e)}")
        return jsonify({"error": "Internal error processing deposit"}), 500

def handle_failed_deposit(data):
    """Handle failed bank deposit - log for tracking"""
    try:
        amount = float(data.get("amount", 0))
        account_number = data.get("destinationAccountNumber") or data.get("accountNumber")
        reference = data.get("transactionReference") or data.get("paymentReference")
        
        logger.warning(f"Failed bank deposit: ₦{amount:,.2f} to account {account_number}, ref: {reference}")
        
        # Log failed transaction (optional)
        # save_failed_transaction(reference, amount, account_number, data)
        
        return jsonify({"message": "Failed deposit logged"}), 200
        
    except Exception as e:
        logger.error(f"Error handling failed deposit: {str(e)}")
        return jsonify({"error": "Internal error"}), 500

def handle_reversed_deposit(data):
    """Handle reversed bank deposit - deduct from balance if needed"""
    try:
        amount = float(data.get("amount", 0))
        account_number = data.get("destinationAccountNumber") or data.get("accountNumber")
        reference = data.get("transactionReference") or data.get("paymentReference")
        
        logger.warning(f"Reversed bank deposit: ₦{amount:,.2f} from account {account_number}, ref: {reference}")
        
        # Find user and deduct from balance if needed
        client = get_supabase_client()
        if client:
            account_resp = client.table('virtual_accounts').select('user_id').eq('accountnumber', account_number).execute()
            
            if account_resp.data:
                user_id = account_resp.data[0]['user_id']
                # Deduct the reversed amount
                update_user_balance(user_id, -amount)  # Negative amount for deduction
                logger.info(f"Deducted ₦{amount:,.2f} from user {user_id} due to reversal")
        
        return jsonify({"message": "Reversed deposit handled"}), 200
        
    except Exception as e:
        logger.error(f"Error handling reversed deposit: {str(e)}")
        return jsonify({"error": "Internal error"}), 500

def save_bank_transaction(user_id: str, transaction_reference: str, amount: float, 
                         account_number: str, status: str = "success", webhook_data: dict = None) -> bool:
    """Save bank transaction record to database"""
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        transaction_data = {
            'user_id': user_id,
            'transaction_reference': transaction_reference,
            'amount': amount,
            'account_number': account_number,
            'transaction_type': 'deposit',
            'status': status,
            'webhook_data': webhook_data,
            'created_at': datetime.now().isoformat()
        }
        
        result = client.table('bank_transactions').insert(transaction_data).execute()
        
        if result.data:
            logger.info(f"Saved bank transaction: {transaction_reference}")
            return True
        else:
            logger.error(f"Failed to save bank transaction: {result}")
            return False
        
    except Exception as e:
        logger.error(f"Error saving bank transaction: {str(e)}")
        return False

def update_user_balance(user_id: str, amount: float) -> bool:
    """Update user's NGN balance in virtual_accounts table"""
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        # Get current balance
        balance_resp = client.table('virtual_accounts').select('balance').eq('user_id', user_id).execute()
        
        if not balance_resp.data:
            logger.error(f"Virtual account not found for user {user_id}")
            return False
        
        current_balance = balance_resp.data[0].get('balance', 0.0)
        new_balance = current_balance + amount
        
        # Update balance
        update_resp = client.table('virtual_accounts').update({
            'balance': new_balance,
            'updated_at': datetime.now().isoformat()
        }).eq('user_id', user_id).execute()
        
        if update_resp.data:
            logger.info(f"Updated balance for user {user_id}: ₦{current_balance:,.2f} → ₦{new_balance:,.2f}")
            return True
        else:
            logger.error(f"Failed to update balance for user {user_id}")
            return False
        
    except Exception as e:
        logger.error(f"Error updating user balance: {str(e)}")
        return False

def get_user_balance(user_id: str):
    """Get user's current balance"""
    try:
        client = get_supabase_client()
        if not client:
            return {"balance": 0}
        
        balance_resp = client.table('virtual_accounts').select('balance').eq('user_id', user_id).execute()
        
        if balance_resp.data:
            return {"balance": balance_resp.data[0].get('balance', 0)}
        else:
            return {"balance": 0}
        
    except Exception as e:
        logger.error(f"Error getting user balance: {str(e)}")
        return {"balance": 0}

def send_deposit_notification(chat_id, first_name, amount, new_balance, reference=''):
    """Send Telegram notification for successful bank deposit"""
    try:
        from main import send_reply  # Import from main app
        
        message = f"""💰 **Deposit Successful!**

Hey {first_name}! Your bank deposit has been credited:

💵 **Deposited**: ₦{amount:,.2f}
💳 **New Balance**: ₦{new_balance:,.2f}

{f"📝 **Reference**: {reference}" if reference else ""}

✨ **Your money is ready to use!**

🚀 **What you can do now**:
• Send money to friends & family
• Buy airtime & data at discounted rates  
• Make instant payments
• Check balance anytime

Type 'balance' to view your wallet or 'help' for assistance! 💪"""

        send_reply(chat_id, message)
        logger.info(f"Sent deposit notification to chat_id: {chat_id}")
        
    except Exception as e:
        logger.error(f"Error sending deposit notification: {str(e)}")