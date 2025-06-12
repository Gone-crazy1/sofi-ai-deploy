# crypto/webhook.py

from flask import request, jsonify
from .rates import get_crypto_to_ngn_rate, calculate_ngn_equivalent
from .wallet import update_user_ngn_balance, get_user_ngn_balance
from supabase import create_client
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

# Only create supabase client if credentials are available
supabase = None

def get_supabase_client():
    global supabase
    if supabase is None and SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def handle_crypto_webhook():
    """
    Handle incoming crypto deposit webhooks from Bitnob
    
    Expected webhook events:
    - wallet.deposit.successful: Credit user's NGN balance
    - wallet.deposit.pending: Log pending deposit
    - wallet.withdrawal.successful: Log withdrawal
    """
    try:
        data = request.json
        logger.info(f"Crypto Webhook Received: {data}")
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        event_type = data.get("event")
        
        if event_type == "wallet.deposit.successful":
            return handle_successful_deposit(data)
        elif event_type == "wallet.deposit.pending":
            return handle_pending_deposit(data)
        elif event_type == "wallet.withdrawal.successful":
            return handle_successful_withdrawal(data)
        else:
            logger.warning(f"Unhandled webhook event: {event_type}")
            return jsonify({"message": "Event acknowledged but not processed"}), 200
            
    except Exception as e:
        logger.error(f"Error processing crypto webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def handle_successful_deposit(data):
    """Handle successful crypto deposit and convert to NGN"""
    try:
        deposit_data = data.get('data', {})
        
        # Extract deposit information
        customer_email = deposit_data.get('customerEmail', '')
        amount = float(deposit_data.get('amount', 0))
        currency = deposit_data.get('currency', '').upper()
        transaction_id = deposit_data.get('transactionId', '')
        tx_hash = deposit_data.get('txHash', '')  # Blockchain transaction hash
        wallet_id = deposit_data.get('walletId', '')
        
        # Extract user_id from email (format: user_id@sofiwallet.com)
        if '@sofiwallet.com' not in customer_email:
            logger.error(f"Invalid customer email format: {customer_email}")
            return jsonify({"error": "Invalid customer email"}), 400
        
        user_id = customer_email.split('@')[0]
        
        # Get current NGN rate for the cryptocurrency
        ngn_rate = get_crypto_to_ngn_rate(currency)
        if ngn_rate == 0:
            logger.error(f"Could not fetch rate for {currency}")
            return jsonify({"error": f"Rate not available for {currency}"}), 400
        
        # Calculate NGN equivalent
        credited_ngn = amount * ngn_rate
        
        logger.info(f"Processing deposit: {amount} {currency} = ₦{credited_ngn:,.2f} for user {user_id}")
          # Get user data for notification
        client = get_supabase_client()
        if not client:
            logger.error("Database not available")
            return jsonify({"error": "Database error"}), 500
            
        user_resp = client.table('users').select('telegram_chat_id, first_name').eq('id', user_id).execute()
        
        if not user_resp.data:
            logger.error(f"User not found: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        user_data = user_resp.data[0]
        chat_id = user_data.get('telegram_chat_id')
        first_name = user_data.get('first_name', 'User')
        
        # Save crypto transaction record
        transaction_saved = save_crypto_transaction(
            user_id=user_id,
            tx_hash=tx_hash,
            bitnob_tx_id=transaction_id,
            crypto_type=currency,
            amount_crypto=amount,
            amount_naira=credited_ngn,
            rate_used=ngn_rate,
            status="success",
            webhook_data=data  # Store full webhook for debugging
        )
        
        if not transaction_saved:
            logger.error(f"Failed to save transaction record for user {user_id}")
            return jsonify({"error": "Failed to save transaction"}), 500
        
        # Update user's NGN balance
        balance_updated = update_user_ngn_balance(user_id, credited_ngn, crypto_deposit=True)
        
        if balance_updated:
            # Get new balance for notification
            balance_info = get_user_ngn_balance(user_id)
            new_balance = balance_info.get("balance_naira", 0)
            
            # Send notification to user via Telegram if chat_id exists
            if chat_id:
                send_deposit_notification(
                    chat_id=chat_id,
                    first_name=first_name,
                    crypto_amount=amount,
                    crypto_currency=currency,
                    ngn_amount=credited_ngn,
                    new_balance=new_balance,
                    tx_hash=tx_hash
                )
            
            logger.info(f"Successfully processed crypto deposit for user {user_id}")
            return jsonify({
                "message": "Crypto deposit processed successfully",
                "user_id": user_id,
                "crypto_amount": amount,
                "crypto_currency": currency,
                "credited_ngn": credited_ngn,
                "new_balance": new_balance,
                "rate_used": ngn_rate,
                "transaction_id": transaction_id
            }), 200
        else:
            logger.error("Failed to update user balance")
            return jsonify({"error": "Failed to update balance"}), 500
            
    except Exception as e:
        logger.error(f"Error handling successful deposit: {str(e)}")
        return jsonify({"error": "Internal error processing deposit"}), 500

def save_crypto_transaction(user_id: str, tx_hash: str, bitnob_tx_id: str, crypto_type: str, 
                          amount_crypto: float, amount_naira: float, rate_used: float, 
                          status: str = "success", webhook_data: dict = None) -> bool:
    """
    Save crypto transaction to crypto_transactions table
    
    Args:
        user_id: User identifier
        tx_hash: Blockchain transaction hash
        bitnob_tx_id: Bitnob transaction ID
        crypto_type: Cryptocurrency type (BTC, ETH, USDT)
        amount_crypto: Amount in cryptocurrency
        amount_naira: Converted NGN amount
        rate_used: Exchange rate used
        status: Transaction status
        webhook_data: Full webhook payload
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        transaction_data = {
            'user_id': user_id,
            'tx_hash': tx_hash,
            'bitnob_tx_id': bitnob_tx_id,
            'crypto_type': crypto_type,
            'amount_crypto': amount_crypto,
            'amount_naira': amount_naira,
            'rate_used': rate_used,
            'status': status,
            'webhook_data': webhook_data,
            'created_at': datetime.now().isoformat()
        }
        
        result = get_supabase_client().table('crypto_transactions').insert(transaction_data).execute()
        
        if result.data:
            logger.info(f"Saved crypto transaction: {bitnob_tx_id}")
            return True
        else:
            logger.error(f"Failed to save crypto transaction: {result}")
            return False
        
    except Exception as e:
        logger.error(f"Error saving crypto transaction: {str(e)}")
        return False

def handle_pending_deposit(data):
    """Handle pending crypto deposit - log for tracking"""
    try:
        deposit_data = data.get('data', {})
        customer_email = deposit_data.get('customerEmail', '')
        amount = float(deposit_data.get('amount', 0))
        currency = deposit_data.get('currency', '').upper()
        transaction_id = deposit_data.get('transactionId', '')
        
        user_id = customer_email.split('@')[0] if '@sofiwallet.com' in customer_email else 'unknown'
        
        logger.info(f"Pending deposit: {amount} {currency} for user {user_id}, TX: {transaction_id}")
        
        # Log pending transaction
        log_crypto_transaction(
            user_id=user_id,
            transaction_type="deposit_pending",
            crypto_amount=amount,
            crypto_currency=currency,
            transaction_id=transaction_id,
            status="pending"
        )
        
        return jsonify({"message": "Pending deposit logged"}), 200
        
    except Exception as e:
        logger.error(f"Error handling pending deposit: {str(e)}")
        return jsonify({"error": "Internal error"}), 500

def handle_successful_withdrawal(data):
    """Handle successful crypto withdrawal - log for tracking"""
    try:
        withdrawal_data = data.get('data', {})
        customer_email = withdrawal_data.get('customerEmail', '')
        amount = float(withdrawal_data.get('amount', 0))
        currency = withdrawal_data.get('currency', '').upper()
        transaction_id = withdrawal_data.get('transactionId', '')
        
        user_id = customer_email.split('@')[0] if '@sofiwallet.com' in customer_email else 'unknown'
        
        logger.info(f"Successful withdrawal: {amount} {currency} for user {user_id}, TX: {transaction_id}")
        
        # Log withdrawal transaction
        log_crypto_transaction(
            user_id=user_id,
            transaction_type="withdrawal",
            crypto_amount=amount,
            crypto_currency=currency,
            transaction_id=transaction_id,
            status="completed"
        )
        
        return jsonify({"message": "Withdrawal logged"}), 200
        
    except Exception as e:
        logger.error(f"Error handling withdrawal: {str(e)}")
        return jsonify({"error": "Internal error"}), 500

def log_crypto_transaction(user_id, transaction_type, crypto_amount, crypto_currency, 
                          ngn_amount=0, transaction_id='', wallet_id='', rate_used=0, status='completed'):
    """Log crypto transaction to database"""
    try:
        transaction_data = {
            'user_id': user_id,
            'transaction_type': transaction_type,
            'crypto_amount': crypto_amount,
            'crypto_currency': crypto_currency,
            'ngn_amount': ngn_amount,
            'transaction_id': transaction_id,
            'wallet_id': wallet_id,
            'rate_used': rate_used,
            'status': status,
            'created_at': datetime.now().isoformat()
        }
          # Create crypto_transactions table if it doesn't exist (you may need to run this SQL manually)
        get_supabase_client().table('crypto_transactions').insert(transaction_data).execute()
        logger.info(f"Logged crypto transaction: {transaction_id}")
        
    except Exception as e:
        logger.error(f"Error logging crypto transaction: {str(e)}")

def send_deposit_notification(chat_id, first_name, crypto_amount, crypto_currency, ngn_amount, new_balance, tx_hash=''):
    """Send Telegram notification for successful crypto deposit with instant NGN conversion"""
    try:
        from main import send_reply  # Import from main app
        
        message = f"""🎉 **Crypto Deposit Successful!**

Hey {first_name}! Your crypto has been instantly converted to NGN:

💰 **Deposited**: {crypto_amount} {crypto_currency}
💵 **Converted to**: ₦{ngn_amount:,.2f}
💳 **New Balance**: ₦{new_balance:,.2f}

{f"🔗 **Transaction**: {tx_hash[:10]}...{tx_hash[-10:]}" if tx_hash else ""}

✨ **Instant Conversion**: Your crypto has been automatically converted to NGN at live market rates!

🚀 **Ready to use your NGN for**:
• Transfer money to friends & family
• Buy airtime & data at discounted rates
• Make instant payments
• Send more crypto for conversion

Type 'balance' to check your wallet or 'help' for assistance! 💪"""

        send_reply(chat_id, message)
        logger.info(f"Sent crypto deposit notification to chat_id: {chat_id}")
        
    except Exception as e:
        logger.error(f"Error sending deposit notification: {str(e)}")

def get_user_crypto_transactions(user_id: str, limit: int = 10):
    """
    Get user's crypto transaction history
    
    Args:
        user_id: User identifier
        limit: Number of transactions to retrieve
    
    Returns:
        list: Transaction history    """
    try:
        result = get_supabase_client().table('crypto_transactions') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .limit(limit) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error fetching crypto transactions: {str(e)}")
        return []

def get_crypto_stats(user_id: str):
    """
    Get user's crypto statistics
    
    Args:
        user_id: User identifier
    
    Returns:
        dict: Crypto statistics
    """
    try:
        # Get transaction stats
        transactions = get_user_crypto_transactions(user_id, limit=100)
        
        if not transactions:
            return {
                "total_deposits": 0,
                "total_ngn_earned": 0.0,
                "favorite_crypto": None,
                "last_deposit": None
            }
        
        # Calculate statistics
        total_deposits = len(transactions)
        total_ngn = sum(float(tx.get('amount_naira', 0)) for tx in transactions)
        
        # Find most used crypto
        crypto_counts = {}
        for tx in transactions:
            crypto = tx.get('crypto_type')
            crypto_counts[crypto] = crypto_counts.get(crypto, 0) + 1
        
        favorite_crypto = max(crypto_counts, key=crypto_counts.get) if crypto_counts else None
        last_deposit = transactions[0].get('created_at') if transactions else None
        
        return {
            "total_deposits": total_deposits,
            "total_ngn_earned": total_ngn,
            "favorite_crypto": favorite_crypto,
            "last_deposit": last_deposit,
            "crypto_breakdown": crypto_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting crypto stats: {str(e)}")
        return {
            "total_deposits": 0,
            "total_ngn_earned": 0.0,
            "favorite_crypto": None,
            "last_deposit": None
        }
