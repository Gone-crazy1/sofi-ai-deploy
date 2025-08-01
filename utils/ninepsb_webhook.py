#!/usr/bin/env python3
"""
9PSB Webhook Handler for Credit/Debit Alerts
Handles incoming transaction notifications from 9PSB and updates Supabase
"""

import os
import json
import hashlib
import hmac
from datetime import datetime
from flask import request, jsonify
from supabase import create_client

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_9psb_webhook_signature(payload, signature, secret):
    """
    Verify 9PSB webhook signature for security
    """
    try:
        # Create HMAC signature using webhook secret
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures securely
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        print(f"❌ Signature verification error: {e}")
        return False

def process_9psb_credit_alert(transaction_data):
    """
    Process incoming credit alert from 9PSB
    """
    try:
        # Extract transaction details
        account_number = transaction_data.get("accountNumber")
        amount = float(transaction_data.get("amount", 0))
        sender_name = transaction_data.get("senderName") or transaction_data.get("remitterName")
        sender_bank = transaction_data.get("senderBank") or transaction_data.get("remitterBank")
        reference = transaction_data.get("reference") or transaction_data.get("transactionRef")
        narration = transaction_data.get("narration") or transaction_data.get("description")
        transaction_date = transaction_data.get("transactionDate") or datetime.utcnow().isoformat()
        
        print(f"💰 Processing credit alert: ₦{amount:,.2f} from {sender_name}")
        
        # Find user by account number
        user_result = supabase.table("users").select("*").eq("account_number", account_number).execute()
        
        if not user_result.data:
            print(f"❌ User not found for account: {account_number}")
            return {"status": "error", "message": "User not found"}
            
        user = user_result.data[0]
        user_id = user["id"]
        telegram_chat_id = user.get("telegram_chat_id")
        whatsapp_phone = user.get("whatsapp_phone")
        
        # Update user balance
        new_balance = float(user.get("balance", 0)) + amount
        
        supabase.table("users").update({
            "balance": new_balance,
            "last_transaction_date": transaction_date
        }).eq("id", user_id).execute()
        
        # Record transaction in bank_transactions table
        transaction_record = {
            "user_id": user_id,
            "transaction_type": "credit",
            "amount": amount,
            "balance_after": new_balance,
            "sender_name": sender_name,
            "sender_bank": sender_bank,
            "recipient_account": account_number,
            "reference": reference,
            "narration": narration,
            "transaction_date": transaction_date,
            "status": "completed",
            "platform": "9psb",
            "raw_data": json.dumps(transaction_data)
        }
        
        supabase.table("bank_transactions").insert(transaction_record).execute()
        
        # Send notifications
        send_credit_notifications(user, amount, sender_name, new_balance, telegram_chat_id, whatsapp_phone)
        
        print(f"✅ Credit processed successfully: User {user_id}, New balance: ₦{new_balance:,.2f}")
        
        return {
            "status": "success", 
            "message": "Credit processed",
            "user_id": user_id,
            "new_balance": new_balance
        }
        
    except Exception as e:
        print(f"❌ Credit processing error: {e}")
        return {"status": "error", "message": str(e)}

def process_9psb_debit_alert(transaction_data):
    """
    Process incoming debit alert from 9PSB
    """
    try:
        # Extract transaction details
        account_number = transaction_data.get("accountNumber")
        amount = float(transaction_data.get("amount", 0))
        recipient_name = transaction_data.get("recipientName") or transaction_data.get("beneficiaryName")
        recipient_bank = transaction_data.get("recipientBank") or transaction_data.get("beneficiaryBank")
        recipient_account = transaction_data.get("recipientAccount") or transaction_data.get("beneficiaryAccount")
        reference = transaction_data.get("reference") or transaction_data.get("transactionRef")
        narration = transaction_data.get("narration") or transaction_data.get("description")
        transaction_date = transaction_data.get("transactionDate") or datetime.utcnow().isoformat()
        
        print(f"💸 Processing debit alert: ₦{amount:,.2f} to {recipient_name}")
        
        # Find user by account number
        user_result = supabase.table("users").select("*").eq("account_number", account_number).execute()
        
        if not user_result.data:
            print(f"❌ User not found for account: {account_number}")
            return {"status": "error", "message": "User not found"}
            
        user = user_result.data[0]
        user_id = user["id"]
        telegram_chat_id = user.get("telegram_chat_id")
        whatsapp_phone = user.get("whatsapp_phone")
        
        # Update user balance
        new_balance = float(user.get("balance", 0)) - amount
        
        supabase.table("users").update({
            "balance": new_balance,
            "last_transaction_date": transaction_date
        }).eq("id", user_id).execute()
        
        # Record transaction in bank_transactions table
        transaction_record = {
            "user_id": user_id,
            "transaction_type": "debit",
            "amount": amount,
            "balance_after": new_balance,
            "recipient_name": recipient_name,
            "recipient_bank": recipient_bank,
            "recipient_account": recipient_account,
            "reference": reference,
            "narration": narration,
            "transaction_date": transaction_date,
            "status": "completed",
            "platform": "9psb",
            "raw_data": json.dumps(transaction_data)
        }
        
        supabase.table("bank_transactions").insert(transaction_record).execute()
        
        # Send notifications
        send_debit_notifications(user, amount, recipient_name, new_balance, telegram_chat_id, whatsapp_phone)
        
        print(f"✅ Debit processed successfully: User {user_id}, New balance: ₦{new_balance:,.2f}")
        
        return {
            "status": "success", 
            "message": "Debit processed",
            "user_id": user_id,
            "new_balance": new_balance
        }
        
    except Exception as e:
        print(f"❌ Debit processing error: {e}")
        return {"status": "error", "message": str(e)}

def send_credit_notifications(user, amount, sender_name, new_balance, telegram_chat_id, whatsapp_phone):
    """
    Send credit notifications via Telegram and WhatsApp
    """
    message = f"""
💰 **CREDIT ALERT**

Amount: ₦{amount:,.2f}
From: {sender_name}
Balance: ₦{new_balance:,.2f}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Thank you for using Sofi! 🎉
"""
    
    # Send Telegram notification
    if telegram_chat_id:
        try:
            import requests
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            
            requests.post(telegram_url, json={
                "chat_id": telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })
        except Exception as e:
            print(f"❌ Telegram notification error: {e}")
    
    # Send WhatsApp notification
    if whatsapp_phone:
        try:
            send_whatsapp_message(whatsapp_phone, message)
        except Exception as e:
            print(f"❌ WhatsApp notification error: {e}")

def send_debit_notifications(user, amount, recipient_name, new_balance, telegram_chat_id, whatsapp_phone):
    """
    Send debit notifications via Telegram and WhatsApp
    """
    message = f"""
💸 **DEBIT ALERT**

Amount: ₦{amount:,.2f}
To: {recipient_name}
Balance: ₦{new_balance:,.2f}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Transaction completed successfully! ✅
"""
    
    # Send Telegram notification
    if telegram_chat_id:
        try:
            import requests
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            
            requests.post(telegram_url, json={
                "chat_id": telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })
        except Exception as e:
            print(f"❌ Telegram notification error: {e}")
    
    # Send WhatsApp notification
    if whatsapp_phone:
        try:
            send_whatsapp_message(whatsapp_phone, message)
        except Exception as e:
            print(f"❌ WhatsApp notification error: {e}")

def send_whatsapp_message(phone_number, message):
    """
    Send WhatsApp message using Meta's API
    """
    import requests
    
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Flask route handlers (to be added to main.py)
def handle_9psb_webhook():
    """
    Main webhook handler for 9PSB transactions
    """
    try:
        # Get webhook data
        webhook_data = request.get_json()
        webhook_signature = request.headers.get("X-9PSB-Signature")
        webhook_secret = os.getenv("NINEPSB_WEBHOOK_SECRET")
        
        print(f"📡 9PSB Webhook received: {json.dumps(webhook_data, indent=2)}")
        
        # Verify webhook signature for security
        if webhook_secret and webhook_signature:
            payload_string = json.dumps(webhook_data, sort_keys=True)
            if not verify_9psb_webhook_signature(payload_string, webhook_signature, webhook_secret):
                print("❌ Invalid webhook signature")
                return jsonify({"status": "error", "message": "Invalid signature"}), 401
        
        # Determine transaction type
        transaction_type = webhook_data.get("transactionType") or webhook_data.get("type")
        
        if transaction_type == "credit" or webhook_data.get("amount", 0) > 0:
            result = process_9psb_credit_alert(webhook_data)
        elif transaction_type == "debit" or webhook_data.get("amount", 0) < 0:
            result = process_9psb_debit_alert(webhook_data)
        else:
            print(f"⚠️ Unknown transaction type: {transaction_type}")
            return jsonify({"status": "error", "message": "Unknown transaction type"}), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Test webhook function
def test_9psb_webhook():
    """
    Test the 9PSB webhook with sample data
    """
    print("🧪 Testing 9PSB Webhook...")
    
    # Sample credit alert
    sample_credit = {
        "transactionType": "credit",
        "accountNumber": "1100060144",  # Mosese's account
        "amount": 5000,
        "senderName": "JOHN DOE",
        "senderBank": "ACCESS BANK",
        "reference": "TXN12345678",
        "narration": "Test credit transfer",
        "transactionDate": datetime.utcnow().isoformat()
    }
    
    print("💰 Testing credit alert...")
    result = process_9psb_credit_alert(sample_credit)
    print(f"Result: {result}")
    
    # Sample debit alert
    sample_debit = {
        "transactionType": "debit",
        "accountNumber": "1100060144",  # Mosese's account
        "amount": 2000,
        "recipientName": "JANE SMITH",
        "recipientBank": "GTBANK",
        "recipientAccount": "0123456789",
        "reference": "TXN87654321",
        "narration": "Test debit transfer",
        "transactionDate": datetime.utcnow().isoformat()
    }
    
    print("💸 Testing debit alert...")
    result = process_9psb_debit_alert(sample_debit)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_9psb_webhook()
