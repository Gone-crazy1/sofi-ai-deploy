from typing import Dict, Optional
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def execute_transfer(user_data: dict, transfer: dict) -> tuple[bool, str]:
    """Execute a transfer and return status and receipt/error message"""
    try:
        response = requests.post(
            'http://localhost:5000/transfer',
            json={
                'sender_name': user_data.get('first_name', 'User'),
                'amount': transfer['amount'],
                'recipient_name': transfer['recipient_name'],
                'recipient_account': transfer['account_number'],
                'recipient_bank': transfer['bank']
            }
        )
        
        if response.status_code == 200:
            receipt = generate_pos_style_receipt(
                sender_name=user_data.get('first_name', 'User'),
                amount=transfer['amount'],
                recipient_name=transfer['recipient_name'],
                recipient_account=transfer['account_number'],
                recipient_bank=transfer['bank'],
                balance=user_data.get('balance', 0),
                transaction_id=f"TRF{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            return True, receipt
        else:
            return False, "Transfer failed. Please try again later."
            
    except Exception as e:
        logger.error(f"Transfer error: {str(e)}")
        return False, "Something went wrong with the transfer. Please try again later."

def generate_pos_style_receipt(sender_name, amount, recipient_name, recipient_account, recipient_bank, balance, transaction_id):
    """Generate a POS-style receipt for a transaction."""
    receipt = f"""
=================================
      SOFI AI TRANSFER RECEIPT
=================================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Transaction ID: {transaction_id}
---------------------------------
Sender: {sender_name}
Amount: ₦{amount:,.2f}
Recipient: {recipient_name}
Account: {recipient_account}
Bank: {recipient_bank}
---------------------------------
Balance: ₦{balance:,.2f}
=================================
    Thank you for using Sofi AI!
=================================
"""
    return receipt
