#!/usr/bin/env python3
"""
🧪 PIN VERIFICATION TEST SERVER
Minimal Flask server to test PIN verification flow without full dependencies
"""

from flask import Flask, request, jsonify, render_template, make_response
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple in-memory storage for testing
test_tokens = {}
test_transactions = {}

class TestSecurePinVerification:
    def __init__(self):
        self.tokens = test_tokens
        self.transactions = test_transactions
        
    def store_pending_transaction(self, transaction_id: str, transaction_data: Dict) -> str:
        """Store transaction and return secure token"""
        # Generate secure token
        secure_token = secrets.token_urlsafe(32)
        
        # Store transaction
        transaction_data['expires_at'] = datetime.now() + timedelta(minutes=15)
        self.transactions[transaction_id] = transaction_data
        
        # Map token to transaction
        self.tokens[secure_token] = {
            'transaction_id': transaction_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=15),
            'used': False
        }
        
        logger.info(f"🔑 Generated test token: {secure_token[:10]}...")
        return secure_token
        
    def get_pending_transaction_by_token(self, secure_token: str) -> Optional[Dict]:
        """Get transaction by secure token"""
        token_data = self.tokens.get(secure_token)
        
        if not token_data:
            logger.warning(f"❌ Invalid token: {secure_token[:10]}...")
            return None
            
        if datetime.now() > token_data['expires_at']:
            logger.warning(f"⏰ Expired token: {secure_token[:10]}...")
            return None
            
        if token_data['used']:
            logger.warning(f"🔄 Used token: {secure_token[:10]}...")
            return None
            
        transaction_id = token_data['transaction_id']
        transaction = self.transactions.get(transaction_id)
        
        if not transaction:
            logger.warning(f"❌ Transaction not found: {transaction_id}")
            return None
            
        logger.info(f"✅ Valid token access: {secure_token[:10]}...")
        return transaction
        
    def mark_token_as_used(self, secure_token: str):
        """Mark token as used"""
        token_data = self.tokens.get(secure_token)
        if token_data:
            token_data['used'] = True
            logger.info(f"🔒 Token marked as used: {secure_token[:10]}...")

# Global test instance
test_pin_verification = TestSecurePinVerification()

@app.route("/")
def home():
    return jsonify({
        "service": "PIN Verification Test Server",
        "status": "running",
        "endpoints": [
            "/test-token - Generate test token",
            "/verify-pin?token=TOKEN - PIN verification page", 
            "/api/verify-pin - PIN verification API"
        ]
    })

@app.route("/test-token")
def generate_test_token():
    """Generate a test token for testing"""
    txn_id = f"TEST{uuid.uuid4().hex[:8].upper()}"
    test_data = {
        'chat_id': '12345',
        'user_data': {'id': 'test_user', 'full_name': 'Test User'},
        'transfer_data': {
            'recipient_name': 'John Doe',
            'account_number': '1234567890',
            'bank': 'Test Bank'
        },
        'amount': 5000
    }
    
    secure_token = test_pin_verification.store_pending_transaction(txn_id, test_data)
    
    return jsonify({
        "success": True,
        "transaction_id": txn_id,
        "secure_token": secure_token,
        "pin_url": f"/verify-pin?token={secure_token}",
        "test_instructions": "Use PIN: 1234 for testing"
    })

@app.route("/verify-pin")
def pin_verification_page():
    """PIN verification page with bot detection"""
    user_agent = request.headers.get('User-Agent', '')
    secure_token = request.args.get('token')
    client_ip = request.remote_addr
    
    logger.info(f"📊 /verify-pin accessed - IP: {client_ip}, UA: {user_agent[:50]}..., token: {secure_token[:10] if secure_token else 'None'}...")
    
    # Bot detection
    bot_user_agents = ['TelegramBot', 'TwitterBot', 'facebookexternalhit', 'WhatsApp', 'Slackbot']
    if any(bot in user_agent for bot in bot_user_agents):
        logger.info(f"🤖 Bot preview blocked: {user_agent}")
        return make_response('', 204)
    
    if not secure_token:
        return jsonify({"error": "Missing secure token"}), 400
    
    # Validate token
    transaction = test_pin_verification.get_pending_transaction_by_token(secure_token)
    if not transaction:
        return jsonify({"error": "Invalid or expired token"}), 404
    
    # Return simple HTML PIN form
    transfer_data = transaction.get('transfer_data', {})
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PIN Verification - Sofi AI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .amount {{ font-size: 24px; color: #2196F3; font-weight: bold; text-align: center; margin-bottom: 20px; }}
            .recipient {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .pin-input {{ width: 100%; padding: 15px; font-size: 18px; border: 2px solid #ddd; border-radius: 5px; text-align: center; letter-spacing: 2px; }}
            .submit-btn {{ width: 100%; padding: 15px; background: #2196F3; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
            .submit-btn:hover {{ background: #1976D2; }}
            .error {{ color: red; margin-top: 10px; }}
            .success {{ color: green; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔐 Enter Your PIN</h2>
            
            <div class="amount">₦{transaction['amount']:,.2f}</div>
            
            <div class="recipient">
                <strong>To:</strong> {transfer_data.get('recipient_name', 'Unknown')}<br>
                <strong>Bank:</strong> {transfer_data.get('bank', 'Unknown')}<br>
                <strong>Account:</strong> {transfer_data.get('account_number', 'Unknown')}
            </div>
            
            <form id="pinForm">
                <input type="password" id="pin" class="pin-input" placeholder="Enter 4-digit PIN" maxlength="4" pattern="[0-9]{{4}}" required>
                <button type="submit" class="submit-btn">Verify Transfer</button>
                <div id="message"></div>
            </form>
        </div>
        
        <script>
            document.getElementById('pinForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const pin = document.getElementById('pin').value;
                const messageDiv = document.getElementById('message');
                
                if (pin.length !== 4) {{
                    messageDiv.innerHTML = '<div class="error">Please enter a 4-digit PIN</div>';
                    return;
                }}
                
                messageDiv.innerHTML = '<div>Verifying...</div>';
                
                try {{
                    const response = await fetch('/api/verify-pin', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            secure_token: '{secure_token}',
                            pin: pin
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        messageDiv.innerHTML = '<div class="success">✅ Transfer completed successfully!</div>';
                        setTimeout(() => {{
                            window.close() || (window.location.href = '/');
                        }}, 2000);
                    }} else {{
                        messageDiv.innerHTML = '<div class="error">❌ ' + (result.error || 'Verification failed') + '</div>';
                    }}
                }} catch (error) {{
                    messageDiv.innerHTML = '<div class="error">❌ Connection error. Please try again.</div>';
                }}
            }});
            
            // Auto-focus PIN input
            document.getElementById('pin').focus();
        </script>
    </body>
    </html>
    """
    
    return html

@app.route("/api/verify-pin", methods=["POST"])
def verify_pin_api():
    """PIN verification API"""
    try:
        data = request.get_json()
        secure_token = data.get('secure_token')
        pin = data.get('pin')
        
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if not secure_token or not pin:
            return jsonify({
                'success': False,
                'error': 'Missing token or PIN'
            }), 400
        
        # Get transaction
        transaction = test_pin_verification.get_pending_transaction_by_token(secure_token)
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 400
        
        # Mark token as used
        test_pin_verification.mark_token_as_used(secure_token)
        
        # Simple PIN validation (in real app, this would verify against user's actual PIN)
        if pin == '1234':
            logger.info(f"✅ PIN verified successfully for token: {secure_token[:10]}...")
            return jsonify({
                'success': True,
                'message': 'Transfer completed successfully',
                'transaction_id': transaction.get('transaction_id', 'unknown')
            })
        else:
            logger.warning(f"❌ Invalid PIN attempt for token: {secure_token[:10]}...")
            return jsonify({
                'success': False,
                'error': 'Invalid PIN. Use 1234 for testing.'
            }), 400
        
    except Exception as e:
        logger.error(f"❌ PIN API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == "__main__":
    print("🧪 PIN Verification Test Server Starting...")
    print("=" * 50)
    print("📍 Server: http://localhost:5000")
    print("🔑 Test PIN: 1234")
    print("📝 Steps:")
    print("1. Visit: http://localhost:5000/test-token")
    print("2. Copy the pin_url from response")
    print("3. Open pin_url in browser")
    print("4. Enter PIN: 1234")
    print("=" * 50)
    
    app.run(debug=True, port=5000)
