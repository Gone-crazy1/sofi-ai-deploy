"""
Account verification functions for OpenAI Assistant
"""

import logging
from typing import Dict, Any
from utils.bank_api import BankAPI

logger = logging.getLogger(__name__)

async def verify_account_name(account_number: str, bank_name: str, **kwargs) -> Dict[str, Any]:
    """
    Verify account name with bank using Bank API
    
    Args:
        account_number: The account number to verify
        bank_name: The bank name (will be converted to bank code)
        
    Returns:
        Dict with verification result
    """
    try:
        logger.info(f"🔍 Verifying account {account_number} at {bank_name}")
        
        bank_api = BankAPI()
        
        # Get bank code
        bank_code = bank_api._get_bank_code(bank_name)
        if not bank_code:
            logger.warning(f"❌ Unsupported bank: {bank_name}")
            return {
                "verified": False,
                "error": "Unsupported bank",
                "message": f"Sorry, {bank_name} is not supported yet."
            }
        
        # Verify account using async method
        result = await bank_api.verify_account_name(account_number, bank_code)
        
        if result and result.get('success'):
            logger.info(f"✅ Account verified: {result.get('account_name')}")
            return {
                "verified": True,
                "account_name": result.get('account_name'),
                "bank_name": result.get('bank_name', bank_name),
                "account_number": account_number,
                "bank_code": bank_code,
                "message": f"Account verified: {result.get('account_name')} at {bank_name}"
            }
        else:
            error_msg = result.get('error', 'Account verification failed')
            logger.warning(f"❌ Account verification failed for {account_number} at {bank_name}: {error_msg}")
            return {
                "verified": False,
                "error": error_msg,
                "message": "Could not verify this account. Please check the account number and bank name."
            }
            
    except Exception as e:
        logger.error(f"❌ Error verifying account {account_number}: {str(e)}")
        return {
            "verified": False,
            "error": f"Error verifying account: {str(e)}",
            "message": "Sorry, there was an error verifying this account. Please try again."
        }
