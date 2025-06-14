#!/usr/bin/env python3
"""
🔗 CRYPTO DEPOSIT WEBHOOK HANDLER
================================

This handles incoming crypto deposits and credits user accounts
with the customer-friendly rate system.
"""

from flask import Flask, request, jsonify
import asyncio
from crypto_rate_manager import handle_crypto_deposit
from webhooks.monnify_webhook import send_telegram_message

app = Flask(__name__)

@app.route('/crypto-webhook', methods=['POST'])
def crypto_webhook():
    """Handle crypto deposit notifications"""
    try:
        data = request.get_json()
        
        # Extract deposit information
        user_id = data.get('user_id')
        crypto_type = data.get('crypto_type', '').upper()
        amount = float(data.get('amount', 0))
        tx_hash = data.get('transaction_hash')
        
        if not all([user_id, crypto_type, amount]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Process the deposit
        result_message = asyncio.run(
            handle_crypto_deposit(user_id, crypto_type, amount, tx_hash)
        )
        
        # Send notification to user
        send_telegram_message(user_id, result_message)
        
        return jsonify({
            'success': True,
            'message': 'Crypto deposit processed successfully'
        })
        
    except Exception as e:
        print(f"❌ Crypto webhook error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
