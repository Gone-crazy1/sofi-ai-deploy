#!/usr/bin/env python3
"""
Xara-Style Transfer Flow for Sofi AI
Implements the seamless one-line transfer command with beautiful receipts
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from functions.transfer_functions import send_money
from functions.security_functions import verify_pin
from utils.receipt_generator import SofiReceiptGenerator
import asyncio

logger = logging.getLogger(__name__)

class XaraStyleTransfer:
    """Implement Xara-style transfer flow for Sofi AI"""
    
    def __init__(self):
        self.receipt_generator = SofiReceiptGenerator()
        
    def parse_xara_command(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Parse Xara-style command: "9067927398 Opay send 5300"
        Format: [account_number] [bank] send [amount]
        """
        # Clean the message
        message = message.strip()
        
        # Pattern to match: account_number bank send amount
        patterns = [
            r'^(\d{10,11})\s+(\w+)\s+send\s+(\d+(?:\.\d{2})?)$',  # 9067927398 Opay send 5300
            r'^(\d{10,11})\s+(.+?)\s+send\s+(\d+(?:\.\d{2})?)$',  # 9067927398 Access Bank send 5300
        ]
        
        for pattern in patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                account_number = match.group(1)
                bank = match.group(2).strip()
                amount = float(match.group(3))
                
                return {
                    'account_number': account_number,
                    'bank': bank,
                    'amount': amount,
                    'format': 'xara_style'
                }
        
        return None
    
    def normalize_bank_name(self, bank_input: str) -> str:
        """Convert bank input to proper bank name/code"""
        bank_mapping = {
            'opay': 'OPay Digital Services Limited',
            'access': 'Access Bank',
            'gtb': 'Guaranty Trust Bank',
            'zenith': 'Zenith Bank',
            'first': 'First Bank of Nigeria',
            'uba': 'United Bank for Africa',
            'fidelity': 'Fidelity Bank',
            'union': 'Union Bank of Nigeria',
            'sterling': 'Sterling Bank',
            'fcmb': 'First City Monument Bank',
            'wema': 'Wema Bank',
            'unity': 'Unity Bank',
            'keystone': 'Keystone Bank',
            'polaris': 'Polaris Bank',
            'providus': 'Providus Bank',
            'jaiz': 'Jaiz Bank',
            'suntrust': 'SunTrust Bank',
            'titan': 'Titan Trust Bank',
            'globus': 'Globus Bank',
            'parallex': 'Parallex Bank'
        }
        
        bank_lower = bank_input.lower()
        return bank_mapping.get(bank_lower, bank_input)
    
    async def create_xara_style_confirmation(self, chat_id: str, transfer_data: Dict[str, Any], verified_name: str) -> str:
        """Create Xara-style confirmation message"""
        
        confirmation = f"""Click the Verify Transaction button below to complete transfer of *₦{transfer_data['amount']:,.2f}* to *{verified_name}* ({transfer_data['account_number']}) at {transfer_data['bank']}"""
        
        return confirmation
    
    async def create_xara_style_receipt(self, transfer_data: Dict[str, Any]) -> str:
        """Create Xara-style receipt card"""
        
        from datetime import datetime
        
        receipt_card = f"""
🏦 **SOFI AI TRANSFER RECEIPT**

**₦{transfer_data['amount']:,.2f}** ✅ *completed*
*On {datetime.now().strftime('%m/%d/%Y')}*

**Recipient:** {transfer_data['recipient_name']}
**Account number:** {transfer_data['account_number']}
**Bank:** {transfer_data['bank']}
**Reference:** {transfer_data.get('reference', 'N/A')}

*Transfer completed successfully via Sofi AI*
"""
        
        return receipt_card.strip()

# Integration functions for main bot

async def handle_xara_style_command(chat_id: str, message: str, bot) -> bool:
    """
    Handle Xara-style transfer commands in the main bot
    Returns True if message was handled, False if not a Xara command
    """
    
    xara_handler = XaraStyleTransfer()
    
    # Try to parse as Xara command
    parsed_command = xara_handler.parse_xara_command(message)
    if not parsed_command:
        return False
    
    logger.info(f"🎯 Xara-style command detected: {parsed_command}")
    
    try:
        # Step 1: Auto-verify account and get real name
        await bot.send_message(chat_id, "🔍 *Verifying recipient account...*", parse_mode='Markdown')
        
        # Import verification function
        from functions.transfer_functions import verify_account_number
        
        # Normalize bank name
        bank_name = xara_handler.normalize_bank_name(parsed_command['bank'])
        
        # Verify account (this will give us the real name)
        verification_result = await verify_account_number(
            parsed_command['account_number'], 
            bank_name
        )
        
        if not verification_result.get('success'):
            await bot.send_message(
                chat_id, 
                f"❌ *Account verification failed*\n\n{verification_result.get('error', 'Invalid account details')}", 
                parse_mode='Markdown'
            )
            return True
        
        verified_name = verification_result['account_name']
        
        # Step 2: Show Xara-style confirmation
        confirmation_msg = await xara_handler.create_xara_style_confirmation(
            chat_id,
            {**parsed_command, 'bank': bank_name},
            verified_name
        )
        
        # Send confirmation with verify button
        await bot.send_message(
            chat_id,
            confirmation_msg,
            parse_mode='Markdown',
            reply_markup={
                'inline_keyboard': [[
                    {'text': '✅ Verify Transaction', 'callback_data': f'verify_xara_{chat_id}_{parsed_command["account_number"]}_{parsed_command["amount"]}'}
                ]]
            }
        )
        
        # Store transfer data for callback
        # You'd typically store this in a database or memory store
        # For now, we'll use a simple approach
        
        return True
        
    except Exception as e:
        logger.error(f"Error handling Xara command: {e}")
        await bot.send_message(
            chat_id,
            f"❌ *Transfer failed*\n\n{str(e)}",
            parse_mode='Markdown'
        )
        return True

# Test the parser
if __name__ == "__main__":
    handler = XaraStyleTransfer()
    
    test_commands = [
        "9067927398 Opay send 5300",
        "1234567890 Access Bank send 1000",
        "0123456789 gtb send 500.50",
        "invalid command",
        "1234567890 zenith send 2000"
    ]
    
    print("🧪 Testing Xara-Style Command Parser")
    print("=" * 40)
    
    for cmd in test_commands:
        result = handler.parse_xara_command(cmd)
        if result:
            print(f"✅ '{cmd}' → {result}")
        else:
            print(f"❌ '{cmd}' → Not a valid Xara command")
