"""
Airtime Handler for Sofi AI
Handles airtime and data purchase requests
"""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class AirtimeHandler:
    """Handle airtime and data purchase requests"""
    
    def __init__(self):
        self.logger = logger
        
    async def handle_airtime_request(self, chat_id: str, message: str, user_data: dict, virtual_account: dict = None) -> Optional[str]:
        """Process airtime/data purchase requests"""
        try:
            # Import the existing airtime API
            from utils.airtime_api import AirtimeAPI
            from utils.airtime_fallback import get_ussd_codes  # Use this function if fallback needed
            
            # Check for airtime/data keywords
            airtime_keywords = ['airtime', 'recharge', 'top up', 'buy airtime', 'data', 'data plan']
            message_lower = message.lower()
            
            if not any(keyword in message_lower for keyword in airtime_keywords):
                return None  # Not an airtime request
            
            # Extract amount and phone number from message
            import re
            
            # Look for amount
            amount_match = re.search(r'(\d+)', message)
            amount = int(amount_match.group(1)) if amount_match else None
            
            # Look for phone number
            phone_match = re.search(r'(\d{11})', message)
            phone = phone_match.group(1) if phone_match else None
            
            # Use user's phone if not provided
            if not phone and user_data:
                phone = user_data.get('phone_number', '').replace('+234', '0')
            
            if 'data' in message_lower:
                # Handle data purchase
                if amount and phone:
                    try:
                        airtime_api = AirtimeAPI()
                        result = await airtime_api.buy_data(phone, amount)
                        
                        if result.get('success'):
                            return f"✅ Data purchase successful!\n\n💾 {amount}MB data sent to {phone}\n📱 Reference: {result.get('reference', 'N/A')}"
                        else:
                            # Fall back to manual instructions
                            return get_ussd_codes(amount, phone, 'data')
                    except Exception as e:
                        # Fall back to manual instructions
                        return get_ussd_codes(amount, phone, 'data')
                else:
                    return "To buy data, please specify amount and phone number. Example: 'Buy 1000MB data for 08012345678'"
            
            else:
                # Handle airtime purchase
                if amount and phone:
                    try:
                        airtime_api = AirtimeAPI()
                        result = await airtime_api.buy_airtime(phone, amount)
                        
                        if result.get('success'):
                            return f"✅ Airtime purchase successful!\n\n💰 ₦{amount} airtime sent to {phone}\n📱 Reference: {result.get('reference', 'N/A')}"
                        else:
                            # Fall back to manual instructions
                            return get_ussd_codes(amount, phone, 'airtime')
                    except Exception as e:
                        # Fall back to manual instructions
                        return get_ussd_codes(amount, phone, 'airtime')
                else:
                    return "To buy airtime, please specify amount and phone number. Example: 'Buy 1000 airtime for 08012345678'"
            
        except Exception as e:
            self.logger.error(f"Error in airtime handler: {e}")
            return "Sorry, I'm having trouble with airtime services right now. Please try again later."
