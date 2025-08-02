"""
WhatsApp API Helper for Read Receipts and Typing Indicators
Fixed implementation using Meta's official typing indicator API
"""

import logging
import requests
import time
import asyncio
from typing import Optional
import os

logger = logging.getLogger(__name__)

class WhatsAppAPI:
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        
        if not self.access_token or not self.phone_number_id:
            logger.error("❌ WhatsApp credentials not configured")
    
    def _get_headers(self):
        """Get headers for WhatsApp API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def mark_message_as_read_with_typing(self, message_id: str) -> bool:
        """
        Mark a WhatsApp message as read AND show typing indicator (Meta's official API)
        
        Args:
            message_id (str): The ID of the message to mark as read
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📨⌨️ Marking message {message_id} as read with typing indicator")
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
                "typing_indicator": {
                    "type": "text"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Message {message_id} marked as read with typing indicator shown")
                return True
            else:
                logger.error(f"❌ Failed to mark message as read with typing: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marking message as read with typing: {e}")
            return False
    
    async def send_message_with_read_and_typing(self, phone_number: str, message: str, 
                                               message_id_to_read: Optional[str] = None,
                                               typing_duration: float = 2.0) -> bool:
        """
        Send a message with proper read receipt and typing using Meta's official API
        
        Args:
            phone_number (str): Recipient's phone number
            message (str): Message to send
            message_id_to_read (str, optional): Message ID to mark as read with typing
            typing_duration (float): How long to wait before sending actual message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Step 1: Mark incoming message as read with typing indicator (Meta's official way)
            if message_id_to_read:
                await self.mark_message_as_read_with_typing(message_id_to_read)
            
            # Step 2: Wait to simulate processing time (typing indicator shows for up to 25 seconds)
            await asyncio.sleep(min(typing_duration, 20))  # Max 20 seconds to be safe
            
            # Step 3: Send the actual message (this dismisses the typing indicator)
            return await self.send_text_message(phone_number, message)
            
        except Exception as e:
            logger.error(f"❌ Error in send_message_with_read_and_typing: {e}")
            return False
    
    async def send_text_message(self, phone_number: str, message: str) -> bool:
        """
        Send a text message via WhatsApp
        
        Args:
            phone_number (str): Recipient's phone number
            message (str): Message text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📤 Sending message to {phone_number}")
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Message sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"❌ Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

# Global instance
whatsapp_api = WhatsAppAPI()
