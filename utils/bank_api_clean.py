"""
Bank API Integration for Sofi AI Banking Service
Official Banking Partner: Monnify

This module handles all banking operations including:
- Account verification
- Money transfers
- Bank code mapping for Nigerian banks
"""

import os
import requests
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class BankAPI:
    """Monnify-powered banking operations for Sofi AI"""
    
    def __init__(self):
        self.provider = "monnify"  # Official banking partner
        logger.info("BankAPI initialized with Monnify as banking partner")

    def execute_transfer(self, transfer_data: dict) -> dict:
        """Execute a real transfer via Monnify API"""
        try:
            from monnify.monnify_api import MonnifyAPI
            import uuid
            
            # Initialize Monnify API
            monnify_api = MonnifyAPI()
            
            # Get bank code from bank name
            bank_code = self.get_bank_code(transfer_data['recipient_bank'])
            if not bank_code:
                return {
                    'success': False,
                    'error': f"Unsupported bank: {transfer_data['recipient_bank']}"
                }
            
            # Call Monnify transfer API
            result = monnify_api.execute_transfer({
                'amount': transfer_data['amount'],
                'recipient_account': transfer_data['recipient_account'],
                'recipient_bank': bank_code,
                'recipient_name': transfer_data.get('recipient_name', 'Account Holder'),
                'narration': transfer_data.get('narration', 'Transfer via Sofi AI'),
                'reference': f"SOFI_{uuid.uuid4().hex[:8]}"
            })
            
            # Process Monnify response
            if result.get('success'):
                return {
                    'success': True,
                    'transaction_id': result.get('transaction_id'),
                    'reference': result.get('reference'),
                    'status': result.get('status', 'pending'),
                    'message': 'Transfer initiated successfully',
                    'monnify_response': result
                }
            else:
                error_message = result.get('error', 'Transfer failed')
                return {
                    'success': False,
                    'error': error_message,
                    'monnify_response': result
                }
                
        except Exception as e:
            logger.error(f"Transfer execution error: {str(e)}")
            return {
                'success': False,
                'error': f"Transfer processing error: {str(e)}"
            }

    def verify_account(self, account_number: str, bank_code: str) -> Optional[Dict]:
        """Verify a bank account and return the account holder's name using Monnify's API"""
        try:
            from monnify.monnify_api import MonnifyAPI
            
            # Initialize Monnify API
            monnify_api = MonnifyAPI()
            
            # Call Monnify account verification
            result = monnify_api.verify_account_name(account_number, bank_code)
            
            if result.get('success'):
                return {
                    "account_name": result.get('account_name'),
                    "account_number": account_number,
                    "bank_code": bank_code,
                    "verified": True
                }
            else:
                logger.warning(f"Account verification failed: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error verifying account: {str(e)}")
            return None

    def get_bank_code(self, bank_name: str) -> Optional[str]:
        """Get the bank code for a given bank name - COMPREHENSIVE NIGERIAN BANKS & FINTECH"""
        # Complete mapping of Nigerian banks and fintech platforms
        bank_codes = {
            # Traditional Banks
            "access": "044",
            "access bank": "044",
            "gtb": "058",
            "gtbank": "058",
            "guaranty trust": "058",
            "gt bank": "058",
            "zenith": "057",
            "zenith bank": "057",
            "first bank": "011",
            "firstbank": "011",
            "fbn": "011",
            "uba": "033",
            "united bank for africa": "033",
            "fidelity": "070",
            "fidelity bank": "070",
            "fcmb": "214",
            "first city monument bank": "214",
            "sterling": "232",
            "sterling bank": "232",
            "wema": "035",
            "wema bank": "035",
            "union": "032",
            "union bank": "032",
            "polaris": "076",
            "polaris bank": "076",
            "keystone": "082",
            "keystone bank": "082",
            "eco bank": "050",
            "ecobank": "050",
            "heritage": "030",
            "heritage bank": "030",
            "stanbic": "221",
            "stanbic ibtc": "221",
            "standard chartered": "068",
            "citi bank": "023",
            "citibank": "023",
            
            # Digital Banks & Fintech (Supported by Monnify)
            "kuda": "50211",
            "kuda bank": "50211",
            "carbon": "565",
            "carbon microfinance bank": "565",
            "vfd": "566",
            "vfd microfinance bank": "566",
            "taj": "302",
            "taj bank": "302",
            "sun trust": "100",
            "suntrust": "100",
            "titan": "102",
            "titan trust bank": "102",
            "coronation": "559",
            "coronation merchant bank": "559",
            "rand": "559",
            "rand merchant bank": "559",
            "providus": "101",
            "providus bank": "101",
            "jaiz": "301",
            "jaiz bank": "301",
            "lotus": "303",
            "lotus bank": "303",
            "diamond": "063",
            "diamond bank": "063",
            
            # Digital Platform Aliases
            "alat": "035",  # Wema ALAT
            "alat by wema": "035",
            "gtworld": "058",  # GTBank digital
        }
        
        # Return bank code or None if not found
        return bank_codes.get(bank_name.lower())

    def get_supported_banks(self) -> Dict:
        """Get list of banks supported by Monnify"""
        try:
            from monnify.monnify_api import MonnifyAPI
            
            monnify_api = MonnifyAPI()
            result = monnify_api.get_banks()
            
            if result.get('success'):
                return {
                    'success': True,
                    'banks': result.get('data', []),
                    'count': result.get('count', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to get banks')
                }
                
        except Exception as e:
            logger.error(f"Error getting supported banks: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_virtual_account(self, customer_data: Dict) -> Dict:
        """Create virtual account for customer using Monnify"""
        try:
            from monnify.monnify_api import MonnifyAPI
            
            monnify_api = MonnifyAPI()
            result = monnify_api.create_virtual_account(customer_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating virtual account: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_transaction_status(self, reference: str) -> Dict:
        """Get transaction status from Monnify"""
        try:
            from monnify.monnify_api import MonnifyAPI
            
            monnify_api = MonnifyAPI()
            result = monnify_api.verify_transaction(reference)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
